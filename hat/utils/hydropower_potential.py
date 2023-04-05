'''
Copyright 2021, Battelle Energy Alliance, LLC
'''

"""
03-2023
@author: MITRB, J. Gallego-Calderon, Camilo J. Bastidas Pacheco

This module calculates hydropower potential under diffrent alternatives
"""

import numpy as np
import math
from numpy.core.fromnumeric import mean
from numpy.lib.function_base import median
import pandas as pd
from datetime import datetime
import os
from abc import ABC, abstractmethod
from hydraulic_processing import *
from turbine_calculation import *
from numbers import Number
   
# TODO: add documentation along the class: reference equations, describe the inputs, outputs, constants.
# TODO: validate that the method implemented is correct. Juan to cross-check the equations

# Constant definition / unit conversion
rho = 1000 # water density in Kg/m^3
g = 9.81 # acceleration of gravity (m/s^2)
cfs_to_cms = 0.0283168 # cubic feet per second to cubic meter per second
ft_to_m = 0.3048 # feet to meters
nu = 0.0000011223 # Kinematic viscosity of water (m2/s) at 60F (~15.6C) - prevalent stream water temperature 

# Function to combine two instances
def merge_instances(ob1, ob2):
    ob1.__dict__.update(ob2.__dict__)
    return ob1

# function to calculated head 
def calculate_head(rated_flow, rated_power):
    '''
    Returns the head in meters based on known rated flow (m3/s) and rated power (W)
    '''
    return rated_power/(rho*g*rated_flow) 

# function to calculate design flow
def calculate_design_flow(flow, pctime_runfull = None):
    '''
    Function to calculate the design flow for a turbine given a percent of exceedance and 
    flow values 
    
    Inputs:
    - flow: a set of flow values meassured at the site of interest
    - pctime_runfull: percent of time the turbine is running full [1:100]
    '''

    if isinstance(flow, Number):
        design_flow = flow # when a single value of flow is provided this is the design flow
        pe = pctime_runfull

    else:
        pc_e = np.linspace(100, 1, 100) # 100:1
        flow_percentiles = np.percentile(flow, q = np.linspace(1, 100, 100)) # percentiles to compute, 1:100
        flowduration_curve = {'Flow': flow_percentiles, 'Percent_Exceedance':pc_e} # Flow duration curve
    
        if pctime_runfull is not None: # for user defined parameters
            pe = np.round(pctime_runfull)
        else: 
            pe = 20 # default value for the percent of time a turine will run full 

        design_flow = float(flowduration_curve['Flow'][flowduration_curve['Percent_Exceedance'] == pe])

    return design_flow, pe

# Unit transformation
class Units:

    def si_to_us_conversion(flow, head, design_flow, head_loss, penstock_length, penstock_diameter):

        if flow is not None:
            flow = flow * cfs_to_cms # cfs to m3/s
        
        if head is not None:
            head = head * ft_to_m # ft to m 

        if design_flow is not None:
            design_flow = design_flow * cfs_to_cms # cfs to m3/s
    
        if head_loss is not None:
            head_loss = head_loss * ft_to_m # ft to m 

        if penstock_length is not None:
            penstock_length = penstock_length * ft_to_m # ft to m 

        if penstock_diameter is not None:
            penstock_diameter = penstock_diameter * ft_to_m # ft to m 
        
        return flow, head, design_flow, head_loss, penstock_length, penstock_diameter

    def us_to_si_conversion(flow, head, design_flow, head_loss, penstock_length, penstock_diameter):
        
        if flow is not None:
            flow = flow / cfs_to_cms # m3/s tp cfs
        
        if head is not None:
            head = head / ft_to_m # m to ft 

        if design_flow is not None:
            design_flow = design_flow / cfs_to_cms #  # m3/s tp cfs
    
        if head_loss is not None:
            head_loss = head_loss / ft_to_m # m to ft 

        if penstock_length is not None:
            penstock_length = penstock_length / ft_to_m # m to ft 

        if penstock_diameter is not None:
            penstock_diameter = penstock_diameter / ft_to_m # m to ft 
        
        return flow, head, design_flow, head_loss, penstock_length, penstock_diameter

# Hydropower calculation
class Hydropower(ABC):
    
    @abstractmethod
    def hydropower_calculation(self, turbine, hydraulic_parameters):
        pass

# General calculation
class Simple(Hydropower):
            
    def hydropower_calculation(flow, head, rated_power, 
                               head_loss, overall_system_efficiency):
        
        if len([i for i in [flow, head, rated_power] if i is None]) > 1:
            raise ValueError('Missing inputs. Users must provide flow and head to compute power, flow and power' \
                             ' to compute head, or power and head to compute flow')

        # Overal system efficiency
        if overall_system_efficiency is not None:
            n = overall_system_efficiency
        else: 
            n = 0.85

        # Compute head
        if head is not None: 
            if head_loss is not None:
                h = head - head_loss
            else:
                h = head
        else:
            P = rated_power
            h = P * 1000 / (n * g * rho * flow) # Net head, in m

        # Compute Flow 
        if flow is None:
           P = rated_power
           flow = P  * 1000 / (n * g * rho * h)

        # Compute hydropower
        if rated_power is None:
            P = n * g * rho * flow * h / 1000 # HP potential in kilowatts
        
        return flow, h, P

# Diversion - Run-of-river
class Diversion(Hydropower):

    # def hydropower_calculation(self, turbine, hydraulic_parameters):
    def hydropower_calculation(self, hp_params):

        # If a head is not given - update later
        # if hydraulic_parameters.head is None:
        #     hydraulic_parameters.head = calculate_head(hydraulic_parameters.design_flow,
        #                                                turbine_parameters.rated_power)

        head = hp_params.head
        
        # Select turbine type
        if hp_params.turbine_type is None:
            hp_params.turbine_type = turbine_type_selector(head) # Turbine type

        # Calculate design flow
        if hp_params.design_flow is None:
            hp_params.design_flow, hp_params.pctime_runfull = calculate_design_flow(hp_params.flow)

        # Head loss calculation
        if hp_params.headloss_method == 'Darcy-Weisbach': # DW
            print('DW_here')
            hl = DarcyWeisbach()
            hl.headloss_calculator(hp_params)


            # for time series of flow
            if not isinstance(hp_params.flow, float):
                hp_params.head_loss = hl.headloss_calculator_ts(hp_params)

        # Turbine calculation
        if hp_params.turbine_type == 'Kaplan':
                turb = KaplanTurbine()
                turb.turbine_calculator(hp_params)
        
        # Generator efficiency
        if hp_params.generator_efficiency is None:
            hp_params.generator_efficiency = 0.98 
        else:
             hp_params.generator_efficiency =  hp_params.generator_efficiency / 100 # percent to proportion
        
        generator_effieincy = hp_params.generator_efficiency
        turbine_efficiency = hp_params.effi_cal
        n = turbine_efficiency * generator_effieincy
        n_max = np.max(turbine_efficiency) * generator_effieincy
        h = hp_params.head

        hp_params.rated_power = n_max * g * rho *  hp_params.design_flow * h / 1000 # HP potential in kilowatts
        hp_params.power = n * g * rho *  hp_params.flow * h / 1000 # HP potential in kilowatts


 
# Function to calculate hydropower potential  
def calculate_hp_potential(flow, head= None, rated_power= None, 
                           hydropower_type= 'Simple', units= 'US',
                           headloss_method= 'Darcy-Weisbach',
                           design_flow= None, # flow_data_type= 'Timeseries', flow_column='discharge(cfs)', 
                           overall_system_efficiency = None,
                           turbine_type= None, generator_efficiency= None,  
                           head_loss= None, 
                           penstock_length= None, penstock_diameter= None, penstock_material= None,
                           pctime_runfull = None, max_headloss_allowed= None,
                           turbine_Rm = None,
                           pelton_n_jets = None):
        
        # units conversion
        if units == 'US':
            flow, head, design_flow, head_loss, penstock_length, penstock_diameter = \
                Units.si_to_us_conversion(flow, head, design_flow, head_loss, penstock_length, penstock_diameter)

        # General hydropower calculation
        if hydropower_type == 'Simple':
            flow, head, rated_power = Simple.hydropower_calculation(flow, head, rated_power, head_loss, overall_system_efficiency)
    
            flow, head, design_flow, head_loss, penstock_length, penstock_diameter = \
                Units.us_to_si_conversion(flow, head, design_flow, head_loss, penstock_length, penstock_diameter)
            return flow, head, rated_power

        else:
            hyd_pm = HydraulicDesignParameters(flow= flow, design_flow= design_flow, head= head, 
                                               penstock_length= penstock_length, penstock_diameter= penstock_diameter, 
                                               penstock_material= penstock_material, head_loss= head_loss, 
                                               max_headloss_allowed= max_headloss_allowed,
                                               headloss_method = headloss_method)       # Initialize

            turb_pm = TurbineParameters(turbine_type= turbine_type, flow= flow, design_flow= design_flow, head= head,
                                        head_loss= head_loss, generator_efficiency= generator_efficiency,
                                        Rm= turbine_Rm, pctime_runfull= pctime_runfull, pelton_n_jets = pelton_n_jets)        # Initialize
            
            all_params = merge_instances(hyd_pm, turb_pm) # merge 
        
        # Diversion projects
        if hydropower_type == 'Diversion':
            Diversion().hydropower_calculation(hp_params = all_params)

        # Hydropower.hydropower_calculation(all_params)
        
        return all_params

if __name__ == "__main__":

    # df = pd.read_csv(os.path.join('.','data','turbine.csv'))
    # flow_info = pd.read_csv(os.path.join('.','data_test.csv'))
    
    flow = 500
    flow_info = pd.read_csv('data_test.csv')['discharge_cfs']
    head = 5
    rated_power = None

    # hp_calculator = HydroPowerPotential()
    test = calculate_hp_potential(flow= flow_info, rated_power= rated_power, head= head,
                           hydropower_type= 'Diversion', penstock_length = 50)
    
    print('\nHead_losses:',test.head_loss)
    print('\nTurbine type:',test.turbine_type)
    print('\nEfficiency:',test.effi_cal)
    print('\nRated Power:',test.rated_power)
    print('\nPower:',test.power)
    print('\nGenerator Efficiency:',test.generator_efficiency)
    
    
    
          

    
