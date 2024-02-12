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



# Switches
make_ct_nifti = True
