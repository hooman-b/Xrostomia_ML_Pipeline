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
from WeeklyCTs_collection.ReaderWriter import Writer
import RadiomicsConfig as rc

class NiftiFileMaker():
    """
    Explanation: This class makes NIFTI files and store them in the desired paths.
    """

    def __init__(self):
        self.nifti_ct_output_path = rc.nifti_ct_output_path
        self.nifti_seg_output_path = rc.nifti_seg_output_path

        self.writer_obj = Writer('Excel')

    def saving_nifti_files(self, name, matrix, ct_image, nifti_patient_dir):
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

        # Save the SimpleITK image to a NIfTI file
        sitk.WriteImage(image, os.path.join(nifti_patient_dir, f'{name}.nii'))


    def making_contour_nifti_file(self, filled_contours_dict, ct_image, patient_id):

        # Make folder for each patient in the defined path
        nifti_patient_dir = self.nifti_seg_output_path + f'/{int(patient_id)}'
        self.writer_obj.directory_maker(nifti_patient_dir)

        # Sum the matrices to make a whole matrix
        matrices_list = list(filled_contours_dict.values())
        final_matrix = np.sum(matrices_list, axis=0)

        # Save all the OARs in one mask
        self.saving_nifti_files('total', final_matrix, ct_image, nifti_patient_dir)

        # Save each OAR seperately
        for key, value in filled_contours_dict.items():
            self.saving_nifti_files(key, value, ct_image, nifti_patient_dir)
        
        return nifti_patient_dir

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