"""
Explanation: In this module, Nifti files from different images (CT, RTDOSE,
and Segmentation Map) are made based on the DICOM files.

TODO: Add the make_rtdose_nifti_file

Author: Hooman Bahrdo
Last Revised:...
"""
# General Libraries
import os
import re
import glob
import math
import shutil
import panel as pn
import numpy as np
import pandas as pd
from random import randint
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import time, datetime, date

# Image analysis packages
import cv2
import pydicom
from pydicom.tag import Tag
import nibabel as nib
import SimpleITK as sitk
from radiomics import featureextractor
from skimage.draw import polygon
from PIL import Image, ImageDraw

# Custom Modules
import RadiomicsConfig as rc
from ContourMaker import ContourMaker
from NiftiFileMaker import NiftiFileMaker
from ImageMatchChecker import ImageMatchChecker
from WeeklyCTs_collection.ReaderWriter import Writer, Reader
from WeeklyCTs_collection.ImageFeatureExtractor import ImageFeatureExtractor


class NiftiFileMaker():
    """
    Explanation: This class makes NIFTI files and store them in the desired paths.
    """

    def __init__(self):
        self.ct_path = rc.ct_path
        self.seg_path = rc.seg_path
        self.oar_names = rc.oar_names
        self.oar_extra_names = rc.oar_extra_names
        self.nifti_ct_output_path = rc.nifti_ct_output_path
        self.make_ct_nifti_contour = rc.make_ct_nifti_contour
        self.nifti_seg_output_path = rc.nifti_seg_output_path
        self.inclusion_criteria_condition = rc.inclusion_criteria_condition

        self.cm = ContourMaker()
        self.reader_obj = Reader()
        self.nfm_obj = NiftiFileMaker()
        self.writer_obj = Writer('Excel')
        self.imc_obj = ImageMatchChecker()       
        self.ife_obj = ImageFeatureExtractor()
        # logger_obj = log('main_program.log')



    def save_nifti_files(self, name, matrix, ct_image, nifti_patient_dir, patient_id):
        """
        Explanation: This function saves segmentation maps NIFTI file in a desired direction
        """
        # make affine matrix
        pixel_spacing = [float(x) for x in ct_image.PixelSpacing]
        slice_thickness = float(ct_image.SliceThickness)
        origin = ct_image.ImagePositionPatient 

        # Make and save the NIFTI file
        fm = (matrix / 255).astype('int')

        # Convert NumPy array to SimpleITK image
        image = sitk.GetImageFromArray(fm)

        # Set the spacing, origin, and direction cosines (modify as needed)
        image.SetSpacing((pixel_spacing[0], pixel_spacing[1], slice_thickness))
        image.SetOrigin(origin)
        image.SetDirection(np.identity(3).flatten())
        image.SetMetaData('ID', patient_id)

        # Save the SimpleITK image to a NIfTI file
        sitk.WriteImage(image, os.path.join(nifti_patient_dir, f'{name}.nii'))


    def make_contour_nifti_file(self, filled_contours_dict, ct_image, patient_id):

        # Make folder for each patient in the defined path
        nifti_patient_dir = self.nifti_seg_output_path + f'/{int(patient_id)}'
        self.writer_obj.directory_maker(nifti_patient_dir)

        # Sum the matrices to make a whole matrix
        matrices_list = list(filled_contours_dict.values())
        final_matrix = np.sum(matrices_list, axis=0)

        # Save all the OARs in one mask
        self.save_nifti_files('total', final_matrix, ct_image, nifti_patient_dir)

        # Save each OAR seperately
        for key, value in filled_contours_dict.items():
            self.save_nifti_files(key, value, ct_image, nifti_patient_dir, patient_id)

    def make_ct_nifti_file(self, dicom_im_dirs, patient_id):

        # Make CT NIFTI file
        series_reader = sitk.ImageSeriesReader()
        series_reader.SetFileNames(dicom_im_dirs)

        # Now only by executing series_reader one can have a list of DICOM files!!! Easy pizi
        dicom_files = series_reader.Execute()

        # Make a sitk writer
        assistant_path = os.path.join(self.nifti_ct_output_path, patient_id)
        self.writer_obj.directory_maker(assistant_path)

        nifti_writer = sitk.ImageFileWriter()
        nifti_writer.SetFileName((os.path.join(assistant_path, 'CT.nii')))

        # Convert the DICOM to nifti
        nifti_writer.Execute(dicom_files)

    def save_match_ct(self, patient_id, contour_uid_list):
        # Find the the CT scan that matches this contour 
        dicom_images, dicom_im_dirs, dicom_images_uid = \
        self.imc_obj.find_ct_match_contour(os.path.join(self.ct_path, patient_id) , contour_uid_list)
        # logger_obj.write_to_logger('CT file has been found')

        # Make the CT NIFTI
        if self.make_ct_nifti_contour:
            self.nfm_obj.make_ct_nifti_file(dicom_im_dirs, patient_id)

        return dicom_images, dicom_images_uid

    def process_patient_folder(self, subf):

        try:
            # Implement the inclusion criteria of the folders
            if self.inclusion_criteria_condition:
                directions = os.listdir(subf)

                if '.dcm' in directions[0].lower():
                    # Add the contour image to the IFE object
                    self.ife_obj.make_ct_image(subf)
                    patient_id = str(int(self.ife_obj.get_patient_id()))
                    number_list = self.ife_obj.find_number_list(self.oar_names, self.oar_extra_names)

                    # make a dictionary dor masks
                    filled_contours_dict = {}

                    # logger_obj.write_to_logger(f'Patient {patient_id} has started')

                    for counter, number in enumerate(number_list):

                        try:
                            # call contour sequences and its name
                            contour_sequence = self.ife_obj.get_contour_sequence(number)
                            contour_name = self.ife_obj.get_contour_name(number)
                            contour_uid_list = self.ife_obj.get_contour_uid_list(contour_sequence) # Make a list of contour uids

                            # Only search for images once
                            if counter == 0:
                                dicom_images, dicom_images_uid = self.save_match_ct(patient_id, contour_uid_list)
                            
                        except Exception as e:
                            print(patient_id, e)
                            break

                        # make continous hollow contour matrix
                        contour_matrix = self.cm.make_hollow_contour_matrix(contour_sequence, dicom_images, dicom_images_uid)

                        # fill the hollow contour matrix
                        filled_matrix = self.cm.fill_contours(contour_matrix)

                        # Add each mask to the dictionary
                        filled_contours_dict[contour_name] = filled_matrix
                        # logger_obj.write_to_logger(f'{contour_name} matrix has been made')
                    return filled_contours_dict, dicom_images[0], str(int(patient_id))
    
        except Exception as e:
            print(patient_id, e)
            return None, None, None

    def make_contour_nifti_main(self):
    
        # Loop through all the DLCs
        for r, d, f in os.walk(self.seg_path):
            subfolders = [os.path.join(r, folder) for folder in d]

        for subf in subfolders:
            filled_contours_dict, dicom_image, patient_id = self.process_patient_folder(subf)
            if filled_contours_dict is not None:
                self.make_contour_nifti_file(filled_contours_dict, dicom_image, patient_id)
            else:
                print(f'Warning: contour NIFTI ia not made for {patient_id} ')

    def make_ct_nifti_main(self):

        for r, d, f in os.walk(self.ct_path):

            # make a list from all the directories 
            subfolders = [os.path.join(r, folder) for folder in d]
    
            for subf in subfolders:

                if self.inclusion_criteria_condition:

                    try:
                        self.ife_obj.make_ct_image(os.path.join(subf))
                        patient_id = str(int(self.ife_obj.get_patient_id()))
                        dicom_im_dirs =self.reader_obj.order_dicom_direction(subf)
                        self.nfm_obj.make_ct_nifti_file(dicom_im_dirs, patient_id)

                    except Exception as e:
                        print(subf, e)
                        pass
