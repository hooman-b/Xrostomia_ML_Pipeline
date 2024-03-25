"""
Explanation:
This config file contains all the necessary parameters to run
all types of Logistic Regression models.

User Specific:
NOTE: NO preprocessing is done in this module, so be sur that you are using a preprocessed
dataset here.
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
3. col_name_list: This should contain all the columns that should be used in the process of making models.
NOTE: this list MUST contain the name of the label column. 
4. submodel_col_name_list: This list should be made from other lists as its elements, each list should 
contain the columns used in one sub-model. If you do NOT have any submodel just leave this list empty.
NOTE: The name of the columns in the submodel list MUST be a sub-list of the col_name_list.
5. train_percent: If this percentage is equal to 1 it means every time all the datapoints goes into the 
forward selection model. The outcome of the forward selection function will be the number of times that 
each feature is chosen in the model.
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
col_name_list = ['xer_06', 'xer_bsl', 'Parotid_R_Dmean', 'Parotid_L_Dmean', 'Parotid_Dmean']
submodel_col_name_list = [] 
df_name = 'delta_rf_df.csv'
split_col_name = 'Split'
label_col_name = 'xer_06'
writer_type = 'Excel'

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


### Feature Selection (Forward, Backward) with Bootstrapping ###
boot_num = 1000
train_percent = 0.85
replace_boot = True

# feature selection parameters
tol = 1e-7
direction = 'forward' # Other option is 'backward'
cv_forward = 10
scoring_forward = 'roc_auc'
estimator_forward = LogisticRegression() # One can add some hyperparameters, but there no 
# capability for tunning the parameters duting this procedure.

### Main function switches ###
univariable_key = True
feature_selection_swtich = True
logistic_regression_switch = True

### Directory for saving the model ###
save_path = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Deep_learning_datasets'
model_name = 'LR_model.pkl'