"""
Explanation: This module is used to implement different statistical tests.

Author: Hooman Bahrdo
Last Revised:...
"""
from scipy.stats import shapiro, levene, wilcoxon, kruskal, bartlett, ttest_ind, ttest_rel, f_oneway

class StatisticalTests():

    def shapiro_test(self, main_df, param_dict, alpha):
        stat, p_value = shapiro(main_df[param_dict['col_names'][0]])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def levene_test(self, main_df, param_dict, alpha):
        stat, p_value = levene(main_df[param_dict['col_names'][0]], main_df[param_dict['col_names'][1]])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def bartlett_test(self, main_df, param_dict, alpha):
    
        stat, p_value = bartlett(main_df[param_dict['col_names'][0]], main_df[param_dict['col_names'][1]])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def wilcoxon_test(self, main_df, param_dict, alpha):
        stat, p_value = wilcoxon(main_df[param_dict['col_names'][0]], main_df[param_dict['col_names'][1]],
                                  alternative=param_dict['alternative'])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def ttest_ind_test(self, main_df, param_dict, alpha):
        stat, p_value = ttest_ind(main_df[param_dict['col_names'][0]], main_df[param_dict['col_names'][1]],
                                  alternative=param_dict['alternative'])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def ttest_rel_test(self, main_df, param_dict, alpha):
        stat, p_value = ttest_rel(main_df[param_dict['col_names'][0]], main_df[param_dict['col_names'][1]],
                                  alternative=param_dict['alternative'])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def kruskal_test(self, main_df, param_dict, alpha):
        stat, p_value = kruskal(main_df[param_dict['col_names']])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def f_oneway_test(self, main_df, param_dict, alpha):
        stat, p_value = f_oneway(main_df[param_dict['col_names']])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def test_selector(self, test_name):

        # make the function name
        method_name = f'{test_name}_test'

        return getattr(self, method_name)
