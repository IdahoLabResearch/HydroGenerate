'''
Copyright 2023, Battelle Energy Alliance, LLC
'''

"""
07-2024 
@author: Soumyadeep Nag, Camilo J. Bastidas Pacheco, J. Gallego-Calderon

This module applies the flow limit constaints and incorporates the impact of annual maintenance activities
"""

import numpy as np
import pandas as pd
from datetime import datetime
   

# Hydraulic design parameters
class FlowPreProcessingParameters:
    def __init__(self, minimum_turbineflow, minimum_turbineflow_percent,       # Flow parameters
                 annual_maintenance_flag, major_maintenance_flag): 
        '''
#         This class initializes Flow preprocessing parameters needed for multiple calculations 
#         Parameter descriptions are provided below:
#         '''         
# Inputs
        self.minimum_turbineflow = minimum_turbineflow        # minimum flow through the turbine (m3/s)     
        self.minimum_turbineflow_percent = minimum_turbineflow_percent      # Set minimum flow by using a percent of design flow, deault is 10  (%, 1-100)
        self.annual_maintenance_flag = annual_maintenance_flag        # Boolean to include annual maintenance or not
        self.major_maintenance_flag = major_maintenance_flag      # Boolean to include major maintenance or not



class FlowPreProcessing():

    # Function that sets max turbine flow to the design flow
    def max_turbineflow_checker(self, flow_obj):

        flow = flow_obj.flow            # this is a numpy array
        design_flow = flow_obj.design_flow
        flow_obj.turbine_flow = np.where(flow > design_flow, design_flow, flow)         # turbine_flow is created here as this code is always active and runs 1st. flow is < design flow

    # Function that sets min turbine flow to the design flow
    def min_turbineflow_checker(self, flow_obj):
        flow = flow_obj.turbine_flow # this is a numpy array        
        design_flow = flow_obj.design_flow

        # check if the user entered a min flow value
        if flow_obj.minimum_turbineflow is not None:
            min_flow = flow_obj.minimum_turbineflow
        else:
            if flow_obj.minimum_turbineflow_percent is not None:         # Check if a user entered min flow percentage if not, use 10% as default
                min_flow_percent =  flow_obj.minimum_turbineflow_percent
            else:
                min_flow_percent = 10           # Default   
     
            min_flow = (min_flow_percent / 100) * design_flow           # Compute minimum flow that passes through the turbine
            flow_obj.minimum_turbineflow = min_flow            # update

        flow_obj.turbine_flow = np.where(flow < min_flow, 0, flow)          # replace flows less than min flow with 0

    def annual_maintenance_implementer(self, flow_obj):
        # Function to set annual maintennace - i.e., make the flow 0 for a week a year

        turbine_flow = flow_obj.turbine_flow            # turbine flow series with max and min (if on) limits implemented
        datetime_index = flow_obj.datetime_index            # datetime index of the user flow
        flow = pd.DataFrame(data= turbine_flow, index= datetime_index, columns=['flow_cms'])            # create dataframe with date and flow in m3/s
        
        # Create series with maintennance years
        start_date = datetime_index[0].year         # Start Year
        end_date = datetime_index[-1].year          # End year
        maint_years = list(range(start_date, end_date, 1))          # Years where there will be maintenance - every year

        # Find minimum week - maintennance week
        weekly = flow .groupby(pd.Grouper(level="dateTime", freq='W')).mean().iloc[1:-1]             # compute the two-weekly mean and drop first and last
        weekly['week'] = weekly.index.strftime('%W')
        week_maint = weekly.groupby('week').mean().idxmin()[0]
        
        # Generate a series with the monday of every maintenance week
        start_days = []
        for m in maint_years:
            start_days.append(datetime.strptime(str(m) + str(week_maint) + '1', "%Y%W%w"))          # Monday of the week where maintenance starts

        # Generate a date series of maintenance from start date
        dates_maint = []        # maintenance dates
        for d in start_days:
            # for day in range(7):
            dates_maint.append(pd.date_range(d, periods= 7).date)           # generate 7 days for each year
            #  dates_maint.append((sd + datetime.timedelta(days=day)).strftime("%Y-%m-%d"))

        dates_maint = np.concatenate(dates_maint, axis= 0)      # generate single array
        flow['date'] = flow.index.date          # add date to dataframe
        flow.loc[flow.date.isin(dates_maint), 'flow_cms'] = 0           # replace flow in minimum weeks with 0

        flow_obj.turbine_flow = flow['flow_cms'].to_numpy()         # update

    # Function that schedules the major maintennace
    def major_maintenance_implementer(self, flow_obj):
        # Major maintenance will happend on the month with lowest flow a year - during the first 15 days of this month.

        turbine_flow = flow_obj.turbine_flow            # turbine flow series with max and min (if on) limits implemented
        datetime_index = flow_obj.datetime_index            # datetime index of the user flow
        flow = pd.DataFrame(data= turbine_flow, index= datetime_index, columns=['flow_cms']) # create dataframe with date and flow in m3/s
        
        # Find maintennance years
        start_date = datetime_index[0].year         # Start Year
        end_date = datetime_index[-1].year          # End year
        maint_years = list(range(start_date, end_date, 5))          # Years where there will be maintenance - every 5 years
        del maint_years[0]          # remove the first year

        # Find minimum two-week period - maintennance week
        weekly = flow .groupby(pd.Grouper(level="dateTime", freq='2W')).mean().iloc[1:-1]             # compute the two-weekly mean and drop first and last
        weekly['week'] = weekly.index.strftime('%W')
        week_maint = weekly.groupby('week').mean().idxmin()[0]

        # Generate a series with the monday of every maintenance week
        start_days = []
        for m in maint_years:
            start_days.append(datetime.strptime(str(m) + str(week_maint) + '1', "%Y%W%w"))          # Monday of the week where maintenance starts
            
        # Generate a date series of maintenance from start date
        dates_maint = []
        for d in start_days:
            dates_maint.append(pd.date_range(d, periods= 14).date)           # generate 14 days for each year
        
        dates_maint = np.concatenate(dates_maint, axis= 0)

        # Make flow 0 during those days
        flow['date'] = flow.index.date
        flow.loc[flow.date.isin(dates_maint), 'flow_cms'] = 0           # replace flow in minimum weeks with 0
        
        flow_obj.turbine_flow = flow['flow_cms'].to_numpy()         # update


