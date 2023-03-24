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
"""

import numpy as np
import math
from numpy.core.fromnumeric import mean
from numpy.lib.function_base import median
import pandas as pd
from datetime import datetime
import os
   
# TODO: add documentation along the class: reference equations, describe the inputs, outputs, constants.
# TODO: validate that the method implemented is correct. Juan to cross-check the equations

# Constant definition
rho = 1000 # water density in Kg/m^3
g = 9.81 # acceleration of gravity (m/s^2)
# gamma = rho * g # specicif weight of water




class TurbinePower:
    def __init__(self, name, flow_range, head, maxflow, h_f, k1, k2, sys_effi, Rm):
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
        Returns: None
        '''

        # Inputs
        self.tur_name = name
        self.flow_range = flow_range
        self.head = head
        self.maxflow = maxflow
        self.h_f = h_f
        self.k1 = k1
        self.k2 = k2
        self.sys_effi = sys_effi
        self.Rm = Rm

        # Calculated 
        self.h = abs(self.head-np.nanmax(self.h_f)) # rated head on turbine [m]
        
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
        #Reaction turbine runner size (d)
        reac_runsize = self.k1*(self.maxflow)**(0.473)
        
        # Specific speed based on flow (n_q)
        speci_speed = self.k2*(self.h**(-0.5))
        
        # Specific speed adjustment to peak efficiency (^e_nq)
        speed_ad = ((speci_speed - 56)/256)**2

        # Runner size adjustment to peak efficiency (^e_d)
        run_size = (0.081 + speed_ad)*(1-(0.789*(reac_runsize**(-0.2))))

        # Turbine peak efficiency (e_p)
        peak_eff = (0.919 - speed_ad + run_size)-0.0305 + 0.005*self.Rm

        # Peak efficiency flow (Q_p)
        peak_eff_flow = 0.65 * self.maxflow * (speci_speed**0.05)
        
        # Drop in efficiency at full load (^e_p)
        full_load_eff_drop = 0.0072 *(speci_speed)**0.4
        
        # Efficiency at full load (e_r)
        eff_full_load = (1-full_load_eff_drop)*peak_eff
        
        # Efficiencies at flows below peak efficiency flow ()
        for i in range(len(self.flow_range)):
            if (peak_eff_flow > self.flow_range[i]):
                effi = (1-(1.25*((peak_eff_flow- self.flow_range[i])/peak_eff_flow)**(3.94 - 0.0195 *speci_speed)))*peak_eff
                if (effi <= 0):
                    effi = 0
                self.effi_cal.append(effi)
            else:
                effi = peak_eff- (((self.flow_range[i] - peak_eff_flow)/(self.maxflow - peak_eff_flow)**2)*(peak_eff - eff_full_load))
                self.effi_cal.append(effi)
        
        self.calculate_power()
    
        return None


    def kaplan(self):
        '''
        This function calculates the efficiency as a function of flow for Kaplan turbine
        '''    
        # print('Entering Kaplan Calculation Module')
        reac_runsize = self.k1*(self.maxflow)**(0.473)
        #print("reac_runsize: ",reac_runsize)
        speci_speed = self.k2*(self.h**(-0.5))
        #print("speci_speed: ",speci_speed)
        speed_ad= ((speci_speed-170)/700)**2
        run_size = (0.095 + speed_ad)*(1-(0.789*(reac_runsize**(-0.2))))
        peak_eff = (0.905 - speed_ad + run_size)-0.0305 + 0.005*self.Rm
        #print("Peak_eff: ", peak_eff)
        if (self.tur_name=='Kaplan'):
            peak_eff_flow = 0.75 * self.maxflow
            #print("Peak eff flow: ",peak_eff_flow)
            self.effi_cal = (1- 3.5*((peak_eff_flow - self.flow_range)/peak_eff_flow)**6)*peak_eff
            #print(self.effi_cal)
            self.effi_cal = np.where(self.effi_cal <=0 , 0, self.effi_cal)
            #print(self.effi_cal)
        elif (self.tur_name=='Propellor'):
            peak_eff_flow = self.maxflow
            self.effi_cal = (1-1.25((peak_eff_flow - self.flow_range)/peak_eff_flow)**1.13)*peak_eff
            self.effi_cal = np.where(self.effi_cal <=0 , 0, self.effi_cal)

        self.calculate_power()
    
        return None

    def pelton(self):
        '''
        This function calculates the efficiency as a function of flow for Pelton turbine
        '''
        j = 5   # number of jets (j)
        # Rotational speed (n)
        rot_sp = 31*self.h*(self.maxflow/j)**0.5
        
        # Outside diameter of runner (d)
        out_run_dia = (49.4*(self.h**0.5)*j**0.02)/rot_sp

        peak_eff = 0.864* out_run_dia**0.04
        peak_eff_flow = (0.662+0.001*j)*self.maxflow
        
        # Efficiency at flows above and below peak efficiency flow (e_q)
        effi_pelo = (1-((1.31+0.025*j)*(abs(peak_eff_flow - self.flow_range)/(peak_eff_flow))**(5.6+0.4*j)))*peak_eff    
        if (self.tur_name==' Pelton turbine'):
            self.effi_cal = effi_pelo
        elif(self.tur_name==' Turgo turbine'):
            self.effi_cal = effi_pelo - 0.03
        self.effi_cal = np.where(self.effi_cal <=0 , 0, self.effi_cal)
        
        self.calculate_power()
    
        return None

    def crossflow(self):
        '''
        This function calculates the efficiency as a function of flow for 
        Cross-flow turbine
        '''
        peak_eff_flow = self.maxflow
        # Efficiency (e_q)
        effi = 0.79 - 0.15 *((peak_eff_flow - self.flow_range)/peak_eff_flow) - 1.37*((peak_eff_flow - self.flow_range)/(peak_eff_flow))**(14)
        self.effi_cal=effi
        self.effi_cal = np.where(self.effi_cal <=0 , 0, self.effi_cal)
        
        self.calculate_power()
    
        return None
    
    def calculate_power(self, rated_power=None,val_min=0 ):
        '''
        This function calculates power
        P = rho * g * (head - head_loss) * system_efficiency * turbine_efficiency
        '''
        self.power = abs(self.flow_range * (self.head - self.h_f) * self.effi_cal * self.sys_effi * g * rho)
        self.power = self.power/10**6    # converts to MW
        self.raw_power = self.power
        self.pmax = max(self.power)
        self.pmin = min([i for i in self.power if i > val_min], default="EMPTY")
        if rated_power is not None:
            turb_cap = rated_power
        else:
            self.turb_cap = np.percentile(self.power,75)
        
        self.power=np.where(self.power>self.turb_cap,self.turb_cap,self.power)
        self.effi_cal = [i*100 for i in self.effi_cal]   #Converting the efficiency to percentage
        return None


def calculate_head(rated_flow, rated_power):
    '''
    Returns the head in meters based on known rated flow (m3/s) and rated power (W)
    '''
    return rated_power/(rho * g * rated_flow) 


def calculate_head_loss(system, flow_range, head):
    # h_f: head loss
    h_f = 0
    if (system=='pipe'):
        h_f = 0.05* flow_range
        # h_f = f*L*V**2 / (2*g*D) # Darcy-Weisbach euqation for head loss
        
    elif (system=='canal'):
        h_f= 0.2* flow_range
    elif (system =='reservoir'):
        h_f = 0.01*flow_range
    
    if (min(head-h_f)<0):
        print("Check value(s) for diameter and Flow")
        #                   raise SystemExit

    return h_f


def max_flow_detection(flow_range):
    ''' '''
    return


# Annual energy calculation
# TODO: the constants cent and const are hardcoded. They should an inout from the front-end at some point
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

# def calculate_design_flow(flow):
#     flow_percentile = np.percentile(flow)





def calculate_potential(flow, rated_flow = None, rated_power = None, turb = None, 
                        head = None, flow_data_type = 'Timeseries', sys_effi = None,
                        system ='pipe', flow_column ='discharge(cfs)', units = "US"):
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
    - units: unit system used for computations. Options are: 'US'for U.S. Customary or 'SI' for metric. * Note: Power units are kept in Watts as
    this is more commonly used by the hydropower community
    '''
    df = turbine_type()
        
# transform units, if 'US' is selected as the unit system
    if units == 'US':
        if flow_data_type == 'Generalized':
            flow = flow * 0.028316846591999675 # cfs to m3/s
        elif flow_data_type == 'Timeseries':
            flow[flow_column] = flow[flow_column] * 0.028316846591999675 # cfs to m3/s
        if head is not None:
            head = head * 0.3048  # ft to meters
        if rated_flow is not None:
            rated_flow = rated_flow * 0.028316846591999675 # cfs to m3/s
        #     rated_flow = rated_flow

    if head is None:
        head = calculate_head(rated_flow, rated_power) # head in m
        # head = abs(diff_m)

    # Ensure head is sufficient
    if head <= 0.6:
        #raise ValueError('Head height too low for small-scale hydropower')
        print("Vertical drops of less than 2 ft (0.6 m) will probably make small-scale hydropower unfeasible")
        # Ref: https://www.energy.gov/energysaver/planning-microhydropower-system
        raise SystemExit
    
    #op = 'Timeseries'  # other option is 'Generalized' and we will need to define maxflow = 350 cfs 
    #length = length*1609.34 #Converting mi to m
    #turb = 'Default'

    if (flow_data_type == 'Timeseries'): # For working with 
        designflow = flow[flow_column].max() # Modify this
        #designflow = calculate_design_flow(flow[flow_column].values) # Modify this
        
        flow_range = flow[flow_column].values

        #print(f'Flow range: {flow_range}')

    elif (flow_data_type == 'Generalized'):
        if rated_flow is not None:
            designflow = rated_flow 
        else:
            designflow = flow_info 
            
        flow_arr = np.linspace(0.7, 1.3, 12) # the values are %
        flow_range = designflow * flow_arr
    
    # Turbine selection
    df1 = df[(head > df.Start) & (head <= df.End)]
    # print(df1)
    #if (turb == 'Default'):
        #print(df1)
    #    turb_name = df1['Turbine'].to_string(index=False).strip()
        #print(tur_name)
    if turb is not None:
        turb_name = turb
    else:
        turb_name = df1['Turbine'].to_string(index=False).strip()
        #print("Override Performed")
    # turbine constant variables
    #print(df1['k2'])
    k2 = df1['k2'].tolist()[0]
    # TODO: figure out what k1 and Rm mean
    k1 = 0.41
    Rm = 4.5 # turbine manufacturer design coefficient
    h_f = calculate_head_loss(system, flow_range, head)
    if sys_effi is not None:
        sys_effi = sys_effi
    else:
        sys_effi = 0.98 # generator efficiency
    #print(h_f)
    turbine = TurbinePower(turb_name, flow_range, head, designflow, h_f, k1, k2, sys_effi, Rm)
    turbine.calculate_turbine_efficiency()
    
    return turbine

if __name__ == "__main__":

    '''
    1 ft = 0.3048m # Ft to m conversion
    '''

    # df = pd.read_csv(os.path.join('.','data','turbine.csv'))
    flow_info = pd.read_csv(os.path.join('.','data_test.csv'))
    head = 500
    # flow_info = 1500
    # Calculate the hydropower potential
    # turbine = calculate_potential(flow = flow_info, rated_flow=None, rated_power=None, head = head, system='pipe', flow_column='discharge_cfs')
    turbine = calculate_potential(flow = flow_info, head = head, flow_column='discharge_cfs')
    # turbine = calculate_potential(flow_info, head = head, flow_data_type = 'Generalized', rated_flow = 1500)

    # revenue, const_cost, tot_mwh = aep_calculation(turbine, op, time_step_hr)

    print("\n Recommended Nameplate Capacity: %0.2f (MW)" %(turbine.turb_cap))
    # print("\n Annual Energy Generation: %0.2f (MWh)" %(tot_mwh))
    # print("\n Total Construction cost: $ %0.2f per_75million" %(const_cost))
    # print("\n Annual Revenue: $ %0.2f"%(revenue))
    # print("\n Head categorization: %s" %df1['Head'].to_string(index=False))
    # print("\n Suggested Tubine: %s" %(turb))

