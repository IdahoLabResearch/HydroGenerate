# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt







dfg=pd.read_csv(r'C:\Users\MITRB\Downloads\20200425isolf.csv')

new = dfg["Time Stamp"].str.split(" ", n = 1, expand = True)

dfg["Day"]=new[0]
dfg["Time"]=new[1]

dfg.drop(columns =["Time Stamp"], inplace = True)
df1=dfg.iloc[0:24]
df1 = df1.reset_index(drop=True)
df2=dfg.iloc[24:48]
df2 = df2.reset_index(drop=True)
df3=dfg.iloc[48:72]
df3 = df3.reset_index(drop=True)
df4=dfg.iloc[72:96]
df4 = df4.reset_index(drop=True)


ax=df1.plot(y='NYISO',label='04/25/2020',figsize=(12,8))
df2.plot(ax=ax,y='NYISO',label='04/26/2020')
df3.plot(ax=ax,y='NYISO',label='04/27/2020')
df4.plot(ax=ax,y='NYISO',label='04/28/2020')
ax.set_title('Load Commitment for New York ISO',fontdict={'fontsize':25})
ax.xaxis.set_ticks(np.arange(0, 24, 1))
ax.tick_params(which='both',labelsize=20)
ax.grid(True,axis='x')
ax.set_xlabel('Time (hr)',fontdict={'fontsize':20},labelpad=15)
ax.set_ylabel('Load (MWh)',fontdict={'fontsize':20},labelpad=15)


