"""
Explanation: This module contains  making the transferring Dataframe, and also use
the dataframe to transfer CTs to the destination folder.

Author: Hooman Bahrdo
Last Revised: 3/28/2024
"""
# General Libraries
import os

# Custom Modules
import DataCollectionConfig as dcc

class TransferringWeeklycts():
    """
    Explanation: This class handles the creation of a transferring DataFrame and transferring CT scans 
                 to the destination folder.

    Inputs: 1. weeklyct_df_maker: Object of the WeeklyctDataframeMaker class.
            2. df_processor_obj: Object of the DataFrame processor class.
            3. reader_obj: Object of the reader class for reading dataframes.
            4. writer_obj: Object of the writer class for writing dataframes.
            5. log_obj: Object of the logger class for logging events.

    Attributes: 1. week_list (list): List of weeks.
                2. general_df_path (str): Path to the general DataFrame.
                3. weeklyct_df_path (str): Path to the weekly CT DataFrame.
                4. final_weeklyct_name (str): Name of the final weekly CT DataFrame file.
                5. common_initial_name (str): Common name for initial dataframes.
                6. transferring_df_path (str): Path to the transferring DataFrame.
                7. common_transfer_name (str): Common name for transferring dataframes.
                8. transferring_file_name (str): Name of the transferring DataFrame file.
                9. log_obj: Object of the logger class for logging events.
                10. reader_obj: Object of the reader class for reading dataframes.
                11. writer_obj: Object of the writer class for writing dataframes.
                12. df_processor_obj: Object of the DataFrame processor class.
                13. weeklyct_df_maker: Object of the WeeklyctDataframeMaker class.

    Methods: 1. make_transferring_df: Creates the transferring DataFrame.
             2. transfering_weeklycts: Transfers weekly CT scans to the destination folder.
    """    
    def __init__(self, weeklyct_df_maker, df_processor_obj, reader_obj, writer_obj, log_obj):

        self.week_list = dcc.week_list
        self.general_df_path = dcc.general_df_path
        self.weeklyct_df_path = dcc.weeklyct_df_path
        self.final_weeklyct_name = dcc.final_weeklyct_name
        self.common_initial_name = dcc.common_initial_name
        self.transferring_df_path = dcc.transferring_df_path
        self.common_transfer_name = dcc.common_transfer_name
        self.transferring_file_name = dcc.transferring_file_name

        self.log_obj = log_obj
        self.reader_obj = reader_obj
        self.writer_obj = writer_obj
        self.df_processor_obj = df_processor_obj
        self.weeklyct_df_maker = weeklyct_df_maker

    def make_transferring_df(self):
        """
        Type: instance method
        Explanation: Creates the transferring dataFrame from initial general datframes.
        """

        try:
            # Make a dataframe from all the general files
            file_names = self.reader_obj.raed_dataframe_names(self.general_df_path , self.common_initial_name)
            general_df = self.df_processor_obj.concat_dataframes(file_names, self.general_df_path , self.reader_obj)
            weekly_df = self.reader_obj.read_dataframe(self.weeklyct_df_path, self.final_weeklyct_name)
            final_transferring_df = self.df_processor_obj.concat_transferring_df(general_df, weekly_df,
                                                                                self.week_list, self.weeklyct_df_maker)

            # Save the final datframe
            self.writer_obj.write_dataframe(dcc.transferring_filename_excess, self.transferring_file_name, 
                                            final_transferring_df, self.transferring_df_path)

        except Exception as e:
            self.log_obj.error_to_logger(f'Warning: There is NO possibility to make a dataframe for {file_names} list of names \nError: {e}')
            pass   

    def transfering_weeklycts(self):
        """
        Type: instance method
        Explanation: Transfers weekly CT scans to the destination folder from all the input folders.
        """
        try:
            # Find the name of the general files
            self.log_obj.write_to_logger(f'Looking for Transferring datframe has been started...')
            transfer_df_name = self.reader_obj.raed_dataframe_names(self.transferring_df_path, self.common_transfer_name)
            transferring_df = self.reader_obj.read_dataframe(self.transferring_df_path, transfer_df_name[0])
            self.log_obj.write_to_logger(f'Following dataframes have been found: {transfer_df_name[0]}')        

        except Exception as e:
            self.log_obj.error_to_logger(f'Warning: There is NO possibility to read {transferring_df} datframe \nError: {e}')

        # Keep track of the patients
        previous_patient_id = None
        self.log_obj.write_to_logger(f'Initializing the process of transferring...')

        # For each CT scan, iterate through the information
        for index, row in transferring_df.iterrows():

            try:
                current_patient_id = row.ID

                if current_patient_id != previous_patient_id:
                    self.log_obj.write_to_logger(f'Transferring data for patient {current_patient_id} is started')

                # List the direction to the DICOM files
                dicom_files = os.listdir(row.path)

                # Make the destination directory
                final_destination_path = os.path.join(self.transferring_df_path, str(row.ID),
                                                    str(f'{row.treatment_week}_{row.Fraction_magnitude}'))

                # Try to make the destination directory
                self.writer_obj.directory_maker(final_destination_path)

                # Loop through all the CT images
                for file in dicom_files:
                    src_path = os.path.join(row.path, file)
                    dst_path = os.path.join(final_destination_path, file)

                    # Transfer the data to the destination directory
                    self.writer_obj.copy_file(src_path, dst_path)

                # Check whether this patient has finished
                if current_patient_id != previous_patient_id :
                    previous_patient_id  = current_patient_id
                    self.log_obj.write_to_logger(f'Transferring data for patient {current_patient_id} is ended {index}')

            except Exception as e:
                self.log_obj.error_to_logger(f'Warning: Process of transferring has been failed for {current_patient_id} patient.\nError: {e}')
                pass


if __name__ == "__main__":
    aaa = TransferringWeeklycts()
    aaa.transfering_weeklycts()
