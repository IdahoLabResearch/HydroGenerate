# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 19:07:22 2020

@author: MITRB
"""


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

'''
df=pd.DataFrame(index=['2011','2012','2013','2014','2015','2016','2017',
                       '2018','2019'],
                data={'EV + PHEV':[17763,53171,97102,118882,114023,159616,
                            195581,361615,326644],
                      'Charging Outlet':[3394,13392,19410,25602,30945,
                                         42029,50627,61067,78301]})
'''
df1=pd.DataFrame(index=['2010','2011','2012','2013','2014','2015','2016','2017',
                       '2018','2019'],
                data={'EV':[0,10064,14251,47694,67990,71064,84275,
                            104487,241413,244569],
                      'Plug-in Hybrid':[345,7671,38584,49008,55357,
                                        42958,72837,89992,119894,84959]})




'''
x=len(df['EV + PHEV'])
plt.figure(1)
ax=df.plot(figsize=(8,6))
ax.grid(True,axis='y',color='k',alpha=0.3)
ax.set_title('EV Sales vs Charging Outlets (2011 to 2019)')
'''
plt.figure(2)
ax=df1.plot(kind='bar',stacked=True,figsize=(8,6))
ax.grid(False,axis='y',color='k',alpha=0.3)
ax.set_title('Annual Sales of plug-in electric cars in the U.S. by type of powertrain(2010 to 2019)')

df1['Total']=df1['EV']+df1['Plug-in Hybrid']

g=df1['Total']

for rec in ax.patches:
    height=rec.get_height()
    ax.text(rec.get_x() + rec.get_width()/2,
            rec.get_y() + height/20,
            "{:.0f}".format(height),
            ha='left',va='bottom',rotation=90,fontsize=10)

for rec,i in zip(ax.patches,range(len(g.values))):
    #for i in range(len(g.values)):
        height=rec.get_height()
    
        ax.text(rec.get_x() + rec.get_width()/70,
                rec.get_y() + g.values[i]+1000,
                g.values[i],
                ha='left',va='bottom',rotation=00,fontsize=12)
        
        print(rec)
    
plt.show()



# plt.show()