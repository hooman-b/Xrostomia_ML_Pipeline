"""
Explanation: This module is used to gather all the processes on the dataframe just in one module.
"""


import os
import sys
import pandas as pd

module_directory = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Models/Xrostomia_ML_Pipeline/WeeklyCTs_collection'
sys.path.append(module_directory)

import DataCollectionConfig as dcc

class DataframeProcessor():
    
    def get_merged_df(self, week_df, main_df):
        """
        This function is used to make a week dataset
        """
        try:
            final_df = week_df.merge(main_df, on=['ID', 'date']).drop(columns=['fraction'])
        
        except KeyError:
            print(f'Warning: this week dataset has {week_df.shape} shape')
            final_df = pd.DataFrame()
        
        return final_df

    def make_dataframe(self, group_list, df_type='Normal'):

        try:
            if df_type == 'WeeklyCT':
                # Make a datafrme from the main folder
                df_final = pd.DataFrame(group_list)

                # Drop the patients who does not have weeklyCTs
                df_final = df_final[~(df_final.Number_of_weeklyCTs == 0)]
                df_final = df_final.reset_index().drop(columns=['index'])
                return df_final

            elif df_type == 'RTDose':
                # Initialize an empty DataFrame
                df = pd.DataFrame()

                # Loop through each dictionary in the list
                for item in group_list:
                    # Extract the key (column name) and its corresponding dictionary
                    for key, value in item.items():
                        # Append the dictionary as a row to the DataFrame, specifying the index as the key
                        df = df.append(pd.Series(value, name=key))

                # Reset the index to ensure proper indexing
                df = df.reset_index()
                # Rename the 'index' column to 'Column_Name'
                df = df.rename(columns={'index': 'OAR_num'}) 
                return df
                  
            else:
                df_final = pd.DataFrame(group_list)
                df_final = df_final.reset_index().drop(columns=['index'])
                return df_final
        
        except Exception as e:
            print(f'Warning: There is an error with this dataset {e}')
            return pd.DataFrame()

    def make_dataframe_radiomics(self, radiomics_dict):
        df = pd.DataFrame.from_dict(radiomics_dict).transpose()
        df = df.reset_index()
        df = df.rename(columns={'level_0':'ID', 'level_1':'OAR'})
        
        return df
        
    def clean_dataframe(self, df):
        """
        clean the dataset
        """
        time_limit = dcc.time_limit

        df_copy = df.copy()

        # Slice the part of the dataset after the mentioned time.

        df_copy = df_copy[pd.to_datetime(df_copy.date) > time_limit]

        # Drop the doplicated folders
        df_copy = df_copy.drop_duplicates(subset=['ID', 'folder_name', 'date'],
                                        keep='first', inplace=False, ignore_index=True)

        return df_copy

    def drop_duplicate_columns(self, df):
        # Count the number of non-null session dates
        df['NumNonNullSessions'] = df.iloc[:,1:10].count(axis=1)

        # Drop duplicates keeping the row with the maximum number of non-null session dates
        df = df.sort_values(by='NumNonNullSessions', ascending=False).drop_duplicates(subset='ID')

        # Drop the helper column
        df = df.drop(columns='NumNonNullSessions')

        return df

    def concat_dataframes(self, df_name_list, df_path, reader_obj):
        """
        This function accepts excel and csv files. csvs can be comma-seperated or semicolon-seperated
        """
        # Make an empty df to gather all of the dataframes here.
        final_df = pd.DataFrame()

        for name in df_name_list:
            
            df = reader_obj.read_dataframe(df_path, name)

            try:
                final_df = pd.concat([final_df, df], ignore_index=True)

            except Exception as e:
                print(f'ERROR:error {e} ocurs for {name} folder')
                pass

        # Drop duplicated patients
        if 'weeklyct' in df_name_list[0].lower(): 
            final_df = self.drop_duplicate_columns(final_df)

        # Reset the index
        final_df = final_df.sort_values('ID').reset_index().drop(columns=['index'])

        return final_df
    
    def concat_transferring_df(self, general_df, weekly_df, week_list, weeklyct_df_maker):

        final_transferring_df = pd.DataFrame()

        # Make the datframe for each week and concat all of them to make a dataset
        for week_name in week_list :
            week_df = weeklyct_df_maker.make_a_week_df(general_df, weekly_df, week_name)
            final_transferring_df = pd.concat([final_transferring_df, week_df], ignore_index=True)
        
        # Drop the doplicated folders
        final_transferring_df = final_transferring_df.drop_duplicates(subset=['ID', 'folder_name', 'date'],
                                        keep='first', inplace=False, ignore_index=True)        
        # Sort the dataset based on ID
        final_transferring_df = final_transferring_df.sort_values('ID').reset_index().drop(columns=['index'])

        return final_transferring_df


    def get_clinical_dataframe(self, reader_obj, clinical_df_path, clinical_df_name):
        """
        Slice the part of the df that is necessary for the weeklyCT.
        """
        column_mapping = dcc.column_mapping
        
        # Call the main clinical df
        clinical_df = reader_obj.read_dataframe(clinical_df_path, clinical_df_name)

        # determine the desired columns
        desired_column_list = list(column_mapping.keys())

        # Slice the desired part
        clinical_df = clinical_df.loc[:,desired_column_list]

        # Map the name of the columns to the desired names
        clinical_df = clinical_df.rename(columns=column_mapping)

        return clinical_df