"""
Explanation: In this main file all the phases will be put together to make a whole pipeline.
"""

# Custom Modules
from Logger import Log
from Navigator import Navigator
import DataCollectionConfig as dcc
from ReaderWriter import Reader, Writer
from DataframePanel import DashboardMaker
from DataframeProcessor import DataframeProcessor
from WeeklyctTransferor import TransferringWeeklycts
from WeeklyctDataframeMaker import WeeklyctDataframeMaker
from WeeklyctFeatureExtractor import WeeklyctFeatureExtractor 

class Main():
    """
    Main class responsible for orchestrating the data processing pipeline.
    """
    def main_pipeline(self):
        """
        Executes the DataCollection pipeline based on configurations.
        """

        # Make objects from supplying class
        reader_obj = Reader()
        log_obj = Log('Data_collection.log')
        writer_obj = Writer(dcc.writer_type)
        df_processor_obj = DataframeProcessor()
        wfe_obj = WeeklyctFeatureExtractor() # Use abbreviation

        # Navigator phase
        if dcc.navigator_switch:  
            navigator_obj = Navigator(df_processor_obj, writer_obj, log_obj)
            navigator_obj.make_image_feature_dfs()

        # Weeklyct Dataframe creation phase        
        if dcc.weeklyct_df:
            wdm_obj = WeeklyctDataframeMaker(wfe_obj, df_processor_obj, reader_obj, writer_obj) # Use abbreviation
            wdm_obj.save_weeklyct_df()

        # Final Weeklyct Dataframe creation phase
        if dcc.weeklyct_final_df:
            wdm_obj.make_final_weeklyct_df()

        # Making transferring df phase     
        if dcc.transferring_df:
            transferring_obj =  TransferringWeeklycts(wdm_obj, df_processor_obj, reader_obj, writer_obj)
            transferring_obj.make_transferring_df()

        # Transferring phase
        if dcc.transferor:
            transferring_obj.transfering_weeklycts()
        
        # Plotting phase by using a dashboard
        if dcc.dashboard:
            dashboard_obj = DashboardMaker()
            dashboard_obj.make_dashboard()

if __name__ == "__main__":
    # Create an instance of Main class and execute the main pipeline
    main_obj = Main()
    main_obj.main_pipeline()