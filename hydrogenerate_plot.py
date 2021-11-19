# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 15:45:45 2020

@author: MITRB
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from matplotlib.ticker import NullFormatter
from matplotlib.dates import MonthLocator, DateFormatter,WeekdayLocator
import numpy as np


# from WPTO_turbine_eff_flow_option_advanced_VRG_website import *

def plot(flow_info,op,site_no,):
    
    if(op=='From File'):
    
        def make_patch_spines_invisible(ax):
            ax.set_frame_on(True)
            ax.patch.set_visible(False)
            for sp in ax.spines.values():
                sp.set_visible(False)
        
        #dates = flow_info['Date/Time'].map(lambda t: t.date()).unique()
        dates = flow_info['Date/Time'].tolist()
        
        
        xfmt = mdates.DateFormatter('%m\n%y')
        months = mdates.MonthLocator()
        fig,host=plt.subplots()
        fig.subplots_adjust(right=0.85)
        #ax = fig.add_subplot(1,1,1)
        plt.gca().xaxis.set_major_locator(MonthLocator())
        plt.gca().xaxis.set_major_formatter(xfmt)
        
        par1 = host.twinx()
        par2 = host.twinx()
        
        par2.spines["right"].set_position(("axes",1.2))
        make_patch_spines_invisible(par2)
        par2.spines["right"].set_visible(True)
        p1,= host.plot(dates,flow_info['Efficiency (%)'].values,'g-',label="Efficiency")
        p2,= par1.plot(dates,flow_info['Power (MW)'].values,'b-',label="Power")
        p3,= par2.plot(dates,flow_info['Average_clipped (cfs)'],'r',label="Flow rate")
         
        
        host.set_ylabel("Efficiency (%)",color='g')
        par1.set_ylabel("Power (MW)",color='b')
        
        #ax1=ax.twinx()
        #ax1.plot(power,'b-')
        #vals = ax1.get_xticks()
        #ax1.set_xticklabels(['{:,.0%}'.format(x) for x in vals])
        host.grid(True, axis='both', color='k',linestyle='--',alpha=0.4)
        #ax1.set_xlabel("Days")
        par2.set_ylabel("Flow rate (cu.ft/s)",color='r')
        lines = [p1,p2,p3]
        host.legend(lines, [l.get_label() for l in lines], loc='upper center',bbox_to_anchor=(0.5,-0.2),fancybox=True,
                    shadow=True, ncol=5)
        plt.title("Data from USGS Site {}".format(site_no))
        
        plt.gcf().autofmt_xdate()
        plt.show()
        
    else:
        
        effi_cal= np.insert(effi_cal,0,0)
        flow_arr1 = np.insert(flow_arr,0,0)
        power = np.insert(power,0,0)
        
        flow_arr = flow_range/maxflow
        fig,ax=plt.subplots()
        #ax = fig.add_subplot(1,1,1)
        ax.plot(flow_arr1,effi_cal,'g-',marker='*',markerfacecolor='b',markersize=7)
        vals = ax.get_xticks()
        ax.set_xticklabels(['{:,.0%}'.format(x) for x in vals])
        ax.grid(True, axis='both', color='k',linestyle='--',alpha=0.4)
        ax.set_xlabel("Percentage of rated flow (%)")
        ax.set_ylabel("Efficiency",color='g')
        
        ax1=ax.twinx()
        ax1.plot(flow_arr1,power,'b-',marker='o',markerfacecolor='r',markersize=7)
        vals = ax1.get_xticks()
        ax1.set_xticklabels(['{:,.0%}'.format(x) for x in vals])
        ax1.grid(True, axis='both', color='k',linestyle='--',alpha=0.4)
        ax1.set_xlabel("Percentage of rated flow (%)")
        ax1.set_ylabel("Power (MW)",color='b')
        plt.title('Estimated Power and Turbine Efficiency as a Function of Rated Flow')
        plt.show()
        
        return None