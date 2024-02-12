"""
Explanation: This module is used for RTDose calculation, this is a 
combination of RTSTRUCT and Segmentation map.

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
import nibabel as nib
import SimpleITK as sitk
from pydicom.tag import Tag
from skimage.draw import polygon
from PIL import Image, ImageDraw
from radiomics import featureextractor
from dicompylercore import dicomparser, dvh, dvhcalc

# Custom Modules
import RadiomicsConfig as rc
from ContourMaker import ContourMaker
from NiftiFileMaker import NiftiFileMaker
from ImageMatchChecker import ImageMatchChecker
from WeeklyCTs_collection import DataframeProcessor
from WeeklyCTs_collection.ReaderWriter import Writer, Reader
from WeeklyCTs_collection.ImageFeatureExtractor import ImageFeatureExtractor


class RtDoseCalculator():
    
    def __init__(self):
        self.seg_path = rc.seg_path
        self.oar_names = rc.oar_names
        self.rtdose_df_name = rc.rtdose_df_name
        self.rtdose_df_path = rc.rtdose_df_path
        self.rtdose_oar_list = rc.rtdose_oar_list
        self.rdose_folder_condition = rc.rdose_folder_condition

        self.writer_obj = Writer('Excel')
        self.dp_obj = DataframeProcessor()
        self.imc_obj = ImageMatchChecker()
        self.ife_obj = ImageFeatureExtractor()
        

    def find_patient_rtdose_path(patient_path):
        for r, d, f in os.walk(patient_path):
            subfolders = [os.path.join(r, folder) for folder in d]

            # try:
            for subf in subfolders:

                directions = os.listdir(subf)

                if '.dcm' in directions[0].lower() and 'rtdose' in subf.lower():
                    rtdose_path = os.path.join(subf, directions[0])
                    return(rtdose_path)

    # reference: https://dicompyler-core.readthedocs.io/en/latest/readme.html
    def get_dvh(self, rtstructFile, rtdoseFile, structure_ROI, patient_id):
        RTss = dicomparser.DicomParser(rtstructFile)
        RTstructures = RTss.GetStructures()
        for key, structure in RTstructures.items():
            if RTstructures[key]['name']==structure_ROI:
                calcdvh = dvhcalc.get_dvh(rtstructFile, rtdoseFile, key)
                dvhs = {}
                dvhs[key]  = {
                            'ID': patient_id,                    
                            'name': structure['name'],
                            'max': calcdvh.max,
                            'min': calcdvh.min,
                            'mean':calcdvh.mean,
                            'dose_units': calcdvh.dose_units,
                            'volume_units': calcdvh.volume_units
                            }     
                    
        return dvhs

    def process_patient_folder(self, subf):

        dvh_data = list()
        directions = os.listdir(subf)

        if any('.dcm' in item.lower() for item in directions):
            # Find the patient_id
            self.ife_obj.make_ct_image(subf)
            patient_id = self.ife_obj.get_patient_id()

            patient_rtdose_path = self.imc_obj.find_ct_match_contour(os.path.join(self.rtdose_path, patient_id))
            # print(patient_rtdose_path)

            for oar in self.rtdose_oar_list:

                try:
                    dvh_data.append(self.get_dvh(os.path.join(subf, directions[0]), patient_rtdose_path, oar, patient_id))
                except:
                    print(f'failed !!! There is no {oar} RTDOSE value for {patient_id}')
        
            print(f'Patient {patient_id} has been Done Successfully')

        return dvh_data

    def calculate_rtdose_main(self):
        # Make a raw dataset for RTDOSEs
        dvhreord = list()

        # Loop through all the DLCs
        for r, d, f in os.walk(self.seg_path):
            subfolders = [os.path.join(r, folder) for folder in d]

            for subf in subfolders:
                if self.rdose_folder_condition:
                    dvhreord.append(self.process_patient_folder(subf))
                
        rtdose_df = self.dp_obj.make_dataframe(dvhreord)
        self.writer_obj.write_dataframe(self.seg_path, self.rtdose_df_name, rtdose_df, self.rtdose_df_path)    
