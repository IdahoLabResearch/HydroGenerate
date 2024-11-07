'''
Copyright 2023, Battelle Energy Alliance, LLC
'''

"""
10-2024 
@author: Camilo J. Bastidas Pacheco, J. Gallego-Calderon, Soumyadeep Nag

This module includes function to summarize HydroGenerate results. 
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry import Polygon
   

# define constants needed
cfs_to_cms = 0.0283168 # 1 cubic feet per second to cubic meter per second
ft_to_m = 0.3048 # 1 feet to meters

# function to plot turbine efficiency and power generation as a function of flow
def flow_efficiency_power_plot(x) :
    # extract dataframe output, order and subset wanted values
    if x.pandas_dataframe:
        df = x.dataframe_output
        df_plot = df[['turbine_flow_cfs','efficiency','power_kW']].drop_duplicates('turbine_flow_cfs')
        df_plot = df_plot.sort_values(by='turbine_flow_cfs')
        df_plot.reset_index(drop=True, inplace=True)

        fig, ax1 = plt.subplots(figsize=(8, 5))

        color_plot = 'tab:red'
        ax1.set_xlabel('Flow')
        ax1.set_ylabel('Turbine Efficiency', color=color_plot)
        ax1.plot(df_plot['efficiency'], label="Turbine Efficiency", color=color_plot)
        ax1.tick_params(axis='y', labelcolor=color_plot)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color_plot2 = 'tab:blue'
        ax2.set_ylabel('Power (kW)', color=color_plot2)  # we already handled the x-label with ax1
        ax2.plot(df_plot['power_kW'],'b-', label="Power")
        ax2.tick_params(axis='y', labelcolor=color_plot2)
        ax1.grid(True, axis='both', color='k',linestyle='--',alpha=0.4)
        plt.title("Flow (cfs) versus Turbine Efficiency and Power (kW)")
        fig.tight_layout()  
        plt.close()
        return fig
    
    else:
        print('Plotting turbine efficiency annd power requires flow time series data '\
              'provided as pandas dataframe')

def flow_efficiency_plot(x) :
    # extract dataframe output, order and subset wanted values
    if x.pandas_dataframe:
        df = x.dataframe_output
        df_plot = df[['turbine_flow_cfs','efficiency','power_kW']].drop_duplicates('turbine_flow_cfs')
        df_plot = df_plot.sort_values(by='turbine_flow_cfs')
        df_plot.reset_index(drop=True, inplace=True)

        fig, ax = plt.subplots(figsize=(8, 5))
        color_plot = 'tab:red'
        ax.set_xlabel('Flow')
        ax.set_ylabel('Turbine Efficiency', color=color_plot)
        ax.plot(df_plot['efficiency'], label="Turbine Efficiency", color=color_plot)
        ax.tick_params(axis='y', labelcolor=color_plot)

        ax.grid(True, axis='both', color='k',linestyle='--',alpha=0.4)
        plt.title("Flow (cfs) versus Turbine Efficiency")
        fig.tight_layout()  
        plt.close()
        return fig

    else:        
        print('Plotting turbine efficiency requires flow time series data '\
              'provided as pandas dataframe')

# function to plot the flow duration curve
def flow_duration_curve_plot(x):

    # if x.flowduration_curve:
    try:
        df = x.flowduration_curve.copy()

        fig, ax = plt.subplots(figsize=(8, 5))
        
        ax.set_xlabel('% of time river discharge is exceeded')

        if x.units == 'US':
            ax.set_ylabel('River discharge (ft^3/s)')
            df.Flow = df.Flow / cfs_to_cms
        else:
            ax.set_ylabel('River discharge (m^3/s)')
        
        ax.plot(df['Percent_Exceedance'], df['Flow'], label="Flow duration curve", linewidth=2)
        ax.tick_params(axis='y')
        # Plot horizontal and vertical line with values
        d_flow = x.design_flow
        pcrf = x.pctime_runfull
        plt.xlim([0, 100])
        plt.ylim([0, df.Flow.max() * 1.05])
        ax.hlines(y = d_flow, xmin = 0, xmax = pcrf, color='r', linestyle=':')
        ax.vlines(x = pcrf, ymin = 0, ymax = d_flow, color='r', linestyle=':')
        ax.plot(pcrf, d_flow, 'ro', markersize = 10, label = 'Design flow')
        plt.legend()
        plt.close()
        return fig
    
    # else:
    except AttributeError:
        print('Plotting the flow duration curve requires flow time series data '\
              'provided as pandas dataframe')

# function to plot turbine selection figure
def turbine_type_plot(x):

 # inputs
    head = x.net_head           # head, m
    
    if x.design_flow:
        design_flow = x.design_flow         # flow, m3/s
    else:
        design_flow = x.flow

    if x.units == 'US':
        head = head * ft_to_m
        design_flow = design_flow * cfs_to_cms

    # define polygons of influence for every turbine type
    polygon_pelton = Polygon([(1, 50), (1, 1000), (20, 1000), (60, 500), (50, 400),(1, 50)])
    polygon_turgo = Polygon([(1, 50), (1, 260), (10, 50),(1, 50)])
    polygon_francis = Polygon([(1, 50), (5, 10), (200, 10), (900, 15), (900,80), (100, 700), (6,700),(1, 50)])
    polygon_kaplan = Polygon([(1,1), (1, 20), (9,80), (175,80), (1000,15), (60,1),(1,1)])
    polygon_crossflow = Polygon([(1,4), (1, 100), (10,10), (10, 4),(1,4)])

    # create figure 
    xpoints = np.array([design_flow])
    ypoints = np.array([head]) 

    x,y = polygon_pelton.exterior.xy
    plt.ioff()
    fig = plt.figure(figsize=(8, 5))
    plt.loglog(x, y,label = 'Pelton')
    x,y = polygon_turgo.exterior.xy
    plt.loglog(x, y,label = 'Turgo')
    x,y = polygon_francis.exterior.xy
    plt.loglog(x, y,label = 'Francis')
    x,y = polygon_crossflow.exterior.xy
    plt.loglog(x, y,label = 'Crossflow')
    x,y = polygon_kaplan.exterior.xy
    plt.loglog(x, y,label = 'Kaplan')
    plt.xlim([1, 1000])
    plt.ylim([1, 1000])
    plt.xlabel('Flow (m^3/s)')
    plt.ylabel('Head (m)')
    plt.plot(xpoints, ypoints,'o', label='Site characteristics')
    plt.legend()
    plt.legend(loc='upper right')
    plt.close()

    return fig

# function that generates a monhtly figure given a dataframe and a column name
def monthly_figure_plot(df, var_fig):
    y_mean = df[var_fig].groupby(df[var_fig].index.month).mean()
    y_med = df[var_fig].groupby(df[var_fig].index.month).median()
    x = y_mean.index

    # Compute upper and lower bounds using the IQR
    lower = df[var_fig].groupby(df[var_fig].index.month).agg(lambda x: x.quantile(0.25))
    upper = df[var_fig].groupby(df[var_fig].index.month).agg(lambda x: x.quantile(0.75))

    # Draw plot with error band and extra formatting to match seaborn style
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(x.values, y_mean, label='Mean')
    ax.plot(x.values, y_med, label='Median')
    ax.plot(x.values, lower, color='tab:blue', alpha=0.1)
    ax.plot(x.values, upper, color='tab:blue', alpha=0.1)
    ax.fill_between(x.values, lower, upper, alpha=0.2, label= 'Interquartile Range')
    ax.set_xlim([1,12])
    ax.set_xlabel('Month [-]')

    if var_fig == 'turbine_flow_cfs':
        ax.set_ylabel('Turbine Flow [cfs]')

    if var_fig == 'energy_kWh':
        ax.set_ylabel('Electricity Generation [kWh]')

    if var_fig == 'capacity_factor':
        ax.set_ylabel('Capacity Factor')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.locator_params(axis='x', nbins=12)
    ax.legend()
    ax.figure.tight_layout()
    plt.close()
    return fig

# functions to generate monthly figures for capacity factor, turbine flow, electricity generation 

# 1) Capacity factor
def plant_capfactor_plot(x):
    
    if x.pandas_dataframe:
        df = x.dataframe_output
        df['rated_power_kw'] = x.rated_power 
        df['capacity_factor'] = df.power_kW / df.rated_power_kw
        cf = monthly_figure_plot(df, 'capacity_factor')
        return(cf)
    
    else:
        print('Plotting plant performance requires flow time series data '\
              'provided as pandas dataframe')
        
# 2) turbine flow
def plant_turbineflow_plot(x):
    
    if x.pandas_dataframe:
        df = x.dataframe_output
        tf = monthly_figure_plot(df, 'turbine_flow_cfs')
        return(tf)
    
    else:
        print('Plotting plant performance requires flow time series data '\
              'provided as pandas dataframe')
        
# 3) Electricty generation
def plant_elecgeneration_plot(x):
    
    if x.pandas_dataframe:
        df = x.dataframe_output
        eg = monthly_figure_plot(df, 'energy_kWh')
        return(eg)
    
    else:
        print('Plotting plant performance requires flow time series data '\
              'provided as pandas dataframe')