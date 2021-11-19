# -*- coding: utf-8 -*-
"""
Created on Thu May 27 12:23:35 2021

@author: MITRB
"""

import pandas as pd
import numpy as np

df = pd.read_csv(r'C:\Work\My_Code\IFPFieldDemo04222021_OneMinuteMicroPMURecord.csv',low_memory=False)

names = np.unique(df['PPA ID'])

for i in range(len(names)):
    
    val = df.loc[df['PPA ID'] == names[i]]
    
    val.to_csv('C:\Work\My_Code\Files\Value_{}.csv'.format(i),index=False)
    