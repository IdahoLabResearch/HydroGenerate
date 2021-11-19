# -*- coding: utf-8 -*-
"""
Created on Mon May 17 07:06:52 2021

@author: MITRB
"""

'''
Importing from the wavelet family
'''

import pywt
import pandas as pd
import numpy as np

k=['db1','db2','db3','db4','db5','db6','db7','db8','db9','db10','db11','db12','db13','db14','db15']

wavedata = pd.DataFrame()

for i in range(len(k)):
    
    wave = pywt.Wavelet(k[i])
    wavedata[k[i]]= [wave.dec_hi]
wavedata.to_csv(r'C:\Work\My_Code\Files\wavelet_coeff.csv')
#print(wavelet.dec_hi)