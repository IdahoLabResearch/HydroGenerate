#!/usr/bin/env python
# coding: utf-8

# # Hydrokinetics
# 
# **_HydroGenerate_** can compute hydrokinetic potential based on the aerage cross-sectional velocity of a river or canal. Hydrokinetic calculations are currently under development. 
# 

# In[1]:


from HydroGenerate.hydropower_potential import calculate_hp_potential


# In[2]:


# 1 Average velocity is known. hk_blade_type= 'ConventionalRotor' - Default turbine size.

V = 2  # average cross-section velocity m/s

hp = calculate_hp_potential(channel_average_velocity = V,
                           hydropower_type = 'Hydrokinetic', units = 'SI',
                           hk_blade_type= 'ConventionalRotor',
                           hk_blade_diameter= 1,
                           hk_blade_heigth = 2)

print('Rated Power (kW):', round(hp.rated_power, 2))


# In[3]:


# 2 Average velocity is known. US units. hk_blade_type= 'H-DarrieusRotor'

V = 6.6 # average cross-section velovicty ft/s

hp = calculate_hp_potential(channel_average_velocity = V,
                           hydropower_type = 'Hydrokinetic', units = 'US',
                           hk_blade_type= 'H-DarrieusRotor',
                           hk_blade_diameter= 1.5,
                           hk_blade_heigth = 2)

print('Rated Power (kW):', round(hp.rated_power, 2))

