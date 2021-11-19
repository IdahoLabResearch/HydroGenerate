# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 14:16:53 2021

@author: MITRB
"""

import matplotlib.pyplot as plt
import numpy as np

width=0.25

uncontrolled=[80,85,90,100,120,130,155,175,195,190,140,120,80,75,70,60,55]
controlled=[75,85,90,100,105,110,120,125,130,125,120,85,80,80,80,80,80]
nopv=[75,80,85,95,105,110,120,120,125,120,110,80,75,70,60,60,55]    

r1=np.arange(len(uncontrolled))
r2=[x+width for x in r1]
r3=[x-(width) for x in r1]
plt.figure(figsize=(8,6))

plt.bar(r1,uncontrolled,width=width,edgecolor='k',color='red', label='Unmanaged')
plt.bar(r2,controlled,width=width,edgecolor='k',color='blue',label='Managed')
plt.bar(r3,nopv,width=width,edgecolor='k',color='yellow',label='No PEV Load')

'''
plt.plot(r1,uncontrolled,color='b', label='Unmanaged')
plt.plot(r2,controlled,color='r',label='Managed')
plt.plot(r3,nopv,color='g',label='No PEV Load')
'''
plt.xticks(np.arange(min(range(len(uncontrolled))),max(range(len(uncontrolled)))+1,4),['12:00 PM','4:00 PM','8:00 PM','12:00 AM','4:00 AM'])
plt.grid(True,axis='both',color='k',alpha=0.4,linestyle='--')
plt.xlabel('Time',fontweight='bold')
plt.ylabel('Feeder Power (MW)', fontweight='bold')
plt.title('Feeder Power for Managed vs Unmanaged Charging',fontsize=12,fontweight='bold')
plt.legend(loc='upper center',bbox_to_anchor=(0.5,-0.098),fancybox=True,shadow=True, ncol=5)
plt.show()