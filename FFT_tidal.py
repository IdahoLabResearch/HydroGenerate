# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 14:42:37 2021

@author: MITRB
"""

'''
IMPLEMENTING ARIMA FOR FORECASTING STREAM FLOW
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import datetime
from scipy.fft import fft, fftfreq

idx = pd.date_range("2011-05-01",periods=8760,freq='1H')

data1 = pd.read_excel(r'C:\Work\My_Code\Files\ElectricPowerGeneration_May2011_May2012_AdmiraltyInletWA_05052021.xlsx')
data2 = pd.read_excel(r'C:\Work\My_Code\Files\ElectricPowerGeneration_February2010_August2010_AdmiraltyInletWA_05052021.xlsx')
data3 = pd.read_excel(r'C:\Work\My_Code\Files\ElectricPowerGeneration_2019_UpperBayNY_06152021.xlsx')
idx1 = pd.date_range("2011-05-01",periods=len(data1['Hour']),freq='1H')
idx2 = pd.date_range("2010-02-01",periods=len(data2['Hour']),freq='1H')
idx3 = pd.date_range("2019-01-01",periods=len(data3['Hour']),freq='1H')
data1['Date/Time'] = idx1
data1 = data1.drop(columns=['Hour'])
data1 = data1.set_index('Date/Time')

data2['Date/Time'] = idx2
data2 = data2.drop(columns=['Hour'])
data2 = data2.set_index('Date/Time')

data3['Date/Time'] = idx3
data3 = data3.drop(columns=['Hour'])
data3 = data3.set_index('Date/Time')
'''
june = data1[data1.index.month==6]
may = data1[data1.index.month==5]
july  = data1[data1.index.month==7]
'''
data_input = data2[(data2.index.month==5) | (data2.index.month==6) | (data2.index.month==7)]
data_target = data1[(data1.index.month==5) | (data1.index.month==6) | (data1.index.month==7)]
data_upper_bay = data3[(data3.index.month==5) | (data3.index.month==6) | (data3.index.month==7)]

data_input = data_input.reset_index()
data_target = data_target.reset_index()
data_upper_bay = data_upper_bay.reset_index()

'''
Computing FFT
'''
N = len(data_input['Date/Time'])
T = 1.0/60
y = data_input['Velocity (m/s)'].values
yf_inp = fft(y)
xf_inp = fftfreq(N, T)[:N//2]

fig,ax = plt.subplots()
ax.plot(xf_inp, 1.0/N * np.abs(yf_inp[0:N//2]),linewidth=3,label='Admirality Inlet 2010')


N = len(data_target['Date/Time'])
T = 1.0/60
y = data_target['Velocity (m/s)'].values
yf_out = fft(y)
xf_out = fftfreq(N, T)[:N//2]
ax.plot(xf_out, 1.0/N * np.abs(yf_out[0:N//2]),linewidth=2,label='Admilarity Inlet 2011')

N = len(data_upper_bay['Date/Time'])
T = 1.0/60
y = data_upper_bay['Velocity (m/s)'].values
yf_out = fft(y)
xf_out = fftfreq(N, T)[:N//2]
ax.plot(xf_out, 1.0/N * np.abs(yf_out[0:N//2]),linewidth=1,label='Upper Bay 2019')

plt.title('FFT for Tidal data for months May, June, July')
plt.legend()
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid()
plt.show()
'''
from scipy.fft import fft, fftfreq
# Number of sample points
N = len(data2['Date/Time'])
# sample spacing
T = 1.0/60
#x = np.linspace(0.0, N*T, N, endpoint=False)
#y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
y = data2['Velocity (m/s)'].values
yf = fft(y)
xf = fftfreq(N, T)[:N//2]
'''
'''
plt.plot(xf, 1.0/N * np.abs(yf[0:N//2]))
plt.grid()
plt.show()
'''
'''
fig,ax=plt.subplots()
ax.plot(data2['Velocity (m/s)'][:50].values)
ax.plot(data2['Velocity (m/s)'][101:151].values)
plt.grid()
plt.show()
plt.imshow(model.get_weights()[0], vmin=-1, vmax=1, cmap='coolwarm')
'''


'''

Estimate:
    
    X_hat = inv(H(T)H)*H(T)*Z(tidal_velo_data)
    
    Z_est = DC + H*X_hat
    
    
    H = [sinw1 cosw1 sinw2 ...]
    
'''
'''
df = pd.read_csv(r'C:\Work\My_Code\train.csv')
df = df[(df['store'] == 1) & (df['item'] == 1)] # item 1 in store 1
df = df.set_index('date')
y = df['sales']


plt.plot(y)'''