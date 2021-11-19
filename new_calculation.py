# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 10:37:37 2021

@author: MITRB
"""

import pandas as pd
import numpy as np

df = pd.read_excel(r'C:\Work\My_Code\Files\final_data.xlsx')

load = df['Total Load (kW)'].values
solar0 = df['0.5MW'].values
solar1 = df['1MW'].values
hydro0 = df['Power_0_5 (MW)'].values
hydro1 = df['Power_1 (MW)'].values
price_lmp = df['LMP ($\MW)'].values
#check_tmp = df['check'].values
price_nma = 0.22 #$/kWh
price_ppa = 0.18 #$/kWh

original_cost = load*price_nma

'''
For revenue calculations we consider abs(load - generation)*price of sale
'''

net_pv_hy = (load/1000)-(solar0 + hydro0)
#lmp_pv_hydro = ((load/1000)-(solar0 + hydro0))*price_lmp

penalty =[]
cal=[]
mal=[]
for (idx,abc) in zip(price_lmp,net_pv_hy):
    if idx <0 and abc <0:
        penalty.append(idx*abc)
    elif idx<0 and abc>0:
        cal.append(idx*abc)
    else:
        mal.append(idx*abc)

lmp_pv_hydro = abs(sum(mal) + sum(cal)) #- sum(penalty)

nma_pv_hydro = (load-(solar0+hydro0)*1000)*price_nma
ppa_pv_hydro = (solar0+hydro0)*1000*price_ppa

# lmp_pv = ((load/1000)-(solar1))*price_lmp
net_pv = (load/1000)-(solar1)
penalty =[]
cal=[]
mal=[]
for (idx,abc) in zip(price_lmp,net_pv):
    if idx <0 and abc <0:
        penalty.append(idx*abc)
    elif idx<0 and abc>0:
        cal.append(idx*abc)
    else:
        mal.append(idx*abc)

lmp_pv = abs(sum(mal) + sum(cal)) #- sum(penalty)


nma_pv = (load-(solar1*1000))*price_nma

ppa_pv = (solar1*1000)*price_ppa

# lmp_hy = ((load/1000)-(hydro1))*price_lmp
net_hy = (load/1000)-(hydro1)

penalty =[]
cal=[]
mal=[]
for (idx,abc) in zip(price_lmp,net_hy):
    if idx <0 and abc <0:
        penalty.append(idx*abc)
    elif idx<0 and abc>0:
        cal.append(idx*abc)
    else:
        mal.append(idx*abc)

lmp_hy = abs(sum(mal) + sum(cal)) #- sum(penalty)

nma_hy = (load-(hydro1)*1000)*price_nma

ppa_hy = (hydro1)*1000*price_ppa
'''
df = pd.DataFrame({"No DER":sum(original_cost),"Revenue_LMP_Hy":lmp_hy,"Revenue_NMA_Hy":sum(nma_hy),
                    "Revenue_PPA_Hy":sum(ppa_hy),"Revenue_NMA_PV":sum(nma_pv),"Revenue_LMP_PV":lmp_pv,
                    "Revenue_PPA_PV":sum(ppa_pv),"Revenue_NMA_PV_Hy":sum(nma_pv_hydro),
                    "Revenue_LMP_PV_Hy":lmp_pv_hydro,"Revenue_PPA_PV_Hy":sum(ppa_pv_hydro)}, 
                  index=[0])

df.to_csv(r"C:\Work\My_Code\Files\Revenue_Comparison.csv",index=False)
'''

capex_hydro_0_5 = 3329597.45
opex_hydro_0_5 =  83239.93

capex_hydro_1 = 6357186.47
opex_hydro_1 = 158929.66

capex_pv_0_5 = 860000
opex_pv_0_5 = 9500

capex_pv_1 = 1720000
opex_pv_1 =19000

capex_sys = np.array([capex_pv_1,capex_hydro_1,capex_pv_0_5+capex_hydro_0_5])
opex_sys = np.array([opex_pv_1,opex_hydro_1,opex_pv_0_5+opex_hydro_0_5])
rev_sys_nma = np.array([abs(sum(nma_pv)),abs(sum(nma_hy)),abs(sum(nma_pv_hydro))])
rev_sys_ppa = np.array([sum(ppa_pv),sum(ppa_hy),sum(ppa_pv_hydro)])
rev_sys_lmp = np.array([lmp_pv,lmp_hy,lmp_pv_hydro])


'''
Payback period, formula from "https://unboundsolar.com/solar-information/return-on-solar-investment#roi-calculator"
'''
'''
df_payback = pd.DataFrame()
df_payback['grant [%]'] = np.arange(0,1,0.1)
list_names = ['payback_years_pv','payback_years_hydro','payback_years_pv_hydro']

for i in range(len(capex_sys)):
    name = list_names[i]
    for idx,row in df_payback.iterrows():
        # print(idx)
        # print(row)
        df_payback.loc[idx,name]= ((capex_sys[i]-(capex_sys[i]*row['grant [%]'] - rev_sys_ppa[i]))/price_nma)/sum(load)
        # df_payback.loc[idx,name]= ((capex_sys[i]-(capex_sys[i]*row['grant [%]']))/price_nma)/sum(load)

'''

# Payback period
def payback_period(capex, opex, yearly_revenue, grant=0.1):
    '''
    grant is percentage of capex
    '''
    count = 0
    # This is the initial cost at year 0
    cost = capex*(1-grant)
    
    while cost>0:
        cost = cost + opex - yearly_revenue
        count = count + 1
        
        # if count > 50:
        #     break
    return count


df_payback = pd.DataFrame()
df_payback['grant [%]'] = np.arange(0,100,10)

list_names = ['payback_years_pv','payback_years_hydro','payback_years_pv_hydro']

for index in range(len(capex_sys)):
    #print(index)
    capex = capex_sys[index]
    opex = opex_sys[index]
    yearly_revenue = rev_sys_ppa[index]
    name = list_names[index]
    
    for idx,row in df_payback.iterrows():
        #print(row['grant'])
        df_payback.loc[idx,name] = payback_period(capex, opex, yearly_revenue, grant=row['grant [%]']/100)
        

for i in range(len(rev_sys_lmp)):
    
    new_rev = [capex_sys[i]/7] + opex_sys[i]
    
    # print(new_rev)
    
    change_nma = ((new_rev - rev_sys_nma[i])/rev_sys_nma[i])*100
    
    print("Change Revene NMA",change_nma)
    
    change_ppa = ((new_rev - rev_sys_ppa[i])/rev_sys_ppa[i])*100
    
    print("Change Revene PPA",change_ppa)
    
    new_capex_nma = 7*(rev_sys_nma[i]-opex_sys[i])
    
        
    change_capex_nma = ((new_capex_nma - capex_sys[i])/capex_sys[i])*100
    
    print("Change Capex NMA",change_capex_nma)
    
    new_capex_ppa = 7*(rev_sys_ppa[i]-opex_sys[i])
    
    change_capex_ppa = ((new_capex_ppa - capex_sys[i])/capex_sys[i])*100
    
    print("Change Capex PPA",change_capex_ppa)
    
    
for j in range(len(capex_sys)):
    cost = capex_sys[j]
    opex = opex_sys[j]
    revenue = rev_sys_nma[j]
    revenue_ppa = rev_sys_ppa[j]
    cost_ppa = capex_sys[j]
    for i in range(0,5):
    
        cost = cost + opex - rev_sys_nma
        cost_ppa = cost_ppa + opex - rev_sys_ppa
    #print(cost)
    
    roi_5y = (capex_sys[j]+opex_sys[j]-cost[j])/(capex_sys[j]+opex_sys[j])
    
    print(roi_5y)
    
    roi_5y_ppa = (capex_sys[j]+opex_sys[j]-cost_ppa[j])/(capex_sys[j]+opex_sys[j])
    
    print(roi_5y_ppa)