"""
Explanation: This module is a complemantary module to WeeklyctDataframeMake
that contains all the nacessary functions to make the final WeeklyCT dataframe.

Author: Hooman Bahrdo
Last Revised: 3/28/2024
"""

# General Libraries
import re
import numpy as np
import pandas as pd

# Custom Modules
import DataCollectionConfig as dcc


class WeeklyctFeatureExtractor():
    """
    Explanation: A class containing functions to extract features from weekly CT data.

    Methods: 1. get_firstday: Get the weekday of the first treatment session.
                2. find_matching_header: Find the header that matches the specified criteria.
                3. get_weeklycts_names: Get the names of the weekly CTs.
                4. get_accelerated_rt: Get the type of accelerated radiotherapy for a patient.
                5. extract_numbers: Extract numbers from text.
                6. get_existing_fractions: Extract existing fractions from the dataset.
                7. get_coef: Get the coefficient for fractions.
                8. calculate_fraction: Calculate fraction based on different factors.
    """

    def get_firstday(self, df, date_list):
        """
        Type: instance method
        Inputs: 1. df (DataFrame): DataFrame containing treatment session information.
                2. date_list (list): List of treatment session dates.
        Explanation: Get the weekday of the first treatment session.
        Outputs: 1. str: Weekday of the first treatment session.
        """
        try:
            first_day = df[df.date == date_list[1]].iloc[0].week_day
        except:
            first_day = None
        
        return first_day

    def find_matching_header(self, info_headers):
        """
        Type: instance method
        Inputs: 1. info_headers (list): List of information headers.
        Explanation: Find the image header that matches the specified criteria.
        Outputs: 1. str: Matching header.
        """
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
        """
        Type: instance method
        Inputs: 1. df (DataFrame): DataFrame containing treatment session information.
                2. date_list (list): List of treatment session dates.
        Explanations: Get the names of the weekly CTs.
        Outputs: 1. list: List of weekly CT names.
        """
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
        """
        Type: instance method
        Inputs: 1. patient_id (int): Patient ID.
                2. clinical_df (DataFrame): DataFrame containing clinical information.
        Explanation: Get the type of accelerated radiotherapy for a patient.
        Outputs: 1. str: Type of accelerated radiotherapy.
        """
        try:
            accelerated_rt = clinical_df[clinical_df.UMCG==int(patient_id)].Modality_adjusted.values[0]
        
        except:
            accelerated_rt = 'Not Mentioned'
        
        return accelerated_rt
        
    # Define a custom function to extract numbers only if 'wk' is not present
    def extract_numbers(self, text):
        """
        Type: instance method
        Inputs: 1. text (str): Input text.
        Explanation: Extract numbers from text.
        Outputs: 1. float: Extracted numbers.
        """
        if isinstance(text, str) and 'wk' not in text and re.search(r'\d', text):
            
            return  float(''.join(filter(str.isdigit, text)))       
        else:
            return text

    def get_existing_fractions(self, df):
        """
        Type: instance method
        InputL 1. df (DataFrame): DataFrame containing fraction information.
        Explanation: Extract existing fractions from the dataset.
        Output: 1. DataFrame: DataFrame with extracted fractions.
        """
        for header in df.iloc[:, 11:20].columns:
            df[header] = df[header].apply(self.extract_numbers)

        return df

    def get_coef(self, Modality_adjusted):
        """
        Type: instance method
        Inputs: 1. Modality_adjusted (str): Type of adjusted modality.
        Explanation: Get the coefficient for fractions (Based on treatment-modality).
                     One can change the order of the modalities in the configu file.
        Outputs: 1. float: Coefficient for fractions.
        """
        
        if Modality_adjusted in dcc.not_accelerated_list:
            coef = 1.0
        
        elif Modality_adjusted in dcc.accelerated_list:
            coef = 1.2

        else:
            coef = 0.0

        return coef

    def calculate_fraction(self, raw, fraction, fraction_num, coef, counter):
        """
        Type: instance method
        Inputs: 1. raw (Series): Raw data for a patient.
                2. fraction: Fraction value.
                3. fraction_num (float): Fraction number.
                4. coef (float): Coefficient for fractions.
                5. counter (int): Counter value.
        Explanation: Calculate fraction based on different factors.
        Outputs: 1. float: Calculated fraction number.
        """
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

    def get_fraction_info(self, raw, week_name):
        """
        Type: instance method
        Inputs: 1. raw (DataFrame): The raw DataFrame containing patient information.
                2. week_name (str): The name of the week.
        Explanation: Extract fraction information based on modality adjustment and week name.
        Outputs: 1. list: A list of column names containing matching fractions.
        """
        accelerated_list = dcc.accelerated_list
        not_accelerated_list = dcc.not_accelerated_list
        fraction_range_dict = dcc.fraction_range_dict

        matching_list = []
        fraction_seri = raw.iloc[11:20]

        # Find any columns that have values inside the range of a a specific week
        if raw.modality_adjusted in not_accelerated_list:
            matching_list = [column for column in fraction_seri.index \
            if (raw[column]is not None and raw[column] > fraction_range_dict[week_name]['not_accelerated'][0] \
                and raw[column] <= fraction_range_dict[week_name]['not_accelerated'][1])]

        elif raw.modality_adjusted in accelerated_list:
            matching_list = [column for column in fraction_seri.index \
            if (raw[column]is not None and raw[column] > fraction_range_dict[week_name]['accelerated'][0] \
                and raw[column] <= fraction_range_dict[week_name]['accelerated'][1])]

        return matching_list

    def process_matching_fractions(self, raw, matching_list, week_name, week_list):
        """
        Type: instance method
        Inputs: 1. raw (DataFrame): The raw DataFrame containing patient information.
                2. matching_list (list): A list of column names containing matching fractions.
                3. week_name (str): The name of the week.
                4. week_list (list): A list containing patient information for the week.
        Explanation:Process matching fractions and add relevant patient information to week_list.
        Outputs: 1. list: Updated week_list containing patient information.
        """
        # If finds a column, add some information of  that patient to the dictionary
        if len(matching_list) > 0:
            for matched_fraction in matching_list:
                week_num = matched_fraction[-1]
                week_list.append({'ID': raw.ID,
                                'date': raw[f'Session{week_num}'],
                                'treatment_week': week_name,
                                'Fraction_num': matched_fraction, 
                                'Fraction_magnitude': raw[matched_fraction], 
                                'modality_adjusted': raw.modality_adjusted})

            return week_list

    def extract_raw_weeklyct_features(self, id_num, patient_df, clinical_df):
        """
        Type: instance method        
        Inputs: 1. id_num (int): The ID number of the patient.
                2. patient_df (DataFrame): DataFrame containing patient data.
                3. clinical_df (DataFrame): DataFrame containing clinical data.
        Explanation: Extract raw weekly CT features from patient data.
        Outputs: 1. dict: Dictionary containing extracted raw weekly CT features.
        """            
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
        Type: instance method       
        Inputs: 1. df (DataFrame): The DataFrame containing patient information.
        Explanation: Find or calculate all the fractions.
        Outputs: 1. DataFrame: DataFrame with corrected fractions.
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

