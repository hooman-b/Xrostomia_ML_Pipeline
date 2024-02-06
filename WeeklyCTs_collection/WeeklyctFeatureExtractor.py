"""
Explanation: This module is a complemantary module to WeeklyctDataframeMake
that contains all the nacessary functions to make the final WeeklyCT dataframe.
"""

# General Libraries
import os
import re
import glob
import math
import shutil
import numpy as np
import pandas as pd
from random import randint
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import time, datetime, date

# DICOM Libraries
import pydicom as pdcm
from pydicom.tag import Tag

# Custom Modules
import DataCollectionConfig as dcc



class WeeklyctFeatureExtractor():

    
    def get_firstday(self, df, date_list):
        try:
            first_day = df[df.date == date_list[1]].iloc[0].week_day
        except:
            first_day = None
        
        return first_day

    def find_matching_header(self, info_headers):
        for header in info_headers:
            try:
                lowercase_header = header.lower()

                if any(keyword in lowercase_header for keyword in ['rct', 'w']) and re.search(r'\d', header):
                    return header

                elif 'wk..' in lowercase_header and not re.search(r'\d', header):
                    return header

                elif re.search(r'rct.*[..]|rct.*[#]', lowercase_header) and not re.search(r'\d', header):
                    return header

            except Exception as e:
                print(f"An exception occurred: {e}")

        return None

    def get_weeklycts_names(self, df, date_list):

        header_list = list()

        # Find the headers
        for session in date_list[1:]:
            info_headers = df[df.date == session].info_header.tolist()
            header = self.find_matching_header(info_headers)

            header_list.append(header)

        # Ensure the header_list has 9 elements
        header_list += [None] * (9 - len(header_list))

        return header_list

    def get_accelerated_rt(self, patient_id, clinical_df):

        try:
            accelerated_rt = clinical_df[clinical_df.UMCG==int(patient_id)].Modality_adjusted.values[0]
        
        except:
            accelerated_rt = 'Not Mentioned'
        
        return accelerated_rt
        
    # Define a custom function to extract numbers only if 'wk' is not present
    def extract_numbers(self, text):
        if isinstance(text, str) and 'wk' not in text and re.search(r'\d', text):
            
            return  float(''.join(filter(str.isdigit, text)))       
        else:
            return text

    def get_existing_fractions(self, df):
        """
        This function extract all the fractions exist in the data itself.
        """
        for header in df.iloc[:, 11:20].columns:
            df[header] = df[header].apply(self.extract_numbers)

        return df

    def get_coef(self, Modality_adjusted):
        """
        Get the coefficient of the fractions
        """
        accelerated_list = ['Accelerated RT', 'Bioradiation'] # CONFIG File
        not_accelerated_list = ['Chemoradiation', 'Conventional RT'] # CONFIG File
        
        if Modality_adjusted in not_accelerated_list:
            coef = 1.0
        
        elif Modality_adjusted in accelerated_list:
            coef = 1.2

        else:
            coef = 0.0

        return coef

    def calculate_fraction(self, raw, fraction, fraction_num, coef, counter):
        try:
        
            if isinstance(fraction, str) and 'wk' in fraction and  counter == 0:
                fraction_num = (len(pd.bdate_range( raw[f'Baseline'], raw[f'Session{1}'])) - 1) * coef + 1

            elif isinstance(fraction, str) and 'wk' in fraction and  counter != 0:
                fraction_num += (len(pd.bdate_range( raw[f'Session{counter}'], raw[f'Session{counter+1}'])) - 1) * coef
                    
            elif isinstance(fraction, str) and 'wk' not in fraction and not re.search(r'\d', fraction) and counter==0:
                fraction_num += (len(pd.bdate_range( raw[f'Baseline'], raw[f'Session{1}'])) - 1) * coef + 1

            # This part does not work  if the rct.. or rct# is seperated from other part
            elif isinstance(fraction, str) and 'wk' not in fraction and not re.search(r'\d', fraction) and counter!=0:
                fraction_num += (len(pd.bdate_range( raw[f'Session{counter}'], raw[f'Session{counter+1}'])) - 1) * coef

            elif fraction is np.nan and counter < raw.Number_of_weeklyCTs and counter==0:
                fraction_num = (len(pd.bdate_range( raw[f'Baseline'], raw[f'Session{1}'])) - 1) * coef + 1

            elif fraction is np.nan and counter < raw.Number_of_weeklyCTs and counter!=0:
                fraction_num += (len(pd.bdate_range( raw[f'Session{counter}'], raw[f'Session{counter+1}'])) - 1) * coef              

            elif isinstance(fraction, int) or isinstance(fraction, float):
                fraction_num = fraction

            else:
                fraction_num = None
            return fraction_num 

        except:
            return fraction_num
        

    def extract_raw_weeklyct_features(self, id_num, patient_df, clinical_df):
            
            # Extract the parts suspected to contain weeklyCTs
            df = patient_df[(patient_df['folder_name'].str.lower().str.contains('rct') & \
                (patient_df['date'] != patient_df['date'].min())) | ((patient_df['date'] == patient_df['date'].min()))]
        
            date_list = sorted(list(df.date.unique())) # Find the list of dates
            rtstart = date_list[0] # Extract RTSTART  
            first_day = self.get_firstday(df, date_list) # the week day of the first treatment

            # Extract the weeklyCTs names and first day of the treatment
            header_list= self.get_weeklycts_names(df, date_list)

            # Extract other parameters
            durations = date_list[1:]
            weekly_ct_num = len(durations)       
            durations += [None] * (9 - len(durations)) # Ensure it has 9 elements
            Modality_adjusted = self.get_accelerated_rt(id_num, clinical_df) # int(patient_df['ID'].iloc[0])

            return {'ID': int(id_num), 'Baseline': rtstart, 'Session1': durations[0],
                    'Session2': durations[1], 'Session3': durations[2],'Session4': durations[3],
                    'Session5': durations[4], 'Session6': durations[5],'Session7': durations[6],
                    'Session8': durations[7],'Session9': durations[8], 'Fraction1': header_list[0],
                    'Fraction2': header_list[1], 'Fraction3': header_list[2],'Fraction4': header_list[3],
                    'Fraction5': header_list[4], 'Fraction6': header_list[5], 'Fraction7': header_list[6],
                    'Fraction8': header_list[7],'Fraction9': header_list[8], 'First_day': first_day,
                    'Number_of_CTs': df.shape[0], 'Number_of_weeklyCTs': weekly_ct_num, 
                    'modality_adjusted':Modality_adjusted}
    
    def correct_fractions(self, df):
        """
        This function finds or calculates all the fractions
        """
        # Make a copy of the dataset
        df_copy = df.copy()
        coef_list = list()
        # Find all the existing fractions in the dataset
        df_copy = self.get_existing_fractions(df_copy)

        # Iterate through patients
        for index, raw in df_copy.iterrows():

            fraction_list = list()
            fraction_num = 0

            # Calculate the coefficient
            coef = self.get_coef(raw.modality_adjusted)

            # Iterate through fractions
            for counter, fraction in enumerate(raw.iloc[11:20]):

                # Calculate and add different fractions to the list of fractions
                fraction_num = self.calculate_fraction(raw, fraction, fraction_num, coef, counter)
                fraction_list.append(fraction_num)

            df_copy.iloc[index, 11:20] = fraction_list
            coef_list.append(coef)
    
        df_copy['Coefficient'] = coef_list

        return df_copy

