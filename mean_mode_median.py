# -*- coding: utf-8 -*-
"""
Created on Mon May  3 16:07:48 2021

@author: MITRB
"""

import pandas as pd
import statistics

takey = pd.read_csv(r'C:\Work\My_Code\Files\Narrows_11418000_forecast_hourly.csv')

y = takey['Average (cfs)'].values


mean = statistics.mean(y)

mode = statistics.mode(y)

median = statistics.median(y)


#print(mean,mode,median)


flow_info = pd.DataFrame()
flow_info['Date/Time'] = takey['Date/Time'].copy()
flow_info['Average (cfs)'] = (y/mean)*730

flow_info.to_csv(r'C:\Work\My_Code\Files\mean_check_11418000_forecast.csv',index=False)
'''
flow_info = pd.DataFrame()
flow_info['Date/Time'] = takey['Date/Time'].copy()
flow_info['Average (cfs)'] = (y/mode)*730

flow_info.to_csv(r'C:\Work\My_Code\mode.csv',index=False)

flow_info = pd.DataFrame()
flow_info['Date/Time'] = takey['Date/Time'].copy()
flow_info['Average (cfs)'] = (y/median)*730

flow_info.to_csv(r'C:\Work\My_Code\median.csv',index=False)

'''

