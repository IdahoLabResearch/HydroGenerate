# -*- coding: utf-8 -*-
"""
Created on Tue May 18 17:14:46 2021

@author: MITRB
"""

'''
Computing a regression analysis for the generated data of IFP
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import datetime as dt
from matplotlib.ticker import NullFormatter
from matplotlib.dates import MonthLocator, DateFormatter,WeekdayLocator

#Final file for validation
df = pd.read_csv(r'C:\Work\My_Code\Files\Comparison_IFP_clipped.csv') 


date = df['Date/Time'].tolist()
date = pd.to_datetime(date, format="%m/%d/%Y")
IFP_flow = df['Average_IFP_flow (cfs)']
USGS_flow = df['Average_USGS_flow (cfs)']
IFP_calpower_IFP_flow = df['Power_from_IFP_flow (MW)']
IFP_calpower_USGS_flow = df['Power_from_USGS_flow (MW)']
IFP_avgpower = df['Average_IFP_provided (MW)']

'''
#sns.regplot(IFP_calpower_USGS_flow,IFP_avgpower)
m, b = np.polyfit(IFP_calpower_IFP_flow, IFP_avgpower, 1)
fig,ax = plt.subplots()

ax.plot(IFP_calpower_USGS_flow,IFP_avgpower,'o')

ax.plot(IFP_calpower_USGS_flow,(m*IFP_calpower_USGS_flow)+b)
'''
diff_USGS = IFP_calpower_USGS_flow - IFP_avgpower
fig,ax = plt.subplots(figsize=(12,6))
p1,=ax.plot(date,IFP_avgpower,label='Actual Generation from IFP (MW)')

p2,=ax.plot(date,IFP_calpower_USGS_flow,label='Estimated Generation of IFP (MW)')
xfmt = mdates.DateFormatter('%d/%m/%y')
months = mdates.MonthLocator()
plt.gca().xaxis.set_major_locator(MonthLocator())
plt.gca().xaxis.set_major_formatter(xfmt)
#ax.fill_between(date,diff_USGS,IFP_calpower_USGS_flow,alpha=0.3,
                #label='Reserve (MW)')
lines=[p1,p2]
plt.legend(lines, [l.get_label() for l in lines], loc='upper center',
           bbox_to_anchor=(0.5,-0.2),fancybox=True,shadow=True, ncol=5)
plt.ylabel('Power (MW)')
plt.xticks(rotation=45)
plt.title('Comparison of Idaho Falls Power Generation')

plt.grid()
plt.show()


'''
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
'''