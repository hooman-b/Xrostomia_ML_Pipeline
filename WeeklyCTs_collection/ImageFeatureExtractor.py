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
import glob
from datetime import datetime

# DICOM Libraries
import pydicom as pdcm
from pydicom.tag import Tag


class ImageFeatureExtractor():

    def __init__(self):
        self.image = ''
    
    def make_ct_image(self, subf):

        try:
            # Make the image
            ct_image = pdcm.dcmread(glob.glob(subf+"/*.DCM")[0],force=True)
        
        except:
            print(f'Warning: There is no image in {subf}')
        
        self.image = ct_image

    def get_folder_name(self):

        # find the name of the folder
        try:
            folder_name = self.image[Tag(0x0008103e)].value

        # Make the folder name based on the name of the folder
        except:
            study = self.get_study_inf()
            patient_id = self.get_patient_id()
            folder_name = self.subf.split('\\')[-1]  
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

    def get_image_position(self):

        # Extract the image position (x, y, z)
        try:
            im_position = self.image.ImagePositionPatient
    
        except:
            im_position = None
    
        return im_position

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
    
    def get_image_information(self):
        """
        This function extract the information of an image in the form of a dictionary
        """
        folder_name = self.get_folder_name()
        patient_id = self.get_patient_id()
        slice_num = len(glob.glob(self.subf+"/*.DCM"))

        # split the name of the folder into strings of information
        names_list = folder_name.split()

        # Initialize the following three patameters
        saver = None
        hd_fov = 0
        fraction = None

        for number, name in enumerate(names_list):
            saver = self.get_probable_weklyct_name(name, number, names_list, saver) 
            hd_fov = self.get_hd_fov(name, hd_fov)
            fraction = self.get_fraction(name, fraction)

        # Find different information
        date_info, weekday, week_num = self.get_date_information()
        slice_thickness = self.get_slice_thickness()
        contrast = self.get_contrast()
        pixel_spacing = self.get_pixel_spacing()
        uid = self.get_ref_uid()

        # return the information of this image
        return  {
                'ID': patient_id, 'folder_name': folder_name, 'date': date_info,
                'week_day': weekday, 'week_num': week_num, 'info_header': saver,
                'fraction': fraction, 'HD_FoV': hd_fov, 'slice_thickness': slice_thickness,
                'num_slices': slice_num, 'pixel_spacing': pixel_spacing, 'contrast': contrast,
                'UID': uid, 'path': self.subf
                }
    
    # Make some functions related to Segmentation images
    def get_contour_uid(self, contour_item):
        
        # Extract contour information and uids
        contour_inf = contour_item.get((0x3006, 0x0016))
        contour_uid = contour_inf[0]['00081155'].value

        return contour_uid
    def get_contour_data(self,contour_item):

        try:
            contour_data = contour_item.get((0x3006, 0x0050))
        
        except Exception:
            contour_data = None
        
        return contour_data

    def find_ct_match_seg(self, dicom_images, dicom_images_uid, contour_uid):
        # Assign a set of images to th eimage attribut to get the attribut
        self.image = dicom_images[dicom_images_uid.index(contour_uid)]
    
    