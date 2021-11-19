# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 12:21:05 2021

@author: MITRB
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from matplotlib.ticker import NullFormatter
from matplotlib.dates import MonthLocator, DateFormatter,WeekdayLocator,DayLocator

#df = pd.read_excel(r'C:\Work\My_Code\Files\energy_yearly_load.xlsx')
#df = pd.read_excel(r'C:\Work\My_Code\Files\1year_data_load_energy_task.xlsx')
df = pd.read_excel(r'C:\Work\My_Code\Files\final_data.xlsx')
date = df['Date/Time'].tolist()
date = pd.to_datetime(date, format="%m/%d/%Y %H:%M")
jan = df.loc[df['Date/Time'].dt.month ==1]
feb = df.loc[df['Date/Time'].dt.month ==2]
mar = df.loc[df['Date/Time'].dt.month ==3]
apr = df.loc[df['Date/Time'].dt.month ==4]
may = df.loc[df['Date/Time'].dt.month ==5]
june = df.loc[df['Date/Time'].dt.month ==6]
july = df.loc[df['Date/Time'].dt.month ==7]
aug = df.loc[df['Date/Time'].dt.month ==8]
sep = df.loc[df['Date/Time'].dt.month ==9]
octo = df.loc[df['Date/Time'].dt.month ==10]
nov = df.loc[df['Date/Time'].dt.month ==11]
dec = df.loc[df['Date/Time'].dt.month ==12]



fig,ax = plt.subplots()



date = df['Date/Time'].tolist()
date = pd.to_datetime(date, format="%m/%d/%Y %H:%M")

# ax.plot(jan['power_1_mw'],label='January')
# ax.plot(feb['power_1_mw'],label='February')
# ax.plot(mar['power_1_mw'],label='March')
ax.plot(apr['power_1_mw'],label='April')
ax.plot(may['power_1_mw'],label='May')
ax.plot(june['power_1_mw'],label='June')
ax.plot(july['power_1_mw'],label='July')
ax.plot(aug['power_1_mw'],label='August')
ax.plot(sep['power_1_mw'],label='September')
# ax.plot(octo['power_1_mw'],label='October')
# ax.plot(nov['power_1_mw'],label='November')
# ax.plot(dec['power_1_mw'],label='December')

plt.title('Total Load',fontsize=20)
plt.ylabel('Power (kW)', fontsize = 20)
plt.legend(loc='upper center',bbox_to_anchor=(0.5,-0.098),fancybox=True,shadow=True, ncol=5)
plt.grid()
plt.show()