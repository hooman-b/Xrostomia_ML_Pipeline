"""
Explanation:  This module will check whether a ct and segmentation map or
a ct and rt dose image or rt dose images and segmentation maps can match 
based on uid or not

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
from WeeklyCTs_collection.ImageFeatureExtractor import ImageFeatureExtractor
from WeeklyCTs_collection.ReaderWriter import Writer, Reader


class ImageMatchChecker():

    def __init__(self):
        self.inclusion_criteria = rc.inclusion_criteria_checker
        self.slide_threshold = rc.slide_threshold
        # self.image_read_mode = rc.image_read_mode

        self.ife = ImageFeatureExtractor()
        self.reader_obj =Reader()

    def find_ct_match_contour(self, patient_ct_dir, contour_uid_list):
        
        # Loop through all the directories inside this folder
        for r, d, f in os.walk(patient_ct_dir):
            subfolders = [os.path.join(r, folder) for folder in d]

            for subf in subfolders: # Loop through the folders 

                # Find ct files
                if any(substring in subf.lower() for substring in self.inclusion_criteria):
                    match_uid_list = []

                    try:
                        # Find the uid of the images
                        dicom_im_dirs =self.reader_obj.order_dicom_direction(subf)
                        dicom_images = [pydicom.dcmread(path) for path in dicom_im_dirs]
                        dicom_images_uid = [ct_image.SOPInstanceUID for ct_image in dicom_images]
            
                        # Loop through CTs uids
                        for image_uid in dicom_images_uid:

                            if image_uid in contour_uid_list:
                                match_uid_list.append(image_uid)
                        
                        # return the CT that matches the contour
                        if len(match_uid_list) > self.slide_threshold :
                            return dicom_images, dicom_im_dirs, dicom_images_uid
                            
                    except Exception as e:
                        print(subf, e)
                        pass
    
    def find_ct_match_contour_nifti(self, subf, patient_id):

            patient_ct_path = os.path.join(subf, patient_id)
            files_names = os.listdir(patient_ct_path)
            if '.nii' in files_names[0]:
                return os.path.join(patient_ct_path, files_names[0])
            
            else:
                return None
        
    
    def find_rtdose_match_contour(self, path):

        try:
            for r, d, f in os.walk(path):
                subfolders = [os.path.join(r, folder) for folder in d]

                # try:
                for subf in subfolders:

                    directions = os.listdir(subf)

                    if '.dcm' in directions[0].lower() and 'rtdose' in subf.lower():
                        rtdose_path = os.path.join(subf, directions[0])
                        return rtdose_path
        
        except Exception as e:
            print(f'Warning: error {e} has been occured in matching RTDOSE')
            return None