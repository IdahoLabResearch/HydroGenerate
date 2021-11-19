# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 15:06:41 2021

@author: MITRB
"""

'''
Tidal Generation
'''

import pandas as pd
import numpy as np
import math

'''
angular_velo = Angular Velocity in rad/sec
radius =  turbine rotor radius in meter (dia = 2 * radius)
tidal_velo = upstream water velocity at the entrance of the turbine m/sec
p_turb = desnity of seawater in kg/m^3 (assumed constant at 1025 kg/m^3)
TSR = Tip Speed Ratio
v_cut_in = Rotor cut-in velocity (m/sec) (How to get or estimate v_cut_in and v_cut_out ?)
v_cut_out = Rotor cut-out velocity (m/sec)
P_max = Maximum power rating of the turbine
Turbines are operated in mainly four regions
Region 1 if (tidal_vel < v_cut_in), power = 0
Region 4 if (tidal_vel > v_cut_out), power = 0
Region 2 and 3 when v_cut_in < tidal_velo < v_cut_out, power generated using eqn (2)
if power > p_max, power = p_max, p_max must be defined
'''
v_cut_in = 2 '''Units in m/sec '''
v_cut_out = 4 '''Units in m/sec'''
p_turb = 1025 '''Units in kg/m^3'''
p_max = 2 '''Units in MW'''
radius = 10 '''Units in m'''

tidal_velo = pd.read_csc(r'')


tur_coeff_performance = 0.5*(1-(angular_velo*radius/tidal_velo))**2*(1+(angular_velo*radius/tidal_velo))
'''
Usually tur_coeff_performance (max) < 0.5
'''

if (tidal_velo < v_cut_in) or (tidal_velo > v_cut_out): '''No power generated if operation in Region 1 and 4'''
    
    power = 0
    
else: '''Region 2 and 3 operation'''
    
    power = (0.5*p_turb*((math.pi*2*radius**2)/4)*tur_coeff_performance*tidal_velo**3)/10**6 ''' Eqn (2), power calculated in MW '''


TSR = (angular_velo*radius)/tidal_velo '''Dimensionless'''
