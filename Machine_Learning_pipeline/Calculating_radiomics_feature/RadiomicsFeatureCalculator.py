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
from WeeklyCTs_collection.DataframeProcessor import DataframeProcessor
class RadiomicsFeatureCalculator():

    def __init__(self):
        self.radiomics_df_name = rc.radiomics_df_name
        self.nifti_ct_output_path = rc.nifti_ct_output_path
        self.nifti_seg_output_path = rc.nifti_seg_output_path
        self.seg_nifti_folder_condition = rc.seg_nifti_folder_condition
        self.radiomics_settings =rc.radiomics_settings
        self.radiomics_df_path = rc.radiomics_df_path
        self.Radiomics_df_type = rc.Radiomics_df_type

        self.cm = ContourMaker()
        self.nfm_obj = NiftiFileMaker()
        self.dp_obj = DataframeProcessor()
        self.imc_obj = ImageMatchChecker()       
        self.ife_obj = ImageFeatureExtractor()
        self.writer_obj = Writer(self.Radiomics_df_type)

    def calculate_radiomics_features(self, contour_nifti_dir, ct_nifti_dir, patient_id):

        radiomics_features_dict = {}
        
        #print(ct_patient_nifti_file)
        # Find the radiomics features for each mask in the patient's folder
        nifti_masks = os.listdir(contour_nifti_dir)
            
        # Loop through all the masks
        for nifti_mask in nifti_masks:
            nifti_mask_file = os.path.join(contour_nifti_dir, nifti_mask)

            # find the name of the organ at risk
            oar_name = nifti_mask[:-4]

            # set the extractor for imaging biomarkers
            extractor = featureextractor.RadiomicsFeatureExtractor(**self.radiomics_settings)

            # Extract radiomics features
            features = extractor.execute(ct_nifti_dir, nifti_mask_file) # feature extraction
            
            # Add new features to the dictionary
            radiomics_features_dict[(int(patient_id),oar_name)] = features
            # logger_obj.write_to_logger(f'{oar_name} Radiomics Features have been extracted')
            
        return radiomics_features_dict


    def calculate_radiomics_main(self):

        radiomics_features_total_dict = {}

        # Loop through all the DLCs
        for r, d, f in os.walk(self.nifti_seg_output_path):
            subfolders = [os.path.join(r, folder) for folder in d]

            try:
                for subf in subfolders:
                    
                    if self.seg_nifti_folder_condition:
                        directions = os.listdir(subf)

                        if '.nii' in directions[0].lower():
                            self.ife_obj.make_ct_image_nifti(subf)
                            patient_id = self.ife_obj.get_contour_patient_id(subf)
                            ct_nifti_path = self.imc_obj.find_ct_match_contour_nifti(self.nifti_ct_output_path, patient_id)

                            radiomics_features_dict = self.calculate_radiomics_features(subf, ct_nifti_path, patient_id)

                            # add the new features to the man dictionary
                            radiomics_features_total_dict.update(radiomics_features_dict)

            except Exception as e:
                print(f'Warning: an error occurs {e}')
                pass
        
        # Make the dataframe
        df = self.dp_obj.make_dataframe_radiomics(radiomics_features_total_dict)
        # Save the dataframe
        self.writer_obj.write_dataframe(self.nifti_seg_output_path, self.radiomics_df_name, df, self.radiomics_df_path)
        
        return df