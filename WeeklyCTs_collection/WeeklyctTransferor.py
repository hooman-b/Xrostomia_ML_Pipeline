"""
Explanation: This module contains  making the transferring Dataframe, and also use
the dataframe to transfer CTs to the destination folder.

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

# DICOM Libraries
import pydicom as pdcm
from pydicom.tag import Tag

# Custom Modules
import DataCollectionConfig as dcc
from ReaderWriter import Reader, Writer
from DataframeProcessor import DataframeProcessor
from WeeklyctFeatureExtractor import WeeklyctFeatureExtractor as wfe
from WeeklyctDataframeMaker import WeeklyctDataframeMaker
class TransferringWeeklycts():
    
    def __init__(self):
        self.general_df_path = dcc.general_df_path
        self.final_weeklyct_name = dcc.final_weeklyct_name
        self.weeklyct_df_path = dcc.weeklyct_df_path
        self.week_list = dcc.week_list
        self.transferring_file_name = dcc.transferring_file_name
        self.transferring_df_path = dcc.transferring_df_path
        self.reader_obj = Reader()
        self.writer_obj = Writer('Excel')
        self.df_processor_obj = DataframeProcessor()
        self.weeklyct_df_maker = WeeklyctDataframeMaker()

    def make_transferring_df(self):

        # Make a dataframe from all the general files
        file_names = self.reader_obj.raed_dataframe_names(self.general_df_path , 'general')
        general_df = self.df_processor_obj.concat_dataframes(file_names, self.general_df_path , self.reader_obj)
        weekly_df = self.reader_obj.read_dataframe(self.weeklyct_df_path, self.final_weeklyct_name)
        final_transferring_df = self.df_processor_obj.concat_transferring_df(general_df, weekly_df,
                                                                              self.week_list, self.weeklyct_df_maker)

        # Save the final datframe
        self.writer_obj.write_dataframe(dcc.transferring_filename_excess, self.transferring_file_name, 
                                        final_transferring_df, self.transferring_df_path)


    def transfering_weeklycts(self):

        # Find the name of the general files
        transfer_df_name = self.reader_obj.raed_dataframe_names(self.transferring_df_path, 'transfer')
        transferring_df = self.reader_obj.read_dataframe(self.transferring_df_path, transfer_df_name[0])

        # Keep track of the patients
        previous_patient_id = None

        # For each CT scan, iterate through the information
        for index, row in transferring_df.iterrows():
            current_patient_id = row.ID

            if current_patient_id != previous_patient_id:
                print(f'Transferring data for patient {current_patient_id} is started')

            # List the direction to the DICOM files
            dicom_files = os.listdir(row.path)

            # Make the destination directory
            final_destination_path = os.path.join(self.transferring_df_path, str(row.ID),
                                                   str(f'{row.treatment_week}_{row.Fraction_magnitude}'))

            # Try to make the destination directory
            self.writer_obj.directory_maker(final_destination_path)

            # Loop through all the CT images
            for file in dicom_files:
                src_path = os.path.join(row.path, file)
                dst_path = os.path.join(final_destination_path, file)

                # Transfer the data to the destination directory
                self.writer_obj.copy_file(src_path, dst_path)

            # Check whether this patient has finished
            if current_patient_id != previous_patient_id :
                previous_patient_id  = current_patient_id
                print(f'Transferring data for patient {current_patient_id} is ended {index}')



if __name__ == "__main__":
    aaa = TransferringWeeklycts()
    aaa.transfering_weeklycts()
