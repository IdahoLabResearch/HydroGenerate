'''
Copyright 2023, Battelle Energy Alliance, LLC
'''

"""
03-2023
@author: Camilo J. Bastidas Pacheco, MITRB, J. Gallego-Calderon

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


    def turbine_flow_checker(self, flow_obj):
        flow = flow_obj.flow # this is a numpy array
        min_flow = flow_obj.min_flow 
        design_flow = flow_obj.design_flow
        #print(flow)
        if min_flow is not None:
            flow_obj.turbine_flow = np.where(flow < min_flow, 0, flow)
            flow = flow_obj.turbine_flow 
        
        flow_obj.turbine_flow = np.where(flow > design_flow, design_flow, flow)