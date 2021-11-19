# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 09:27:33 2021

@author: MITRB
"""

import pandas as pd
import numpy as np

df = pd.read_excel(r'C:\Work\My_Code\Files\1year_data_load_energy_task.xlsx')

load = df['Total Load (kW)'].values

solar0 = df['0.5MW'].values
solar1 = df['1MW'].values
hydro0 = df['power_0_5_mw'].values
hydro1 = df['power_1_mw'].values
price_lmp = df['LMP ($\MW)'].values
price_nma = 0.22 #cents/kW

original_cost = load*price_nma

print('Original cost no DER: $%f'%sum(original_cost))


'''
For revenue calculations we consider abs(load - generation)*price of sale
'''

'''Combined solar and hydro'''
lmp_pv_hydro = ((load/1000)-(solar0 + hydro0))*price_lmp

#print('Revenue from PV+Hydro under LMP: $ %f'%sum(revenue_lmp))

#revenue_lmp_pvhy = abs(sum(original_cost) - sum(lmp_pv_hydro))
    
nma_pv_hydro = abs(load-(solar0+hydro0)*1000)*price_nma

revenue_nma_pvhy = abs(sum(original_cost) - sum(nma_pv_hydro))

#print('Revenue from PV+Hydro under NMA: $ %f'%sum(revenue_nma))

ppa_pv_hydro = (solar0+hydro0)*1000*price_nma

revenue_ppa_pvhy = abs(sum(original_cost) - sum(ppa_pv_hydro))

#print('Revenue from PV+Hydro under PPA: $ %f'%sum(revenue_ppa))

# df = pd.DataFrame({"Revenue_LMP_PV_HY":revenue_lmp,"Revenue_NMA_PV_HY":revenue_nma,
#                     "Revenue_PPA_PV_HY":revenue_ppa})

# df.to_csv(r"C:\Work\My_Code\Files\Revenue_PV_Hy.csv",index=False)

'''Solar Only'''

lmp_pv = abs((load/1000)-(solar1))*price_lmp

revenue_lmp_pv = abs(sum(original_cost) - sum(lmp_pv))

#print('Revenue from PV under LMP: $ %f'%sum(revenue_lmp))

nma_pv = abs(load-(solar1*1000))*price_nma

revenue_nma_pv = abs(sum(original_cost) - sum(nma_pv))

#print('Revenue from PV under NMA: $ %f'%sum(revenue_nma))

ppa_pv = (solar1*1000)*price_nma

revenue_ppa_pv = abs(sum(original_cost) - sum(ppa_pv))

# df = pd.DataFrame({"Revenue_LMP_PV":revenue_lmp,"Revenue_NMA_PV":revenue_nma,
#                     "Revenue_PPA_PV":revenue_ppa})

# df.to_csv(r"C:\Work\My_Code\Files\Revenue_PV.csv",index=False)

#print('Revenue from PV under PPA: $ %f'%sum(revenue_ppa))



'''Hydro Only'''

lmp_hy = ((load/1000)-(hydro1))*price_lmp

revenue_lmp_hy = (sum(original_cost) - sum(lmp_hy))
#print('Revenue from hydro under LMP: $ %f'%sum())

nma_hy = (load-(hydro1)*1000)*price_nma

revenue_nma_hy = (sum(original_cost) - sum(nma_hy))

#print('Revenue from hydro under NMA: $ %f'%sum(revenue_nma))

ppa_hy = (hydro1)*1000*price_nma

revenue_ppa_hy = (sum(original_cost) - sum(ppa_hy))

#print('Revenue from Hydro under PPA: $ %f'%sum(revenue_ppa))

df = pd.DataFrame({"No DER":sum(original_cost),"Revenue_LMP_Hy":revenue_lmp_hy,"Revenue_NMA_Hy":revenue_nma_hy,
                    "Revenue_PPA_Hy":revenue_ppa_hy,"Revenue_NMA_PV":revenue_nma_pv,"Revenue_LMP_PV":revenue_lmp_pv,
                    "Revenue_PPA_PV":revenue_ppa_pv,"Revenue_NMA_PV_Hy":revenue_nma_pvhy,"Revenue_LMP_PV_Hy":revenue_lmp_pvhy,
                    "Revenue_PPA_PV_Hy":revenue_ppa_pvhy}, index=[0])

df.to_csv(r"C:\Work\My_Code\Files\Revenue_Comparison.csv",index=False)



# P =[0.5,1]
# H = 40

# for i in range(len(P)):
#     cap_hydro = 9297820*P[i]**(0.81)* H**(-0.102)
#     print(cap_hydro)
#     opex_hydro = 0.025*cap_hydro
#     print(opex_hydro)
    
#     cap_solar = 1.72*P[i]*10**6
#     print(cap_solar)
#     opex_solar = 19*P[i]*10**3
#     print(opex_solar)




# capex_hydro_0_5 = 3329597.45
# opex_hydro_0_5 =  83239.93

# capex_hydro_1 = 6357186.47
# opex_hydro_1 = 158929.66

# capex_pv_0_5 = 860000
# opex_pv_0_5 = 9500

# capex_pv_1 = 1720000
# opex_pv_1 =19000


# rev_pv_hydro = 141923.782713
# rev_pv = 72077.700885
# rev_hydro = 248298.103775

# capex_sys = np.array([capex_pv_1,capex_hydro_1,capex_pv_0_5+capex_hydro_0_5])
# opex_sys = np.array([opex_pv_1,opex_hydro_1,opex_pv_0_5+opex_hydro_0_5])
# rev_sys = np.array([rev_pv,rev_hydro,rev_pv_hydro])



# # Payback period
# def payback_period(capex, opex, yearly_revenue, grant=0.1):
#     '''
#     grant is percentage of capex
#     '''
#     count = 0
#     # This is the initial cost at year 0
#     cost = capex*(1-grant)
    
#     while cost>0:
#         cost = cost + opex - yearly_revenue
#         count = count + 1
        
#         #if count > 50:
#           #   break
#     return count

# '''
# cost = capex
# for i in range(0,5):
    
#     cost = cost + opex - yearly_revenue

# roi_5y = (capex+opex-cost)/(capex+opex)
# '''
# df_payback = pd.DataFrame()
# df_payback['grant [%]'] = np.arange(0,100,10)



# list_names = ['payback_years_pv','payback_years_hydro','payback_years_pv_hydro']

# for index in range(len(capex_sys)):
#     #print(index)
#     capex = capex_sys[index]
#     opex = opex_sys[index]
#     yearly_revenue = rev_sys[index]
#     name = list_names[index]
    
#     for idx,row in df_payback.iterrows():
#         #print(row['grant'])
#         df_payback.loc[idx,name] = payback_period(capex, opex, yearly_revenue, grant=row['grant [%]']/100)