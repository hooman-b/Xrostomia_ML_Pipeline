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
import torch
from datetime import datetime
from itertools import chain, combinations


# Paths
# navigation_path can be a list of paths that user wants to search for WeeklyCTs
navigation_paths = ['//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART_DATA1']
# Genral output path
output_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART_DATA1'

# Navigation Phase
exclusion_set = {'detail', 'ac_ct', 'ld_ct', 'ld ct', 'ac ct'}  # images wanted to be excluded
navi_file_name = 'General_information_{}.xlsx'  # The name of the excel file. it should contain
min_slice_num = 50 # Minum number of slides per folder
modality = 'CT' # Desired modality