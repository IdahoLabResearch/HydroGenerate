# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 11:23:33 2021

@author: MITRB
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import datetime
from keras.models import Sequential
from keras.layers import Dense
from scipy.fft import fft, fftfreq

def create_fourier_weights(signal_length):  
    "Create weights, as described above."
    k_vals, n_vals = np.mgrid[0:signal_length, 0:signal_length]
    theta_vals = 2 * np.pi * k_vals * n_vals / signal_length
    return np.hstack([np.cos(theta_vals), -np.sin(theta_vals)])

idx = pd.date_range("2011-05-01",periods=8760,freq='1H')

data1 = pd.read_excel(r'C:\Work\My_Code\Files\ElectricPowerGeneration_May2011_May2012_AdmiraltyInletWA_05052021.xlsx')
data2 = pd.read_excel(r'C:\Work\My_Code\Files\ElectricPowerGeneration_February2010_August2010_AdmiraltyInletWA_05052021.xlsx')
idx1 = pd.date_range("2011-05-01",periods=len(data1['Hour']),freq='1H')
idx2 = pd.date_range("2010-02-01",periods=len(data2['Hour']),freq='1H')
data1['Date/Time'] = idx1
data1 = data1.drop(columns=['Hour'])
data1 = data1.set_index('Date/Time')

data2['Date/Time'] = idx2
data2 = data2.drop(columns=['Hour'])
data2 = data2.set_index('Date/Time')
data_input = data2[(data2.index.month==5) | (data2.index.month==6) | (data2.index.month==7)]
data_target = data1[(data1.index.month==5) | (data1.index.month==6) | (data1.index.month==7)]
data_input = data_input.reset_index()
data_target = data_target.reset_index()

data_input = data2['Velocity (m/s)'].values
data_target = data1['Velocity (m/s)'].values


signal_len = len(data_input)

W_fou = create_fourier_weights(signal_len)

y = np.matmul(data_input,W_fou)


fft = np.fft.fft(data_input)
y_fft = np.hstack([fft.real, fft.imag])

print('rmse: ', np.sqrt(np.mean((y - y_fft)**2)))
'''
X = np.hstack([data_input.real,data_input.imag])
Y = np.hstack([fft.real,fft.imag])

X = np.reshape(X,(1,8858))
Y = np.reshape(Y,(1,8858))
batch = 100000
model = Sequential([Dense(signal_len*2, input_dim=signal_len*2, use_bias=False)])
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(X, Y, epochs=100, batch_size=100)

plt.imshow(model.get_weights()[0], vmin=-1, vmax=1, cmap='coolwarm')
'''
