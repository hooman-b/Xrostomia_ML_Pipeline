"""
Explanation: This config file is designed for the radiomics features and dose extraction.
It contains all the directions and parameters that the user should adjust with his/her condition.

Author: Hooman Bahrdo
Last Revised:...
"""

# NiftiFileMaker Module:
nifti_ct_output_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/NIFTI_CT'
nifti_seg_output_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/NIFTI_segmentation'
seg_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/rtdose'
ct_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/OPC_data/ART Hooman/Hooman_project_data/WeeklyCTs'
rtdose_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/PRI2MA/Now_Has_endpoint_for_at_least_1_toxicity'

# This variable can be any condition. It is used as the criteria for searching contours folders.
# If there is a specific structure in the order of the folders, write it here.
inclusion_criteria_condition_ct = ['\ct']
inclusion_criteria_condition_seg = ['']
# List of OARs, one wants to calculates the radiomics features for it. 
oar_names = ['DLC_Parotid_L', 'DLC_Parotid_R']
# This list is the extra names of the OARs that one wants to calculate the Radiomics Features.
oar_extra_names = ['parotis_li', 'parotis_re', 'Parotid_L_TA', 'Parotid_R_TA']
make_ct_nifti_contour = True

# The part of the link that you want to have in the CT NIFTI file. 
# If it is false the path will be patient_id/ct.nii. It should be
# a number that pinpoint a part of the directory. For example, (-1)
# is the last layer of the folders. NOTE: be sure to put this equal to
# False when you want to calculate CT NIFTI during making segmentation NIFTI files.
extra_folder_nifti_ct = None

# ContourMaker Module
binary_mask_name = 'binary_mask.png'

# ImageMatchChecker Module
inclusion_criteria_checker = ['\ct', '\hals', '\week3', '\w3ct']
image_read_mode = 'Checking'
slide_threshold = 5

# RadiomicsFeatureCalculator Module:
# This is another criteria for the condition of the folders that one store nifti files in it.
seg_nifti_folder_condition = ['']
radiomics_settings = {'binWidth': 25} # One can use other settings such as 'geometryTolerance'
radiomics_df_name = 'Radiomics_features'
radiomics_df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman'
Radiomics_df_type = 'Excel'

# RTDoseCalculator Module
# It can be any condition compatible with the folder structure of the RTDOSE.

rtdose_df_name = 'RTDose'
rtdose_df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman'
rtdose_oar_list = ['DLC_Parotid_L', 'DLC_Parotid_R']
rtdose_df_type = 'Excel'
inclusion_criteria_condition_rtdose = ['']

# Switches
make_ct_nifti = False

make_seg_nifti = False

calculate_radiomics_features = False

calculate_rtdose = True