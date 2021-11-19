# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 16:04:34 2021

@author: MITRB
"""

'''
Creating a MLR
'''


import pandas as pd
from sklearn import linear_model
import numpy as np

y=pd.read_csv(r'C:\Work\My_Code\Files\y.csv') #Yuba 11421000
x1 = pd.read_csv(r'C:\Work\My_Code\Files\x1.csv') #Englebright 11418000
x2=pd.read_csv(r'C:\Work\My_Code\Files\x2.csv') #Deer Creek 11418500


y = y['Average (cfs)'].values

x1_flow = x1['Average (cfs)'].values

x2_flow = x2['Average (cfs)'].values


X = pd.DataFrame({'x1':x1_flow,'x2':x2_flow},columns=['x1','x2'])

#X = pd.DataFrame({'x1':x1_flow},columns=['x1'])

#X = X['x1','x2'].values.reshape(-1,1)


#y = pd.DataFrame({'y':y},columns=['y'])

regr = linear_model.LinearRegression()

fit =regr.fit(X,y)

coef = regr.coef_

intercept = regr.intercept_

r2 = regr.score(X,y)

response = regr.predict(X)

'''
print(coef)
print(intercept)
print(r2)
'''


'''
Calculating new 15 min flow values for x1
'''

'''
y_new = pd.read_csv(r'C:\Work\My_Code\Files\11421000_2019-01-01_corr.csv')
x2_new = pd.read_csv(r'C:\Work\My_Code\Files\11418500_2019-01-01.csv')
'''
y_new = pd.read_csv(r'C:\Work\My_Code\Files\Narrows_forecast_15min.csv')

y_new_val = y_new['Average (cfs)'].values

#x2_new_val = x2_new['Average (cfs)'].values

x1_new = (y_new_val - intercept)/coef[:1]

flow_info = pd.DataFrame()

flow_info['Date/Time'] = y_new['Date/Time'].copy()

flow_info['Average (cfs)'] = x1_new.tolist()

flow_info.to_csv(r'C:\Work\My_Code\Files\x1_new.csv',index=False)

'''
Making hourly data
'''

flow_info['Date/Time'] = pd.to_datetime(flow_info['Date/Time'])
flow_info=flow_info.set_index('Date/Time')
flow_info = flow_info.resample('60min').mean()
flow_info=flow_info.reset_index()

flow_info.to_csv(r'C:\Work\My_Code\Files\Narrows_11418000_forecast_hourly.csv',index=False)

