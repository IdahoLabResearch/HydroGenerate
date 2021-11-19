# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 14:32:50 2021

@author: MITRB
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from matplotlib.ticker import NullFormatter
from matplotlib.dates import MonthLocator, DateFormatter,WeekdayLocator,DayLocator
csfont = {'fontname':'Times New Roman'}
daf = pd.read_excel(r'C:\Work\My_Code\Files\scaled_hydropower.xlsx')
fuf = pd.read_excel(r'C:\Work\My_Code\Files\final_data.xlsx',sheet_name='Payback Period')
huf = pd.read_excel(r'C:\Work\My_Code\Files\final_data.xlsx')
date = daf['Date/Time'].tolist()
date = pd.to_datetime(date, format="%m/%d/%Y %H:%M")

'''
Hydro Generation
'''
# fig,bx = plt.subplots(figsize=(20,10))
# bx.plot(date,huf['Power_0_5 (MW)'].values,label='0.5MW',linewidth=3)
# bx.plot(date,huf['Power_1 (MW)'].values,label='1MW',linewidth=3)
# xfmt = mdates.DateFormatter('%b')
# months = mdates.MonthLocator()
# plt.gca().xaxis.set_major_locator(MonthLocator())
# plt.gca().xaxis.set_major_formatter(xfmt)
# plt.title('Hydropower Generation',fontsize=30,**csfont)
# plt.xticks(rotation=45,fontsize=20)
# plt.yticks(fontsize=20)
# plt.xlabel('Month',fontsize=30,**csfont)
# plt.ylabel('Power (MW)',fontsize=30,**csfont)
# plt.legend(loc='upper center',bbox_to_anchor=(0.5,-0.15),fancybox=True,shadow=True,fontsize=20,
#             ncol=5)
# plt.grid(linewidth=0.85,color='k')
# plt.show()
'''
Load Plot
'''
# fig,cx = plt.subplots(figsize=(20,10))
# cx.plot(date,(huf['LMP ($\MW)'].values),label='Price',linewidth=3)
# # cx.plot(date,(huf['PPA_PV_Hydro'].values),label='PPA',linewidth=3)
# # cx.plot(date,(huf['NMA_PV_Hydro'].values),label='NMA',linewidth=3)
# xfmt = mdates.DateFormatter('%b')
# months = mdates.MonthLocator()
# plt.gca().xaxis.set_major_locator(MonthLocator())
# plt.gca().xaxis.set_major_formatter(xfmt)
# plt.title('Locational Marginal Pricing',fontsize=30,**csfont)
# plt.xticks(rotation=45,fontsize=20)
# plt.yticks(fontsize=20)
# plt.xlabel('Month',fontsize=30,**csfont)
# plt.ylabel('Price ($/MWh)',fontsize=30,**csfont)
# plt.legend(loc='upper center',bbox_to_anchor=(0.5,-0.15),fancybox=True,shadow=True,fontsize=20,
#             ncol=5)
# plt.grid(linewidth=0.85,color='k')
# plt.show()

'''
Revenue Plots
'''
# fig,cx = plt.subplots(figsize=(20,10))
# cx.plot(date,(huf['LMP_PV_Hydro'].values),label='LMP',linewidth=3)
# cx.plot(date,(huf['PPA_PV_Hydro'].values),label='PPA',linewidth=3)
# cx.plot(date,(huf['NMA_PV_Hydro'].values),label='NMA',linewidth=3)
# xfmt = mdates.DateFormatter('%b')
# months = mdates.MonthLocator()
# plt.gca().xaxis.set_major_locator(MonthLocator())
# plt.gca().xaxis.set_major_formatter(xfmt)
# plt.title('Revenue from PV & Hydro installation under different market contracts',fontsize=30,**csfont)
# plt.xticks(rotation=45,fontsize=20)
# plt.yticks(fontsize=20)
# plt.xlabel('Month',fontsize=30,**csfont)
# plt.ylabel('Revenue ($)',fontsize=30,**csfont)
# plt.legend(loc='upper center',bbox_to_anchor=(0.5,-0.15),fancybox=True,shadow=True,fontsize=20,
#             ncol=5)
# plt.grid(linewidth=0.85,color='k')
# plt.show()

'''
Scaled Hydro Plot
'''
fig,ax = plt.subplots(figsize=(20,10))
#ax.plot(date,rev_lmp,label='Revenue from Wholesale Markets',linewidth=2)
#ax.plot(date,rev_nma,label = 'Revenue from NMA',linewidth=3)
ax.plot(date,daf['Average (cfs)'].values/max(daf['Average (cfs)']),label='Scaled flow for irrigation channel',linewidth=3)
ax.plot(date,daf['Ramp'].values,label='Expected scaling of irrigational channels',linewidth=3, color = 'r')

xfmt = mdates.DateFormatter('%b')
months = mdates.MonthLocator()
plt.gca().xaxis.set_major_locator(MonthLocator())
plt.gca().xaxis.set_major_formatter(xfmt)
plt.title('Seasonal Profile',fontsize=30,**csfont)
plt.xticks(rotation=45,fontsize=20)
plt.yticks(fontsize=20)
plt.xlabel('Month',fontsize=30,**csfont)
plt.ylabel('Flow rate (p.u.)',fontsize=30,**csfont)
plt.legend(loc='upper center',bbox_to_anchor=(0.5,-0.15),fancybox=True,shadow=True,fontsize=20,
            ncol=5)
plt.grid(linewidth=0.85,color='k')
plt.show()

'''
Payback Period
'''
# fig,px = plt.subplots(figsize=(20,10))

# px.plot(fuf['Grant [%]'],fuf['PV'],label='PV Only (NMA)',linestyle='--',color='r',linewidth=3)
# px.plot(fuf['Grant [%]'],fuf['Hydro'],label='Hydro Only (NMA)',linestyle='--',color='g',linewidth=3)
# px.plot(fuf['Grant [%]'],fuf['PV & Hydro'],label='PV & Hydro (NMA)',linestyle='--',color='b',linewidth=3)

# px.plot(fuf['Grant [%]'],fuf['PV.1'],label='PV Only (PPA)',linestyle='-',color='orange',linewidth=3)
# px.plot(fuf['Grant [%]'],fuf['Hydro.1'],label='Hydro Only (PPA)',linestyle='-',color='grey',linewidth=3)
# px.plot(fuf['Grant [%]'],fuf['PV & Hydro.1'],label='PV & Hydro (PPA)',linestyle='-',color='k',linewidth=3)

# plt.title('Payback Period Under Different Market Contracts',fontsize=30,**csfont)
# plt.xticks(rotation=0,fontsize=20)
# plt.yticks(fontsize=20)
# plt.xlabel('External Grant (%)',fontsize=30,**csfont)
# plt.ylabel('Payback Period (years)',fontsize=30,**csfont)
# plt.legend(loc='upper center',bbox_to_anchor=(0.5,-0.19),fancybox=True,shadow=True,fontsize=20,
#             ncol=5,)

# plt.grid(linewidth=0.85,color='k')
# plt.show()