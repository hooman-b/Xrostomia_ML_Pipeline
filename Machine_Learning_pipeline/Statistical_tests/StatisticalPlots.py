"""
Explanation: This module is used to draw different statistical plots.

Author: Hooman Bahrdo
Last Revised:...
"""


import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import norm
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression



class StatisticalPlots():
    
    def scatter_plot_input_processor(self, main_df, parameters_dict):
        x_element_list = [main_df[col_name] for col_name in parameters_dict['x_element_list']]
        y_element_list = [main_df[col_name] for col_name in parameters_dict['y_element_list']]
        line_info = [[np.min(main_df[parameters_dict['line_info'][0]]) - parameters_dict['line_info'][1],
                     np.max(main_df[parameters_dict['line_info'][0]]) + parameters_dict['line_info'][1]], 
                    [np.min(main_df[parameters_dict['line_info'][0]]) - parameters_dict['line_info'][1], 
                     np.max(main_df[parameters_dict['line_info'][0]]) + parameters_dict['line_info'][1]],
                     parameters_dict['line_info'][3]]

        return x_element_list, y_element_list, line_info

    def scatter_plot_maker(self, main_df, parameters_dict):
        
        x_element_list, y_element_list, line_info = self.scatter_plot_input_processor(main_df, parameters_dict)
        color_list = parameters_dict['color_list']
        label_list = parameters_dict['label_list']
        alpha_list = parameters_dict['alpha_list']
        figure_dict = parameters_dict['figure_dict']
        line = parameters_dict['line']
        logistic = parameters_dict['logistic']

        fig, ax = plt.subplots(figsize=(10, 10))

        for counter, x_element in enumerate(x_element_list): 
            ax.scatter(x=x_element, y=y_element_list[counter], color=color_list[counter],
                        alpha=alpha_list[counter], marker='o', label=label_list[counter])

            if logistic:
                X = x_element.values.reshape(-1, 1)
                y = y_element_list[counter].values.reshape(-1, 1)

                # Create and fit a linear regression model
                model = LinearRegression()
                model.fit(X, y)

                ax.plot(X, model.predict(X), color='salmon',  linestyle=':', linewidth=2,
                        label='Fitted Line')
        
        if line:
            ax.plot(line_info[0], line_info[1], label=line_info[2])

        # Add labels to the plot
        ax.set_xlabel(figure_dict['x'], fontsize=16)
        ax.set_ylabel(figure_dict['y'], fontsize=16)

        # Add a title to the plot
        ax.set_title(figure_dict['title'], fontsize=18)

        # Add a legend to the plot
        ax.legend()

        # Add support lines in the x and y axes
        ax.grid(True, linestyle='--', alpha=0.5)

        return fig


    def histogram_plot_maker(self, main_df, parameters_dict):

        # Make the input elements
        element_list = main_df[parameters_dict[element_list][0]]
        color_list = parameters_dict[color_list]
        label_list = parameters_dict[label_list]
        alpha_list = parameters_dict[alpha_list]
        figure_dict = parameters_dict[figure_dict]

        # Create a histogram
        fig, ax = plt.subplots(figsize=(10, 5))
        n, bins, patches = ax.hist(element_list[0], bins=30, color=color_list[0], density=True, edgecolor='black', alpha=0.7, label=label_list[0])

        # Add a line plot (probability density function)
        ax.plot(bins, norm.pdf(bins, np.mean(element_list[0]), np.std(element_list[0])), color='darkgreen', linestyle='dashed')

        ax.axvline(x=np.mean(element_list[0]), color="darkgreen", linestyle='--', label=f'Mean {label_list[0]}')

        y_place = (np.max(n) * 3) / 4.
        # Annotate the mean value with text
        ax.annotate(f'Mean: {np.mean(element_list[0]):.2f}',
                    xy=(np.mean(element_list[0]), y_place),
                    xytext=(np.mean(element_list[0]) - np.mean(element_list[0]) * 0.15, y_place),
                    arrowprops=dict(arrowstyle='->', edgecolor='black', facecolor='white'),
                    color='darkgreen',
                    fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.3', edgecolor='none', facecolor='white'))

        # Add labels to the plot
        ax.set_xlabel(figure_dict['x'], fontsize=16)
        ax.set_ylabel(figure_dict['y'], fontsize=16)

        # Add a title to the plot
        ax.set_title(figure_dict['title'], fontsize=18)

        # Add a legend to the plot
        ax.legend()

        return fig

    def violin_plot_maker(self, main_df, parameters_dict):

        category_df = main_df.loc[:,parameters_dict['element_list']]

        # Create a violin plot using Seaborn
        sns.set(style="whitegrid")
        sns.catplot(kind='violin', data=category_df, height=8, aspect=1.5, palette="Set2")

        # Customize labels and title if needed
        plt.xlabel('Categories', fontsize=16)
        plt.ylabel('Delta Surface Area', fontsize=16)
        plt.title('Delta Surface Area', fontsize=18)
        plt.tight_layout()

        # Get the current figure and return it
        fig = plt.gcf()
        return fig

    def heatmap_plot_maker(self, main_df, parameters_dict):

        category_df = main_df.loc[:,parameters_dict['element_list']]
        title = parameters_dict['title']

        corre = category_df.corr()

        # Create a heatmap using seaborn
        plt.figure(figsize=(10, 8))
        sns.heatmap(corre, cmap='viridis', annot=True, fmt=".2f", linewidths=.5)
        plt.title(f'Heatmap of {title}')

        # Get the current figure and return it
        fig = plt.gcf()
        return fig    

    def plot_selector(self, test_name):

        # make the function name
        method_name = f'{test_name}_plot_maker'

        return getattr(self, method_name)