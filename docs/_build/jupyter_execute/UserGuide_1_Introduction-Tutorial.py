#!/usr/bin/env python
# coding: utf-8

# # Introduction - Tutorial
# 
# 
# This page contains introductory examples of HydroGenerate python usage. It is assumed that users are familiar with using Python. 
# 

# ## Basic hydropower computations
# 
# All the functionality of HydroGenerate is encapsulated in a sigle function, **_calculate_hp_potential_**. In *basic* mode HydroGenerate can estimate power, head, or flow, given the other two values. This sections includes examples using the *basic* functionality. 
# 
# Let’s use **_calculate_hp_potential_** to calculate the power, flow, and head in an example. 

# In[1]:


from HydroGenerate.hydropower_potential import calculate_hp_potential


# ## Calculate power from a given head and flow

# In[2]:


flow = 8000 # given flow, in cfs
head = 20 # head, in ft
power = None

hp = calculate_hp_potential(flow= flow, head= head, rated_power= power)

print("The hydropower potential is {} kW".format(round(hp.rated_power, 0)))


# For a full list of the inputs and output parameters, go to [Inputs / Outputs - General Workflow](UserGuide_7_HydroGenerateWorkflow.md)

# ## Calculate head from a given head and flow

# In[3]:


flow = 8000 # given flow, in cfs
power = 11515 # Power, in Kw

hp = calculate_hp_potential(flow= flow, rated_power= power)

print("The head required to produce {} kW with a flow of {} cfs is {} ft".format(hp.rated_power, hp.flow, round(hp.head,1)))


# #### Calculate flow from a given head and power

# In[4]:


head = 20 # head, in ft
power = 11515

hp = calculate_hp_potential(head= head, rated_power= power)
print("The flow required to produce {} kW with a head of {} ft is {} cfs".format(hp.rated_power, hp.head, round(hp.flow, 0)))

