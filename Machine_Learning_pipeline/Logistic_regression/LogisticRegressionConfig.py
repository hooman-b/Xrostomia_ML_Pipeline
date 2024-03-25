"""
Explanation:
This config file contains all the necessary parameters to run
all types of Logistic Regression models.

User Specific:
1. The first section in this config file contains to the information of the dataset.
2. The second part contains all the hyperparameters used in hyperparameter tunning in
GridSearchCV. 
NOTE: The parameters for GridSearchCV contains four parameters:
    1. estimator_dict: This dictionary contains the name of the model as the keys, and
    a list contains the model as the first element and a dictionary of hyper parameters
    and their suggested parameters as the value.
    2. scoring_list: contains all the evaluation metrics one wants to evaluate during 
    hyperparameter tunning.
    3. cv_number: number of folds
    4. refit_method: is an evaluation metrics that is used for refitting the best model
    to the data. 
"""
import pandas as pd
import numpy as np

# Data generating and feature modules
from sklearn.preprocessing import PolynomialFeatures

# Classification modules
from sklearn.linear_model import LogisticRegression
from sklearn.svm import  SVC
from pygam import LogisticGAM
from sklearn.pipeline import Pipeline

### Dataset Information ###
df_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Deep_learning_datasets/Twelve_month_final_df/datasets/dataset_old_v2'
df_name = 'delta_rf_df.csv'
split_col_name = 'Split'

### GridSearchCV hyper parameters ###

# make parameters dictionaries
#LinearSVC
svc_param = {'C': np.arange(0.01, 10, 0.25),
             'kernel': ['linear', 'rbf', 'poly'],
             'gamma': ['scale', 'auto'],
             'degree': np.arange(2,10,1)}

# GAMS
gams_param= param_grid = [{'s(0)': [5, 10, 15], 's(1)': [5, 10, 15]},
                          {'s(0)': [10, 20, 30], 's(1)': [10, 20, 30]}]

# Create a pipeline with PolynomialFeatures and LogisticRegression
logistic_regression_pipeline = Pipeline([('polynomial', PolynomialFeatures()),
                                         ('LogisticRegression', LogisticRegression())])

# Logitic Regression
lr_param = {'polynomial__degree': np.arange(2,10,1),
            'LogisticRegression__C':  np.arange(0.01, 10, 0.25),
            'LogisticRegression__penalty': ['l1', 'l2']}

# Scoring list
scoring_list = ['roc_auc', 'f1', 'accuracy']

# Make estimator dictionary
estimator_dict={'SVC': [SVC(), svc_param],
                'LogisitcGAMS': [LogisticGAM(), gams_param],
                'LogisticRegression': [logistic_regression_pipeline, lr_param]}

# Number of folds
cv_number = 10

# Evaluation metrics for final refitting
refit_method = 'roc_auc'