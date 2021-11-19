# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 14:21:13 2021

@author: MITRB
"""

'''
FFT as least square fit
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math


L = 10
N=15
x = np.linspace(0.05,L,N+1).T
x = x[:-1]
y=x**2

yk=np.fft.fft(x)/len(x)
yk=yk[0:N//2]

A0=yk[0]
A=2*(yk.real[2:])
B= -2*(yk.imag[2:])

yy=A0

'''
for k in range(1,len(A)):
    print(k)
    yy=yy+A[k]*math.cos(2*np.pi/(L*k*x[k]))+B[k]*math.sin(2*np.pi/(L*k*x[k]))  
'''
