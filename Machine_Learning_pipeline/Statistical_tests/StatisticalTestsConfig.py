"""
NOTE:
This folder can be used to implement statistical tests on a pre-made dataset
to evaluate some of the statistical properties of its columns. It contains three
classes one is for calculating the results of statistical tests, another one is 
used to draw some graphs, and the last one is used to present the results of the classes.
Again, I would rather like to use Jupyter Notebook when it comes to statistical tests since
it gives me a better control and view about the tests' results and presentations.

User Specific:
1. statistical_test_dict is used to tell the program which tests should be implemented
and which columns should be used for the input of the tests.{test_name: [list of columns]}
NOTE: if the main dictionary are empty, the program skip the test ot plotting part.
2. statistical_plot_dict is used to tell the program which plots should be drown, and
which columns should be used for the input of the plots. {plot_name: {dict of parameters}}
NOTE: if the main dictionary are empty, the program skip the test ot plotting part.

"""
# The statistical test options are: 'shapiro', 'levene', 'wilcoxon', 'kruskal', 'bartlett',
# 'ttest_ind', 'ttest_rel', 'f_oneway'
statistical_test_dict = {'shapiro': ['delta_surf_dlc']}

# The statistical plot options are: 'scatter', 'histogram', 'heatmap', 'violin'
statistical_plot_dict = {}