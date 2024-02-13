"""
Explanation: This main module is the only interface that the user can use the
switches to turn off and on the functionalities.

Author: Hooman Bahrdo
Last Revised:...
"""

# General Libraries
import os
import re
import sys
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

module_directory = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Models/Xrostomia_ML_Pipeline/'
sys.path.append(module_directory)

# Custom Modules
import RadiomicsConfig as rc
from ContourMaker import ContourMaker
from NiftiFileMaker import NiftiFileMaker
from ImageMatchChecker import ImageMatchChecker
from RtDoseCalculator import RtDoseCalculator
from WeeklyCTs_collection.ReaderWriter import Writer, Reader
from RadiomicsFeatureCalculator import RadiomicsFeatureCalculator

from WeeklyCTs_collection.ImageFeatureExtractor import ImageFeatureExtractor

class Main():

    def main_pipeline(self):
        nfm_obj = NiftiFileMaker()
        rfc_obj = RadiomicsFeatureCalculator()
        rdc_obj = RtDoseCalculator()

        if rc.make_ct_nifti:
            nfm_obj.make_ct_nifti_main()

        if rc.make_seg_nifti:
            nfm_obj.make_contour_nifti_main()
        
        if rc.calculate_radiomics_features:
            rfc_obj.calculate_radiomics_main()
        
        if rc.calculate_rtdose:
            rdc_obj.calculate_rtdose_main()
        
if __name__ == "__main__":
    main_obj = Main()
    main_obj.main_pipeline()