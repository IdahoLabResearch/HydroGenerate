# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 14:22:46 2021

@author: MITRB
"""

import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

df = pd.DataFrame()

list_names = ['Fault Resistance','Current Limiting Inductance']

df['Fault Location']=np.linspace(50,900,35)
res =[]
cli = []

for i in range(len(df['Fault Location'])):
    n = random.randint(1,200)
    j = random.randint(10,200)
    res.append(n)
    cli.append(j)
    
plt.plot(cli)    
# df['Fault Resistance'],df['Current Limiting Inductance']=[res,cli]

df.to_csv(r'C:\Work\My_Code\Files\Fault_Info_new.csv',index=False)