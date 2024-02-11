"""
Explanation: This config file is designed for the radiomics features and dose extraction.
It contains all the directions and parameters that the user should adjust with his/her condition.

Author: Hooman Bahrdo
Last Revised:...
"""

# NiftiFileMaker Module:
nifti_ct_output_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/NIFTI_CT'
nifti_seg_output_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Test_code_hooman/NIFTI_segmentation'

# ContourMaker Module
binary_mask_name = 'binary_mask.png'

# ImageMatchChecker Module
inclusion_criteria = ct_substrings = ['\ct', '\hals', '\week3', '\w3ct']
image_read_mode = 'Checking'