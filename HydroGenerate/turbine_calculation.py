'''
Copyright 2023, Battelle Energy Alliance, LLC
'''

"""
03-2023
@authors: Camilo J. Bastidas Pacheco, J. Gallego-Calderon, Soumyadeep Nag, MITRB

This module handles turbine selection and efficiency calculation
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from numbers import Number
import math
from shapely.geometry import Point
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
   
# TODO: add documentation along the class: reference equations, describe the inputs, outputs, constants.
# TODO: validate that the method implemented is correct. Juan to cross-check the equations

max_flow_turbine = 1      # multiplier for the maximum flow that can be passed through a turbine

# Turbine Parameters
class TurbineParameters:

    def __init__(self, turbine_type, flow, design_flow, flow_column, head, 
                 rated_power,
                 system_efficiency,
                 generator_efficiency, Rm, pctime_runfull, pelton_n_jets, 
                 hk_blade_diameter, hk_blade_heigth, hk_blade_type, hk_swept_area):
        '''
        This class initializes the calculation of all turbines parameters.        
        Parameter descriptions are provided below:
        '''

        # Inputs
        self.turbine_type = turbine_type        # type of turbine. Options are: Hydrokinetic, Francis, Propellor, Pelton, Turgo, CrossFlow
        self.flow = flow        # Flow, cfs or m3/s
        self.design_flow = design_flow      # desing flow of the hydropower system, cfs or m3/s
        self.head = head        # hydraulic head, ft or m
        self.rated_power = rated_power        # Rated Power (KW)
        self.system_efficiency = system_efficiency        # Overal system efficiency [0:1]
        self.generator_efficiency = generator_efficiency        # efficiency of the generator, default: 98%
        self.Rm = Rm        # Turbine manufacture / design coefficient, default: 4.5 (https://www.ieahydro.org/media/1ccb8c33/RETScreen%C2%AE-Engineering-Cases-Textbook%E2%80%93-PDF.pdf)
        self.pctime_runfull = pctime_runfull        # percent of time a turbine will run full, default: 80%
        self.pelton_n_jets = pelton_n_jets      # number of jets in a Pelton turbine, default: 3
        self.flow_column = flow_column      # when flow is a pandas dataframe, name of the column containing the flow data
        
        self.hk_blade_diameter = hk_blade_diameter      # Hydrokinetic turbine blade diameter m
        self.hk_blade_heigth = hk_blade_heigth      # Hydrokinetic turbine blade height m
        self.hk_blade_type = hk_blade_type      # Hydrokinetic turbine blade type: 'ConventionalRotor' , "H-DarrieusRotor", "DarrieusRotor"
        self.hk_swept_area = hk_swept_area      # Hydrokinetic turbine blade spwept area m2

        # Calculated 

        if self.Rm is None:
            self.Rm = 4.5        # turbine manufacture/design coefficient
        
        # Additional parameters
        self.design_efficiency = None       # placeholder for the fficiency at design flow
        self.turbine_flow = None        # FLow passing through the turbine, cfs or m3/s
        self.dataframe_output = None    # placeholder for pandas dataframe output
        self.runner_diameter = None    # placeholder for the runner diameter   
    
def turbine_type_selector(hp_params):

    # inputs
    head = hp_params.head           # head, m
    design_flow = hp_params.design_flow         # flow, m3/s

    # define polygons of influence for every turbine type
    polygon_pelton = Polygon([(1, 50), (1, 1000), (20, 1000), (60, 500), (50, 400),(1, 50)])
    polygon_turgo = Polygon([(1, 50), (1, 260), (10, 50),(1, 50)])
    polygon_francis = Polygon([(1, 50), (5, 10), (200, 10), (900, 15), (900,80), (100, 700), (6,700),(1, 50)])
    polygon_kaplan = Polygon([(1,1), (1, 20), (9,80), (175,80), (1000,15), (60,1),(1,1)])
    polygon_crossflow = Polygon([(1,4), (1, 100), (10,10), (10, 4),(1,4)])
 
    # define polygons centroids
    centroid_pelton = polygon_pelton.centroid
    centroid_turgo = polygon_turgo.centroid
    centroid_francis = polygon_francis.centroid
    centroid_crossflow = polygon_crossflow.centroid
    centroid_kaplan = polygon_kaplan.centroid

    # Point with head, design_flow
    point = Point(design_flow, head)        # point - [flow, head] - [m3/s, m]


    # empty lists to store outputs
    turbines_list = []
    centroids_list = []

                    # 'Turbine':['Kaplan','Kaplan'],

    # find which polygon contains the point and distance between the point and centroid of that polygon

    # Kaplan
    if polygon_kaplan.contains(point):
        turbines_list.append('Kaplan')
        centroids_list.append(math.sqrt((point.x - centroid_kaplan.x)**2 + (point.y - centroid_kaplan.y)**2))

    # Francis
    if polygon_francis.contains(point):
        turbines_list.append('Francis')
        centroids_list.append(math.sqrt((point.x - centroid_francis.x)**2 + (point.y - centroid_francis.y)**2))

    # Pelton
    if polygon_pelton.contains(point):
        turbines_list.append('Pelton')
        centroids_list.append(math.sqrt((point.x - centroid_pelton.x)**2 + (point.y - centroid_pelton.y)**2))

    # Turgo 
    if polygon_turgo.contains(point):
        turbines_list.append('Turgo')
        centroids_list.append(math.sqrt((point.x - centroid_turgo.x)**2 + (point.y - centroid_turgo.y)**2))
    
    # Crossflow    
    if polygon_crossflow.contains(point):
        turbines_list.append('Crossflow')
        centroids_list.append(math.sqrt((point.x - centroid_crossflow.x)**2 + (point.y - centroid_crossflow.y)**2))

    # Case when there are no turbines in range
    if not turbines_list:       # the head and flow are in in range for any turbine
        raise ValueError('Head or flow paramters are out of range for all turbine types supported in HydroGenerate')       
    else:
        turbines_dict = dict(zip(turbines_list, centroids_list))            # create a dictionary with all turbine responsed
        hp_params.turbine_type = min(turbines_dict, key=turbines_dict.get)
        hp_params.turbine_type_dict = turbines_dict

        # create figure showing
        xpoints = np.array([design_flow])
        ypoints = np.array([head]) 

        x,y = polygon_pelton.exterior.xy
        plt.ioff()
        turbine_type_fig = plt.figure(figsize=(7, 5))
        plt.loglog(x, y,label = 'Pelton')
        x,y = polygon_turgo.exterior.xy
        plt.loglog(x, y,label = 'Turgo')
        x,y = polygon_francis.exterior.xy
        plt.loglog(x, y,label = 'Francis')
        x,y = polygon_crossflow.exterior.xy
        plt.loglog(x, y,label = 'Crossflow')
        x,y = polygon_kaplan.exterior.xy
        plt.loglog(x, y,label = 'Kaplan')
        plt.xlim([1, 1000])
        plt.ylim([1, 1000])
        plt.xlabel('Flow (m^3/s)')
        plt.ylabel('Head (m)')
        plt.plot(xpoints, ypoints,'o', label='Site characteristics')
        plt.legend()
        plt.legend(loc='upper right')
        hp_params.turbinetype_figure = turbine_type_fig
        plt.close(turbine_type_fig)

# Flow range calculation
class FlowRange():

    '''
    Function to calculate a range of flows from 0.5 to max_flow_turbine.
    '''

    def flowrange_calculator(self, turbine):
        if isinstance(turbine.flow, Number):
            range = np.linspace(0.5, max_flow_turbine, 18) # the values are %
            turbine.flow = turbine.flow * range

# Turbine efficiency and sizing

# Runner diameter for reaction turbines
class ReactionTurbines():      
    '''
    Function to calculate the turbine runner diameter
    '''

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
    '''
    Francis turbine calculation
    '''
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
        Q = turbine.turbine_flow # turbine flow
        turbine.turbine_efficiency = [] # placeholder
        for i in range(len(Q)):
            if (Q[i] < Qp):        # flows below Qd
                effi = (1 - (1.25 * ((Qp - Q[i]) / Qp)**(3.94 - 0.0195*nq))) * ep
                if (effi <= 0):
                    effi = 0
                turbine.turbine_efficiency.append(effi)
            else:       
                effi = ep - (((Q[i] - Qp) / (Qd - Qp)**2) * (ep - er))
                turbine.turbine_efficiency.append(effi)
        
        turbine.turbine_efficiency = np.array(turbine.turbine_efficiency)
        turbine.runner_diameter = d     # update

class KaplanTurbine(Turbine):
    '''
    Kaplan turbine calculation
    '''
    def turbine_calculator(self, turbine):
        
        Qd = turbine.design_flow        # design flow
        d = ReactionTurbines().runnersize_calculator(Qd)
        nq = 800 * turbine.head**(-0.5)     # Specific speed
        enq = ((nq - 170) / 700)**2     # Specific speed adjustment to peak efficiency (^e_nq)
        ed = (0.095 + enq) * (1 - 0.789 * d**(-0.2))         # Runner size adjustment to peak efficiency (^e_d)
        ep = (0.905 - enq + ed) - 0.0305 + 0.005 * turbine.Rm      # Turbine peak efficiency (e_p)
        Qp = 0.75 * Qd      # Peak efficiency flow (Q_p)
        FlowRange().flowrange_calculator(turbine= turbine)      # generate a flow range from 60% to 120% of the flow given
        Q = turbine.turbine_flow
        turbine.turbine_efficiency = (1 - 3.5 * ((Qp - Q) / Qp)**6) * ep     # Efficiency at flows above and below Qp
        turbine.turbine_efficiency = np.where(turbine.turbine_efficiency <= 0 , 0, turbine.turbine_efficiency)        # Correct negative efficiencies
        turbine.runner_diameter = d     # update

class PropellerTurbine(Turbine):
    '''
    Propellor turbine calculation
    '''
      
    def turbine_calculator(self, turbine):
        
        Qd = turbine.design_flow        # design flow
        d = ReactionTurbines().runnersize_calculator(Qd)
        nq = 800 * turbine.head**(-0.5)     # Specific speed
        enq = ((nq - 170) / 700)**2     # Specific speed adjustment to peak efficiency (^e_nq)
        ed = (0.095 + enq) * (1 - 0.789 * d**(-0.2))         # Runner size adjustment to peak efficiency (^e_d)
        ep = (0.905 - enq + ed) - 0.0305 + 0.005 * turbine.Rm      # Turbine peak efficiency (e_p)
        Qp = Qd      # Peak efficiency flow (Q_p)
        FlowRange().flowrange_calculator(turbine= turbine)      # generate a flow range from 60% to 120% of the flow given
        Q = turbine.turbine_flow
        turbine.turbine_efficiency = (1 - 1.25 * ((Qp - Q) / Qp)**1.13) * ep     # Efficiency at flows above and below Qp
        turbine.turbine_efficiency = np.where(turbine.turbine_efficiency <= 0 , 0, turbine.turbine_efficiency) # Correct negative efficiencies
        turbine.runner_diameter = d     # update

class PeltonTurbine(Turbine):  
    '''
    Pelton turbine calculation
    '''

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
        Q = turbine.turbine_flow
        turbine.turbine_efficiency = (1 - ((1.31 + 0.025*j) * (abs(Qp - Q) / (Qp))**(5.6 + 0.4*j))) * ep          # Efficiency at flows above and below peak efficiency flow (e_q)
        turbine.runner_diameter = d     # update

class TurgoTurbine(Turbine):
    '''
    Pelton turbine calculation
    '''

    def turbine_calculator(self, turbine):
          PeltonTurbine().turbine_calculator(turbine)       # Calculate Pelton efficiency
          turbine.turbine_efficiency = turbine.turbine_efficiency - 0.03        # Pelton efficiency - 0.03
          turbine.turbine_efficiency = np.where(turbine.turbine_efficiency <= 0 , 0, turbine.turbine_efficiency)        # Correct negative efficiencies 
          
class CrossFlowTurbine(Turbine):
    '''
    Pelton turbine calculation
    '''
      
    def turbine_calculator(self, turbine):
        Qd = turbine.design_flow 
        FlowRange().flowrange_calculator(turbine= turbine)      # generate a flow range from 60% to 120% of the flow given
        Q = turbine.turbine_flow
        turbine.turbine_efficiency = 0.79 - 0.15 *((Qd - Q) / Qd) - 1.37 * ((Qd - Q) / Q)**14     # Efficiency (e_q)
        turbine.turbine_efficiency = np.where(turbine.turbine_efficiency <= 0 , 0, turbine.turbine_efficiency)        # Correct negative efficiencies

class Hydrokinetic_Turbine(Turbine):
    '''
    Hydrokinetic turbine calculation
    '''       

    def turbine_calculator(self, turbine):

        if turbine.hk_blade_type is None:       # if a turbine type is not given
            turbine.hk_blade_type = 'ConventionalRotor'     # default - update
            
        if turbine.hk_blade_diameter:
            D = turbine.hk_blade_diameter
        else:
            D = 1       # default, 1 m
            
        turbine.hk_blade_diameter = D       # update

        if turbine.hk_blade_type == 'ConventionalRotor':
            A = np.pi * D**2 / 4        # Hydrokinetic turbine blade spwept area m2
           
        else:       # Height is needed
            if turbine.hk_blade_heigth:     # if the blade height is known
                H = turbine.hk_blade_heigth
            else:
                H = 1 # default, 1 m

            turbine.hk_blade_heigth = H       # update

        if turbine.hk_blade_type == 'H-DarrieusRotor':
            A = D * H       # Hydrokinetic turbine blade spwept area m2

        elif turbine.hk_blade_type == 'DarrieusRotor':         
            A = 0.65 * D * H        # Hydrokinetic turbine blade spwept area m2
            
        turbine.hk_swept_area = A       # update

# End of turbine funcitons

# Functions to calculate design flow. 
class DesignFlow(ABC):
    @abstractmethod
    def designflow_calculator(self, turbine):
        pass

# Desing flow selected from the flow duration curve for a percentage of exceedance
class PercentExceedance(DesignFlow):
    '''
    Design flow calculation based on the percent exceedance
    '''

    def designflow_calculator(self, turbine):

        pe = turbine.pctime_runfull     # percentage of time a turbine is running full
        flow = turbine.flow     # user-entered flow
        
        if pe is not None:      # user defined percent of time a turbine is running full. pe ∝ 1/(design flow)
            pe = np.round(pe)       # round to find in 'flow_percentiles' list
        else: 
            pe = 30     # default value for the percent of time a turine will run full 

        if isinstance(flow, Number):
            design_flow = flow      # when a single value of flow is provided, this is the design flow

        else:
            pc_e = np.linspace(100, 1, 100)     # sequence from 100 to 1.
            flow = flow[~np.isnan(flow)] # remove nan values
            flow_percentiles = np.percentile(flow, q = np.linspace(1, 100, 100))        # percentiles to compute, 1:100
            flowduration_curve = {'Flow': flow_percentiles, 'Percent_Exceedance':pc_e}      # Flow duration curve
            design_flow = float(flowduration_curve['Flow'][flowduration_curve['Percent_Exceedance'] == pe])     # flow for the selected percent of excedante
            turbine.flowduration_curve = pd.DataFrame(data = flowduration_curve)
        
        turbine.design_flow = design_flow       # Update
        turbine.pctime_runfull = pe     # Update
        


if __name__ == "__main__":

    turbine_parameters = TurbineParameters(turbine_type = None, flow= 90, head= 200, design_flow = 100, 
                                           rated_power= None, system_efficiency = None,
                                           Rm= None, pctime_runfull= None, generator_efficiency = None,
                                           flow_column= None, pelton_n_jets= None,
                                           hk_blade_diameter= None, hk_blade_heigth= None, hk_blade_type= None, hk_swept_area= None)  # Initialize a TurbinePower instance
    
    # # Cross-Flow turbine
    turb = CrossFlowTurbine()
    turb.turbine_calculator(turbine = turbine_parameters)
    print("\nCrossFlow")
    print("\nEfficiency",turbine_parameters.turbine_efficiency)

    turbine_parameters = TurbineParameters(turbine_type = None, flow= 90, head= 200, design_flow = 100, 
                                           rated_power= None, system_efficiency = None, Rm= None, pctime_runfull= None, 
                                           generator_efficiency = None,
                                           flow_column= None, pelton_n_jets= None,
                                           hk_blade_diameter= None, hk_blade_heigth= None, hk_blade_type= None, hk_swept_area= None)  # Initialize a TurbinePower instance
    # # Pelton turbine
    turb = PeltonTurbine()
    turb.turbine_calculator(turbine = turbine_parameters)
    print("\nPelton")
    print("\nEfficiency",turbine_parameters.turbine_efficiency)

    turbine_parameters = TurbineParameters(turbine_type = None, flow= 90, head= 200, design_flow = 100, 
                                           rated_power= None, system_efficiency = None,
                                           Rm= None, pctime_runfull= None, generator_efficiency = None,
                                           flow_column= None, pelton_n_jets= None,
                                           hk_blade_diameter= None, hk_blade_heigth= None, hk_blade_type= None, hk_swept_area= None)  # Initialize a TurbinePower instance
    # Turgo turbine
    turb = TurgoTurbine()
    turb.turbine_calculator(turbine = turbine_parameters)
    print("\nTurgo")
    print("\nEfficiency",turbine_parameters.turbine_efficiency)

    turbine_parameters = TurbineParameters(turbine_type = None, flow= 90, head= 200, design_flow = 100, 
                                           rated_power= None, system_efficiency = None,
                                           Rm= None, pctime_runfull= None, generator_efficiency = None,
                                           flow_column= None, pelton_n_jets= None,
                                           hk_blade_diameter= None, hk_blade_heigth= None, hk_blade_type= None, hk_swept_area= None)  # Initialize a TurbinePower instance
    # Propellor Turbine
    turb = PropellorTurbine()
    turb.turbine_calculator(turbine = turbine_parameters)
    print("\nPropellor")
    print("\nEfficiency",turbine_parameters.turbine_efficiency)

    turbine_parameters = TurbineParameters(turbine_type = None, flow= 90, head= 200, design_flow = 100, 
                                           rated_power= None, system_efficiency = None,
                                           Rm= None, pctime_runfull= None, generator_efficiency = None,
                                           flow_column= None, pelton_n_jets= None,
                                           hk_blade_diameter= None, hk_blade_heigth= None, hk_blade_type= None, hk_swept_area= None)  # Initialize a TurbinePower instance
    # Kaplan Turbine
    turb = KaplanTurbine()
    turb.turbine_calculator(turbine = turbine_parameters)
    print("\nKaplan")
    print("\nEfficiency",turbine_parameters.turbine_efficiency)
 
    turbine_parameters = TurbineParameters(turbine_type = None, flow= 90, head= 200, design_flow = 100, 
                                           rated_power= None, system_efficiency = None,
                                           Rm= None, pctime_runfull= None, generator_efficiency = None,
                                           flow_column= None, pelton_n_jets= None,
                                           hk_blade_diameter= None, hk_blade_heigth= None, hk_blade_type= None, hk_swept_area= None)  # Initialize a TurbinePower instance
    # Francis Turbine
    turb = FrancisTurbine()
    turb.turbine_calculator(turbine = turbine_parameters)
    print("\nFrancis")
    print("\nEfficiency",turbine_parameters.turbine_efficiency)