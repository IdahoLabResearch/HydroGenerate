'''
Copyright 2023, Battelle Energy Alliance, LLC
'''

"""
03-2023
@author: MITRB, J. Gallego-Calderon, Camilo J. Bastidas Pacheco

This module handles turbine selection and efficiency calculation
"""

import numpy as np
# import math
# from numpy.core.fromnumeric import mean
# from numpy.lib.function_base import median
import pandas as pd
from abc import ABC, abstractmethod
# from datetime import datetime
# from abc import ABC, abstractmethod

from numbers import Number
   
# TODO: add documentation along the class: reference equations, describe the inputs, outputs, constants.
# TODO: validate that the method implemented is correct. Juan to cross-check the equations

# Turbine Parameters
class TurbineParameters:
    def __init__(self, turbine_type, flow, design_flow, flow_column, head, head_loss, rated_power,
                 system_efficiency,
                 generator_efficiency, Rm, pctime_runfull, pelton_n_jets):
        '''
        This class initializes the calculation of hydropower potential for a specific turbine type
        Input variables:
        - turbine_type: Selects the particular turbine based on available head
        - flow: flow value (s)
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
        self.turbine_type = turbine_type
        self.flow = flow
        self.design_flow = design_flow
        self.head = head
        self.head_loss = head_loss
        self.rated_power = rated_power        # Rated Power (KW)
        self.system_efficiency = system_efficiency        # Overal system efficiency [0:1]
        self.generator_efficiency = generator_efficiency
        self.Rm = Rm
        self.pctime_runfull = pctime_runfull
        self.pelton_n_jets = pelton_n_jets
        self.flow_column = flow_column

        # Calculated 
        # self.h = abs(self.head - np.nanmax(self.h_f)) # rated head on turbine [m]
        self.h = self.head      # rated head on turbine [m]
        
        if self.Rm is None:
            self.Rm = 4.5        # turbine manufacture/design coefficient
        
        # Outputs
        self.runner_diameter = [] # runner diameter
        self.pmax = 0       # maximum power
        self.pmin = 0       # minimun power
        self.power = []     # array that contains the power 
        self.design_efficiency = None
        self.effi_cal = []  # contains the range of efficiencies for the flow range
        self.turb_cap = 0
        self.raw_power = []
    
def turbine_type_selector(head):
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
    df1 = df[(head > df.Start) & (head <= df.End)] # Select turbine type based on head
    return df1['Turbine'].to_string(index=False).strip()

# Flow range calculation
class FlowRange():

    def flowrange_calculator(self, turbine):
        if isinstance(turbine.flow, Number):
            range = np.linspace(0.6, 1.2, 18) # the values are %
            turbine.flow = turbine.flow * range

# Turbine efficiency and sizing

# Runner diameter for reaction turbines
class ReactionTurbines():

    def runnersize_calculator(self, design_flow):  

        if design_flow > 23: # d > 1.8 - The formula in the document has an 'undefined' area
            k = 0.41
        else:
            k = 0.46

        d = k * design_flow**0.473     # runner throat diameter in m
        
        return d
    
# Functions to calculate turbine efficiency by turbine type (CANMET Energy Technology Center, 2004)
class Turbine(ABC):   
    
    @abstractmethod
    def turbine_calculator(self, turbine):
        pass

class FrancisTurbine(Turbine):

    def turbine_calculator(self, turbine):   

        Qd = turbine.design_flow        # design flow
        d = ReactionTurbines().runnersize_calculator(Qd)
        nq = 600 * turbine.head**(-0.5)     # Specific speed
        enq = ((nq - 56) / 256)**2      # Specific speed adjustment to peak efficiency (^e_nq)
        ed = (0.081 + enq) * (1 - (0.789 * d**(-0.2)))      # Runner size adjustment to peak efficiency (^e_d)
        ep = (0.919 - enq + ed) - 0.0305 + 0.005 * turbine.Rm      # Turbine peak efficiency (e_p)
        Qp = 0.65 * Qd * (nq**0.05)        # Peak efficiency flow (Q_p)
        ep_ = 0.0072 * nq**0.4      # Drop in efficiency at full load (^e_p)
        er = (1 - ep_) * ep     # Efficiency at full load (e_r)

        # Efficiencies at flows below and above peak efficiency flow
        FlowRange().flowrange_calculator(turbine= turbine)      # generate a flow range from 60% to 120% of the flow given
        Q = turbine.flow
        for i in range(len(Q)):
            if (Q[i] < Qp):        # flows below Qd
                effi = (1 - (1.25 * ((Qp - Q[i]) / Qp)**(3.94 - 0.0195*nq))) * ep
                if (effi <= 0):
                    effi = 0
                turbine.effi_cal.append(effi)
            else:       
                effi = ep - (((Q[i] - Qp) / (Qd - Qp)**2) * (ep - er))
                turbine.effi_cal.append(effi)
        
        turbine.effi_cal = np.array(turbine.effi_cal)
        turbine.runner_diameter = d     # update

class KaplanTurbine(Turbine):
      
      def turbine_calculator(self, turbine):

        Qd = turbine.design_flow        # design flow
        d = ReactionTurbines().runnersize_calculator(Qd)
        nq = 800 * turbine.head**(-0.5)     # Specific speed
        enq = ((nq - 170) / 700)**2     # Specific speed adjustment to peak efficiency (^e_nq)
        ed = (0.095 + enq) * (1 - 0.789 * d**(-0.2))         # Runner size adjustment to peak efficiency (^e_d)
        ep = (0.905 - enq + ed) - 0.0305 + 0.005 * turbine.Rm      # Turbine peak efficiency (e_p)
        Qp = 0.75 * Qd      # Peak efficiency flow (Q_p)
        # FlowRange().flowrange_calculator(turbine= turbine)      # generate a flow range from 60% to 120% of the flow given
        Q = turbine.flow
        turbine.effi_cal = (1 - 3.5 * ((Qp - Q) / Qp)**6) * ep     # Efficiency at flows above and below Qp
        turbine.effi_cal = np.where(turbine.effi_cal <= 0 , 0, turbine.effi_cal)        # Correct negative efficiencies
        turbine.runner_diameter = d     # update

class PropellorTurbine(Turbine):
      
      def turbine_calculator(self, turbine):

        Qd = turbine.design_flow        # design flow
        d = ReactionTurbines().runnersize_calculator(Qd)
        nq = 800 * turbine.head**(-0.5)     # Specific speed
        enq = ((nq - 170) / 700)**2     # Specific speed adjustment to peak efficiency (^e_nq)
        ed = (0.095 + enq) * (1 - 0.789 * d**(-0.2))         # Runner size adjustment to peak efficiency (^e_d)
        ep = (0.905 - enq + ed) - 0.0305 + 0.005 * turbine.Rm      # Turbine peak efficiency (e_p)
        Qp = Qd      # Peak efficiency flow (Q_p)
        FlowRange().flowrange_calculator(turbine= turbine)      # generate a flow range from 60% to 120% of the flow given
        Q = turbine.flow
        turbine.effi_cal = (1 - 1.25 * ((Qp - Q) / Qp)**1.13) * ep     # Efficiency at flows above and below Qp
        turbine.effi_cal = np.where(turbine.effi_cal <= 0 , 0, turbine.effi_cal) # Correct negative efficiencies
        turbine.runner_diameter = d     # update

class PeltonTurbine(Turbine):
      
      def turbine_calculator(self, turbine):
          
          if turbine.pelton_n_jets is None:
              turbine.pelton_n_jets = 3
    
          j = turbine.pelton_n_jets   # number of jets (j)
          h = turbine.head
          Qd = turbine.design_flow
          n =  31 * (h * Qd / j)**0.5       # Rotational speed (n)
          d = 49.4 * h**0.5 * j**0.02 / n       # Outside diameter of runner (d)
          ep = 0.864 * d**0.04      # Turbine peak efficiency
          Qp = (0.662 + 0.001 * j) * Qd # Peak efficiency flow
          FlowRange().flowrange_calculator(turbine= turbine)      # generate a flow range from 60% to 120% of the flow given
          Q = turbine.flow
          turbine.effi_cal = (1 - ((1.31 + 0.025*j) * (abs(Qp - Q) / (Qp))**(5.6 + 0.4*j))) * ep          # Efficiency at flows above and below peak efficiency flow (e_q)
          turbine.runner_diameter = d     # update

class TurgoTurbine(Turbine):
      
      def turbine_calculator(self, turbine):
          PeltonTurbine().turbine_calculator(turbine)       # Calculate Pelton efficiency
          turbine.effi_cal = turbine.effi_cal - 0.03        # Pelton efficiency - 0.03
          turbine.effi_cal = np.where(turbine.effi_cal <= 0 , 0, turbine.effi_cal)        # Correct negative efficiencies 
          
class CrossFlowTurbine(Turbine):
        
        def turbine_calculator(self, turbine):

            Qd = turbine.design_flow 
            FlowRange().flowrange_calculator(turbine= turbine)      # generate a flow range from 60% to 120% of the flow given
            Q = turbine.flow    # flow range
            turbine.effi_cal = 0.79 - 0.15 *((Qd - Q) / Qd) - 1.37 * ((Qd - Q) / Q)**14     # Efficiency (e_q)
            turbine.effi_cal = np.where(turbine.effi_cal <= 0 , 0, turbine.effi_cal)        # Correct negative efficiencies
# End of turbine funcitons

# Functions to calculate design flow. 
class DesignFlow(ABC):
    @abstractmethod
    def designflow_calculator(self, turbine):
        pass

# Flow duration curve selection based on a percentage of exceedance
class PercentExceedance(DesignFlow):
    
    def designflow_calculator(self, turbine):

        pe = turbine.pctime_runfull     # percentage of time a turbine is running full
        flow = turbine.flow     # user-entered flow
        
        if pe is not None:      # user defined percent of time a turbine is running full. pe ∝ 1/(design flow)
            pe = np.round(pe)       # round to find in 'flow_percentiles' list
        else: 
            pe = 80     # default value for the percent of time a turine will run full 

        if isinstance(flow, Number):
            design_flow = flow      # when a single value of flow is provided, this is the design flow

        else:
            pc_e = np.linspace(100, 1, 100)     # sequence from 100 to 1.
            flow_percentiles = np.percentile(flow, q = np.linspace(1, 100, 100))        # percentiles to compute, 1:100
            flowduration_curve = {'Flow': flow_percentiles, 'Percent_Exceedance':pc_e}      # Flow duration curve
            design_flow = float(flowduration_curve['Flow'][flowduration_curve['Percent_Exceedance'] == pe])     # flow for the selected percent of excedante
        
        turbine.design_flow = design_flow       # Update
        turbine.pctime_runfull = pe     # Update


if __name__ == "__main__":


    # Example 1. Calculating the design flow based on an existing time seriers
    flow_info = pd.read_csv('data_test.csv')['discharge_cfs']
    
    turbine_parameters = TurbineParameters(turbine_type = None, flow= flow_info, head= 20, design_flow = 100, 
                                           rated_power= None, system_efficiency = None,
                                           head_loss = None, Rm= None, pctime_runfull= None, generator_efficiency = None,
                                           flow_column = None, pelton_n_jets= None)  # Initialize a TurbinePower instance
    
    # design_flow = PercentExceedance(pctime_runfull = None).designflow_calculator(flow = flow_info['discharge_cfs'])
    # PercentExceedance(pctime_runfull = None).designflow_calculator(flow = flow_info['discharge_cfs'])
    # print(design_flow)
    
    # # Cross-Flow turbine
    turb = CrossFlowTurbine()
    turb.turbine_calculator(turbine = turbine_parameters)
    print("\nEfficiency",turbine_parameters.effi_cal)
    print("\nCrossFlow")
    print(len(turbine_parameters.effi_cal))
    print(type(turbine_parameters.effi_cal))

    # turbine_parameters = TurbineParameters(turbine_type = None, flow= flow_info, head= 100, design_flow = 4120, 
    #                                        head_loss = None, Rm= None, pctime_runfull= None, generator_efficiency = None)  # Initialize a TurbinePower instance
    # # # Pelton turbine
    # turb = PeltonTurbine()
    # turb.turbine_calculator(turbine = turbine_parameters)
    # # print("\nEfficiency",turbine_parameters.effi_cal)
    # print("\nPelton")
    # print(len(turbine_parameters.effi_cal))
    # print(type(turbine_parameters.effi_cal))

    # turbine_parameters = TurbineParameters(turbine_type = None, flow= flow_info, head= 100, design_flow = 4120, 
    #                                        head_loss = None, Rm= None, pctime_runfull= None, generator_efficiency = None)  # Initialize a TurbinePower instance
    # # Turgo turbine
    # turb = TurgoTurbine()
    # turb.turbine_calculator(turbine = turbine_parameters)
    # # print("\nEfficiency",turbine_parameters.effi_cal)
    # print("\nTurgo")
    # print(len(turbine_parameters.effi_cal))
    # print(type(turbine_parameters.effi_cal))

    # turbine_parameters = TurbineParameters(turbine_type = None, flow= flow_info, head= 100, design_flow = 4120, 
    #                                        head_loss = None, Rm= None, pctime_runfull= None, generator_efficiency = None)  # Initialize a TurbinePower instance
    # # Propellor Turbine
    # turb = PropellorTurbine()
    # turb.turbine_calculator(turbine = turbine_parameters)
    # # print("\nEfficiency",turbine_parameters.effi_cal)
    # print("\nPropellor")
    # print(len(turbine_parameters.effi_cal))
    # print(type(turbine_parameters.effi_cal))

    # turbine_parameters = TurbineParameters(turbine_type = None, flow= flow_info, head= 100, design_flow = 4120, 
    #                                        head_loss = None, Rm= None, pctime_runfull= None, generator_efficiency = None)  # Initialize a TurbinePower instance
    # # Kaplan Turbine
    # turb = KaplanTurbine()
    # turb.turbine_calculator(turbine = turbine_parameters)
    # # print("\nEfficiency",turbine_parameters.effi_cal)
    # print("\nKaplan")
    # print(len(turbine_parameters.effi_cal))
    # print(type(turbine_parameters.effi_cal))

    # turbine_parameters = TurbineParameters(turbine_type = None, flow= flow_info, head= 100, design_flow = 4120, 
    #                                        head_loss = None, Rm= None, pctime_runfull= None, generator_efficiency = None)  # Initialize a TurbinePower instance
    # # Francis Turbine
    # turb = FrancisTurbine()
    # turb.turbine_calculator(turbine = turbine_parameters)
    # # print("\nEfficiency",turbine_parameters.effi_cal)
    # print("\nFrancis")
    # print(len(turbine_parameters.effi_cal))
    # print(type(turbine_parameters.effi_cal))

    