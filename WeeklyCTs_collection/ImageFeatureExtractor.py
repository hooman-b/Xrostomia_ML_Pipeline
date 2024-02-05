"""
Explanation:
This class extracts and calculates many features from images,
the images can be any kind e.g. CT, MRI, and PET.

Author: Hooman Bahrdo
Last Revised:...
"""
# Import Libraries
# General Libraries
import re
from datetime import datetime

# DICOM Libraries
from pydicom.tag import Tag


class ImageFeatureExtractor:

    def __init__(self, image):
        self.image = image
    
    def get_folder_name(self, subf):

        # find the name of the folder
        try:
            folder_name = self.image[Tag(0x0008103e)].value

        except:
            study = self.get_study_inf(self)
            patient_id = self.get_patient_id(self)
            folder_name = subf.split('\\')[-1]  
            print(f'Warning: folder {study} with {patient_id} ID does NOT have Series Description')
    
        return folder_name
    

    def get_patient_id(self):

        # Extract the patient ID
        try:
            patient_id = int(self.image[Tag(0x00100020)].value)

        except:
            print(f'Warning: There is NO patient ID')
            patient_id = None

        return patient_id
    
    def get_study_inf(self):
        # Extract the patient ID
        try:
            study = self.image[Tag(0x00081030)].value

        except:
            print(f'Warning: There is NO patient ID')
            study = None

        return study

    def get_date_information(self):

        # Extract the date, the week day, and the week number from study date time
        try:
            study_datetime_CT = datetime.strptime(self.image[Tag(0x00080020)].value ,"%Y%m%d")
            date_info = study_datetime_CT.date()
            weekday = study_datetime_CT.weekday() + 1
            week_num = study_datetime_CT.isocalendar()[1] #week

        except:
            date_info = None
            weekday = None
            week_num = None 
        
        return date_info, weekday, week_num

    def get_slice_thickness(self):
        
        # Extract slice thickness
        try:
            slice_thickness = self.image['00180050'].value
        except:
            slice_thickness = None
        
        return slice_thickness

    def get_contrast(self):
        
        # Extract contrast information
        try:
            self.image[Tag(0x00180010)].value
            contrast=1

        except:
            contrast=0
        
        return contrast

    def get_pixel_spacing(self):

        # Extract pixel spacing
        try:
            pixel_spacing = self.image[Tag(0x00280030)].value
        except:
            pixel_spacing = None
        
        return pixel_spacing   

    def get_ref_uid(self):

        # Extract UID
        try:
            uid = self.image['00200052'].value
        except:
            uid = None
        
        return uid

    def get_probable_weklyct_name(self, name, number, names_list, saver):
        """
        Explanation: This method find the name of the weeklyCT. It can be a combination with
        'rct..', 'wk..', 'w..' or any othe combination
        """
        lowercase_name = name.lower()

        # Search to find 'rct' or 'w' with a number
        if ('rct' in lowercase_name or 'w' in lowercase_name) and re.search(r'\d', name):
            saver = name

        elif 'wk..' in lowercase_name and not re.search(r'\d', name):
            saver = name

        # Check if 'w' is in 'j' and the next element in 'sep_names' is an integer
        elif 'w' in lowercase_name and number + 1 < len(names_list) and not re.search(r'\d', name):

            if '2.0' not in names_list[number + 1] and '2,' not in names_list[number + 1]:
                saver = name + str(names_list[number + 1])

        elif re.search('rct.*[..]|rct.*[#]', lowercase_name) and not re.search(r'\d', name):
            saver = name
        
        else:
            pass

        return saver 

    def get_hd_fov(self, name, hd_fov):

        lowercase_name = name.lower()
        # Search whether there is 'hd' or 'fov' in j
        if 'hd' in lowercase_name or 'fov' in lowercase_name:
            hd_fov = 1 
        
        else:
            pass
        
        return hd_fov

    def get_fraction(self, name, fraction):

        lowercase_name = name.lower()

        # Find the fraction number
        if 'rct' in lowercase_name and re.search(r'\d', name):
            fraction = int(re.findall(r'\d+', name)[0])
        
        else:
            pass
        
        return fraction