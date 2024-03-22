"""
Note: 
This module make the final dataframe of this study. The user can change some items to make
the dataframe. and all the components can be find in the FinalDfConfig.py file. 

For making the dataset, I would rather use the notebook that I provided in this folder
to see the effect the changes each preprocessig process on the data. However, an automated
pipeline provided here. Consequently, if you just want to make the dataframe and use it in
the next section (Statistical Analysis or Machine Learning/Deep Learning modelling), you 
can use this pipeline. 

NOTE: This pipeline does NOT contain labelizing the catecorical columns since this operation 
is really subjective. In the other words, the user him/herself should decide how to labelize 
these columns or which columns should convert to the dumy columns. So, to prevent HARDCODING,
I provide my labeling functions in the relavant Jupyter Notebook.

User Specific:
there is no need for any adjuctment. All the adjustments can be done in the configue file.

"""

import pandas as pd
import sys

module_directory = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Models/Xrostomia_ML_Pipeline/'
sys.path.append(module_directory)

import FinalDfConfig as fdc
from DfCleaner import DfCleaner
from WeeklyCTs_collection import ReaderWriter



class FinalDataFrameMaker():
    def __init__(self):
        self.main_folder_dir = fdc.main_folder_dir
        self.xer_df_name = fdc.xer_df_name
        self.rf_name_dict = fdc.rf_name_dict
        self.dose_name_dict = fdc.dose_name_dict
        self.clinical_features = fdc.clinical_features
        self.dose_features = fdc.dose_features
        self.rf_features = fdc.rf_features
        self.id_column_name = fdc.id_column_name
        self.delta_num = fdc.delta_num
        self.names_to_change_dict = fdc.names_to_change_dict
        self.column_names_to_drop = fdc.column_names_to_drop
        self.change_position_dict = fdc.change_position_dict

        self.reader_obj = ReaderWriter.Reader()
        self.DfCleaner_obj = DfCleaner(self.reader_obj, self.main_folder_dir)
    
    def make_initial_df(self):
        """
        This function merges all the cleaned initial datframes to gether and make a raw final dataset.
        """
        clinical_df = self.DfCleaner_obj.clean_clinical_df(self.xer_df_name, self.clinical_features, self.id_column_name)
        dose_df_dict = self.DfCleaner_obj.clean_dose_df(self.dose_name_dict, self.dose_features)
        rf_df_dict = self.DfCleaner_obj.clean_radiomics_df(self.rf_name_dict, self.rf_features, dose_df_dict)

        raw_final_df = clinical_df.merge(list(rf_df_dict.values())[0], on=self.id_column_name, how='inner')

        for rf_df in list(rf_df_dict.values())[1:]:
            raw_final_df = raw_final_df.merge(rf_df, on=self.id_column_name, how='inner')
        
        for dose_df in list(dose_df_dict.values()):
            raw_final_df = raw_final_df.merge(dose_df, on=self.id_column_name, how='inner')
        
        return raw_final_df
    
    def make_final_df(self):
        raw_df = self.make_initial_df()
        rf_files_names = list(self.rf_name_dict.keys())

        for number, feature in enumerate(self.rf_features[2:]):
            raw_df[f'Delta_{feature}_{rf_files_names[2*number+1]}'] = \
            (raw_df[f'{feature}_{rf_files_names[2*number+1]}'] - raw_df[f'{feature}_{rf_files_names[2*number]}']) / self.delta_num
        final_df = self.DfCleaner_obj.clean_final_df(raw_df, self.names_to_change_dict,
                                                      self.column_names_to_drop, self.change_position_dict)

        return final_df

if __name__== '__main__':
    dataframe_maker_obj = FinalDataFrameMaker()
    df = dataframe_maker_obj.make_final_df()



