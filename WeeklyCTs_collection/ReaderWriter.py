"""
Explanation: This program contains all the reading and writing functions and methods.

Author: Hooman Bahrdo
Last Revised:...
"""
import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from joblib import dump, load

class Writer():

    def directory_maker(self, directory):
        """
        Explanation: Creates a directory if it doesn't exist.

        Args:
            directory (str): The directory to create.
        """
        try:
            os.makedirs(directory)
            os.chdir(directory)
            self.logger_obj.write_to_logger(f'Directory {directory} created successfully')

        except OSError:
            os.chdir(directory)
            self.logger_obj.error_to_logger(f'Directory {directory} has already created')

    def make_folder_name_navigation(self, path):

        try:
            path_parts = path.split('/')
            folder_name = path_parts[-1]
        
        except Exception as e:
            print(f'Warning: An exception in finding folder_name happened {e}')
            folder_name = ''
        
        return folder_name


    def write_dataframe(self, folder_path, dataframe, dst_path):
        """
        Input: 1. output_path (str): The name of the configuration key containing
                                     the directory path.
               2. df (pd.DataFrame): The dataframe to save.
               3. file_name (str): The name of the output file.
        """
        folder_name = self.make_folder_name_navigation(self, folder_path)
        self.directory_maker(dst_path)
        # save the dataframe
        dataframe.to_excel(os.path.join(dst_path, folder_name), index=False)
        
