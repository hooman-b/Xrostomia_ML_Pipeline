"""
Note: 
This configuration file belongs to data collection module, and contains all
the constants and also parameters that should be changed by users

User Specific:
the parameters in this section should be adjusted by users.

"""

import os
import sys
import math
import pandas as pd
from datetime import datetime
from itertools import chain, combinations


# Paths
# navigation_path can be a list of paths that user wants to search for WeeklyCTs
navigation_paths = ['//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART_DATA1', 
                    '//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART_DATA3']
# Path to clinical daframe
clinical_df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART Hooman'
# Genral output path
general_df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART_DATA2/General_dataframes'
# WeeklyCT output path
weeklyct_df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART_DATA2/WeeklyCT_dataframes'


# Navigation Phase
exclusion_set = {'detail', 'ac_ct', 'ld_ct', 'ld ct', 'ac ct'}  # images wanted to be excluded
navigation_file_name = 'General_information'  # The name of the excel file. it should contain
time_limit = pd.Timestamp('2014-01-01') # the threshold time (all the images before this time will be removed)
min_slice_num = 50 # Minum number of slides per folder
modality = 'CT' # Desired modality
general_writer_type = 'Excel' # This determines the typr os savinh files ('Excel', 'CSV')


# Make WeeklyCT Dataframe Phase
save_individual_weeklyct_df = True # Whether you want to save an individual dataframe or not
weeklyct_file_name = 'WeeklyCT_dataframe'
make_label_df = True # If you want weeklyCT df based on each folder change this True
label_list = ['xer_06', 'xer_12'] # If the above is false, this program does not count this one
weeklyct_final_df_name = 'final'

# Clinical df
clinical_df_name = 'Xerostomia_dataset.xlsx' # CONFIG File
# Define a mapping between source and target column names
column_mapping = {'UMCG': 'ID', # One can change this one to the desirede labels and features
                'GESLACHT': 'gender', 
                'LEEFTIJD': 'age',
                'Loctum2': 'tumor_location',
                'N_stage': 'n_stage',
                'TSTAD_DEF': 't_stage',
                'HN35_Xerostomia_M06': 'xer_06',
                'HN35_Xerostomia_M12': 'xer_12'}   