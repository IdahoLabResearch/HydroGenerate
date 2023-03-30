'''
Copyright 2021, Battelle Energy Alliance, LLC
'''

# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 14:15:46 2020
@author: MITRB

This module calculates the power capacity potential and annual energy production based on a head loss and different turbine technologies

01.21.2021 J. Gallego-Calderon:
- Removed the GUI code since it is no longer needed 
- The code is modular by using a class that computs the power capacity of different technologies
- Additional functions support the calculation above by computing the head loss and the AEP
- An if __name__ == "__main__": section is added so the script can be tested on its own

03/2023:
- Code re-organization
- Replacing the design flow based on a value selected from the flow duration curve
- Adding head loss calculation
- Adding flexibility for SI units
- Adding diffrent hydropower facilities
"""

import numpy as np
import math
from numpy.core.fromnumeric import mean
from numpy.lib.function_base import median
import pandas as pd
from datetime import datetime
import os
from abc import ABC, abstractmethod
   
# TODO: add documentation along the class: reference equations, describe the inputs, outputs, constants.
# TODO: validate that the method implemented is correct. Juan to cross-check the equations

# Constant definition / unit conversion
rho = 1000 # water density in Kg/m^3
g = 9.81 # acceleration of gravity (m/s^2)
cfs_to_cms = 0.0283168 # cubic feet per second to cubic meter per second
ft_to_m = 0.3048 # feet to meters
nu = 0.0000011223 # Kinematic viscosity of water (m2/s) at 60F (~15.6C) - prevalent stream water temperature 


# Turbine Parameters
class TurbinePower:
    def __init__(self, name, flow_range, head, design_flow, h_f, k1, k2, generator_efficiency, Rm, pctime_runfull):
        '''
        This class initializes the calculation of hydropower potential for a specific turbine type
        Input variables:
        - name: Selects the particular turbine based on available head
        - flow_range: Range of flow values
        - head: Potential head of the stream,
        - maxflow: The maximum flow observed within the data provided
        - h_f: Head loss
        - k1 and k2: These are turbine constants
        - effi_sys: Water to wire efficiency, assumed to be 0.97 or 97%
        - Rm: Turbine constant
        - pctime_runfull: percent of time the turbine will be flowing full
        Returns: None
        '''

        # Inputs
        self.tur_name = name
        self.flow_range = flow_range
        self.head = head
        self.design_flow = design_flow
        self.h_f = h_f
        self.k1 = k1
        self.k2 = k2
        self.generator_efficiency = generator_efficiency
        self.Rm = Rm
        self.pctime_runfull = pctime_runfull

        # Calculated 
        self.h = abs(self.head - np.nanmax(self.h_f)) # rated head on turbine [m]
        
        # Outputs
        self.pmax = 0       # maximum power
        self.pmin = 0       # minimun power
        self.power = []     # array that contains the power 
        self.effi_cal = []  # contains the range of efficiencies for the flow range
        self.turb_cap = 0
        self.raw_power = []

    def calculate_turbine_efficiency(self):
        '''
        This function selects the turbine efficiency function for each specific turbine type 
        (user-selected or calculated for the elevation head provided).
        '''
        if (self.tur_name=='Francis'):
            self.francis_turbine()
        elif (self.tur_name=='Kaplan' or  self.tur_name =='Propellor'):
            self.kaplan()
        elif(self.tur_name=='Pelton' or self.tur_name=='Turgo'):
            self.pelton()
        elif(self.tur_name=='Crossflow'):
            self.crossflow()
        
        return None


    def francis_turbine(self):
        '''
        This function calculates the efficiency as a function of flow for francis turbine
        '''
        reac_runsize = self.k1 * (self.design_flow)**(0.473) # Reaction turbine runner size (d)
        speci_speed = self.k2 * (self.h**(-0.5))  # Specific speed based on flow (n_q)
        speed_ad = ((speci_speed - 56)/256)**2 # Specific speed adjustment to peak efficiency (^e_nq)
        run_size = (0.081 + speed_ad) * (1 - (0.789*(reac_runsize**(-0.2)))) # Runner size adjustment to peak efficiency (^e_d)
        peak_eff = (0.919 - speed_ad + run_size) - 0.0305 + 0.005*self.Rm # Turbine peak efficiency (e_p)
        peak_eff_flow = 0.65 * self.design_flow * (speci_speed**0.05) # Peak efficiency flow (Q_p)
        full_load_eff_drop = 0.0072 *(speci_speed)**0.4 # Drop in efficiency at full load (^e_p)
        eff_full_load = (1-full_load_eff_drop)*peak_eff # Efficiency at full load (e_r)

        # Efficiencies at flows below peak efficiency flow ()
        for i in range(len(self.flow_range)):
            if (peak_eff_flow > self.flow_range[i]):
                effi = (1 - (1.25 * ((peak_eff_flow - self.flow_range[i]) / peak_eff_flow)**(3.94 - 0.0195 * speci_speed))) * peak_eff
                if (effi <= 0):
                    effi = 0
                self.effi_cal.append(effi)
            else:
                effi = peak_eff- (((self.flow_range[i] - peak_eff_flow) / (self.design_flow - peak_eff_flow)**2)*(peak_eff - eff_full_load))
                self.effi_cal.append(effi)
          
        # self.calculate_power()
    
        return None


    def kaplan(self):
        '''
        This function calculates the efficiency as a function of flow for Kaplan turbine
        '''    
        reac_runsize = self.k1 * (self.design_flow)**(0.473) # runner size
        speci_speed = self.k2 * (self.h**(-0.5))  # Specific speed based on flow (n_q)
        speed_ad = ((speci_speed - 170)/700)**2 # Specific speed adjustment to peak efficiency (^e_nq)
        run_size = (0.095 + speed_ad) * (1 - (0.789 * (reac_runsize**(-0.2))))
        peak_eff = (0.905 - speed_ad + run_size) - 0.0305 + 0.005 * self.Rm

        # Kaplan Turbines
        if (self.tur_name == 'Kaplan'):
            peak_eff_flow = 0.75 * self.design_flow # Peak efficiency flow (Qp)
            self.effi_cal = (1 - 3.5 * ((peak_eff_flow - self.flow_range)/peak_eff_flow)**6) * peak_eff # Efficiency at flows above and below Qp
            self.effi_cal = np.where(self.effi_cal <= 0 , 0, self.effi_cal) # Correct negative efficiencies
        
        # Propellor turbines
        elif (self.tur_name=='Propellor'):
            peak_eff_flow = self.design_flow
            self.effi_cal = (1 - 1.25((peak_eff_flow - self.flow_range)/peak_eff_flow)**1.13) * peak_eff
            self.effi_cal = np.where(self.effi_cal <=0 , 0, self.effi_cal)

        # self.calculate_power()
    
        return None

    def pelton(self):
        '''
        This function calculates the efficiency as a function of flow for Pelton turbine
        '''
        j = 5   # number of jets (j)
        rot_sp = 31*(self.h*self.design_flow/j)**0.5 # Rotational speed (n)
        out_run_dia = (49.4 * self.h**0.5 * j**0.02) / rot_sp # Outside diameter of runner (d)
        peak_eff = 0.864*out_run_dia**0.04 # Turbine peak efficiency
        peak_eff_flow = (0.662 + 0.001*j)*self.design_flow # Peak efficiency flow
        
        # Efficiency at flows above and below peak efficiency flow (e_q)
        self.effi_cal = (1 - ((1.31 + 0.025*j) * (abs(peak_eff_flow - self.flow_range) / (peak_eff_flow))**(5.6 + 0.4*j))) * peak_eff    
        
        if(self.tur_name == 'Turgo'):
            self.effi_cal = self.effi_cal - 0.03

        self.effi_cal = np.where(self.effi_cal <= 0 , 0, self.effi_cal) # Correct negative efficiencies
        # self.calculate_power()
            
        return None

    def crossflow(self):
        '''
        This function calculates the efficiency as a function of flow for 
        Cross-flow turbine
        '''
        peak_eff_flow = self.design_flow 
        self.effi_cal = 0.79 - 0.15 *((peak_eff_flow - self.flow_range)/peak_eff_flow) - 1.37*((peak_eff_flow - self.flow_range)/(peak_eff_flow))**(14) # Efficiency (e_q)
        self.effi_cal = np.where(self.effi_cal <= 0 , 0, self.effi_cal)
        # self.calculate_power()
    
        return None
    


# Hydropower calculation
class Hydropower(ABC):
    'This class manages hydropower calculations'
    
    @abstractmethod
    def hydropower_calculation(self, turbine, rated_power, val_min):
        pass


class HydropowerFacility(Hydropower):
    '''
    For hydropower facilities the HP equation used is:
    P = generator efficiency * turbine_efficiency * g * rho * Q * net head(available head - head_loss) 
    '''
    def __init__(self, rated_power, val_min):
        self.rated_power = rated_power
        self.val_min = val_min
    # rated_power, val_min
    
    def hydropower_calculation(self, turbine):

        # self.sys_effi = turbine.sys_effi 
        # self.effi_cal = turbine.effi_cal
        # self.flow_range = turbine.flow_range
        # self.head = turbine.head
        # self.h_f = turbine.h_f
        # self.turbine = turbine

        # TODO: if hf > head something is wrong - work on this 
        self.power =  turbine.generator_efficiency * turbine.effi_cal * g * rho * turbine.flow_range * abs(turbine.head - turbine.h_f) # HP potential, W 
        self.power = self.power / 10**6     # Watt to MW
        self.raw_power = self.power # CB: this it not used
        
        self.pmax = max(self.power)
        self.pmin = min([i for i in self.power if i > self.val_min], default = "EMPTY")
       
        # Nameplate capacity
        if self.rated_power is not None:
            self.turb_cap = self.rated_power
        else:
            self.turb_cap = self.pmax
        
        self.power = np.where(self.power > self.turb_cap, self.turb_cap, self.power)
        turbine.effi_cal = [i * 100 for i in turbine.effi_cal]   #Converting the efficiency to percentage
        
        self.turbine = turbine
 
        return None
    
# class Hydrokinetic(Hydropower):
    
    # def calculate_power_hydrokinetic(self)


def calculate_head(rated_flow, rated_power):
    '''
    Returns the head in meters based on known rated flow (m3/s) and rated power (W)
    '''
    return rated_power/(rho*g*rated_flow) 

# def max_flow_detection(flow_range):
#     ''' '''
#     return

# Annual energy calculation
# TODO: the constants cent and const are hardcoded. They should be an input from the front-end at some point
def aep_calculation(turb_obj, op, time_step_hr, cent=5, const=4.1):
    '''
    This function calculates the annual energy generation, potential revenue and estimated cost for the selected hydropower

    tot_mwh - Annual Energy in MWh
    revenue - Estimated total revenue in ($/kWh)
    const_cost - Estimated construction cost (million $/kWh)
    per_75 - 75th percentile of calculated calculated power
    '''

    tot_mwh = 0
    if (op == 'Timeseries'): 
        mwh = turb_obj.power * time_step_hr # MWh calculation
        tot_mwh = sum(mwh)  # Total Energy
    elif (op == 'Generalized'):
        valu= []
        for i in range(len(turb_obj.power)-1):
            create = ((turb_obj.power[i]+turb_obj.power[i+1])/2)
            valu.append(create)
        mwh = sum(valu)  # MWh calculation  
        tot_mwh = sum(valu) * 438 * 0.8 # Total Energy
    revenue = (tot_mwh*cent/100)*10e3 #Calculating revenue in Dollars
    #print((tot_mwh*cent/100)*10e3, revenue, cent)
    const_cost = turb_obj.turb_cap*const #Construction cost
    
    return revenue, const_cost, tot_mwh

# def time_diff_hr(dt1, dt2, date_format = '%Y-%m-%dT%H:%M:%S.%f'):
#     '''
#     Computes the time interval between flow inputs for annual
#     energy calculation
#     '''

#     # Converting str to datetime format
#     dt1 = datetime.strptime(dt1, date_format)
#     dt2 = datetime.strptime(dt2, date_format)
#     # Difference in days
#     timedel = dt2 - dt1
#     time_step_hr = (timedel.days*24*3600 + timedel.seconds)/3600
#     return time_step_hr


def turbine_type():
    '''
    Place holder to define the turbine type from the size of head
    '''
    turb_data = {'Head':['Very low head','Low head','Medium head','High head',
                'Very high head','Very high head'],
                'Start':[0.5,10,60,150,350,2000],
                'End':[10,60,150,350,2000,5000],
                'Turbine':['Kaplan','Kaplan','Francis','Francis','Pelton','Pelton'],
                'k2':[800,800,600,600,0,0]}
    
    df = pd.DataFrame.from_dict(turb_data)
    return df

def calculate_design_flow(flow, pctime_runfull = None):
    '''
    Function to calculate the design flow for a turbine given a percent of exceedance and 
    flow values 
    
    Inputs:
    - flow: a set of flow values meassured at the site of interest
    - pctime_runfull: percent of time the turbine is running full [1:100]
    '''
    pc_e = np.linspace(100, 1, 100) # 100:1
    flow_percentiles = np.percentile(flow, q = np.linspace(1, 100, 100)) # percentiles to compute, 1:100
    df = pd.DataFrame({'Flow': flow_percentiles, 'Percent_Exceedance':pc_e}) # Flow duration curve
    
    if pctime_runfull is not None: # for user defined parameters
        pe = np.round(pctime_runfull)
    else: 
        pe = 20 # default value for the percent of time a turine will run full 

    return df.loc[df['Percent_Exceedance'] == pe]
        



def calculate_potential(flow, rated_flow = None, rated_power = None, turb = None, 
                        head = None, flow_data_type = 'Timeseries', generator_efficiency = None,
                        hydropower_type = 'General', flow_column ='discharge(cfs)', units = 'US',
                        pctime_runfull = None):
    '''
    Parameters
    Top-level function to calculate the hydropower potential
    Inputs:
    - flow_info: single flow value / dataframe with the discharge (cfs or m3/s) time-series.
    - rated_flow: nameplate flow
    - rated_power: nameplate power capacity
    - head_input: hydraulic head value in meters. If it is not provided, the code with estimate the head based on rated_flow and rated_power.
    Output
    - turbine: object of the type turbine class. The estimate power and efficiency can be accessed as turbine.power and turbine.efficiency.
    - op: Calculation options, either 'Timeseries' or 'Generalized', Default = 'Timeseries'
    - rated_flow: Maximum flow or design flow for the turbine, if None the maximum value of the provided timeseries is considered.
    - system: Identifies the type of installation for hydropower, Available options are 'pipe', 'canal' and 'reservoir', default ='pipe'.
    - flow_column: Name of the dataframe column containing the flow values
    - units: unit system used for computations. Options are: 'US' for U.S. Customary or 'SI' for metric. * Note: Power units are kept in Watts 
    for both unit systems (US and SI) as this is more commonly used by the hydropower community
    '''
        
# transform units, if 'US' is selected as the unit system
    if units == 'US':
        if flow_data_type == 'Generalized':
            flow = flow * cfs_to_cms # cfs to m3/s
        elif flow_data_type == 'Timeseries':
            flow[flow_column] = flow[flow_column] * cfs_to_cms # cfs to m3/s
        if head is not None:
            head = head * ft_to_m  # ft to meters
        if rated_flow is not None:
            rated_flow = rated_flow * cfs_to_cms # cfs to m3/s
        #     rated_flow = rated_flow

    if head is None:
        head = calculate_head(rated_flow, rated_power) # head in m

    # Ensure head is sufficient
    if head <= 0.6:
        #raise ValueError('Head height too low for small-scale hydropower')
        print("Vertical drops of less than 2 ft (0.6 m) will probably make small-scale hydropower unfeasible")
        # Ref: https://www.energy.gov/energysaver/planning-microhydropower-system
        raise SystemExit
    
    # Time series flow data
    if pctime_runfull is not None:
        pctime_runfull = pctime_runfull
    else:
        pctime_runfull = 80

    if (flow_data_type == 'Timeseries'): 
        design_flow = calculate_design_flow(flow[flow_column].values, pctime_runfull)['Flow'].iloc[0] # desing flow
        flow_range = flow[flow_column].values

    # Single flow value
    elif (flow_data_type == 'Generalized'):
        if rated_flow is not None:
            design_flow = rated_flow 
        else:
            design_flow = flow
        flow_arr = np.linspace(0.1, 1, 10) # the values are %
        flow_range = design_flow * flow_arr
    
    # Turbine selection
    df = turbine_type() # Turbine selection table
    df1 = df[(head > df.Start) & (head <= df.End)] # Select turbine type based on head

    if turb is not None: # for user defined turbines
        turb_name = turb
    else: # automatic turbine selection
        turb_name = df1['Turbine'].to_string(index=False).strip()

    # Turbine coefficients
    k1 = 0.41
    k2 = df1['k2'].tolist()[0]
    # TODO: figure out what k1 and Rm mean
    Rm = 4.5 # turbine manufacturer design coefficient
    
    # h_f = calculate_head_loss(system, flow_range, head)
    h_f = 0
    
    # Efficiency of the generator
    if generator_efficiency is not None: # user defined generator efficiency
        generator_efficiency = generator_efficiency
    else:
        generator_efficiency = 0.98 # default generator efficiency
    
    # Hydropower Estimation
    turbine = TurbinePower(turb_name, flow_range, head, design_flow, h_f, k1, k2, generator_efficiency, Rm, pctime_runfull) # Initialize a TurbinePower instance
    turbine.calculate_turbine_efficiency()

    hydropower = HydropowerFacility(rated_power = None, val_min = 0)
    hydropower.hydropower_calculation(turbine)
    # turbine.calculate_turbine_efficiency() # compute HP

    # Transform units back to US
    if units == 'US': 
        turbine.design_flow = turbine.design_flow / cfs_to_cms
        turbine.head = turbine.head / ft_to_m
        turbine.h_f = turbine.h_f / ft_to_m
        turbine.flow_range = turbine.flow_range / cfs_to_cms
    
    return hydropower



if __name__ == "__main__":

    '''
    1 ft = 0.3048m # Ft to m conversion
    '''

    # df = pd.read_csv(os.path.join('.','data','turbine.csv'))
    flow_info = pd.read_csv(os.path.join('.','data_test.csv'))
    head = 65
    # flow_info = 1.63
    # Calculate the hydropower potential
    # turbine = calculate_potential(flow = flow_info, rated_flow=None, rated_power=None, head = head, system='pipe', flow_column='discharge_cfs')
    turbine = calculate_potential(flow = flow_info, head = head, flow_column = 'discharge_cfs', flow_data_type = 'Timeseries')
    
    # turbine = calculate_potential(flow = 6000, head = 18, flow_data_type = 'Generalized')
    # print(turbine)
    # turbine = calculate_potential(1600, rated_power = 8300000, flow_data_type = 'Generalized', rated_flow = 1800)
    # turbine = calculate_potential(flow= 1.63, head = 65, flow_data_type = 'Generalized', units='SI') # 

    # revenue, const_cost, tot_mwh = aep_calculation(turbine, op, time_step_hr)

    print("\n Recommended Nameplate Capacity: %0.2f (MW)" %(turbine.turb_cap))
    # print(dir(turbine))
    
    print("Recommended Turbine Type:", turbine.turbine.tur_name)
    # print("Design Flow:", turbine.design_flow)
    # print("Flow:", turbine.flow_range)
    # # # print("Percent time running full:", turbine.pctime_runfull)
    # print("Head:", turbine.head)
    print("Head Loss:", turbine.h_f)
    # print("Efficiency:", turbine.effi_cal)
    # print("EfficiencyGenerator:", turbine.generator_efficiency)




    # print("\n Annual Energy Generation: %0.2f (MWh)" %(tot_mwh))
    # print("\n Total Construction cost: $ %0.2f per_75million" %(const_cost))
    # print("\n Annual Revenue: $ %0.2f"%(revenue))
    # print("\n Head categorization: %s" %df1['Head'].to_string(index=False))
    # print("\n Suggested Tubine: %s" %(turb))
