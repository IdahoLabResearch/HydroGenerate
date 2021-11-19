# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 09:35:10 2021

@author: MITRB
"""

import pandas as pd
import matplotlib.pyplot as plt

flow_info= pd.read_csv(r'C:\Work\My_Code\Files\11421000_2019-01-01_15min_forecast.csv')

flow_info['Date/Time'] = pd.to_datetime(flow_info['Date/Time'])
flow_info=flow_info.set_index('Date/Time')
flow_info = flow_info.resample('60min').mean()
flow_info=flow_info.reset_index()

flow_info.to_csv(r'C:\Work\My_Code\Files\11421000_forecast_hourly_Data.csv',index=False)