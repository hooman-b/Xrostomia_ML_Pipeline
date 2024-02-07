"""
Explanation: In this main file all the phases will be put together to make a whole pipeline.
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

# Bokeh libraries
from bokeh.layouts import gridplot
from bokeh.plotting import ColumnDataSource
from bokeh.models import MultiChoice, LabelSet
from bokeh.io import output_notebook, output_file
from bokeh.plotting import figure, show, row, reset_output

# Custom Modules
from Navigator import Navigator
import DataCollectionConfig as dcc
from ReaderWriter import Reader, Writer
from DataframePanel import DashboardMaker
from DataframeProcessor import DataframeProcessor
from WeeklyctTransferor import TransferringWeeklycts
from WeeklyctDataframeMaker import WeeklyctDataframeMaker
from WeeklyctFeatureExtractor import WeeklyctFeatureExtractor 


class Main():

    def main_pipeline(self):

        # Make objects from supplying class
        reader_obj = Reader()
        writer_obj = Writer(dcc.writer_type)
        df_processor_obj = DataframeProcessor()
        wfe_obj = WeeklyctFeatureExtractor() # Use abbreviation

        if dcc.navigator_switch:
            navigator_obj = Navigator(df_processor_obj, writer_obj)
            navigator_obj.make_image_feature_dfs()
        
        if dcc.weeklyct_df:
            wdm_obj = WeeklyctDataframeMaker(wfe_obj, df_processor_obj, reader_obj, writer_obj) # Use abbreviation
            wdm_obj.save_weeklyct_df()

        if dcc.weeklyct_final_df:
            wdm_obj.make_final_weeklyct_df()
        
        if dcc.transferring_df:
            transferring_obj =  TransferringWeeklycts(wdm_obj, df_processor_obj, reader_obj, writer_obj)
            transferring_obj.make_transferring_df()

        if dcc.transferor:
            transferring_obj.transfering_weeklycts()
        
        if dcc.dashboard:
            dashboard_obj = DashboardMaker()
            dashboard_obj.make_dashboard()

if __name__ == "__main__":
    main_obj = Main()
    main_obj.main_pipeline()