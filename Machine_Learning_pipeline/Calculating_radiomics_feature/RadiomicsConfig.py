"""
Explanation: This config file is designed for the radiomics features and dose extraction.
It contains all the directions and parameters that the user should adjust with his/her condition.

Author: Hooman Bahrdo
Last Revised:...
"""

# NiftiFileMaker Module:
nifti_ct_output_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/NIFTI_CT'
nifti_seg_output_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/NIFTI_segmentation'
seg_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/segmentation'
ct_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/CT'
rtdose_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/RTDOSE'

# This variable can be any condition. It is used as the criteria for searching contours folders.
# If there is a specific structure in the order of the folders, write it here.
inclusion_criteria_condition = True
# List of OARs, one wants to calculates the radiomics features for it. 
oar_names = ['DLC_Parotid_L', 'DLC_Parotid_R']
# This list is the extra names of the OARs that one wants to calculate the Radiomics Features.
oar_extra_names = ['parotis_li', 'parotis_re', 'Parotid_L_TA', 'Parotid_R_TA']
make_ct_nifti_contour = True

# ContourMaker Module
binary_mask_name = 'binary_mask.png'

# ImageMatchChecker Module
inclusion_criteria_checker = ['\ct', '\hals', '\week3', '\w3ct']
image_read_mode = 'Checking'
slide_threshold = 5

# RadiomicsFeatureCalculator Module:
# This is another criteria for the condition of the folders that one store nifti files in it.
seg_nifti_folder_condition = True 
radiomics_settings = {'binWidth': 25} # One can use other settings such as 'geometryTolerance'
radiomics_df_name = 'Radiomics_features'
radiomics_df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/CT'
Radiomics_df_type = 'Excel'

# RTDoseCalculator Module
# It can be any condition compatible with the folder structure of the RTDOSE.
rdose_folder_condition = True
rtdose_df_name = 'RTDose'
rtdose_df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/RTDOSE'
rtdose_oar_list = ['DLC_Parotid_L', 'DLC_Parotid_R']
rtdose_df_type = 'Excel'

# Switches
make_ct_nifti = True
