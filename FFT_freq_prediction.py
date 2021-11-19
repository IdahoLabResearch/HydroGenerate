# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 14:04:19 2021

@author: MITRB
"""

'''
Checking Frequencies of Predicted Data
'''

import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

df = pd.read_excel(r'C:\Work\My_Code\Files\ElectricPowerGeneration_May2011_May2012_AdmiraltyInletWA_05052021_predicted.xlsx')

x_test = df['Velocity (m/s)'].values
x_pred = df['Predicted Velocity (m/s)'].values

N = len(x_test)
T = 1/60
y_test_fft = fft(x_test)
y_freq = fftfreq(N, T)[:N//2]

y_pred_fft = fft(x_pred)

fig,ax = plt.subplots()
ax.plot(y_freq, 1.0/N * np.abs(y_test_fft[0:N//2]),label='Admirality Inlet original data')
ax.plot(y_freq, 1.0/N * np.abs(y_pred_fft[0:N//2]),label='Admirality Inlet predicted data')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid()
plt.legend()