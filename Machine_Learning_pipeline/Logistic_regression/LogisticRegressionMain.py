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

import sys
import numpy as np
import pandas as pd
import seaborn as sns
from collections import Counter
import matplotlib.pyplot as plt


module_directory = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Models/Xrostomia_ML_Pipeline/'
sys.path.append(module_directory)

# Statistic libraries
import statsmodels.api as sm
from scipy import stats

# Data generating and feature modules
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SequentialFeatureSelector # Forward selection library

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
from WeeklyCTs_collection import ReaderWriter

class LogisticRegressionModel():

    def __init__(self):
        self.tol = lrc.tol

        self.df_path = lrc.df_path
        self.df_name = lrc.df_name
        self.boot_num = lrc.boot_num
        self.save_path = lrc.save_path        
        self.cv_number = lrc.cv_number
        self.direction = lrc.direction
        self.cv_forward = lrc.cv_forward
        self.model_name = lrc.model_name
        self.writer_type = lrc.writer_type
        self.replace_boot = lrc.replace_boot
        self.scoring_list = lrc.scoring_list
        self.refit_method = lrc.refit_method
        self.train_percent = lrc.train_percent
        self.col_name_list = lrc.col_name_list
        self.label_col_name = lrc.label_col_name
        self.estimator_dict = lrc.estimator_dict
        self.split_col_name = lrc.split_col_name
        self.scoring_forward = lrc.scoring_forward
        self.estimator_forward = lrc.estimator_forward
        self.submodel_col_name_list = lrc.submodel_col_name_list

        self.univariable_key = lrc.univariable_key
        self.feature_selection_swtich = lrc.feature_selection_swtich
        self.logistic_regression_switch = lrc.logistic_regression_switch

        self.reader_obj = ReaderWriter.Reader()
        self.writer_obj = ReaderWriter.Writer(self.writer_type)

    def data_loader(self):
        main_df = self.reader_obj.read_dataframe(self.df_path, self.df_name)
        grouped_dfs = pd.DataFrame(main_df.groupby(self.split_col_name))

        # Find the training dataset by using the lenght of the datasets
        general_shape = 0
        for _, row in grouped_dfs.iterrows():
            df_len = row.shape[0]

            if general_shape < df_len:
                train_df_name = row[0]
                general_shape = df_len

        main_df = main_df.loc[:, self.col_name_list]
        train_val_df = main_df[main_df[self.split_col_name] == train_df_name]
        test_df = main_df[~(main_df[self.split_col_name] == train_df_name)]

        return train_val_df, test_df


    def univariable_logistic_regression(self, train_val_df):
        feats_of_interest = train_val_df[~(train_val_df.columns == self.label_col_name)].columns
        DATA = train_val_df[~(train_val_df.columns == self.label_col_name)]
        stats_s = []

        for feat in feats_of_interest:
            X = DATA[feat]
            y = train_val_df[self.label_col_name]
            
            # Model implementation
            model = sm.Logit(y, X)
            result = model.fit()

            # Calculate odds ratio and confidence interval
            params = result.params
            conf_int = result.conf_int()
            OR = np.exp(params)

            # Calculate statistics
            aic = result.aic
            bic = result.bic
            
            stats_s.append([result.summary2().tables[1].index[0], result.summary2().tables[1]['P>|z|'][0], result.llf, aic, bic, 
                        params[feat], OR[feat], np.exp(conf_int.loc[feat, 0]), np.exp(conf_int.loc[feat, 1]), result.nobs, 
                        result.nobs - len(result.params)])

        # Make the final df
        colnames_stats_s = ['variable', 'p_value', 'Log-Likelihood', 'AIC', 'BIC', 'beta', 'OR', 'OR95-', 'OR95+', 'n', 'event']
        univar_result = pd.DataFrame(stats_s, columns=colnames_stats_s)
        univar_result['p_LRT'] = stats.chi2.sf(univar_result['Log-Likelihood'], 1)

        return univar_result


    def feature_selection(self, train_val_df):
        
        chosen_feature_list = list()

        for num in self.boot_num:
            train_X, train_y = resample(train_val_df[~(train_val_df.columns == self.label_col_name)], train_val_df[self.label_col_name], 
                                    n_samples=int(train_val_df.shape[0]*self.train_percent),  replace=self.replace_boot)

            

            sfs = SequentialFeatureSelector(self.estimator_forward, tol=self.tol, direction=self.direction, 
                                            cv=self.cv_forward, scoring=self.scoring_forward, n_jobs=-1)
            sfs.fit(train_X, train_y)
            chosen_feature_list.extend(list(sfs.get_feature_names_out()))
            element_counts = Counter(chosen_feature_list)

            return element_counts


    def multiple_grid_search(self, X_data, y):

        final_dict = {}

        for name in self.estimator_dict.keys():
            # Create the GridSearchCV object
            grid_search = GridSearchCV(estimator=self.estimator_dict[name][0], param_grid=self.estimator_dict[name][1],
                                        scoring=self.scoring_list, cv=self.cv_number, refit=self.refit_method)
            
            # Fit the the best model to the data
            grid_search.fit(X_data, y)

            # Save the best estimator for each model
            final_dict[name] = {'best_model': grid_search.best_estimator_,
                                'best_parameters': grid_search.best_params_,
                                'best_score': grid_search.best_score_}

        # order the dictionary based on the magnitude of the scores
        final_dict = dict(sorted(final_dict.items(), key=lambda item: -1 * item[1]['best_score']))
        
        return final_dict

    def run_submodels(self, train_val_df):
        """
        Source: https://github.com/PRI2MA/DL_NTCP_Xerostomia/blob/main/models/logistic_regression.py
        """
        DATA = train_val_df[~(train_val_df.columns == self.label_col_name)]
        y = train_val_df[self.label_col_name]
        coeffs_list = []
        nr_submodels = len(self.submodel_col_name_list)

        for i, features_i in enumerate(self.submodel_col_name_list):
            # Training set submodel i
            train_X = train_val_df.loc[:, features_i]

            # Fit submodel i
            final_dict = self.multiple_grid_search(train_X, y)
            model = final_dict['best_model']

            # Create dict of coefficients of submodel i
            keys = ['intercept'] + features_i
            values = np.append(model.intercept_, model.coef_)
            coeffs_i_dict = {k: v for (k, v) in zip(keys, values)}
            coeffs_list.append(coeffs_i_dict)

        # Construct coefficients of final model
        lr_coefficients = []
        for f in ['intercept'] + self.col_name_list:
            coeff_i = 0
            # For-loop over coefficients of submodels
            for d_i in coeffs_list:
                if f in d_i.keys():
                    coeff_i += d_i[f]

            lr_coefficients.append(coeff_i / nr_submodels)
        
        # Fit on training set or use pretrained coefficients
        model = model.fit(DATA, y)

        # Adjust the coefficients of the model based on the sub-models
        if lr_coefficients is not None:
            model.intercept_ = np.array([lr_coefficients[0]])
            model.coef_ = np.array([lr_coefficients[1:]])

        return model

    def logistic_regression_main(self):
        
        train_val_df, test_df = self.data_loader()
        DATA_train = train_val_df[~(train_val_df.columns == self.label_col_name)]
        y_train = train_val_df[self.label_col_name]

        if self.univariable_key:
            univar_result = self.univariable_logistic_regression(train_val_df)
            print(univar_result)
        
        if self.feature_selection_swtich:
           element_counts = self.feature_selection(train_val_df)
           print(element_counts)
        
        if self.logistic_regression_switch:
            
            if len(self.submodel_col_name_list) > 0:
                model = self.run_submodels(train_val_df)
            
            else:
                # Fit submodel i
                final_dict = self.multiple_grid_search(DATA_train, y_train)
                model = final_dict['best_model']

        # Save the model
        self.writer_obj.write_ml_model(model, self.save_path, self.model_name)

        # Implement the model on the test set
        test_y_pred = list(model.predict_proba(test_df[~(test_df.columns == self.label_col_name)]))
        test_y = list(test_df[self.label_col_name])
        test_dict = {'Prediction':test_y_pred, 'Label': test_y}
        test_df = pd.DataFrame(test_dict)
        print(test_df)




