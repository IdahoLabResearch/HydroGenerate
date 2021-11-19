# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 13:04:16 2021

@author: MITRB
"""

import pandas as pd
import numpy as np

df = pd.read_excel(r'C:\Work\My_Code\Files\Gen.xlsx')
df1 = pd.read_excel(r'C:\Work\My_Code\Files\Load.xlsx')

df['Date (MST)']=df['Date/Time'].astype('datetime64[ns]')
df1['Date (MST)']=df1['Date/Time'].astype('datetime64[ns]')


    
val=pd.merge(df,df1,on='Date (MST)')
#val=val.drop(columns=['UTC Time (EST +4)','Unnamed: 3', 'Agency', 'Site_ID','TZ','Indic'])

val.to_csv('C:\Work\My_Code\Files\Gen_Load_merge_April.csv',index=False)