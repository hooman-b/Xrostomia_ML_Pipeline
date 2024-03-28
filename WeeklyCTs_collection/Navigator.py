"""
Explanation:
This module contains the first phase of the data collection pipeline, which is navigation 
of multiple folders to find the desired images. These images can be CT, MRI, and PET.

Author: Hooman Bahrdo
Last Revised: 3/28/2024
"""

# General Libraries
import os
import glob

# Custom Modules
import DataCollectionConfig as dcc
from ImageFeatureExtractor import ImageFeatureExtractor


class Navigator():
    """
    Explanation: This class searches multiple folders to find a specific type of images

    Inputs: 1. df_processor_obj: An object of the DataFrame processor class.
            2. writer_obj: An object of the writer class for writing dataframes.
            3. log_obj: An object of the logger class for logging events.

    Attributes: 1. navigation_paths (list): List of paths to navigate through.
                2. time_limit (timestamp): Time limit for navigation like pd.Timestamp('2014-01-01'). 
                3. general_df_path (str): Path to the general DataFrame.
                4. exclusion_set (set): Set of keywords to exclude.
                5. navigation_file_name (str): Name of the navigation file.
                6. min_slice_num (int): Minimum number of slices.
                7. modality (str): Modality of the images.

    Methods: 1. _extract_image_information: Extracts information from images in subfolders.
             2. navigate_folder: Navigates through the specified folder.
             3. make_image_feature_dfs: Makes dataframe based on available images.
    """
    def __init__(self, df_processor_obj, writer_obj, log_obj):
        self.navigation_paths = dcc.navigation_paths
        self.time_limit = dcc.time_limit
        self.general_df_path = dcc.general_df_path
        self.exclusion_set = dcc.exclusion_set
        self.navigation_file_name = dcc.navigation_file_name
        self.min_slice_num = dcc.min_slice_num
        self.modality = dcc.modality
    
        self.feature_extractor_obj = ImageFeatureExtractor()
        self.df_processor_obj = df_processor_obj
        self.writer_obj = writer_obj
        self.log_obj = log_obj


    def _extract_image_information(self, subfolders):
        """
        Inputs: 1. subfolders (list): List of subfolders to extract information from.
        Explanation: Extracts information from images in subfolders.
        Outputs: 1. group (list): List containing extracted information from images.
        """
        group = list()
        for subf in subfolders:
            # number of slices (images) in each DICOM folder, and the name of the folders
            slice_num = len(glob.glob(subf+"/*.DCM"))

            # find whether subf is a path and the number of .DCM images is more than 50
            if slice_num > self.min_slice_num:
                
                # Store the proper CT image in the object
                self.feature_extractor_obj.make_ct_image(subf)
        
                # Extract the information of the image 
                folder_name = self.feature_extractor_obj.get_folder_name()
                
                # Extract the images' information
                if self.feature_extractor_obj.image.Modality == self.modality and \
                    all(keyword not in folder_name.lower() for keyword in self.exclusion_set):

                    # Add the information of this group to the total dataset
                    group.append(self.feature_extractor_obj.get_image_information())
        return group


    def navigate_folder(self, path_folder):
        """
        Inputs: 1. path_folder (str): Path of the folder to navigate through.
        Explanation: Navigates through the specified folder.
        Outputs: 1. group (list): List containing extracted information from images.
        """

        # Make a group to save all the information
        group = list()

        try:
            for r, d, f in os.walk(path_folder):
                # make a list from all the directories 
                subfolders = [os.path.join(r, folder) for folder in d]
                group.extend(self._extract_image_information(subfolders))
        
        except FileNotFoundError as e:
            self.log_obj.write_to_logger(f'Error while navigating folders in path {path_folder}: {e}')

        return group


    def make_image_feature_dfs(self):
        """
        Explanation: Makes dataframe based on available images.
        """
        self.log_obj.write_to_logger(f'{len(self.navigation_paths)} Navigation paths where found')    
        for path_folder in self.navigation_paths:
            self.log_obj.write_to_logger(f'Navigation in {path_folder} has been started')

            # Find all the desired images in different folders
            try:
                folder_list = self.navigate_folder(path_folder)
                self.log_obj.write_to_logger(f'Navigation in {path_folder} has been finished')

                self.log_obj.write_to_logger(f'Making dataframe based on the available WeeklyCTs has been started')
                folder_dataframe = self.df_processor_obj.make_dataframe(folder_list)

                self.log_obj.write_to_logger(f'Cleaning the dataframe...')
                folder_dataframe = self.df_processor_obj.clean_dataframe(folder_dataframe)

                self.writer_obj.write_dataframe(path_folder, self.navigation_file_name, folder_dataframe, self.general_df_path)
                self.log_obj.write_to_logger(f'The dataframe has been saved successfully.')

            except Exception as e:
                self.log_obj.write_to_logger(f'Warning: path {path_folder} shows the following error: {e}')
                pass


def main():
    """
    If somebody wants to navigate some folders without going further, they can use this function.
    """
    navigator_obj = Navigator()
    navigator_obj.make_image_feature_dfs()

if __name__ == "__main__":
    main()




