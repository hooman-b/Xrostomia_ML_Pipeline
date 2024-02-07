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
# Transferring output path 
transferring_df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART_DATA2/General_dataframes'


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
column_mapping =   {'UMCG': 'ID', # One can change this one to the desirede labels and features
                    'GESLACHT': 'gender', 
                    'LEEFTIJD': 'age',
                    'Loctum2': 'tumor_location',
                    'N_stage': 'n_stage',
                    'TSTAD_DEF': 't_stage',
                    'HN35_Xerostomia_M06': 'xer_06',
                    'HN35_Xerostomia_M12': 'xer_12'}

# The two following lists will be used to determine the fractions of each week
accelerated_list = ['Accelerated RT', 'Bioradiation']
not_accelerated_list = ['Chemoradiation', 'Conventional RT']

# This mapping dictionary is used to define the definition of weeks. 
# One can easily change the definition by change the fraction of each week.
fraction_range_dict =  {'week1': {'not_accelerated':[0.0, 5.0], 'accelerated': [0.0, 6.0]},
                        'week2': {'not_accelerated':[5.0, 10.0], 'accelerated': [6.0, 12.0]},
                        'week3': {'not_accelerated':[10.0, 15.0], 'accelerated': [12.0, 18.0]},
                        'week4': {'not_accelerated':[15.0, 20.0], 'accelerated': [18.0, 24.0]},
                        'week5': {'not_accelerated':[20.0, 25.0], 'accelerated': [24.0, 30.0]},
                        'week6': {'not_accelerated':[25.0, 30.0], 'accelerated': [30.0, 36.0]},
                        'week7': {'not_accelerated':[30.0, 35.0], 'accelerated': [36.0, 42.0]},
                        'week8': {'not_accelerated':[35.0, 40.0], 'accelerated': [42.0, 48.0]}}

# Transferring Phase
week_list = list(fraction_range_dict.keys())
transferring_file_name = 'Transferring_information'
final_weeklyct_name = 'WeeklyCT_dataframe_final.xlsx'
transferring_filename_excess = ''