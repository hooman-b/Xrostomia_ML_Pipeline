"""
Explanation: This program contains all the reading and writing functions and methods.

Author: Hooman Bahrdo
Last Revised:...
"""
import os
import re
import cv2
import joblib
import shutil
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from joblib import dump, load

# Custom Modules
# import DataCollectionConfig as dcc

class Reader():
    # def read_general_dataframe_names(self, path):

    #     general_df_name_list = list()

    #     file_names = os.listdir(path)

    #     for name in file_names:
    #         if 'general' in name.lower():
    #             general_df_name_list.append(name)
    #     return general_df_name_list

    def read_cv2_image(self, name):
        try:
            image = cv2.imread(name)

        except Exception as e:
            print(f'Warning: loading cv2 image has faild {e}')
            image = None
        return image

    def raed_dataframe_names(self, path, desired_file):
        """
        This function makes the list of the desired file names. It can be weeklyCT files or General files
        """

        # Find all the relavant dataframes
        file_list = os.listdir(path)
        desired_file_list = [file_name for file_name in file_list if desired_file in file_name.lower()]

        return desired_file_list

    def read_dataframe(self, df_path, name, drop_unnammed = True):

        try:
            # If the file is an excel file
            if '.xlsx' in name:
                df = pd.read_excel(os.path.join(df_path, name))
                
            # If the file is a csv file
            elif '.csv' in name:
                df = pd.read_csv(os.path.join(df_path, name)) # Comma seperated

                # If the csv file is semi-colon seperated
                if ';' in df.columns[0]:
                    df = pd.read_csv(os.path.join(df_path, name), sep=';')

            # Erase the index columns if there is any
            if any('unnamed' in col_name.lower() for col_name in df.columns) and drop_unnammed:
                excess_column_names = [col_name for col_name in df.columns if 'unnamed' in col_name.lower()]
                df = df.drop(columns=excess_column_names)

            return df

        except FileNotFoundError:
            print(f'Warning: file {name} was not found')
        
        except ValueError:
            print(f'File {name} is not supported by this program.')
    
    def order_dicom_direction(self, subf):
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

    @staticmethod
    def uderline_sort_key(filename):
        name_list = filename.split('_')
        return int(name_list[3])

    @staticmethod
    def im_sort_key(filename):
        return int(filename[2:-4])

    @staticmethod
    def dot_sort_key(filename):
        name_list = filename.split('.')
        return int(name_list[-2])
    
class Writer():

    def __init__(self, writer_type):
        self.writer_type = writer_type

    def copy_file(self, src_path, dst_path):
        try:
            shutil.copy(src_path, dst_path)  # Use shutil.copy to copy the file

        except Exception as e:
            print(f"Error copying file: {e}")

    def directory_maker(self, directory):
        """
        Explanation: Creates a directory if it doesn't exist.

        Args:
            directory (str): The directory to create.
        """
        try:
            os.makedirs(directory)
            os.chdir(directory)
            print(f'Directory {directory} created successfully')

        except OSError:
            os.chdir(directory)
            print(f'Directory {directory} has already created')

    def make_folder_name_navigation(self, path, excess=''):
        
        try:

            # When we have a path
            if '/' in path:
                path_parts = path.split('/')
                folder_name = path_parts[-1]

            # When we have a file name
            elif '.xlsx' in path.lower() or '.csv' in path.lower():
                name_list = path.split('.')
                folder_name = name_list[0].replace(excess, '')
                folder_name = folder_name[1:]

            # When we have the actual name
            else:
               folder_name = path

        except Exception as e:
            print(f'Warning: An exception in finding folder_name happened {e}')
            folder_name = ''
        
        return folder_name

    def write_cv2_image(self, name, image):
        
        try:
            cv2.imwrite(name, image)
        
        except Exception as e:
            print(f'Warning: {e} happend during saving cv2 image.')

    def delete_cv2_image(self, name):

        # Check if the file exists
        if os.path.exists(name):
            # Remove the file
            os.remove(name)
        else:
            print(f"The image at {name} does not exist.")

    def write_dataframe(self, folder_path_name, file_name, dataframe, dst_path, excess=''):
        """
        Input: 1. output_path (str): The name of the configuration key containing
                                     the directory path.
               2. df (pd.DataFrame): The dataframe to save.
               3. file_name (str): The name of the output file.
        """
 
        folder_name = self.make_folder_name_navigation(folder_path_name, excess)

        self.directory_maker(os.path.join(dst_path))

        if self.writer_type == 'Excel':
            # save the dataframe
            dataframe.to_excel(os.path.join(dst_path, f'{file_name}_{folder_name}.xlsx'), index=False)
        
        elif self.writer_type == 'CSV':
            # save the dataframe
            dataframe.to_csv(os.path.join(dst_path, f'{file_name}_{folder_name}.csv'), index=False)

    def write_plt_images(self, image, path, name):
        final_dir = self.directory_maker(os.path.join(path, name))
        image.savefig(final_dir)
    
    def write_ml_model(self, model, save_path, model_name):
        final_dir = self.directory_maker(os.path.join(save_path, model_name))

        # Save the model
        joblib.dump(model, final_dir)