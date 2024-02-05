"""
Explanation: This module is used to gather all the processes on the dataframe just in one module.
"""
import pandas as pd
class DataframeProcessor:

    def __init__(self):
        pass
    
    def make_daaframe(self, group_list):
        try:
            return pd.DataFrame(group_list)
        
        except Exception as e:
            print(f'Warning: There is an error with this dataset {e}')
            return pd.DataFrame()

    def clean_dataframe(self, df):
        """
        clean the dataset
        """
        df_copy = df.copy()

        # Slice the part of the dataset after the mentioned time.

        df_copy = df_copy[pd.to_datetime(df_copy.date) > self.time_limit]

        # Drop the doplicated folders
        df_copy = df_copy.drop_duplicates(subset=['ID', 'folder_name', 'date'],
                                        keep='first', inplace=False, ignore_index=True)

        return df_copy
