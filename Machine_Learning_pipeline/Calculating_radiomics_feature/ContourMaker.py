"""
Explanation: This modules makes the contours (segmentation maps). it first reads them,
then makes them continous, and finally fills them.

Author: Hooman Bahrdo
Last Revised:...
"""

# General Libraries
import os
import re
import sys
import glob
import math
import shutil
import panel as pn
import numpy as np
import pandas as pd
from random import randint
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import time, datetime, date

# Image analysis packages
import cv2
import pydicom
from pydicom.tag import Tag
import nibabel as nib
import SimpleITK as sitk
from radiomics import featureextractor
from skimage.draw import polygon
from PIL import Image, ImageDraw

module_directory = '//zkh/appdata/RTDicom/Projectline_HNC_modelling/Users/Hooman Bahrdo/Models/Xrostomia_ML_Pipeline/'
sys.path.append(module_directory)

# Custom Modules
import RadiomicsConfig as rc
from WeeklyCTs_collection.ImageFeatureExtractor import ImageFeatureExtractor
from WeeklyCTs_collection.ReaderWriter import Writer, Reader


class ContourMaker():
    
    def __init__(self):
        self.binary_mask_name = rc.binary_mask_name

        self.ife_obj = ImageFeatureExtractor()
        self.writer_obj = Writer('Excel')
        self.reader_obj = Reader()

    def make_continous_contour(self, binary_mask, y_pix, x_pix):

        output_segmentation_map = np.zeros_like(binary_mask, dtype=np.uint8)
        
        #y_pix, x_pix = np.where(binary_mask == 1)
        #yx = list(zip(y_pix, x_pix))
        yx = [(y, x) for y, x in zip(y_pix, x_pix)]
        #print(yx)
        # Initiate empty image
        image_segmentation_map_i = Image.fromarray(np.zeros_like(output_segmentation_map, dtype=np.uint8))
        
        # Draw contour outline on image_segmentation_map
        draw = ImageDraw.Draw(image_segmentation_map_i)
        draw.polygon(yx, fill=0, outline=1)

        # Add contour outline to segmentation_map_i
        # Use mask, because contours of the same structure may still overlap!
        mask = (output_segmentation_map == 0)
        contour = ((np.array(image_segmentation_map_i) > 0) * 1).astype(output_segmentation_map.dtype)
        output_segmentation_map += mask * contour

        return output_segmentation_map

    def calculate_pixel_coordination(self, contour_data, binary_masks, contour_uid):

        # Consider empty list for dimensions
        x_pixel_list = []
        y_pixel_list = []
        z_pixel_list = []

        image_position = self.ife_obj.get_image_position()  #  Extract (x, y, z)
        pixel_spacing = self.ife_obj.get_pixel_spacing()  #  Extract (pixel_spacing_x, pixel_spacing_y)
        
        # Extract x, y, and z coordinates
        x_coordinates = [float(coord) for coord in contour_data[0::3]]
        y_coordinates = [float(coord) for coord in contour_data[1::3]]
        z_coordinates = [float(coord) for coord in contour_data[2::3]]
        
        # Iterate through the dimensions
        for x, y, z in zip(x_coordinates, y_coordinates, z_coordinates):

            # Convert world coordinates to pixel coordinates
            y_pixel = int((x - image_position[0]) / pixel_spacing[0])
            x_pixel = int((y - image_position[1]) / pixel_spacing[1])

            binary_masks[contour_uid][x_pixel , y_pixel] = 1

            x_pixel_list.append(x_pixel)
            y_pixel_list.append(y_pixel)
            
        return x_pixel_list, y_pixel_list

    def make_hollow_contour_matrix(self, contour_sequence, dicom_images, dicom_images_uid):

        # make a matrix to save the masks in the correct format
        contour_matrix = np.zeros((len(dicom_images), dicom_images[0].Rows, dicom_images[0].Columns), dtype=np.uint8)

        # make two dictionaries to save the masks
        binary_masks = {}
        binary_mask_continous = {}

        # Loop through all the contours of the OAR
        for contour_item in contour_sequence:
            contour_uid = self.ife_obj.get_contour_uid(contour_item) # Extract contour uids
            self.ife_obj.find_ct_match_seg(dicom_images, dicom_images_uid, contour_uid) # Store the proper CT image

            contour_data = self.ife_obj.get_contour_data(contour_item) # Extract the contour dataset

            # Assuming contour_data is a list of (x, y, z) coordinates
            if contour_uid not in binary_masks.keys():
                binary_masks[contour_uid] = np.zeros_like(self.ife_obj.image.pixel_array, dtype=np.uint8)

            # Calculate the real coordination of the pixels
            x_pixel_list, y_pixel_list = self.calculate_pixel_coordination(contour_data, binary_masks, contour_uid)
            
            # Add the continous new mask to the final dictionary
            if contour_uid in binary_mask_continous.keys():
                binary_mask_continous[contour_uid] += self.make_continous_contour(binary_masks[contour_uid], y_pixel_list, x_pixel_list)
            else:
                binary_mask_continous[contour_uid] = self.make_continous_contour(binary_masks[contour_uid], y_pixel_list, x_pixel_list)
            
            assigned_index = dicom_images_uid.index(contour_uid)
            contour_matrix[assigned_index,:,:] = binary_mask_continous[contour_uid]
        
        return contour_matrix

    def fill_contours(self, binary_masks):
        filled_masks = []
        #continous_array = np.array(list(binary_masks.values()))
        continous_array = binary_masks
        
        for counter in  range(continous_array.shape[0]):
            binary_mask = continous_array[counter,:,:]

            # Convert to uint8 image (0s become 0, 1s become 255)
            binary_image = (binary_mask * 255).astype(np.uint8)

            # Save the binary image as a PNG file
            self.writer_obj.write_cv2_image(self.binary_mask_name, binary_image)

            image = self.reader_obj.read_cv2_image(self.binary_mask_name)

            # Convert the image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            
            # Find contours in the grayscale image
            cnts = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]

            # Draw filled contours on the grayscale image
            for c in cnts:
                cv2.drawContours(gray,[c], 0, (255,255,255), -1)
            
            filled_masks.append(gray)

        # Convert the list of filled masks to a numpy array
        filled_matrix = np.array(filled_masks)
        # Delete the image
        self.writer_obj.delete_cv2_image(self.binary_mask_name)
        return filled_matrix