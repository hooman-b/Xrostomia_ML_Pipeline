# Data Collection Phase
### Pipeline Application
This pipeline can be used for finding WeeklyCTs in different folders, Making dataframe from their properties, and transferring them to a destination folder. However, one can use Navigator, WeeklyTransferring modules for other types of the images such as other types of CTs, MRI, and PET scans. 

### Pipeline Sections
In this section, I will describe different sections of the DataCollection pipeline, and I will mention some of the properties of the modules. For more information, one can have a look at each module seperately.

#### **Navigation Phase**
In this phase, the desired paths, in which the user wants to find a specific kind of image such as weeklyCTs, are navigated. Then, dataframes, one dataframe for each directory that contains all the basic necessary information, are created and saved in the destination directory. This phase is implemented through the 'Navigator' module, which contains the Navigator class. A set of controlling keys is available in the 'DataCollectionConfig' file that one can adjust the program for the desired files.

**Navigator Class**

This class searches multiple folders to find a specific type of images.

Attributes:

1. df_processor_obj: An object of the DataFrame processor class.
2. writer_obj: An object of the writer class for writing dataframes.
3. log_obj: An object of the logger class for logging events.
4. navigation_paths (list): List of paths to navigate through.
5. navigation_file_name (str): Name of the navigation file.
6. min_slice_num (int): Minimum number of slices.
7. modality (str): Modality of the images.
8. time_limit (timestamp): Time limit for navigation like pd.Timestamp('2014-01-01'). 
9. general_df_path (str): Path to the general DataFrame.
10. exclusion_set (set): Set of keywords to exclude.