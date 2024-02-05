"""
Explanation:
This module contains the first phase of the data collection pipeline, which is navigation 
of multiple folders to find the desired images. These images can be CT, MRI, and PET.

Author: Hooman Bahrdo
Last Revised:...
"""

# General Libraries
import os
import re
import glob
import math
import shutil
import numpy as np
import pandas as pd
from random import randint
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import time, datetime, date

# DICOM Libraries
import pydicom as pdcm
from pydicom.tag import Tag

# Custom Modules
import DataCollectionConfig
from ImageFeatureExtractor import ImageFeatureExtractor
from ReaderWriter import Writer

class Navigator():
    """
    This class searches multiple folders to find a specific type of images
    """

    def __init__(self):
        self.navigation_paths = DataCollectionConfig.navigation_paths
        self.output_path = DataCollectionConfig.output_path
        self.exclusion_set = DataCollectionConfig.exclusion_set
        self.navigation_file_name = DataCollectionConfig.navigation_file_name
        self.min_slice_num = DataCollectionConfig.min_slice_num
        self.modality = DataCollectionConfig.modality
    
    def navigate_folder(self, path_folder):

        # Make a group to save all the information
        group = list()

        for r, d, f in os.walk(path_folder):
            # make a list from all the directories 
            subfolders = [os.path.join(r, folder) for folder in d]

            for subf in subfolders:
                # number of slices (images) in each DICOM folder, and the name of the folders
                slice_num = len(glob.glob(subf+"/*.DCM"))

                # find whether subf is a path and the number of .DCM images is more than 50
                if slice_num > self.min_slice_num:

                    # Extract the information of the image 
                    feature_extractor_obj = ImageFeatureExtractor(subf)
                    folder_name = feature_extractor_obj.get_folder_name()
                    
                    # Extract the images
                    if feature_extractor_obj.image.Modality == self.modality and \
                        all(keyword not in folder_name.lower() for keyword in self.exclusion_set):

                        # Add the information of this group to the total dataset
                        group.append(feature_extractor_obj.get_image_information())
        
        # Make a datafrme from the main folder
        df = pd.DataFrame(group)

        # # Save the dataframe ###### ADD THIS PART TO READ AND WRITE ########
        # df.to_excel(os.path.join(self.output_path, self.navigation_file_name), index=False)

        return df

    def navigate_folders(self):
    
        writer_obj = Writer()

        for path_folder in self.navigation_paths:
            try:
                folder_dataframe = self.navigate_folder()
                writer_obj.write_dataframe(path_folder, folder_dataframe, self.output_path)
            
            except Exception as e:
                print(f'Warning: path {path_folder} shows the following error: {e}')
                pass
            

def main():
    """
    If somebody wants to navigate some folders without going further, they can use this function.
    """
    navigator_obj = Navigator()
    navigator_obj.navigate_folders()

if __name__ == "__main__":
    main()




