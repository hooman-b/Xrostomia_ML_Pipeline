"""
NOTE:
This folder can be used to implement statistical tests on a pre-made dataset
to evaluate some of the statistical properties of its columns. It contains three
classes one is for calculating the results of statistical tests, another one is 
used to draw some graphs, and the last one is used to present the results of the classes.
Again, I would rather like to use Jupyter Notebook when it comes to statistical tests since
it gives me a better control and view about the tests' results and presentations.

User Specific:
NOTE: Do NOT change the key names of the dictionary of the parameters.
1. statistical_test_dict is used to tell the program which tests should be implemented
and which columns should be used for the input of the tests.{test_name: {dict of parameters}}
NOTE: if the main dictionary are empty, the program skip the test ot plotting part.
2. statistical_plot_dict is used to tell the program which plots should be drown, and
which columns should be used for the input of the plots. {plot_name: {dict of parameters}}
NOTE: if the main dictionary are empty, the program skip the test ot plotting part.
3. NOTE: the name of the plots should be mentioned in each plot dictionary, if one wants 
to save the plots.
"""

df_path = 'C:/Users/BahrdoH/OneDrive - UMCG/Hooman/Models/Preprocessing/Delta_radiomics/Feature_extraction_factory/Radiomics_features'
df_name = 'Rf_bsl_mc_sanne.xlsx'
writer_type = 'Excel'

# The statistical test options are: 'shapiro', 'levene', 'wilcoxon', 'kruskal', 'bartlett',
# 'ttest_ind', 'ttest_rel', 'f_oneway'
statistical_test_dict = {'shapiro': {'col_names':['delta_surf_dlc']},
                         'wilcoxon': {'col_names':['delta_surf_dlc', 'delta_surf_mc'],
                                      'alternative': 'two-sided'}
                        } # Do Not change the key names

# You can change the alpha for the statistical tests by using this parameter
alpha = 0.05

# The statistical plot options are: 'scatter', 'histogram', 'heatmap', 'violin'
statistical_plot_dict = {'scatter':{'x_element_list': ['delta_surf_mc'],
                                    'y_element_list':['delta_surf_dlc'],
                                    'color_list': ['black'],
                                    'label_list': ['MC Vs DLC'],
                                    'alpha_list': [0.7, 0.5],
                                    'figure_dict': {'x': 'Delta-Surface Area (MC)',
                                                    'y': 'Delta-Surface Area (DLC)', 
                                                    'title':'MC and DLC Delta-Surface Area values Comparison'} , 
                                    'line': False,
                                    'logistic': True,
                                    'line_info': ['delta_surf_mc', 0.01, 'Ideal Line'], # First one is the columns one 
                                    # wants to adjust line based on that, second one is the extension of the line, and
                                    # the third one is the name of the line.
                                    'plot_name': 'scatter_plot.png'},
                        'histogram':{'element_list':['Surface_dice'],
                                        'color_list': ['limegreen'],
                                    'label_list': ['Dice_MC_DLC_WK3'],
                                    'alpha_list': [0.7],
                                    'figure_dict': {'x': 'Surface',
                                                    'y': 'Probability Density', 
                                                    'title':'MC Vs DLC Surface Dice Distribution'},
                                    'plot_name': 'histogram_plot.png'},
                        'violin':{'element_list': ['delta_surf_mc', 'delta_surf_dlc'],
                                  'plot_name': 'violin_plot.png'
                                  },
                        'heatmap':{'element_list': ['delta_surf_mc', 'delta_surf_dlc'],
                                   'title': 'Surface Area Changes Between MC and DLC',
                                   'plot_name': 'heatmap_plot.png'
                                   }
                            }

# Save bottom can be used to save the plots
save_path = 'C:/Users/BahrdoH/OneDrive - UMCG/Hooman/Models/Preprocessing/Delta_radiomics/Feature_extraction_factory/Radiomics_features'
save_plots = True
show_plots = True
