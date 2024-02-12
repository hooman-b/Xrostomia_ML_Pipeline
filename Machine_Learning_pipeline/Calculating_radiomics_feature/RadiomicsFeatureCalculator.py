"""
Explanation: This module calculates radiomics features and saves them in 
an poutput direstion.

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

class RadiomicsFeatureCalculator():

    def __init__(self):
        self.inclusion_criteria_condition = rc.inclusion_criteria_condition
        self.oar_names = rc.oar_names
        self.oar_extra_names = rc.oar_extra_names
        self.make_ct_nifti = rc.make_ct_nifti

        self.cm = ContourMaker()
        self.nfm_obj = NiftiFileMaker()
        self.imc_obj = ImageMatchChecker()       
        self.ife_obj = ImageFeatureExtractor()

    def extract_radiomics_features(self, ct_nifti_dir, dlc_nifti_dir, patient_id, logger_obj):

        radiomics_features_dict = {}

        # Make the direction to CT NIFTI file for each patient
        for r, d, f in os.walk(ct_nifti_dir):
            subfolders = [os.path.join(r, folder) for folder in d]

            if len(subfolders) > 0:
                for subf in subfolders:
                    assistant_path = os.path.join(subf, os.listdir(subf)[0])
                    #print(assistant_path)
            
                    if '.nii' in assistant_path.lower():
                        ct_patient_nifti_file = assistant_path

                #break
            else:
                #file_name = os.listdir(ct_nifti_dir)
                #ct_patient_nifti_file = os.path.join(ct_nifti_dir, file_name[0])

                break
        
        #print(ct_patient_nifti_file)
        # Find the radiomics features for each mask in the patient's folder
        nifti_masks = os.listdir(dlc_nifti_dir)
            
        # Loop through all the masks
        for nifti_mask in nifti_masks:
            nifti_mask_file = os.path.join(dlc_nifti_dir, nifti_mask)

            # find the name of the organ at risk
            oar_name = nifti_mask[:-4]

            # set the extractor for imaging biomarkers
            settings = {}
            settings['binWidth'] = 25 # this is an important setting parameters
            #settings['geometryTolerance'] = 1e-5
            extractor = featureextractor.RadiomicsFeatureExtractor(**settings)

            # Extract radiomics features
            features = extractor.execute(ct_patient_nifti_file, nifti_mask_file) # feature extraction
            
            # Add new features to the dictionary
            radiomics_features_dict[(int(patient_id),oar_name)] = features
            logger_obj.write_to_logger(f'{oar_name} Radiomics Features have been extracted')
            
        return radiomics_features_dict


    def main(self, dlc_path, ct_path, nifti_path, ct_nifti_main_dir, radiomics_features, make_ct_nifti):

        # make logging 
        # logger_obj = log('main_program.log')
        prablematic_patients_dict = {}
        radiomics_features_total_dict = {}

        # Loop through all the DLCs
        for r, d, f in os.walk(dlc_path):
            subfolders = [os.path.join(r, folder) for folder in d]

            try:
                for subf in subfolders:

                        # Implement the inclusion criteria of the folders
                        if self.inclusion_criteria_condition:

                            directions = os.listdir(subf)

                            if '.dcm' in directions[0].lower():

                                contour_dir = os.path.join(subf, directions[0])
                                # Add the contour image to the IFE object
                                self.ife_obj.make_ct_image(contour_dir)

                                # Extract the patient ID
                                patient_id = self.ife_obj.get_patient_id()
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
                                            # Find the the CT scan that matches this contour 
                                            dicom_images, dicom_im_dirs, dicom_images_uid = \
                                            self.imc_obj.find_ct_match_contour(os.path.join(ct_path, patient_id) , contour_uid_list)
                                            # logger_obj.write_to_logger('CT file has been found')

                                            # Make and find the path to the ct nifti file
                                            if make_ct_nifti:
                                                self.nfm_obj.make_ct_nifti_file(ct_nifti_main_dir, patient_id, dicom_im_dirs)

                                            # Find the path to ct NIFTI file
                                            ct_nifti_dir = os.path.join(ct_nifti_main_dir, patient_id)
                                        
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
                                
                                # Save all the masks as NIFTI files #################
                                dlc_nifti_dir = making_contour_nifti_file(filled_contours_dict, dicom_images[0], nifti_path, str(making_integer(patient_id)))

                                logger_obj.write_to_logger('Masks have been saved\n')

                                # Extract radiomics features if radiomics_feature is True
                                if radiomics_features:

                                    radiomics_features_dict = extracting_radiomics_features(ct_nifti_dir, dlc_nifti_dir, patient_id, logger_obj)

                                    # add the new features to the man dictionary
                                    radiomics_features_total_dict.update(radiomics_features_dict)

                                logger_obj.write_to_logger(f'Patient {patient_id} has been finished\n')
                    
            except Exception as e:
                print(patient_id, e)
                prablematic_patients_dict[patient_id] = e
                pass
        
        return radiomics_features_total_dict