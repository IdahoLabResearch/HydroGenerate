# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 14:17:15 2021

@author: MITRB
"""
import numpy as np
import pandas as pd

capex_hydro_0_5 = 3329597.45
opex_hydro_0_5 =  83239.93

capex_hydro_1 = 6357186.47
opex_hydro_1 = 158929.66

capex_pv_0_5 = 860000
opex_pv_0_5 = 9500

capex_pv_1 = 1720000
opex_pv_1 =19000


rev_pv_hydro = 141923.782713
rev_pv = 72077.700885
rev_hydro = 248298.103775

rev_ppa_hydro = 279411.24
rev_ppa_pv = 66172.56
rev_ppa_hy_pv = 173858.35

capex_sys = np.array([capex_pv_1,capex_hydro_1,capex_pv_0_5+capex_hydro_0_5])
opex_sys = np.array([opex_pv_1,opex_hydro_1,opex_pv_0_5+opex_hydro_0_5])

rev_sys = np.array([rev_pv,rev_hydro,rev_pv_hydro])

rev_sys_ppa = np.array([rev_ppa_pv, rev_ppa_hydro, rev_ppa_hy_pv])


'''

for j in range(len(capex_sys)):
    cost = capex_sys[j]
    opex = opex_sys[j]
    revenue = rev_sys[j]
    revenue_ppa = rev_sys_ppa[j]
    cost_ppa = capex_sys[j]
    for i in range(0,5):
    
        cost = cost + opex - rev_sys
        cost_ppa = cost_ppa + opex - rev_sys_ppa
    #print(cost)
    
    roi_5y = (capex_sys[j]+opex_sys[j]-cost[j])/(capex_sys[j]+opex_sys[j])
    
    roi_5y_ppa = (capex_sys[j]+opex_sys[j]-cost_ppa[j])/(capex_sys[j]+opex_sys[j])

    print('NMA ROI:',roi_5y*100)
    print('PPA ROI:',roi_5y_ppa*100)
    new_revenue = (capex_sys[j]/7)+opex_sys[j]
    
    change_rev = ((new_revenue - revenue)/revenue)*100
    
    change_rev_ppa = ((new_revenue - revenue_ppa)/revenue_ppa)*100
    
    new_capex  = 7*(revenue - opex)
    new_capex_ppa = 7*(revenue_ppa - opex)
    
    #print(new_capex)
    
    
    change_capex = (new_capex - cost[j])/cost[j]
    change_capex_ppa = (new_capex_ppa - cost[j])/cost[j]
    
    print('change in rev',change_rev)
    
    print('change in capex ppa',change_rev_ppa)
    print('Change in capex',change_capex*100)
    print('Change in capex ppa',change_capex_ppa*100)
    
'''

def payback_period(capex, opex, yearly_revenue, grant=0.1):
    
    count = 0
    # This is the initial cost at year 0
    cost = capex*(1-grant)
    
    while cost>0:
        cost = cost + opex - (yearly_revenue)
        count = count + 1
        
    return count

df_payback = pd.DataFrame()
df_payback['grant'] = np.arange(0,100,10)
'''
capex_sys = np.array([capex_hydro_1])
opex_sys = np.array([opex_hydro_1])
rev_sys_ppa = np.array([rev_ppa_hydro])
'''
list_names = ['payback_years_pv','payback_years_hydro','payback_years_pv_hydro']

for index in range(len(capex_sys)):
    #print(index)
    capex = capex_sys[index]
    opex = opex_sys[index]
    yearly_revenue = rev_sys[index]
    name = list_names[index]
    
    for idx,row in df_payback.iterrows():
        #print(row['grant'])
        df_payback.loc[idx,name] = payback_period(capex, opex, yearly_revenue, grant=row['grant']/100)


