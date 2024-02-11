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
        self.inclusion_criteria = rc.inclusion_criteria
        self.image_read_mode = rc.image_read_mode

        self.ife = ImageFeatureExtractor()
        self.reader_obj =Reader()

    def making_dir_dicom(self, subf):
            dicom_files = os.listdir(subf)

            if 'IM' in dicom_files[0]:
                sorted_im_dirs = sorted(dicom_files, key=self.im_sort_key)

            elif len(re.findall('_' , dicom_files[0])) > 1:
                sorted_im_dirs = sorted(dicom_files, key=self.uderline_sort_key)
            
            elif '95434' in dicom_files[0] or '1005' in dicom_files[0]: 
                sorted_im_dirs = sorted(dicom_files, key=self.dot_sort_key)

            else:
                sorted_im_dirs = sorted(dicom_files)

            dicom_im_dirs = [os.path.join(subf, im_dir) for im_dir in sorted_im_dirs]

            return dicom_im_dirs

    def finding_ct_match_contour(self, patient_ct_dir, contour_uid_list, slide_threshold=5):
        
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
                        if len(match_uid_list) > slide_threshold:
                            return dicom_images, dicom_im_dirs, dicom_images_uid, subf
                            
                    except Exception as e:
                        print(subf, e)
                        pass
    
