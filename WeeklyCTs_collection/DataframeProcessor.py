"""
Explanation: This module is used to gather all the processes on the dataframe just in one module.
"""
import os
import pandas as pd
import DataCollectionConfig as dcc
class DataframeProcessor:

    def __init__(self):
        pass
    
    def make_dataframe(self, group_list, df_type='Normal'):

        try:
            if df_type == 'WeeklyCT':
                # Make a datafrme from the main folder
                df_final = pd.DataFrame(group_list)

                # Drop the patients who does not have weeklyCTs
                df_final = df_final[~(df_final.Number_of_weeklyCTs == 0)]
                df_final = df_final.reset_index().drop(columns=['index'])
                return df_final

            else:
                return pd.DataFrame(group_list)
        
        except Exception as e:
            print(f'Warning: There is an error with this dataset {e}')
            return pd.DataFrame()

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
            final_df = final_df.drop_duplicates(subset=['ID'])

        # Reset the index
        final_df = final_df.sort_values('ID').reset_index().drop(columns=['index'])

        return final_df
    

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