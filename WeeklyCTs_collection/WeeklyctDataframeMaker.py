"""
Explanation: In the following module, weeklyCT datframes of each folder is made.
Moreover, a final weeklyCT dataframe that contains weeklyCTs information of each 
patient and some of their clinical information is made.

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


class WeeklyctDataframeMaker():

    def __init__(self):
        self.general_df_path = dcc.general_df_path
        self.weeklyct_df_path = dcc.weeklyct_df_path
        self.save_individual_df = dcc.save_individual_weeklyct_df
        self.weeklyct_file_name = dcc.weeklyct_file_name

        self.wfe = wfe()
        self.reader_obj = Reader()
        self.writer_obj = Writer('Excel')
        self.df_processor_obj = DataframeProcessor()
        self.clinical_df = self.reader_obj.read_dataframe(dcc.clinical_df_path, dcc.clinical_df_name)


    def make_a_week_df(self, main_df, weeklyct_df, week_name):

        week_list = list()
    
        # Iterate through patients
        for _, raw in weeklyct_df.iterrows():
            matching_list = self.wfe.get_fraction_info(raw, week_name)
            self.wfe.process_matching_fractions(raw, matching_list, week_name, week_list)

        # Make a datafrme from the main folder
        week_df = self.df_processor_obj.make_dataframe(week_list)
        
        # Merge the week dataset with path dataset (general dataset)
        final_week_df = self.df_processor_obj.get_merged_df(week_df, main_df)
        
        return final_week_df


    def make_weeklyct_df(self, general_df):
        """
        This function finds weeklyCTs and drops other types of CTs
        """
        weekly_cts_group = list()

        # Separate each ID dataframe
        id_df = pd.DataFrame(general_df.groupby(['ID']))

        for counter, id_num in enumerate(id_df[0]):
            patient_df = id_df[1][counter]
            weekly_cts_group.append(self.wfe.extract_raw_weeklyct_features(id_num[0], patient_df, self.clinical_df))

        raw_weeklyct_df = self.df_processor_obj.make_dataframe(weekly_cts_group, df_type='WeeklyCT')
        corrected_weeklyct_df = self.wfe.correct_fractions(raw_weeklyct_df)

        return corrected_weeklyct_df

    def save_weeklyct_df(self):
        
        # Find the name of the general files
        general_dfs_names = self.reader_obj.raed_dataframe_names(self.general_df_path, 'general')

        # Loop through the names make weeklyCT df based on that and save it.
        for df_name in general_dfs_names:
            general_df = self.reader_obj.read_dataframe(self.general_df_path, df_name)
            weeklyct_df = self.make_weeklyct_df(general_df)
            self.writer_obj.write_dataframe(df_name, self.weeklyct_file_name, weeklyct_df, 
                                            self.weeklyct_df_path, dcc.navigation_file_name)


    def make_final_weeklyct_df(self):
        """
        This function makes the final weeklyCT dataframe
        """
        # Find the names of weeklyCT dfs
        file_names = self.reader_obj.raed_dataframe_names(self.weeklyct_df_path, 'weeklyct')

        # Concate all the weeklyCT dfs in one
        df = self.df_processor_obj.concat_dataframes(file_names, self.weeklyct_df_path, self.reader_obj)

        # Slice the desired part of clinical df
        clinical_df = self.df_processor_obj.get_clinical_dataframe(self.reader_obj,
                                         dcc.clinical_df_path, dcc.clinical_df_name)

        # Merge weeklyCT and clinical dfs to make the final df.
        final_weeklyct_df = df.merge(clinical_df, on='ID')

        # Save the final datframe
        self.writer_obj.write_dataframe(dcc.weeklyct_final_df_name, self.weeklyct_file_name, 
                                        final_weeklyct_df, self.weeklyct_df_path)

        # If dataframe based on labels is needed
        if dcc.make_label_df:
            for label in dcc.label_list:
                label_df = final_weeklyct_df[final_weeklyct_df[label].notnull()]
                self.writer_obj.write_dataframe(label, self.weeklyct_file_name, 
                                                label_df, self.weeklyct_df_path)
        
if __name__ == "__main__":
    aaa = WeeklyctDataframeMaker()
    aaa.make_final_weeklyct_df()


