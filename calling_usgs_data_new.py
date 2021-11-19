# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 11:46:54 2021

@author: MITRB
"""

'''
Creating a class that can access all my hydrocodes
'''

import pandas as pd
import numpy as np
from usgs_api import get_data
from hydrogenerate import calculate_potential
from hydrogenerate_plot import plot

site_no='11251000'
begin_date = '2012-01-01'
end_date = '2012-12-31'

flow_info = get_data(site_no,begin_date,end_date)


'''
calculate_potential(flow_info, rated_flow=None, rated_power=None, turb= None, 
                        head_input=None,op='Timeseries', sys_effi=None,
                        system='pipe', flow_column='Flow (cfs)')
'''

x= calculate_potential(flow_info,head_input=40,op='Timeseries',system='reservoir', flow_column='Flow (cfs)')

plot(op)