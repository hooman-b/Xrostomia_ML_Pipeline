"""
Explanation: This module is used to clean the raw datasets before mergeing
them into one dataframe.

Author: Hooman Bahrdo
Last Revised:...
"""
import pandas as pd

class DfCleaner():
    def __init__(self, reader_obj, main_folder_dir):
        self.main_folder_dir = main_folder_dir
        self.reader_obj = reader_obj


    def clean_clinical_df(self, xer_df_name, clinical_features, id_column_name):
        """
        This functions cleans the clinical dataset that MUST contain label.
        """
        # Slice the necessary part of Xerostomia datset
        xer_df = self.reader_obj.read_dataframe(self.main_folder_dir, xer_df_name)
        xer_df = xer_df.loc[:,clinical_features].reset_index().drop(columns=['index'])
        xer_df[clinical_features[0]] = xer_df[clinical_features[0]].fillna(0).astype(int)
        xer_df.rename(columns={clinical_features[0]: id_column_name}, inplace=True)
       
        return xer_df
    
    def clean_dose_df(self,dose_name_dict, dose_features):
        """
        This function cleans the dose dataset and return to the main class (FinalDataFrameMaker)
        """

        dose_df_dict = {}

        for name, dose_file_name in dose_name_dict.items():
            ## Read and reshape the dose df
            dose_df = self.reader_obj.read_dataframe(self.main_folder_dir, dose_file_name)
            dose_df = dose_df.loc[:,dose_features]
            total_mean = dose_df.groupby(dose_features[0])[dose_features[2]].mean()
            available_oars = list(dose_df.name.unique())

            # Use pivot to reshape the DataFrame
            dose_df = dose_df.pivot(index=dose_features[0], columns=dose_features[1], values=dose_features[2])
            # Reset the index to make 'ID' a regular column
            dose_df.reset_index(inplace=True)
            # Rename the columns for clarity
            dose_df.columns.name = None 
            dose_df[f'OAR_{name}'] = dose_df.idxmin(axis=1)
            # dose_df['OAR'] = dose_df['OAR'].str.replace('DLC_', '')
            dose_df[f'Contra_Dmean_{name}'] = dose_df.min(axis=1)
            dose_df[f'total_Dmean_{name}'] = total_mean.values
            dose_df = dose_df.drop(columns=available_oars)
            dose_df_dict[name] = dose_df
        
        return dose_df_dict
    
    def add_contralateral_rf(self, rf_df, name, dose_df, dose_name):
        """
        This function adds the contralateral oar to the dataset
        """
        rf_df.columns = [f'{col}_{name}' if col in rf_df.columns[2:] else col for col in rf_df.columns]

        if 'dlc' in name.lower():
            rf_final_df = pd.DataFrame()

            for _, raw in dose_df.iterrows():
                assistant_bsl_df = rf_df[rf_df.ID == raw.ID]
                assistant_bsl_df = assistant_bsl_df[assistant_bsl_df.OAR.str.contains(raw[f'OAR_{dose_name}'])]
                rf_final_df = pd.concat([rf_final_df,assistant_bsl_df])

        elif 'mc' in name.lower():
            rf_final_list = []

            for _, raw in dose_df.iterrows():
                assistant_bsl_df = rf_df[(rf_df.ID == raw.ID) & (rf_df.OAR.str.contains(raw[f'OAR_{dose_name}']))]

            if assistant_bsl_df.shape[0] == 0:
                assistant_bsl_df = rf_df[(rf_df.ID == raw.ID) & (rf_df.OAR.str.contains(raw[f'OAR_{dose_name}'].replace('_TA', '')))]


            if assistant_bsl_df.shape[0] > 1:
                for _, row in assistant_bsl_df.iterrows():
                    if 'ta' in row.OAR.lower():
                        rf_final_list.append(row)
            else:
                for _, row in assistant_bsl_df.iterrows():
                    rf_final_list.append(row)

            rf_final_df = pd.DataFrame(rf_final_list)

        rf_final_df.reset_index(drop=True, inplace=True)
        rf_final_df.rename(columns={'OAR': f'OAR_{name}'}, inplace=True)

        return rf_final_df


    def clean_radiomics_df(self, rf_name_dict, rf_features, dose_df_dict):
        """
        This function cleans the radiomics features dataset and return to the main class (FinalDataFrameMaker)
        """
        rf_df_dict = {}

        for number, (name, rf_dose_name) in enumerate(rf_name_dict.items()):
            rf_df = self.reader_obj.read_dataframe(self.main_folder_dir, rf_dose_name, drop_unnammed=False)
            # print(name, rf_df.columns)
            if not set(['ID', 'OAR']).issubset(rf_df.columns):
                rf_df['Unnamed: 0'] = rf_df['Unnamed: 0'].fillna(method='ffill')
                rf_df.rename(columns= {'Unnamed: 0':'ID', 'Unnamed: 1': 'OAR'}, inplace=True)
                rf_df.ID = rf_df.ID.astype(int)
            
            rf_df = rf_df.loc[:, rf_features]
            dose_df = list(dose_df_dict.values())[int(number//2)]
            dose_name = list(dose_df_dict.keys())[int(number//2)]
            rf_df = self.add_contralateral_rf(rf_df, name, dose_df, dose_name)

            rf_df_dict[name] = rf_df
        
        return rf_df_dict

    def clean_final_df(self, raw_df, names_to_change_dict, column_names_to_drop, change_position_dict, copy_column_dict):
        
        # Change the names of the columns to the desired one.
        if len(names_to_change_dict) > 0:
            df = raw_df.rename(columns=names_to_change_dict)
        
        if len(column_names_to_drop) > 0:
            df = df.drop(columns=column_names_to_drop)
        
        if len(change_position_dict) > 0:
            for col_name, new_index in zip(change_position_dict['col_name'], change_position_dict['index']):
                df.insert(new_index, col_name, df.pop(col_name))
        
        if len(copy_column_dict) > 0:
            for new_name, col_name in copy_column_dict.items():
                df[new_name] = df[col_name].copy()

        return df
