# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 10:05:48 2021

@author: MITRB
"""

'''
All the required libraries
'''

import numpy as np
import pywt
import pandas as pd
import keras
from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from datetime import datetime

'''
Importing Data for training, testing and predicting
using Hybrid ANN (Wavelet + AI)
'''
data1 = pd.read_excel(r'C:\Work\My_Code\Files\ElectricPowerGeneration_May2011_May2012_AdmiraltyInletWA_05052021.xlsx')
data2 = pd.read_excel(r'C:\Work\My_Code\Files\ElectricPowerGeneration_February2010_August2010_AdmiraltyInletWA_05052021.xlsx')
idx1 = pd.date_range("2011-05-01",periods=len(data1['Hour']),freq='1H')
idx2 = pd.date_range("2010-02-01",periods=len(data2['Hour']),freq='1H')
data1['Date/Time'] = idx1
data2['Date/Time'] = idx2
data2 = data2.drop(columns=['Hour'])
data1 = data1.drop(columns=['Hour'])

data2['Normalized'] = (data2['Velocity (m/s)'].values - min(data2['Velocity (m/s)'].values)/(max(data2['Velocity (m/s)'].values)-
                                                                                             min(data2['Velocity (m/s)'].values)))

data1['Normalized'] = (data1['Velocity (m/s)'].values - min(data1['Velocity (m/s)'].values)/(max(data1['Velocity (m/s)'].values)-
                                                                                             min(data1['Velocity (m/s)'].values)))

start_date1 = '2011-05-01'
#start_date2 = '2012-05-01'
start_date3 = '2010-05-01'
end_date1 = '2011-08-04'
#end_date2 = '2012-09-01'
end_date3 = '2010-08-04'

new_1 = (data1['Date/Time']>= start_date1) & (data1['Date/Time'] < end_date1)

#new_2 = (data1['Date/Time']>= start_date2) & (data1['Date/Time'] < end_date2)

new_3 = (data2['Date/Time']>= start_date3) & (data2['Date/Time'] < end_date3)

df_input = data2.loc[new_3]

#df_test = data1.loc[new_2]

df_target = data1.loc[new_1]


#splitting the input and target into a 70/30 split for training and testing

coeffs_input_train = pywt.wavedec(df_input['Velocity (m/s)'][:1596].values,'db15',level=3) #[cD3,cD2,cD1,cA3] = coeffs
coeffs_input_test = pywt.wavedec(df_input['Velocity (m/s)'][1597:].values,'db15',level=3)
coeffs_target_train = pywt.wavedec(df_target['Velocity (m/s)'][:1596].values,'db15',level=3) #[cD3,cD2,cD1,cA3] = coeffs
coeffs_target_test = pywt.wavedec(df_target['Velocity (m/s)'][1597:].values,'db15',level=3)
#start1 = data1.index.searchsorted(dt.datetime(2010, 1, 2))
#train = data2['Normalized'].iloc[:3100].values
#test = data2['Normalized'].iloc[3101:].values

[cD3_input_train,cD2_input_train,cD1_input_train,cA3_input_train] = coeffs_input_train

[cD3_input_test,cD2_input_test,cD1_input_test,cA3_input_test] = coeffs_input_test

[cD3_input_target,cD2_input_target,cD1_input_target,cA3_target_train] = coeffs_target_train

[cD3_target_test,cD2_target_test,cD1_target_test,cA3_target_test] = coeffs_target_test

'''
Computing Wavelet Decomposition of the training set
'''

# coeffs = pywt.wavedec(train,'db15',level=3) #[cD3,cD2,cD1,cA3] = coeffs

# [cD3,cD2,cD1,cA3] = coeffs

'''
Building the Neural Network Model
'''

model = Sequential()

model.add(Dense(128, input_shape=(4,),activation='tanh'))
model.add(Dense(64,activation='relu'))
model.add(Dense(32,activation='relu'))
model.add(Dense(4,activation='sigmoid'))

model.compile(loss='mean_squared_error',optimizer='adam',metrics=['accuracy'])
model.fit([cD3_input_train,cD2_input_train,cD1_input_train,cA3_input_train],
          [cD3_input_target,cD2_input_target,cD1_input_target,cA3_target_train],
          epochs=150,batch_size=10)
loss,accuracy=model.evaluate([cD3_input_test,cD2_input_test,cD1_input_test,cA3_input_test],
                             [cD3_target_test,cD2_target_test,cD1_target_test,cA3_target_test])
july_2011_calculated = model.predict(july_2010)

july_2011_calculated(ifft)

print(accuracy)
