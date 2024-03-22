"""
Note: 
For making the dataset, I would rather use the notebook that I provided in this folder
to see the effect the changes each preprocessig process on the data. However, an automated
pipeline provided here. Consequently, if you just want to make the dataframe and use it in
the next section (Statistical Analysis or Machine Learning/Deep Learning modelling), you 
can use this pipeline. 

User Specific:
1. All the excel or CSV files MUST store in the same folder (main_folder).
2. put the name of the radiomics feature files and RT dose files in dictionaries.
3. NOTE: All the ID columns should have the same name in all the excel files, and you can
 specify it here.
4. NOTE: When making rf_name_dict and dose_name_dict make sure that the first two files of 
 the rf_name_dict file corresponds to the first file in dose_name_dict, the second two files 
 are correspond to the second file in dose_name_dict, and so on. 
5. NOTE: The irst TWO elements in 'dose_features' and 'rf_features' MUST be ID and OAR lists.
6. NOTE: If you want to change the name of the columns in your dataset, assign values to 
 'names_to_change_dict'; otherwise, leave it empty.
7. If one wants to labelize some of the columns, they can use 'labelize_dict'. Keys are names
of the columns, and values are the method's name in LabelMaker class.
8. One can add his/her method to LabelMaker class, it is hardcoding but it is OK :).
"""


# Direcories to the different files
main_folder_dir = 'C:/Users/BahrdoH/OneDrive - UMCG/Hooman/Models/Preprocessing/Delta_radiomics/Feature_extraction_factory/Radiomics_features/'
xer_df_name = 'Xerostomia_dataset.xlsx' # The dataset that contains all the endpoints and necessary clinical features
rf_name_dict = {'baseline_dlc': 'Rf_bsl_dlc_total.xlsx', # Contains radiomics files( NOTE: if you are using deep learning contours be sure to have 'dlc' 
                'week3_dlc': 'Rf_wk3_dlc_total.xlsx'}    # in the names, and if you have manual contours be sure to have 'mc' in the name.)

dose_name_dict = {'dlc_dose': 'DLC_RTDOSE1.xlsx'} # Contains all the RT Dose files ( NOTE: if you are using deep learning contours be sure to have 'dlc' 
                                                  # in the names, and if you have manual contours be sure to have 'mc' in the name.)
# The name of the chosen columns in Clinical Dataset 
clinical_features = ['UMCG', 'GESLACHT', 'LEEFTIJD', 'Modality_adjusted', 'HN35_Xerostomia_BSL', # First one should be the ID column
                       'Loctum2', 'HN35_Xerostomia_W01', 'HN35_Xerostomia_M06', 'HN35_Xerostomia_M12']

# The name of the chosen columns in Dose dataset, NOTE: you can only change the last column unless you did NOT use dicompylercore
# as the rt dose calculater package or you yourself change the name of the columns after making the datset.
dose_features = ['ID', 'name', 'mean']

# The name of the chosen columns in Radiomics Feature dataset
rf_features = ['ID', 'OAR', 'original_shape_SurfaceArea']

# Specify the ID name in different folders
id_column_name = 'ID'

# The number that should be devided to the DELTA feature
delta_num = 100.

# make a dictionary from the column names that you want to change
names_to_change_dict = {'GESLACHT': 'sex', 'LEEFTIJD': 'age',
                         'HN35_Xerostomia_BSL': 'xer_bsl', 'HN35_Xerostomia_W01': 'xer_wk1',
                         'HN35_Xerostomia_M06': 'xer_06', 'HN35_Xerostomia_M12': 'xer_12',
                         'original_shape_SurfaceArea_baseline_dlc': 'Surface_bsl_dlc',
                         'original_shape_SurfaceArea_week3_dlc': 'Surface_wk3_dlc',
                         'Delta_original_shape_SurfaceArea_week3_dlc': 'Delta_surface_dlc',
                         'OAR_dlc_dose': 'OAR'}

# If you want to drop some columns from the dataset, put them in the following list; otherwise leave it empty.
column_names_to_drop = ['OAR_baseline_dlc', 'OAR_week3_dlc']

# If you want to change the position of a column add index and column name elements; otherwise leave it empty.
change_position_dict = {'index': [1],
                        'col_name': ['OAR']}

# If you need to copy and add a column to the dataset, use the following{'new_name': 'column_name'}
copy_column_dict = {'xer_bsl_citor': 'xer_bsl'}

# The following is the dictionary that one can use to labelize some of the columns
labelize_dict = {'xer_bsl': 'str_little_severe_label_maker',
                 'xer_bsl_citor': 'str_moderate_severe_label_maker',
                 'xer_wk1': 'str_moderate_severe_label_maker',
                 'xer_06': 'str_endpoint_label_maker',
                 'xer_12': 'str_endpoint_label_maker',
                 'sex': 'str_sex_label_maker'}

# The following dictionary is used when you want to make dummy column. NOTE: you MUST provide the name of the new columns.
dummy_dict = {'xer_bsl_citor': ['xer_bsl_not_at_all', 'xer_bsl_little', 'xer_bsl_moderate_to_severe'],
              'xer_wk1': ['xer_wk1_not_at_all', 'xer_wk1_little', 'xer_wk1_moderate_to_severe']}

# List of available labels in the dataset
endpoint_list = ['xer_06', 'xer_12']

# parameters for making a new column that contains train-validation, test labels
train_test = True
random_seed = 42
test_size = 0.2

# Variables for saving the dataframes
writer_type = 'Excel'
file_name_main = 'final_df.xlsx'
dst_path = 'C:/Users/BahrdoH/OneDrive - UMCG/Hooman/Models/Preprocessing/Delta_radiomics/Feature_extraction_factory/Radiomics_features/'
