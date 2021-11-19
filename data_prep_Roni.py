# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 09:51:32 2021

@author: MITRB
"""

'''
Preparing data for Roni
'''

import pandas as pd

df= pd.read_csv(r'C:\Work\My_Code\Files\HydroForecast_trinity-center-v6_Bhaskar.csv')

names = [n for n in df if n.startswith('discharge_q')]

#df_new = df.melt(id_vars=["issue_time"]

#df = df[[names[0],names[1],names[2],names[3],names[4],names[5],names[6],
#         names[7],names[8],names[9],names[10]]]

flow_info = pd.melt(df,id_vars='lead_time_hours',value_vars=names,value_name='Average (cfs)')

idx1 = pd.date_range("1870-01-01",periods=len(flow_info['Average (cfs)']),freq='1H')
flow_info['Date/Time']=idx1
flow_info = flow_info.drop(columns=['lead_time_hours','variable'])
#flow_info.to_csv('C:\Work\My_Code\Files\Roni_data_appended.csv',index=False)