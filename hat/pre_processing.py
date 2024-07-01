'''
Copyright 2023, Battelle Energy Alliance, LLC
'''

"""
03-2023
@author: Soumyadeep Nag, Camilo J. Bastidas Pacheco, J. Gallego-Calderon

This module calculates hydropower potential for diffrent type of hydropower installations
"""

import numpy as np
import math
from numpy.core.fromnumeric import mean
from numpy.lib.function_base import median
import pandas as pd
from datetime import datetime
import os
from abc import ABC, abstractmethod
from hat.hydraulic_processing import *
from hat.turbine_calculation import *
from numbers import Number
from math import exp
   
class FlowPreProcessing():

    #TODO: we need to run these functions either with user input (min, max flows) or with defaults and modify the turbine flow

    def annual_maintenance_constraint(self,flow_obj):

        flowx = flow_obj.original_flow

        flowx["flow"] = flow_obj.flow
        
        weekly = flowx.groupby(pd.Grouper(level="dateTime", freq='W')).mean() 
        
        years = (flowx.index.year.unique()).to_numpy()   #['2010','2011','2012']#
        
        if isinstance(years, int)==False:
            years = list(map(str,years.tolist()))

        for year in years:
            min_flowx = weekly[year]['discharge_cfs'].min()
            min_flow_index = weekly.loc[weekly.discharge_cfs == min_flowx].index[0]

            year = min_flow_index.year
            month=min_flow_index.month
            day=min_flow_index.day
            week_start = f'{year}-{month}-{day}'

            Three_one = [1, 3, 5, 7, 8, 10, 12]
            Three_zero = [4, 6, 9, 11]
            day2 = day+6
            if month in Three_one:
                if day2>31:
                    day2 = day2-31
                    month = month+1
                elif month in Three_zero:
                    if day2>30:
                        day2 = day2-30
                        month = month+1
            if np.remainder(year,4)==0 or month==2:
                if day2>29:
                    day2 = day2-29
                    month = month+1
                else:
                    if day2>28:
                        day2 = day2-28
                        month = month+1
            if month>12:
                month = 1
                year = year+1
                               
            week_end = f'{year}-{month}-{day2}'
            flowx.loc[week_start:week_end,'flow'] = 0
                  
        flow_obj.turbine_flow = flowx["flow"].to_numpy()
        

    def turbine_flow_checker(self, flow_obj):

        flow = flow_obj.flow # this is a numpy array
        min_flow = flow_obj.min_flow 
        design_flow = flow_obj.design_flow
        if min_flow is not None:
            flow_obj.turbine_flow = np.where(flow < min_flow, 0, flow)
        else:
             min_flow = .1*design_flow         
             flow_obj.turbine_flow = np.where(flow < min_flow, 0, flow)
             #print('Soumyadeep was here')
        
        flow = flow_obj.turbine_flow 

        flow_obj.turbine_flow = np.where(flow > design_flow, design_flow, flow)      
