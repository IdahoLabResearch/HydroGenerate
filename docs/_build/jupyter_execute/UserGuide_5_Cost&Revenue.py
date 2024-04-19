#!/usr/bin/env python
# coding: utf-8

# # Cost and Revenue calculations
# 
# **_HydroGenerate_** will compute a project cost, O&M, and revenue. Cost and O&M are computed using the [Hydropower Baseline Cost Modeling, Version 2 report](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjkt8SCybqFAxUOOTQIHXtSD4IQFnoECBoQAQ&url=https%3A%2F%2Finfo.ornl.gov%2Fsites%2Fpublications%2Ffiles%2FPub58666.pdf&usg=AOvVaw0OIz-ux1PT7J1dfVfKjMWU&opi=89978449), developed by Oak Ridge National Laboratory.
# 
# Revenue is computed using the weigthed average wholesale electricity price in 2023 (0.0582 $/kWh) obtained from the [EIA](https://www.eia.gov/electricity/wholesale/) by default, or a user entered price.

# #### Exploring economic calcualtion options

# In[1]:


from HydroGenerate.hydropower_potential import calculate_hp_potential
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# In[2]:


# 1) Cost and Annual O&M as part of a project. Resource_category =  'Non-PoweredDam'
flow = 2000 # cfs
head = 1000 # ft
power = None
hydropower_type = 'Diversion'
penstock_length = 1200
resource_category = 'NewStream-reach'
capacity_factor = 0.6

hp = calculate_hp_potential(flow= flow, rated_power= power, head= head,
                            penstock_headloss_calculation= True,
                            hydropower_type= hydropower_type, penstock_length = penstock_length,
                            resource_category= resource_category,
                            capacity_factor = capacity_factor,
                            annual_caclulation = True)

print('\nResource Category:', hp.resource_category)
print('Initial Capital Cost (M$):', np.round(hp.icc,2))
print('Annual Operation and Maintennance (M$):', np.round(hp.annual_om,2))
print('Annual Revenue (M$):', np.round(hp.annual_revenue,2))


# In[3]:


# 2) resource_category: 'Non-PoweredDam'

head = 1000 # ft
power = 20000 # kW

hp = calculate_hp_potential(rated_power= power, head= head,
                            hydropower_type= None, 
                            resource_category= 'Non-PoweredDam')

print('\nResource Category:', hp.resource_category)
print('Initial Capital Cost (M$):', np.round(hp.icc,2))
print('Annual Operation and Maintennance (M$):', np.round(hp.annual_om,2))


# In[4]:


# 3 Rewinding a generator. resource_caterogy= 'GeneratorRewind')
head = 104 # ft
power = 20500 # kWred dev

hp = calculate_hp_potential(rated_power= power, head= head,
                            hydropower_type= None, 
                            resource_category= 'GeneratorRewind')

print('\nResource Category:', hp.resource_category)
print('Initial Capital Cost (M$):', np.round(hp.icc,1))
print('Annual Operation and Maintennance (M$):', np.round(hp.annual_om,1))


# In[5]:


# 4 Adding a new unit. resource_caterogy= 'UnitAddition')
head = 104 # ft
power = 20500 # kW

hp = calculate_hp_potential(rated_power= power, head= head,
                           hydropower_type= None, resource_category= 'UnitAddition')

print('\nResource Category:', hp.resource_category)
print('Initial Capital Cost (M$):', np.round(hp.icc,1))
print('Annual Operation and Maintennance (M$):', np.round(hp.annual_om,1))


# #### Using flow as a pandas dataframe and energy calculation
# 

# In[6]:


flow = pd.read_csv('data_test.csv') # pandas data frame
flow['dateTime'] = pd.to_datetime(flow['dateTime']) # preprocessing convert to datetime
flow = flow.set_index('dateTime') # set datetime index # flolw is in cfs

head = 20 # ft
power = None
penstock_length = 50 # ft
hp_type = 'Diversion' 

hp = calculate_hp_potential(flow= flow, rated_power= power, head= head,
                            pctime_runfull = 30,
                            penstock_headloss_calculation= True,
                            design_flow= None,
                            electricity_sell_price = 0.05,
                            resource_category= 'CanalConduit',
                            hydropower_type= hp_type, penstock_length= penstock_length,
                            flow_column= 'discharge_cfs', annual_caclulation= True)

pd.set_option('display.max_columns', 10) # 
pd.set_option('display.width', 1000)

# Explore output
# print('Design flow (cfs):', hp.design_flow)
# print('Head_loss at design flow (ft):', round(hp.penstock_design_headloss, 2))
# print('Turbine type:', hp.turbine_type)
# print('Rated Power (Kw):', round(hp.rated_power, 2))
# print('Net head (ft):', round(hp.net_head, 2))
# print('Generator Efficiency:',hp.generator_efficiency)
# print('Head Loss method:',hp.penstock_headloss_method)
# print('Penstock length (ft):', hp.penstock_length)
# print('Penstock diameter (ft):', round(hp.penstock_diameter,2))
# print('Runner diameter (ft):', round(hp.runner_diameter,2))

print('\nResource Category:', hp.resource_category)
print('Initial Capital Cost (M$):', np.round(hp.icc,1))
print('Annual Operation and Maintennance (M$):', np.round(hp.annual_om,1))

print('\nPandas dataframe output: \n', hp.dataframe_output)
print('Annual output: \n', hp.annual_dataframe_output) # annual energy generated and revenue

