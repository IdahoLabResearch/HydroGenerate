# -*- coding: utf-8 -*-
"""
Created on Fri May 15 08:22:30 2020

@author: MITRB
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from colour import Color

red = Color("red")
colors = list(red.range_to(Color("green"),10))
colors = [color.rgb for color in colors]

time=['12AM','1AM','2AM','3AM','4AM','5AM','6AM','7AM','8AM','9AM','10AM',
      '11AM','12PM','1PM','2PM','3PM','4PM','5PM','6PM','7PM',
      '8PM','9PM','10PM','11PM']

data=(0.04,0.03,0.02,0.01,0.02,0.03,0.16,0.22,0.09,0.14,0.15,0.22,0.24,
      0.26,0.21,0.20,0.23,0.26,0.22,0.19,0.15,0.11,0.12,0.07)

fig = plt.figure(1, (10,6))
ax = fig.add_subplot(1,1,1)
col=[]
for val in data:
    if val <= 0.07:
        col.append('blue')
    if val >=0.16:
        col.append('red')
    if val > 0.07 and val < 0.16:
        col.append("orange")
ax.bar(time, data,color=col,width=0.6)

vals = ax.get_yticks()
ax.set_yticklabels(['{:,.0%}'.format(x) for x in vals])
plt.xticks(rotation=45,fontweight='bold')
plt.yticks(fontweight='bold',fontsize=10)
ax.grid(True,axis='both',color='k',linestyle='--',alpha=0.3)
plt.axvspan(11.5,19.5,color='cyan', alpha=0.3)
plt.text(4,0.255,'Peak demand period',color='k',fontsize=15)
ax.set_xlabel("Time",fontweight='bold',fontsize=11)
plt.legend()
ax.set_ylabel("Average hourly utilization", fontweight='bold',fontsize=11)
plt.show()
