# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 16:48:42 2021

@author: MITRB
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from matplotlib.ticker import NullFormatter
from matplotlib.dates import MonthLocator, DateFormatter,WeekdayLocator,DayLocator

df = pd.read_excel(r'C:\Work\My_Code\Files\1year_data_load_energy_task.xlsx')

date = df['Date/Time'].tolist()
date = pd.to_datetime(date, format="%m/%d/%Y %H:%M")

rev_lmp = df['Revenue_LMP ($)'].values
rev_nma = df['Revenue_NMA ($)'].values

fig,ax = plt.subplots(figsize=(20,10))
#ax.plot(date,rev_lmp,label='Revenue from Wholesale Markets',linewidth=2)
#ax.plot(date,rev_nma,label = 'Revenue from NMA',linewidth=3)
ax.plot(date,df['Power (MW)'].values,label='Hourly Generation',linewidth=2)
xfmt = mdates.DateFormatter('%m/%d')
months = mdates.MonthLocator()
plt.gca().xaxis.set_major_locator(MonthLocator())
plt.gca().xaxis.set_major_formatter(xfmt)
plt.title('Hydropower Generation',fontsize=30)
plt.xticks(rotation=45,fontsize=20)
plt.yticks(fontsize=20)
plt.xlabel('',fontsize=20)
plt.ylabel('Power (MW)',fontsize=30)
plt.legend(loc='upper center',bbox_to_anchor=(0.5,-0.15),fancybox=True,shadow=True,fontsize=20,
           ncol=5)
plt.grid()
plt.show()