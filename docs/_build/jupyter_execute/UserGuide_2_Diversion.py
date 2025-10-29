#!/usr/bin/env python
# coding: utf-8

# # Diversion Mode
# 
# 
# Using **_hydropower_type = Diversion_** allows computing hydropower potential for a _diversion_ or _run-of-river_ project. 
# 
# A _diversion_, sometimes called a _run-of-river_ facility, channels a portion of a river through a canal and/or a penstock to utilize the natural decline of the river bed elevation to produce energy. A penstock is a closed conduit that channels the flow of water to turbines with water flow regulated by gates, valves, and turbines. A diversion may not require the use of a dam. Check [DOE - Types of Hydropower Plant](https://www.energy.gov/eere/water/types-hydropower-plants#:~:text=There%20are%20three%20types%20of,renewable%20energy%20to%20the%20grid.) for additional information. 
# 
# In diversion projects, HydroGenerate focuses on calculating hydropower under different configurations.
# 
# 
# 
# In this calculation, the flow given is assumed to be the flow aaliable for hydropower generation, i.e., no reservoir storage operation. 
# 

# In[1]:


from HydroGenerate.hydropower_potential import calculate_hp_potential
import numpy as np


# #### Head, power, and length of penstock are known. Flow is a single value.
# 
# In this scenario _HydroGenerate_ will select a turbine, compute efficiency for the given flow and values within 0.6 to 1.2 the given flow, penstock diameter (assuming steel if no material is given), head loss for all flows, rater power, power a given range of flow. 

# In[2]:


flow = 5000 # cfs
head = 330 # ft
power = None
penstock_length = 400 # ft
hp_type = 'Diversion'

hp = calculate_hp_potential(flow= flow, rated_power= power, head= head,
                            penstock_headloss_calculation= True,
                            # penstock_headloss_method= 'Hazen-Williams',
                            units= 'US',
                            hydropower_type= hp_type, penstock_length= penstock_length,
                            # penstock_diameter= 15,
                            max_headloss_allowed= 10)

# Explore output
print('Design flow (cfs):', hp.design_flow)
print('Turbine type:', hp.turbine_type)
print('Rated Power (MW):', round(hp.rated_power/1000, 2))
print('Net head (ft):', round(hp.net_head, 2))
print('Generator Efficiency:',hp.generator_efficiency)
print('Head Loss method:',hp.penstock_headloss_method)
print('Penstock length (ft):', hp.penstock_length)
print('Penstock diameter (ft):', round(hp.penstock_diameter,2))
print('Runner diameter (ft):', round(hp.runner_diameter,2))

print('\nFlow range evaluated (cfs):', np.round(hp.flow, 1))
print('Turbine Efficiency for the given flow range:', np.round(hp.turbine_efficiency, 3))
print('Power (Kw) for the given flow range:', np.round(hp.power,1))


# #### Exploring additional options:
# 
# _HydroGenerate_ includes two functions for head loss calculation: 1) _Darcy-Weisbach_ (default) 2) _Hazen-Williams_.

# In[3]:


# Using Hazen-Williams for head loss calculation.

flow = 8000 # cfs
head = 20 # ft
power = None
penstock_length = 50 # ft
hp_type = 'Diversion'
headloss_method= "Hazen-Williams"

hp = calculate_hp_potential(flow= flow, rated_power= power, head= head,
                            penstock_headloss_calculation= True,
                           hydropower_type= hp_type, penstock_length= penstock_length,
                           penstock_headloss_method= headloss_method)



# Explore output
print('Design flow (cfs):', hp.design_flow)
print('Head_loss at design flow (ft):', round(hp.penstock_design_headloss, 2))
print('Turbine type:', hp.turbine_type)
print('Rated Power (Kw):', round(hp.rated_power, 2))
print('Net head (ft):', round(hp.net_head, 2))
print('Generator Efficiency:',hp.generator_efficiency)
print('Head Loss method:',hp.penstock_headloss_method)
print('Penstock length (ft):', hp.penstock_length)
print('Penstock diameter (ft):', round(hp.penstock_diameter, 2))
print('Runner diameter (ft):', round(hp.runner_diameter, 2))

print('\nFlow range evaluated (cfs):', np.round(hp.flow, 1))
print('Turbine Efficiency for the given flow range:', np.round(hp.turbine_efficiency ,3))
print('Power (kW) for the given flow range:', np.round(hp.power, 1))


# In[4]:


# Exploring additional options:
# Using Hazen-Williams for head loss calculation and a concrete penstock
#  Selecting a diffrent material for the penstock

flow = 8000 # cfs
head = 20 # ft
power = None
penstock_length = 50 # ft
hp_type = 'Diversion'
headloss_method= "Hazen-Williams"
penstock_material = 'Concrete'

hp = calculate_hp_potential(flow= flow, rated_power= power, head= head,
                           hydropower_type= hp_type, penstock_length= penstock_length,
                           penstock_headloss_calculation= True,
                           penstock_headloss_method= headloss_method, penstock_material= penstock_material)

# Explore output
print('Design flow (cfs):', hp.design_flow)
print('Head_loss at design flow (ft):', round(hp.penstock_design_headloss, 2))
print('Turbine type:', hp.turbine_type)
print('Rated Power (Kw):', round(hp.rated_power, 2))
print('Net head (ft):', round(hp.net_head, 2))
print('Generator Efficiency:',hp.generator_efficiency)
print('Head Loss method:',hp.penstock_headloss_method)
print('Penstock length (ft):', hp.penstock_length)
print('Penstock diameter (ft):', round(hp.penstock_diameter, 2))
print('Runner diameter (ft):', round(hp.runner_diameter, 2))

print('\nFlow range evaluated (cfs):', np.round(hp.flow, 1))
print('Turbine Efficiency for the given flow range:', np.round(hp.turbine_efficiency ,3))
print('Power (kW) for the given flow range:', np.round(hp.power, 1))


# In[5]:


# Exploring additional options:
#  Using Hazen-Williams for head loss calculation and using a diffrent C value
# Note: editing hydraulic_processing.py allows adding materials that can be called by name.

flow = 8000 # cfs
head = 20 # ft
power = None
penstock_length = 50 # ft
hp_type = 'Diversion'
headloss_method= "Hazen-Williams"
C = 100 # Hazen_williamns C

hp = calculate_hp_potential(flow= flow, rated_power= power, head= head,
                           penstock_headloss_calculation= True,
                           hydropower_type= hp_type, penstock_length= penstock_length,
                           penstock_headloss_method= headloss_method, penstock_frictionfactor= C)

# Explore output
print('Design flow (cfs):', hp.design_flow)
print('Head_loss at design flow (ft):', round(hp.penstock_design_headloss, 2))
print('Turbine type:', hp.turbine_type)
print('Rated Power (Kw):', round(hp.rated_power, 2))
print('Net head (ft):', round(hp.net_head, 2))
print('Generator Efficiency:',hp.generator_efficiency)
print('Head Loss method:',hp.penstock_headloss_method)
print('Penstock length (ft):', hp.penstock_length)
print('Penstock diameter (ft):', round(hp.penstock_diameter, 2))
print('Runner diameter (ft):', round(hp.runner_diameter, 2))

print('\nFlow range evaluated (cfs):', np.round(hp.flow, 1))
print('Turbine Efficiency for the given flow range:', np.round(hp.turbine_efficiency ,3))
print('Power (kW) for the given flow range:', np.round(hp.power, 1))

