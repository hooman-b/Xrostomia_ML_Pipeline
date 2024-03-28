"""
Explanation: This module plots 'weeklyct_dataframe_final.xlsx' features. 
Also, if you make label dataframe, it will give you the panels for those dataframes as well. 

Author: Hooman Bahrdo for making BarChart class and main function. Other sections were adjusted 
to this work, and the source code can be find: 
https://github.com/Roya-Gharehbeiklou/HydroHomies

Last Revised: 3/28/2024
"""

# General Libraries
import os
import panel as pn
import pandas as pd

# Bokeh libraries
from bokeh.models import LabelSet
from bokeh.plotting import figure
from bokeh.plotting import ColumnDataSource

# Custom Modules
import DataCollectionConfig as dcc

class BarChart:
    def __init__(self, df, columns_names, param):
        self.df = df
        self.columns_names = columns_names
        self.param = param
    
    def bar_chart_panel_maker(self):
        """
        Type: Instance method

        Input: ---

        Explanation: This method assembel all the elements of the pannel and also uses 
                     _update_choices to update the choices of each parameter.

        Output: 1. interactive bar plot pannel
        """

        # Initialize the widgets
        select_param, multi_choice_param = self.widgit_maker()

        # Update the choices
        @pn.depends(select_param[1].param.value, watch=True)
        def _update_choices(select_param):
            """
            Type: dependent function

            Input: 1. the parameter selected by a user

            Explanation: This function is responsible for updating the choices for each parameter.

            Output: ---
            """
            self.param = select_param
            # Extract the new dataset for sketching
            sketch_series = self.data_maker()

            # Change the options and values of the multi_choice widgit for each parameter.
            multi_choice_param[1].options = list(sketch_series.index)
            multi_choice_param[1].value = list(sketch_series.index)

        # Bind all the elements of the interactive plot
        inter_plot = pn.bind(self.render_plot, parameter=select_param[1], choices=multi_choice_param[1])

        # encapsulating the iter_plot to link the plot with the widgits
        final_plot = pn.Row(pn.Column(select_param, multi_choice_param), pn.pane.Bokeh(inter_plot)) 

        return final_plot
    
    def widgit_maker(self):
        """
        Type: instance method

        Input: ---

        Explanation: This method makes selection bar and multichoice box.

        Output: 1. Selection bar.
                2. multi-choice box.
        """

        # Extract the initial dataset
        multi_initial_items = self.data_maker()

        # Make the select bar and assign a name to it
        param_name = pn.pane.Markdown(f'**Parameters**')
        select_param = pn.widgets.Select(value=self.param, options=self.columns_names)
        select_param_layout = pn.Column(param_name, select_param)

        # Make the multi-choice box and assign a name to it 
        item_name = pn.pane.Markdown(f'**Items**')
        multi_choice_param = pn.widgets.MultiChoice( value = list(multi_initial_items.index),
                                                    options= list(multi_initial_items.index))
        choice_item_layout = pn.Column(item_name, multi_choice_param)

        return select_param_layout, choice_item_layout

    
    def render_plot(self, parameter, choices):
        """
        Type: instance method

        Input: 1. parameter: is the parameter like 'year' that we want to sketch its bar plot.
               2. choices: is the group of available items for each parameter.

        Explanation: This metehod sketch the bar plot based on the parameter of interest and return it.

        Output: 1. bar plot.
        """

        # Extract the dataset
        sketch_series = self.data_maker()

        # Extract the dataset for x and y axis
        xaxis = [item for item in sketch_series.index if item in choices]
        yaxis = [sketch_series[value] for value in xaxis]

        # Make  the dataset in ColumnDataSource format
        source = ColumnDataSource(dict(x = xaxis, y = yaxis))

        # Design the plot infrestructure 
        fig = self.fig_maker(parameter, source, xaxis)

        # Add bar plots to the main plot
        fig.vbar(x=xaxis, top=yaxis, width=0.8, color='#EE8262')

        return fig

    def fig_maker(self, parameter, source, xaxis):
        """
        Type: instance method

        Input: 1. parameter: is the parameter like 'year' that we want to sketch its bar plot.
               2. choices: is the group of available items for each parameter.

        Explanation: This metehod sketch the bar plot based on the parameter of interest and return it.

        Output: 1. bar plot.
        """

        # Make labels
        y_label = 'number of patients'
        title = f'number of patients per {parameter}'

        # If the dataset has a list of string as the xaxis make the following figure
        try:
            fig = figure(width=800, height=600,        
                            x_axis_label = parameter,
                            y_axis_label = y_label,
                            title=title,
                            x_range=xaxis)

        # Otherwise, make the following figure
        except:
            fig = figure(width=800, height=600,        
                            x_axis_label = parameter,
                            y_axis_label = y_label,
                            title=title)

        # Add labels to the main figure
        labels = LabelSet(x='x', y='y', text='y', level='glyph',
                        text_align='center', y_offset=5, source=source)
        
        fig.title.align = 'center'
        fig.add_layout(labels)
        return fig

    def data_maker(self):
        """
        Type: instance method

        Input: ---

        Explanation: This metehod makes the dataset that should be sketch as a barplot.

        Output: 1. figure dataset.
        """
        if self.param == 'Year':
            sketch_series = self.df.RTSTART.dt.year.value_counts()

        elif self.param == 'Count_of_weeks':
            sketch_series = self.week_count_maker().sort_index()

        elif self.param == 'age':
            sketch_series = self.age_count_maker().sort_index()

        elif self.param == 'First_day':
            sketch_series = self.fday_count_maker()

        elif self.param == 'n_stage' or self.param == 't_stage':
            sketch_series = self.stage_count_maker().sort_index()

        elif self.param == 'xer_06' or self.param == 'xer_12':
            sketch_series = self.xer_count_maker().sort_index()  

        elif self.param == 'xer_trend':
            sketch_series = self.trend_count_maker().sort_index()   

        else:
            sketch_series = self.df[self.param].value_counts()
        
        return sketch_series

    def trend_count_maker(self):
        """
        Type: instance method

        Input: ---

        Explanation: This metehod counts the number of different trend for patient who are
                     diagnosed with xerostomia.

        Output: 1. a series that contains number of patients per different trends.
        """        
        trend_df = self.df[['xer_06', 'xer_12']]
        stage_list = [self.map_element_to_trend(element) for _, element in trend_df.iterrows()]
        stage_df = pd.DataFrame(stage_list).transpose()
        return stage_df.stack().value_counts()

    def xer_count_maker(self):
        """
        Type: instance method

        Input: ---

        Explanation: This metehod counts the number of labels for xerostomia endpoints.

        Output: 1. a series that contains number of patients per label.
        """
        xer_series = self.df[self.param]
        xer_list = [self.map_element_to_xer(element) for element in xer_series]
        xer_df = pd.DataFrame(xer_list).transpose()
        return xer_df.stack().value_counts()        

    def stage_count_maker(self):
        """
        Type: instance method

        Input: ---

        Explanation: This metehod counts the number of patients in different t or n stages.

        Output: 1. a series that contains number of patients per different t or n stages.
        """
        stage_series = self.df[self.param]
        stage_list = [self.map_element_to_stage(element, self.param) for element in stage_series]
        stage_df = pd.DataFrame(stage_list).transpose()
        return stage_df.stack().value_counts()

    def fday_count_maker(self):
        """
        Type: instance method

        Input: ---

        Explanation: This metehod counts the number of patients per the day of the week that day start
                     their treatment.

        Output: 1. a series that contains number of patients per day of the week.
        """
        fday_series = self.df.First_day
        fday_list = [self.map_element_to_fday(element) for element in fday_series]
        fday_df = pd.DataFrame(fday_list).transpose()
        fday_df = fday_df.stack().value_counts()
        
        # Define the desired order of days of the week
        desired_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        # Reindex the series to match the desired order
        ordered_series = fday_df.reindex(desired_order)    
        return ordered_series

    def age_count_maker(self):
        """
        Type: instance method

        Input: ---

        Explanation: This metehod counts the number of patients per age group.

        Output: 1. a series that contains number of patients per age group.
        """
        age_series = self.df.age

        age_list = [self.map_element_to_age(element) for element in age_series]

        age_df = pd.DataFrame(age_list).transpose()
        return age_df.stack().value_counts()


    def week_count_maker(self):
        """
        Type: instance method

        Input: ---

        Explanation: This metehod counts the number of weekly CTs for each week and make a series of number
                     of patients per each week with number of patients as values and week number as the index.

        Output: 1. a series that contains number of patients per week number.
        """
        fraction_df = self.df.loc[:,'Fraction1':'Fraction9']
        fraction_df['accelerated_rt'] = self.df['accelerated_rt']
        week_list = [fraction_df.apply(lambda row: self.map_element_to_week(row[counter], row[-1]), axis=1) 
                    for counter in range(fraction_df.shape[1] - 1)]

        week_df = pd.DataFrame(week_list).transpose()
        return week_df.stack().value_counts()
    
    @staticmethod
    def map_element_to_week(element, accelerated_rt):
        """
        Type: static method

        Input: 1. element: Is the element that we want to find a week for it.
               2. accelerated_rt: is the plan type of the patient.

        Explanation: this static method get an element let's say 7 with a RT plan type, then assign a proper
                     week for this element and return the week.

        Output: 1. is a week.
        """
        if accelerated_rt == 0:
            element_ranges = {(0, 5): 'Week1', (5, 10): 'Week2', (10, 15): 'Week3', (15, 20): 'Week4', 
                              (20, 25): 'Week5', (25, 30): 'Week6', (30, 35): 'Week7'}

        else:
            element_ranges = {(0, 6): 'Week1', (6, 12): 'Week2', (12, 18): 'Week3',
                           (18, 24): 'Week4', (24, 30): 'Week5', (30, 36): 'Week6'}
        
        for key in element_ranges.keys():

            if element > key[0] and element <= key[1]:
                return element_ranges[key]

    @staticmethod
    def map_element_to_age(individual_age):
        """
        Type: static method

        Input: 1. individual_age: Is the element that we want to find a an age category for .

        Explanation: this static method get an element and find a proper age category for it.

        Output: 1. is a age category.
        """
        age_conditions_dict = {(0, 18):'Under 18', (18, 29): '20-29', (29, 39): '30-39',
                               (39, 49): '40-49', (49, 59): '50-59', (59, 69): '60-69',
                               (69, 79): '70-79', (79, 89): '80-89', (89, 99): '90-99'}

        for key in age_conditions_dict.keys():

            if individual_age > key[0] and individual_age <= key[1]:
                return age_conditions_dict[key]
    
    @staticmethod
    def map_element_to_fday(individual_day):
        """
        Type: static method

        Input: 1. individual_day: Is the element that we want to find a day in week for.

        Explanation: this static method get an element and find a proper day in the week.

        Output: 1. is a day name.
        """
        fday_conditions_dict = {1: 'Monday', 2: 'Tuesday', 3:'Wednesday',
                                4: 'Thursday', 5: 'Friday'}
        
        return fday_conditions_dict[individual_day]
    

    @staticmethod
    def map_element_to_stage(individual_stage, stage_type):
        """
        Type: static method

        Input: 1. individual_stage: Is the element that we want to find a t/n stage for.
               2. stage_type: is the type of stage (n_stage or t_stage)

        Explanation: this static method get an element and find a proper stage.

        Output: 1. is a stage.
        """
        if stage_type == 'n_stage':
            stage_conditions_dict = {('N0'): 'N0', ('N1'): 'N1', ('N2','N2a', 'N2b', 'N2c'): 'N2',
                                  ('N3'): 'N3'}

        else:
            stage_conditions_dict = {('Tis', 'T0', 'T1'): 'T1', ('T2'): 'T2', ('T3'): 'T3',
                                  ('T4a', 'T4b'): 'T4'}

        for key in stage_conditions_dict.keys():
            try:
                if individual_stage in key:
                    return stage_conditions_dict[key]
            
            except TypeError:
                return 'None'   

    @staticmethod
    def map_element_to_xer(individual_xer):
        """
        Type: static method

        Input: 1. individual_xer: Is the element that we want to find a xerostomia label for.

        Explanation: this static method get an element and find a xerostomia endpoint label.

        Output: 1. is a xerostomia endpoint label.
        """
        xer_conditions_dict = {2: 'Positive', 1: 'Negative', 0: 'Not Available'}
        return xer_conditions_dict[individual_xer]

    @ staticmethod
    def map_element_to_trend(individual_trend):
        """
        Type: static method

        Input: 1. individual_trend: Is the element that we want to find a xerostomia trend for.

        Explanation: this static method get an element and find xerostomia trend.

        Output: 1. is a xerostomia trend.
        """
        trend_conditions_dict = {(1, 1):('Negative, Negative'),
                                 (2, 1):('Positive, Negative'),
                                 (1, 2):('Negative, Positive'),
                                 (2, 2):('Positive, Positive')} 
        
        for key in trend_conditions_dict.keys():

            if individual_trend[0] == key[0] and individual_trend[1] == key[1]:
                return trend_conditions_dict[key]
            

class TextPresentor():

    def text_home(self):
        text = pn.pane.Markdown("""
                                ## **Introduction**
                                This panel is made to explain some of the features of the dataset used in my research.
                                It contains one main dataset contains **455** parients. The patients in this dataset can have
                                12- or 6- month endpoint for xerostomia. Moreover, 12 month dataset is a subset of the main
                                dataset that contains **345** patients whose patients only have 12-month endpoint for xerostomia.
                                The patients in the mentioned dataset can have endpoint for 6-month xerostomia. Moreover, the 6-month
                                dataset (contains **418** patients) only contains the patients with 6-month xerostomia endpoint who can have
                                12-month xerostomia endpoint. Finally, 12-6 month dataset (with **310** patients) contains the patients who
                                have both of the endpoints.  

                                ## **Features**
                                The following features are evaluated in this panel:

                                1. **Year**: This bar chart contains the number of patients based on the RT start year.

                                2. **First_day**: This bar chart contains the number of patients based on the RT start weekday. 

                                3. **Number_of_weeklyCTs**: This bar chart investigates for each number of weekly CTs how many patients we have.

                                4. **Modality_adjustment**: This bar chart depicts the number of patients with different treatment approaches in each dataset.

                                5. **Count_of_weeks**: This bar chart evaluate how many patient we have for each week CT.

                                6. **sex**: This bar chart shows the distribution of gender for each cohort.

                                7. **tumor_location**: This bar chart presents the distribution of different tumor locations in each dataset.

                                8. **age**: This bar chart shows the distribution of patients in different age groups in each dataset.

                                9. **n_stage**: This bar chart shows the distribution of different stages of the number of lymph nodes involved in cancer.

                                10. **t_stage**: This bar chart shows the distribution of different stages of the cancer.

                                11. **xer_06**: This bar chart depicts the number of patients with positive, negative and even without 6-month xerostomia label.

                                12. **xer_12**: This bar chart depicts the number of patients with positive, negative and even without 12-month xerostomia label.
                                
                                13. **xer_trend**: This bar chart presents the trend of the side effect in each patient from 6-month endpoint to 12-month endpoint.
                                """)
        return text

    def text_total(self):
        text = pn.pane.Markdown("""
                                 ## Explanation
                                 This dataset contains **455** patients from which **345** patients have 12-month xerostimia endpoint, and **418** patients have
                                 6-month xerostomia endpoint. The extra columns in this bar plot refers to the number of patient who are diagnosed with
                                 positive and negative xerostomia 6 months and 12 months after irradiation.
                                 """)
        return text 

    def text_12month(self):
        text = pn.pane.Markdown("""
                                ## Explanation
                                This dataset contains **345** patients with 12-month xerostimia endpoint. The most important bar chart for this dataset is **Count_of_weeks**
                                since it contains the number of available weekly CTs per week that can be used as an estimation of the number of samples in the dataset to
                                train the model.
                                 """)
        return text 

    def text_6month(self):
        text = pn.pane.Markdown("""
                                ## Explanation
                                This dataset contains **418** patients with 6-month xerostimia endpoint. This dataset is larger than 6-month dataset, and can be a good starting
                                dataset for training different models.The most important bar chart for this dataset is **Count_of_weeks** since it contains the number of available
                                weekly CTs per week that can be used as an estimation of the number of samples in the dataset to train the model.
                                 """)
        return text
    
    def text_12_6_month(self):
        text = pn.pane.Markdown("""
                                ## Explanation
                                This dataset contains **310** patients with available 6-month and 12-month xerostimia endpoints, which is the smallest dataset. The most important
                                feature of this dataset is **xer_trend** bar chart since it depicts the trend ofxerostomia in the patients who have both xerostomia endpoints. As it
                                was expected, the number of negative labels are more than positive labels in this dataset.
                                 """)
        return text 


class Dashboard:
    '''
    This class creates a panel dashboard to which pages can be added
    
    Arguments: 
    title (str): title of the dashboard
    header_color (str): name of a color or hex color code
    css (str): raw css
    
    Returns:    
    dashboard object
    
    Author: Job Mathuis
    reference: https://github.com/Roya-Gharehbeiklou/HydroHomies
    '''

    def __init__(self, title: str, header_color: str, css):
        # initialise dashboard
        self.dashboard = pn.template.BootstrapTemplate(title=title, header_background=header_color, sidebar_width=200)
        self.dashboard.main.extend([pn.pane.Markdown(''), pn.Column(width=1000)]) 
        self.main_page = self.dashboard.main[1]
        pn.extension(raw_css=[css])
        
        # variable to save all the pages
        self.pages = {}
        
        
    def add_page(self, title: str, show_page: bool, *contents):
        ''' 
        Adds a page to the dashboards and create a sidebar navigation button for it 
        
        Arguments:
        title      (str): title of the page
        show_page (bool): boolean to show the page when showing the dahsboard (if more pages have this as True the last page added will be shown)
        
        Returns:
        None
        '''
        sidebar_button = pn.widgets.Button(name=title, width=150, css_classes=['sidebar_button'])  # create sidebar button
        self.dashboard.sidebar.append(sidebar_button)  # append button to sidebar
        sidebar_button.on_click(self._update_page)  # callback
        self.pages[title] = [*contents]  # add the contents to the page dictionary
        if show_page:
            self._show_page(title)
    
    
    def _update_page(self, event):
        '''
        Private callback method to update the page when a sidebar button is clicked 
          
        Arguments:
        event (object): widget cacllback event
        
        Returns:
        None
        '''
        name = event.obj.name  # extract name from event
        self.main_page.clear()  # clear the main page
        self.main_page.append(pn.pane.Markdown(f'# {name}'))  # create title
        self.main_page.extend([item for item in self.pages[name]])  # add all of the contents to the page
        
        
    def _show_page(self, title: str):
        '''
        Private method that show the page of the given page title 
        
        Arguments:
        title (str): title of the page
        
        Returns:
        None
        '''
        self.main_page.clear()
        self.main_page.append(pn.pane.Markdown(f'# {title}'))
        self.main_page.extend([item for item in self.pages[title]])
            
            
    def show(self):
        '''Shows the dashboard''' 
        self.dashboard.show()


class DashboardMaker():

    def __init__(self):
        self.css = dcc.css
        self.title = dcc.title
        self.header_color = dcc.header_color
        self.dashboard_df_path = dcc.dashboard_df_path

    def make_dashboard(self):

        # Change direction to the datasets
        os.chdir(self.dashboard_df_path)

        # Text
        text_obj = TextPresentor()
        home_text = text_obj.text_home()
        total_text = text_obj.text_total()
        twelve_text = text_obj.text_12month()
        six_text = text_obj.text_6month()
        twelve_six_text = text_obj.text_12_6_month()

        # Initialize the Dashboard
        dataset_db = Dashboard(self.title, self.header_color, self.css)

        # Home page
        dataset_db.add_page('Home', True, home_text)

        ## Total Dataset page
        # Assign the total dataset and desired columns
        total_df = pd.read_excel('Overview_weeklyCT_patients.xlsx').drop(columns=['Unnamed: 0'])
        column_names_total = ['Year', 'First_day', 'Number_of_weeklyCTs', 'modality_adjusted', 'Count_of_weeks',
                            'gender', 'tumor_location', 'age', 'n_stage', 't_stage','xer_06', 'xer_12']

        # Make the barplot for this dataset
        bar_plot_total_obj = BarChart(total_df, column_names_total, 'Year')
        bar_plot_total = bar_plot_total_obj.bar_chart_panel_maker()

        # Add total dataset page to the panel
        dataset_db.add_page('Total Datset', False, bar_plot_total, total_text)


        ## 6month Dataset page
        # Assign the total dataset and desired columns
        six_month_df = pd.read_excel('Overview_weeklyCT_patients_6month.xlsx').drop(columns=['Unnamed: 0'])
        column_names_6month = ['Year', 'First_day', 'Number_of_weeklyCTs', 'modality_adjusted', 'Count_of_weeks',
                            'gender', 'tumor_location', 'age', 'n_stage', 't_stage']

        # Make the barplot for this dataset
        bar_plot_6month_obj = BarChart(six_month_df, column_names_6month, 'Year')
        bar_plot_6month = bar_plot_6month_obj.bar_chart_panel_maker()

        # Add 6month dataset page to the panel
        dataset_db.add_page('6 month Dataset', False, bar_plot_6month, six_text)

        ## 12month Dataset page
        # Assign the total dataset and desired columns
        twelve_month_df = pd.read_excel('Overview_weeklyCT_patients_12month.xlsx').drop(columns=['Unnamed: 0'])
        column_names_12month = ['Year', 'First_day', 'Number_of_weeklyCTs', 'modality_adjusted', 'Count_of_weeks',
                            'gender', 'tumor_location', 'age', 'n_stage', 't_stage']

        # Make the barplot for this dataset
        bar_plot_12month_obj = BarChart(twelve_month_df, column_names_12month, 'Year')
        bar_plot_12month = bar_plot_12month_obj.bar_chart_panel_maker()

        # Add 12month dataset page to the panel
        dataset_db.add_page('12 Month Dataset', False, bar_plot_12month, twelve_text)

        ## 12- and 6- month Dataset page
        # Assign the total dataset and desired columns
        twelve_six_month_df = pd.read_excel('Overview_weeklyCT_patients_12_6_month.xlsx').drop(columns=['Unnamed: 0'])
        column_names_12_6_month = ['Year', 'First_day', 'Number_of_weeklyCTs', 'modality_adjusted', 'Count_of_weeks',
                            'gender', 'tumor_location', 'age', 'n_stage', 't_stage', 'xer_trend']

        # Make the barplot for this dataset
        bar_plot_12_6_month_obj = BarChart(twelve_six_month_df, column_names_12_6_month, 'Year')
        bar_plot_12_6_month = bar_plot_12_6_month_obj.bar_chart_panel_maker()

        # Add 12-6month dataset page to the panel
        dataset_db.add_page('12-6 Month Dataset', False, bar_plot_12_6_month, twelve_six_text)


        dataset_db.show()

if __name__ == "__main__":
    aaa = DashboardMaker()
    aaa.make_dashboard()