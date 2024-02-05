"""
Explanation:
This module contains the first phase of the data collection pipeline, which is navigation 
of multiple folders to find the desired images. These images can be CT, MRI, and PET.

Author: Hooman Bahrdo
Last Revised:...
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
import DataCollectionConfig
from ImageFeatureExtractor import ImageFeatureExtractor


class Navigator():
    """
    This class searches multiple folders to find a specific type of images
    """

    def __init__(self):

