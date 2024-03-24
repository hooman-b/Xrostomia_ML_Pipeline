"""
Explanation: This module is used to implement different statistical tests.

Author: Hooman Bahrdo
Last Revised:...
"""
from scipy.stats import shapiro, levene, wilcoxon, kruskal, bartlett, ttest_ind, ttest_rel, f_oneway

import StatisticalTestsConfig as stc

class StatisticalTests():
    def __init__(self):
        self.statistical_test_dict = stc.statistical_test_dict


    def shapiro_test(self, sample, alpha):
        stat, p_value = shapiro(sample[0])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def levene_test(self, samples, alpha):
        stat, p_value = levene(samples[0], samples[1])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def bartlett_test(self, samples, alpha):
        stat, p_value = bartlett(samples[0], samples[1])

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def wilcoxon_test(self, samples, alpha, alternative='two-sided'):
        stat, p_value = wilcoxon(samples[0], samples[1], alternative=alternative)

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def ttest_ind_test(self, samples, alpha, alternative='two-sided'):
        stat, p_value = ttest_ind(samples[0], samples[1], alternative=alternative)

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def ttest_rel_test(self, samples, alpha, alternative='two-sided'):
        stat, p_value = ttest_rel(samples[0], samples[1], alternative=alternative)

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def kruskal_test(self, samples, alpha):
        stat, p_value = kruskal(*samples)

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def f_oneway_test(self, samples, alpha):
        stat, p_value = f_oneway(*samples)

        if p_value < alpha:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nReject the null hypothesis: There is a significant difference in variances.')
        else:
            return (f'p_value: {round(p_value, 3)}, stat: {round(stat, 3)}\nFail to reject the null hypothesis: There is no significant difference')


    def test_selector(self, test_name):

        # make the function name
        method_name = f'{test_name}_test'

        return getattr(self, method_name)
