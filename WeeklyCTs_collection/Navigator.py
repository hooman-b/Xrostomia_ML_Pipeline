"""
Explanation:
This module contains the first phase of the data collection pipeline, which is navigation 
of multiple folders to find the desired images. These images can be CT, MRI, and PET.

Author: Hooman Bahrdo
Last Revised:...
"""

# General Libraries
import os
import glob
import pandas as pd

# Custom Modules
import DataCollectionConfig as dcc
from ReaderWriter import Writer
from DataframeProcessor import DataframeProcessor
from ImageFeatureExtractor import ImageFeatureExtractor


class Navigator():
    """
    This class searches multiple folders to find a specific type of images
    """

    def __init__(self, df_processor_obj, writer_obj):
        self.navigation_paths = dcc.navigation_paths
        self.time_limit = dcc.time_limit
        self.general_df_path = dcc.general_df_path
        self.exclusion_set = dcc.exclusion_set
        self.navigation_file_name = dcc.navigation_file_name
        self.min_slice_num = dcc.min_slice_num
        self.modality = dcc.modality

        self.df_processor_obj = df_processor_obj
        self.writer_obj = writer_obj


    def _extract_image_information(self, subfolders):
        group = list()
        for subf in subfolders:
            # number of slices (images) in each DICOM folder, and the name of the folders
            slice_num = len(glob.glob(subf+"/*.DCM"))

            # find whether subf is a path and the number of .DCM images is more than 50
            if slice_num > self.min_slice_num:

                # Extract the information of the image 
                feature_extractor_obj = ImageFeatureExtractor(subf)
                folder_name = feature_extractor_obj.get_folder_name()
                
                # Extract the images' information
                if feature_extractor_obj.image.Modality == self.modality and \
                    all(keyword not in folder_name.lower() for keyword in self.exclusion_set):

                    # Add the information of this group to the total dataset
                    group.append(feature_extractor_obj.get_image_information())
        return group

    def navigate_folder(self, path_folder):

        # Make a group to save all the information
        group = list()

        try:
            for r, d, f in os.walk(path_folder):
                # make a list from all the directories 
                subfolders = [os.path.join(r, folder) for folder in d]
                group.extend(self._extract_image_information(subfolders))
        
        except FileNotFoundError as e:
            print(f'Error while navigating folders in path {path_folder}: {e}')

        return group

    def make_image_feature_dfs(self):

        for path_folder in self.navigation_paths:

            # Find all the desired images in different folders
            try:
                folder_list = self.navigate_folder(path_folder)
                folder_dataframe = self.df_processor_obj.make_dataframe(folder_list)
                folder_dataframe = self.df_processor_obj.clean_dataframe(folder_dataframe)
                self.writer_obj.write_dataframe(path_folder, self.navigation_file_name, folder_dataframe, self.general_df_path)
            
            except Exception as e:
                print(f'Warning: path {path_folder} shows the following error: {e}')
                pass
            

def main():
    """
    If somebody wants to navigate some folders without going further, they can use this function.
    """
    navigator_obj = Navigator()
    navigator_obj.make_image_feature_dfs()

if __name__ == "__main__":
    main()




