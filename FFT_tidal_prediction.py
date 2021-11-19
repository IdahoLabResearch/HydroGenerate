# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 10:38:29 2021

@author: MITRB
"""

import numpy as np
import pylab as pl
from numpy import fft
import pandas as pd


def fourierExtrapolation(x, n_predict):
    #n = x.size
    T = 1.0/60
    n = len(x)
    n_harm = len(fft.fftfreq(n, T)[:n//2]) # number of harmonics in model
    #n_harm = 1104                     
    t = np.arange(0, n)
    p = np.polyfit(t, x, 1)         # find linear trend in x
    x_notrend = x - p[0] * t        # detrended x
    x_freqdom = fft.fft(x_notrend)  # detrended x in frequency domain
    f = fft.fftfreq(n)              # frequencies
    indexes = list(range(n))
    # sort indexes by frequency, lower -> higher
    indexes.sort(key=lambda i: np.absolute(f[i]))

    t = np.arange(0, n + n_predict)
    restored_sig = np.zeros(t.size)
    for i in indexes[:1 + n_harm * 2]:
        ampli = np.absolute(x_freqdom[i]) / n   # amplitude
        phase = np.angle(x_freqdom[i])          # phase
        restored_sig += ampli * np.cos(2 * np.pi * f[i] * t + phase)
    return restored_sig + p[0] * t


if __name__ == "__main__":
    data2 = pd.read_excel(r'C:\Work\My_Code\Files\UpperBayNYTidalGeneration2018_08052021.xlsx')
    idx2 = pd.date_range("2018-01-01",periods=len(data2['Hour']),freq='1H')
    data2['Date/Time'] = idx2
    data2 = data2.drop(columns=['Hour'])
    x = data2['Velocity (cm/sec)'].values
    n_predict = 8760          # hours of prediction
    extrapolation = fourierExtrapolation(x, n_predict)
    pl.plot(np.arange(0, extrapolation.size), extrapolation, 'C0',
            label='Prediction')
    pl.plot(np.arange(0, x.size), x, 'C1', label='Original', linewidth=1)
    pl.xlabel('Time (Hr)')
    pl.ylabel('Velocity (cm/s)')
    pl.legend()
    pl.grid()
    pl.show()