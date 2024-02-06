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
        

    def make_transferring_df(self):

        # Make a dataframe from all the general files
        file_names = self.reader_obj.raed_dataframe_names(self.general_df_path , 'general')
        general_df = self.df_processor_obj.concat_dataframes(file_names, self.general_df_path , self.reader_obj)
        weekly_df = self.reader_obj.read_dataframe(self, self.weeklyct_df_path, self.final_weeklyct_name)
        final_transferring_df = self.df_processor_obj.concat_transferring_df(self, general_df, weekly_df, self.week_list)

        # Save the final datframe
        self.writer_obj.write_dataframe(dcc.transferring_filename_excess, self.transferring_file_name, 
                                        final_transferring_df, self.transferring_df_path)