"""
Explanation: In the following module, weeklyCT datframes of each folder is made.
Moreover, a final weeklyCT dataframe that contains weeklyCTs information of each 
patient and some of their clinical information is made.

Author: Hooman Bahrdo
Last Revised: 3/28/2024
"""

# General Libraries
import pandas as pd

# Custom Modules
import DataCollectionConfig as dcc


class WeeklyctDataframeMaker():
    """
    Explanation: This class is responsible for creating and managing weekly CT dataframes.

    Inputs: 1. wfe_obj: Object of the WeeklyctFeatureExtractor class.
            2. df_processor_obj: Object of the DataframeProcessor class.
            3. reader_obj: Object of the reader class for reading dataframes.
            4. writer_obj: Object of the writer class for writing dataframes.
            5. log_obj: Object of the logger class for logging events.

    Attributes: 1. general_df_path (str): Path to the general DataFrame.
                2. weeklyct_df_path (str): Path to the weekly CT DataFrame.
                3. save_individual_df (bool): Indicates whether to save individual weekly CT
                   DataFrames.
                4. weeklyct_file_name (str): Name of the weekly CT DataFrame file.
                5. wfe_obj: Object of the WeeklyCT Feature Extractor class.
                6. log_obj: Object of the logger class for logging events.
                7. reader_obj: Object of the reader class for reading dataframes.
                8. writer_obj: Object of the writer class for writing dataframes.
                9. df_processor_obj: Object of the DataFrame processor class.
                10. clinical_df (DataFrame): DataFrame containing clinical data.
                11. desired_file (str): The name of the file that one wants to find and make 
                    the final df from.
                12. common_col (str): This is a string used to merge dataframes based on it.

    Methods: 1. make_a_week_df: Creates a dataframe for a specific week.
             2. make_weeklyct_df: Finds weekly CTs and drops other types of CTs.
             3. save_weeklyct_df: Saves the weekly CT DataFrame.
             4. make_final_weeklyct_df: Creates the final weekly CT DataFrame.
    """
    def __init__(self, wfe_obj, df_processor_obj, reader_obj, writer_obj, log_obj):

        self.common_col = dcc.common_col
        self.desired_file = dcc.desired_file
        self.general_df_path = dcc.general_df_path
        self.weeklyct_df_path = dcc.weeklyct_df_path
        self.save_individual_df = dcc.save_individual_weeklyct_df
        self.weeklyct_file_name = dcc.weeklyct_file_name

        self.wfe_obj = wfe_obj
        self.log_obj = log_obj
        self.reader_obj = reader_obj
        self.writer_obj = writer_obj
        self.df_processor_obj = df_processor_obj
        self.clinical_df = self.reader_obj.read_dataframe(dcc.clinical_df_path,
                                                           dcc.clinical_df_name)


    def make_a_week_df(self, main_df, weeklyct_df, week_name):
        """
        Inputs: 1. main_df (DataFrame): Main DataFrame.
                2. weeklyct_df (DataFrame): DataFrame containing weekly CT data.
                3. week_name (str): Name of the week.
        Explanation: Creates a dataframe for a specific week.
        Output: 1. final_week_df (DataFrame): Final DataFrame for the week.
        """
        week_list = list()
    
        # Iterate through patients
        for _, raw in weeklyct_df.iterrows():
            matching_list = self.wfe_obj.get_fraction_info(raw, week_name)
            self.wfe_obj.process_matching_fractions(raw, matching_list, week_name, week_list)

        # Make a datafrme from the main folder
        week_df = self.df_processor_obj.make_dataframe(week_list)
        
        # Merge the week dataset with path dataset (general dataset)
        final_week_df = self.df_processor_obj.get_merged_df(week_df, main_df)
        
        return final_week_df


    def make_weeklyct_df(self, general_df):
        """
        Inputs: 1. general_df (DataFrame): General DataFrame.
        Explanation: Finds weeklyCTs and drops other types of CTs.
        Outputs: 1. corrected_weeklyct_df (DataFrame): DataFrame containing corrected
                    weekly CT data.
        """
        # Initialize a list to store weekly CT data for each patient
        weekly_cts_group = list()

        # Separate each ID dataframe
        id_df = pd.DataFrame(general_df.groupby([self.common_col]))

        # Iterate through each ID and extract weekly CT features
        for counter, id_num in enumerate(id_df[0]):
            patient_df = id_df[1][counter]
            weekly_cts_group.append(self.wfe_obj.extract_raw_weeklyct_features(id_num[0], patient_df, self.clinical_df))

        # Convert the list of weekly CT data into a DataFrame
        raw_weeklyct_df = self.df_processor_obj.make_dataframe(weekly_cts_group, df_type='WeeklyCT')

        # Correct fractions in the raw weekly CT DataFrame
        corrected_weeklyct_df = self.wfe_obj.correct_fractions(raw_weeklyct_df)

        return corrected_weeklyct_df


    def save_weeklyct_df(self):
        """
        Explanation: Saves the weekly CT DataFrame. This method is used directly into the main pipeline.
        """        
        # Find the name of the general files
        self.log_obj.write_to_logger(f'Looking for preliminary datframe names has been started')  
        general_dfs_names = self.reader_obj.raed_dataframe_names(self.general_df_path, 'general')
        self.log_obj.write_to_logger(f'Following dataframes have been found: {general_dfs_names}')

        # Loop through the names make weeklyCT df based on that and save it.
        for df_name in general_dfs_names:

            try:
                # Read, make, and save a weeklyCT dataframe based on the general df.
                general_df = self.reader_obj.read_dataframe(self.general_df_path, df_name)
                weeklyct_df = self.make_weeklyct_df(general_df)
                self.writer_obj.write_dataframe(df_name, self.weeklyct_file_name, weeklyct_df, 
                                                self.weeklyct_df_path, dcc.navigation_file_name)
                self.log_obj.write_to_logger(f'A dataframe for {df_name} name hass been made and saved')

            except Exception as e:
                self.log_obj.error_to_logger(f'Warning: There is NO possibility to make a dataframe for {df_name} name \nError: {e}')
                pass   


    def make_final_weeklyct_df(self):
        """
        Explanation: This function makes the final weeklyCT dataframe
        """
        try:
            # Find the names of weeklyCT dfs
            self.log_obj.write_to_logger(f'Looking for desired dataframe names has been started')    
            file_names = self.reader_obj.raed_dataframe_names(self.weeklyct_df_path, self.desired_file)
            self.log_obj.write_to_logger(f'Following dataframes have been found: {file_names}')

            # Concate all the weeklyCT dfs in one
            df = self.df_processor_obj.concat_dataframes(file_names, self.weeklyct_df_path, self.reader_obj)
            self.log_obj.write_to_logger(f'Dataframes were concated successfully to one dataframe')

            # Slice the desired part of clinical df
            clinical_df = self.df_processor_obj.get_clinical_dataframe(self.reader_obj,
                                            dcc.clinical_df_path, dcc.clinical_df_name)
            self.log_obj.write_to_logger(f'Clinical datframe has been built')

            # Merge weeklyCT and clinical dfs to make the final df.
            final_weeklyct_df = df.merge(clinical_df, on='ID')
            self.log_obj.write_to_logger(f'Final dataframe has been built')

            # Save the final datframe
            self.writer_obj.write_dataframe(dcc.weeklyct_final_df_name, self.weeklyct_file_name, 
                                            final_weeklyct_df, self.weeklyct_df_path)
            self.log_obj.write_to_logger(f'The final dataframe has been saved successfully')

        except Exception as e:
            self.log_obj.error_to_logger(f'Warning: cannot make the final datframe from {file_names} files.\nError: {e}')
            pass
        
        # If dataframe based on labels is needed
        if dcc.make_label_df:

            try:
                self.log_obj.write_to_logger(f'The used asked for dataframe based on labels...')

                # For each label make its datframe      
                for label in dcc.label_list:     
                    label_df = final_weeklyct_df[final_weeklyct_df[label].notnull()]
                    self.writer_obj.write_dataframe(label, self.weeklyct_file_name, 
                                                    label_df, self.weeklyct_df_path)
                    self.log_obj.write_to_logger(f'A dataframe for {label} label hass been made and saved')
            except Exception as e:
                self.log_obj.error_to_logger(f'Warning: There is NO possibility to make a dataframe for {label} label \nError: {e}')
                pass                


if __name__ == "__main__":
    aaa = WeeklyctDataframeMaker()
    aaa.make_final_weeklyct_df()


