"""
Explanation: This module is used to labelize the categorical columns and making dummy columns from
the pointed columns. In this module, I try to give the freedom to the user to change a column in the 
way that they want; however, a user may want to labelize a column or make dummies in a way that I did 
not introduce here. For solving this problem, I make this module to be compatible to work with another 
module that contains new labelizing functions.

Author: Hooman Bahrdo
Last Revised:...
"""
import pandas as pd

import FinalDfConfig as fdc

class LabelMaker():
    def __init__(self):
        self.labelize_dict = fdc.labelize_dict
        self.dummy_dict = fdc.dummy_dict

    def str_endpoint_label_maker(self, element):
        if element in ['Heel erg', 'Nogal']:
            return 1

        elif element in ['Een beetje', 'Helemaal niet']:
            return 0
        else:
            return element

    def str_little_severe_label_maker(self, element):
        if element in ['Een beetje', 'Heel erg', 'Nogal']:
            return 1

        elif element in ['Helemaal niet']:
            return 0
        
        else:
            return element

    def str_moderate_severe_label_maker(self, element):
        if element in ['Heel erg', 'Nogal']:
            return 2

        elif element in ['Een beetje']:
            return 1
        
        elif element in ['Helemaal niet']:
            return 0
        
        else:
            return element 

    def int_endpoint_label_maker(self, element):
        if element in [3.0, 4.0]:
            return 1

        elif element in [1.0, 2.0]:
            return 0
        else:
            return element

    def int_little_severe_label_maker(self, element):
        if element in [2.0, 3.0, 4.0]:
            return 1

        elif element in [1.0]:
            return 0
        
        else:
            return element

    def str_sex_label_maker(self, element):
        if element in ['Man']:
            return 1
        
        else:
            return 0                     


    def make_dummy_columns(self, df):

        if len(self.dummy_dict) > 0:

            for col_name, name_list in self.dummy_dict.items():
                dummy_columns = pd.get_dummies(df[col_name])
                df = pd.concat([df, dummy_columns], axis=1) 
                
                for number, name in enumerate(name_list):
                    df = df.rename(columns={dummy_columns.columns[number]: name})

        return df

    def labelize_columns(self, df):

        if len(self.labelize_dict) > 0:
            for col_name, method_name in self.labelize_dict.items():
                labelize_method = getattr(self, method_name)
                df[col_name] = [labelize_method(diagnosis) for diagnosis in df[col_name]]

        return df
