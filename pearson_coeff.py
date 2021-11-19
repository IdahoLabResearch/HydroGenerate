# -*- coding: utf-8 -*-
"""
Created on Mon May 17 09:17:39 2021

@author: MITRB
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May 17 08:23:37 2021

@author: MITRB
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import datetime
import pywt

data2 = pd.read_excel(r'C:\Work\My_Code\Files\ElectricPowerGeneration_February2010_August2010_AdmiraltyInletWA_05052021.xlsx')
idx = pd.date_range("2010-02-01",periods=len(data2['Hour']),freq='1H')
data2['Date/Time'] = idx
data2 = data2.drop(columns=['Hour'])

x = data2['Velocity (m/s)'].values

k = ['db3','db4','db5','db6','db7','db8','db9','db10','db11','db12','db13','db14','db15']


for j in range(len(k)):
    wave_db = pywt.Wavelet(k[j])
    
    x = data2['Velocity (m/s)'].values
    
    start = 1000
    y = wave_db.dec_hi
    
    x = x[start:start+len(y)]
    
    val_x = []
    val_y = []
    for i in range(len(y)):
       
        #x = x[:len(y)]
        Ex = (x[i] - np.mean(x))
        val_x.append(Ex)
        Ey = (y[i] - np.mean(y))
        val_y.append(Ey)
        
    numerator = np.sum([a*b for a,b in zip(val_x,val_y)])
    
    denominator = np.sqrt(np.sum([x**2 for x in val_x]))*np.sqrt(np.sum([x**2 for x in val_y]))
    
    pearson = numerator/denominator
    
    print(pearson)


