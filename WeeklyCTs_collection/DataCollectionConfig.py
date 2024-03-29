"""
Note: 
This configuration file belongs to data collection module, and contains all
the constants and also parameters that should be changed by users

User Specific:
the parameters in this section should be adjusted by users.
NOTE: For using the dashboard, one should determine all the input parameters of each page.
      Each page MUST have a title and a show_page boolian, and then other contents can be 
      added freely inside the page. This dashboard considers texts and barcharts related to 
      the clinical aspects and information about weeklCT scans, so for any improve ment like
      adding other types of plots, or other parameters that this program does NOT support, 
      one can add a new module, and link it to the dashboard and the config file.

NOTE: There are two versions for plotting phase, one version is hard-coded one (DataframePannelHardcoded)
      that one needs to change all the parameters inside the classes (that can be easier). Also, another
      version that is the final version (DataframePannel) that every changes should be done inside the 
      config file based on the instructions.

NOTE: The reason that I keep the hard-coded version is that I belieave, working with that can be easier
      particularly for a person who knows python; however, if you do not have any python knowledge, just
      use the soft-coded version (DataframePannel).

"""
import pandas as pd

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
# Dashboard output path
dashboard_df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART Hooman/WeeklyCT Dataset/Program & Docs/Plotting'

# Navigation Phase
exclusion_set = {'detail', 'ac_ct', 'ld_ct', 'ld ct', 'ac ct'}  # images wanted to be excluded
navigation_file_name = 'General_information'  # The name of the excel file. it should contain
time_limit = pd.Timestamp('2014-01-01') # the threshold time (all the images before this time will be removed)
min_slice_num = 50 # Minum number of slides per folder
modality = 'CT' # Desired modality
writer_type = 'Excel' # This determines the typr os savinh files ('Excel', 'CSV')
common_initial_name = 'general' # Common part in the name of initial dataframes

# Make WeeklyCT Dataframe Phase
save_individual_weeklyct_df = True # Whether you want to save an individual dataframe or not
weeklyct_file_name = 'WeeklyCT_dataframe'
make_label_df = True # If you want weeklyCT df based on each folder change this True
label_list = ['xer_06', 'xer_12'] # If the above is false, this program does not count this one
weeklyct_final_df_name = 'final' # Excess part of the final weeklyCT df
desired_file = 'weeklyct' # Key word to help the program can find relevant dataframes
common_col = 'ID' # Column that merging happens based on it

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
common_transfer_name = 'transfer'

# Dashboard phase
# The general title
title = 'Dataset'

# Header color
header_color = '#00C5CD'

# CSS styling
css = '''
.sidebar_button .bk-btn-group button {
    border-radius: 6px;
    font-weight: bolder;
}

.option_button .bk-btn-default.bk-active {
    background-color: #00dcff38;
    font-weight: bold;
    border-color: black;
}
'''

# The following dictionary of dictionaries contains all the pages and column names that one wants to involve
# in the dashboard. One can add as many pages as she/he wants.NOTE: You MUST feel this dictionary if you are 
# using soft-coded version.
pages_dict = {
              {'title': 'Home', ### Page ONE ###
               'show_page': True,
               'text': """
                        ## **Introduction**
                        This panel is made to explain some of the features of the dataset used in my research.
                        It contains one main dataset contains **455** parients. The patients in this dataset can have
                        12- or 6- month endpoint for xerostomia. Moreover, 12 month dataset is a subset of the main
                        dataset that contains **345** patients whose patients only have 12-month endpoint for xerostomia.
                        The patients in the mentioned dataset can have endpoint for 6-month xerostomia. Moreover, the 6-month
                        dataset (contains **418** patients) only contains the patients with 6-month xerostomia endpoint who can have
                        12-month xerostomia endpoint. Finally, 12-6 month dataset (with **310** patients) contains the patients who
                        have both of the endpoints.
                        """},
              {'title': 'Total Datset', ### Page TWO ###
               'show_page': False,
               'text':  """
                        ## Explanation
                        This dataset contains **455** patients from which **345** patients have 12-month xerostimia endpoint, and **418** patients have
                        6-month xerostomia endpoint. The extra columns in this bar plot refers to the number of patient who are diagnosed with
                        positive and negative xerostomia 6 months and 12 months after irradiation.
                        """,
                'file_name': 'Overview_weeklyCT_patients.xlsx',
                'column_names': ['Year', 'First_day', 'Number_of_weeklyCTs', 'modality_adjusted', 'Count_of_weeks',
                            'gender', 'tumor_location', 'age', 'n_stage', 't_stage','xer_06', 'xer_12'],
                'starting_graph': 'Year'
                },
              {'title': '6 month Dataset', ### Page Third ###
               'show_page': False,
               'text':  """
                        ## Explanation
                        This dataset contains **455** patients from which **345** patients have 12-month xerostimia endpoint, and **418** patients have
                        6-month xerostomia endpoint. The extra columns in this bar plot refers to the number of patient who are diagnosed with
                        positive and negative xerostomia 6 months and 12 months after irradiation.
                                 """,
                'file_name': 'Overview_weeklyCT_patients_6month.xlsx',
                'column_names': ['Year', 'First_day', 'Number_of_weeklyCTs', 'modality_adjusted', 'Count_of_weeks',
                            'gender', 'tumor_location', 'age', 'n_stage', 't_stage'],
                'starting_graph': 'Year'
                }
                }

#    ######### Contorl Room :)))) #########
# Here you have access to different switches that can be turned on or off
# based on a part of the pipeline you want to use. I will explain each switch
# in the following part:

# Navigator Switch: If you want to navigate any folder, you need to turn this
# switch ON (True); otherwise, it should be OFF (False).
navigator_switch = True

# WeeklyCT-df Switch: If you want to to make the weeklyCT dataframes based
# on the folders that you have you can just use this switch. you need to turn this
# switch ON (True); otherwise, it should be OFF (False).
weeklyct_df = True

# WeeklyCT-df Switch: If you want to make a whole weeklyCT dataframe based
# on the weeklyCT dfs of all the folders, use this key. you need to turn this
# switch ON (True); otherwise, it should be OFF (False). Note: This step is 
# necessary before making the dashboard since this switch basically make the 
# dataset for dashboard.
weeklyct_final_df = True

# Transferring df Switch: If you want to have a dataframe from all the information
#  regarding the folders in which weeklyCTs are stored, you can use this Switch. you
# need to turn this switch ON (True); otherwise, it should be OFF (False). Note: This
# step is essential before using the transferor since it basically make its dataframe.
transferring_df = True

# Transferor Switch: If you want to transfer the weeklyCT in a new folder you can use
# this switch. you need to turn this switch ON (True); otherwise, it should be OFF (False).
transferor = True

# Dashboard Switch: If you want to have a dashboard from WeeklyCT datasets (final and
# based on labels), you can use this switch. you need to turn this switch ON (True); 
# otherwise, it should be OFF (False). Make sure you make the final WeeklyCT dfs first.
dashboard_hardcoded = False # This one is the hardcoded version of the dahboard
dashboard_softcoded = False # This one is the softcoded version of the dahboard