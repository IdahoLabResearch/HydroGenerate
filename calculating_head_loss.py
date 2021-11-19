# -*- coding: utf-8 -*-
"""
Created on Tue May 18 06:47:35 2021

@author: MITRB
"""

'''
D=dia/1000 #Diameter in meters

'''
import pandas as pd
import numpy as np
import math
max_flow_val = 569
temp = pd.read_excel(r'C:\Work\WPTO\temp.xlsx')
mat = pd.read_excel(r'C:\Work\WPTO\material.xlsx')
flow_info = pd.read_csv(r'C:\Work\My_Code\11292900_2019-01-01.csv')
maxflow = 0.028316846591999675*max_flow_val
flow_range = flow_info['Average (cfs)']* (0.028316846591999675)
flow_range = flow_range.values
flow_range = np.where(flow_range>maxflow,maxflow,flow_range)
dia = 12 #Input in ft
temp_input = 50 #Temperature in F
material = 'Concrete'
D = dia*0.3048 #Diameter from ft to m
L = 18250 #ft
length = L * 0.3048 #Converting from ft to m
g = 9.81 #m/sec^2
rho = 1000 #kg/m^3

# Dynamic Viscosity as a function of temperature
df2= temp[temp.Farenheit == temp_input]
dyn_visc = df2['Mu'].tolist()[0]
nu = df2['Nu'].tolist()[0]

#Roughness Coefficient based on piping type

df3=mat[mat.Material == material]
rough= df3['RoughnessCoefficient'].tolist()[0]

#Relative Roughness
rela_rough = rough/dia

#flow_arr=np.linspace(0.05,1,20)

#flow_range= maxflow * flow_arr
#flow_range = flow_info['Actual (cfs)'] * 0.028316846591999675
#flow_range = flow_range.values
#Reynolds Coefficient

#Re=(4 * flow * D)/(dyn_visc * math.pi * D**2)

Re= (4*flow_range)/(math.pi*D*nu)

#Friction factor

f= 0.11 * ((rela_rough) + (68 / Re)) ** (1/4)



velo=(4*flow_range)/(math.pi * D**2)


h_f = f*(length*velo**2)/(D*2*g)

np.savetxt('h_f_2nd_sec.csv',h_f,delimiter=',')

#print(h_f)