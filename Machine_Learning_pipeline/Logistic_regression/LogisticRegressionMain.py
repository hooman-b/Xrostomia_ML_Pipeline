"""
Explanation: This module is used to run Logistic Regression. It is not recommended 
to use this class for univariable analysis, or feature selection precedure. It is 
good to make a base model to compare with deep learning models.

NOTE: The group that I am working in at the moment is using R for machine learning
modelling purposes. So, I upload all the R codes that I used for machine learning 
modelling in a separated folder along with the Jupyter Notebook for implementation 
of univariable analysis and feature selection in python.

Author: Hooman Bahrdo

Last Revised:...
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Statistic libraries
import statsmodels.api as sm
from scipy import stats

# Data generating and feature modules
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from mlxtend.feature_selection import SequentialFeatureSelector # Forward selection library

# Classification modules
from sklearn.linear_model import LogisticRegression
from sklearn.svm import  SVC
from pygam import LogisticGAM
from sklearn.pipeline import Pipeline

# Evaluation modules
from sklearn.metrics import precision_score, recall_score
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score

# Model selection modules
from sklearn.model_selection import GridSearchCV

# In-built modules
import LogisticRegressionConfig as lrc

class LogisticRegressionModel():

    def __init__(self):
        self.df_path = lrc.df_path
        self.df_name = lrc.df_name
        self.cv_number = lrc.cv_number
        self.scoring_list = lrc.scoring_list
        self.refit_method = lrc.refit_method
        self.estimator_dict = lrc.estimator_dict
        self.split_col_name = lrc.split_col_name
        
    def univariable_logistic_regression(self, DATA, ynam):
        feats_of_interest = DATA.columns
        Model_predict = []
        stats_s = []
        OR_95 = []
        nums = []

        for feat in feats_of_interest:
            X = DATA[feat]
            #X = sm.add_constant(X)
            y = ynam

            model = sm.Logit(y, X)
            result = model.fit()

            # Calculate odds ratio and confidence interval
            params = result.params
            conf_int = result.conf_int()
            StanER = np.sqrt(np.diag(result.cov_params()))
            
            OR = np.exp(params)
            OR_95.append([params[feat], OR[feat], np.exp(conf_int.loc[feat, 0]), np.exp(conf_int.loc[feat, 1])])

            # Calculate statistics
            aic = result.aic
            bic = result.bic
            
            stats_s.append(list(result.summary2().tables[1]['P>|z|']) + [result.llf, aic, bic])
            

            nums.append([result.nobs, result.nobs - len(result.params)])

        colnames_stats_s = list(result.summary2().tables[1].index) + ['Log-Likelihood', 'AIC', 'BIC']
        colnames_OR_95 = ['beta', 'OR', 'OR95-', 'OR95+']
        colnames_nums = ['n', 'event']

        stats_s = np.array(stats_s)
        OR_95 = np.array(OR_95)
        nums = np.array(nums)

        df_stats_s = pd.DataFrame(stats_s, columns=colnames_stats_s)
        df_OR_95 = pd.DataFrame(OR_95, columns=colnames_OR_95)
        df_nums = pd.DataFrame(nums, columns=colnames_nums)

        univar_result = pd.concat([df_stats_s, df_OR_95, df_nums], axis=1)

        univar_result['p_LRT'] = stats.chi2.sf(univar_result['Log-Likelihood'], 1)

        return univar_result


    def multiple_grid_search(self, estimator_dict, scoring_list, cv_number, refit_method, data_dict):

        final_dict = {}

        for name in estimator_dict.keys():
            # Create the GridSearchCV object
            grid_search = GridSearchCV(estimator=estimator_dict[name][0], param_grid=estimator_dict[name][1],
                                        scoring=scoring_list, cv=cv_number, refit=refit_method)
            
            # Fit the the best model to the data
            grid_search.fit(data_dict['x'], data_dict['y'])

            # Save the best estimator for each model
            final_dict[name] = {'best_model': grid_search.best_estimator_,
                                'best_parameters': grid_search.best_params_,
                                'best_score': grid_search.best_score_}

        # order the dictionary based on the magnitude of the scores
        final_dict = dict(sorted(final_dict.items(), key=lambda item: -1 * item[1]['best_score']))
        
        return final_dict
    
    def data_loader(self):
        pass

    def logistic_regression_main(self):
        pass

    def feature_selection(self):
        pass