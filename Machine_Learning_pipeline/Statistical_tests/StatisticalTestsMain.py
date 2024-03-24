"""
Explanation: This module is used to run the tests and draw the plots
that user wants to run.
NOTE: I myself prefer to use Jupyter Notebook for this section, and 
I uploaded my Jupyter Notebook in this folder.

Author: Hooman Bahrdo
Last Revised:...
"""
import sys
import matplotlib.pyplot as plt

module_directory = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Models/Xrostomia_ML_Pipeline/'
sys.path.append(module_directory)

import StatisticalTests
import StatisticalPlots
import StatisticalTestsConfig as stc
from WeeklyCTs_collection import ReaderWriter

class StatisticalTestsMain():

    def __init__(self):

        self.alpha = stc.alpha
        self.df_name =stc.df_name
        self.df_path = stc.df_path
        self.save_path = stc.save_path
        self.save_plots = stc.save_plots
        self.show_plots = stc.show_plots
        self.writer_type = stc.writer_type
        self.statistical_test_dict = stc.statistical_test_dict
        self.statistical_plot_dict = stc.statistical_plot_dict

        self.st_obj = StatisticalTests()
        self.sp_obj = StatisticalPlots()
        self.reader_obj = ReaderWriter.Reader()
        self.writer_obj = ReaderWriter.Writer(self.writer_type)

    def statistical_test_main(self):
        main_df = self.reader_obj.read_dataframe(self.df_path, self.df_name)

        if len(self.statistical_test_dict) > 0:
            for test_name, parameters_dict in self.statistical_test_dict:
                stat_test = self.st_obj.test_selector(test_name)
                stat_test_result = stat_test(main_df, parameters_dict, self.alpha)
                print(stat_test_result)
        
        if len(self.statistical_plot_dict) > 0:
            for plot_name, parameters_dict in self.statistical_plot_dict:
                plot_func = self.sp_obj.plot_selector(plot_name)
                plot = plot_func(main_df, parameters_dict)

                if self.save_plots:
                    self.writer_obj.write_plt_images(self, plot, self.save_path, parameters_dict['plot_name'])
                
                if self.show_plots:
                    plt.show()
