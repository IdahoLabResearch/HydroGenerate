    # -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 14:29:31 2020

@author: MITRB
"""

import pandas as pd
import numpy as np
import matplotlib as plt
from datetime import datetime

df= pd.read_excel(r'C:\Work\VRGHydro\IFP_flow.xlsx')
#df['DateTime']=pd.to_numeric(df['DateTime'])
#df['Generation'] = pd.to_numeric(df['Generation'])
df['DateTime']=df.DateTime.dt.strftime('%m/%d/%Y')
#df1=df.drop('Date',axis=1).groupby(['DateTime'])['GPCFS.PV'].mean().reset_index(name='Average (cfs)')
df1=df.groupby(['DateTime'])['Flow'].mean().reset_index(name='Average (cfs)')
df1.to_excel(r'C:\Work\VRGHydro\IFP_daily_flowdata.xlsx')