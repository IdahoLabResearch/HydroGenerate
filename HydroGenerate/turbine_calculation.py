"""
03-2023
@authors: Camilo J. Bastidas Pacheco, J. Gallego-Calderon, Soumyadeep Nag, MITRB

This module handles turbine selection and efficiency calculation.

Overview
--------
- Selects a feasible turbine type from head/flow via polygon regions.
- Computes turbine efficiencies for Pelton, Turgo, Francis, Kaplan, Propeller,
  Crossflow, and hydrokinetic types across a flow range around design flow.
- Provides helpers for runner sizing and design-flow selection from a flow
  duration curve (percent exceedance).

Expected Inputs
---------------
Most functions receive a `turbine` object with (at minimum):
- head : float
- flow : float or array-like
- design_flow : float
- pelton_n_jets : int or None
- Rm : float or None
- pctime_runfull : float or None
- hk_blade_type, hk_blade_diameter, hk_blade_heigth : optional for hydrokinetic

Notes
-----
- Units must be used consistently (SI or US) across `head` and `flow`.
- Selection polygons assume SI units (head in m, flow in m³/s).
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from numbers import Number
import math
from shapely.geometry import Point
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
   

max_flow_turbine = 1      # multiplier for the maximum flow that can be passed through a turbine

# Turbine Parameters
class TurbineParameters:
    """
    Container for turbine inputs and computed attributes.

    Parameters
    ----------
    turbine_type : str or None
        One of {"Hydrokinetic","Francis","Propellor","Pelton","Turgo","CrossFlow"}.
    flow : float or pandas.Series or numpy.ndarray
        Flow (cfs or m³/s). Use a scalar for single-point design calculations.
    design_flow : float
        Design flow (cfs or m³/s).
    flow_column : str or None
        If `flow` is a DataFrame, column name containing the flow series.
    head : float
        Hydraulic head (ft or m).
    rated_power : float or None
        Rated power (kW).
    system_efficiency : float or None
        Overall system efficiency in [0, 1].
    generator_efficiency : float or None
        Generator efficiency in [0, 1] (default 0.98 if set upstream).
    Rm : float or None
        Manufacturer/design coefficient; if None defaults to 4.5.
    pctime_runfull : float or None
        Percent of time the turbine runs at full flow (0–100).
    pelton_n_jets : int or None
        Number of jets for Pelton turbines (default 3 if None).
    hk_blade_diameter : float or None
        Hydrokinetic rotor/blade diameter (m).
    hk_blade_heigth : float or None
        Hydrokinetic blade height (m) for Darrieus types.
    hk_blade_type : str or None
        {'ConventionalRotor','H-DarrieusRotor','DarrieusRotor'}.
    hk_swept_area : float or None
        Hydrokinetic swept area (m²), computed if not provided.

    Attributes
    ----------
    Rm : float
        Manufacturer/design coefficient (defaults to 4.5 when None).
    design_efficiency : float or None
        Efficiency at design flow (set by calculators when applicable).
    turbine_flow : numpy.ndarray or None
        Flow array used in efficiency curves (may be filled by helpers).
    dataframe_output : pandas.DataFrame or None
        Optional results table.
    runner_diameter : float or None
        Runner diameter (m) for reaction turbines.

    """    

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
    """
    Select a feasible turbine type from head/flow using polygon regions.

    Parameters
    ----------
    hp_params : TurbineParameters
        Must provide `head` (m) and `design_flow` (m³/s).

    Raises
    ------
    ValueError
        If the (flow, head) point falls outside all supported turbine regions.

    Side Effects
    ------------
    Updates
        - `hp_params.turbine_type` with the closest (centroid distance) match.
        - `hp_params.turbine_type_dict` with {turbine: distance} for all hits.

    Notes
    -----
    The polygon limits are specified in SI units (m, m³/s).
    """

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

# Flow range calculation
class FlowRange():
    """
    Utility to expand a scalar flow into a range for efficiency curves.
    """

    def flowrange_calculator(self, turbine):
        """
        If `turbine.flow` is scalar, create a flow vector from 50% to
        `max_flow_turbine` (default 100%) of that scalar.

        Parameters
        ----------
        turbine : TurbineParameters
            Must have scalar `flow`.

        Side Effects
        ------------
        Overwrites `turbine.flow` with an array of 18 values.

        """    
        
        if isinstance(turbine.flow, Number):
            range = np.linspace(0.5, max_flow_turbine, 18) # the values are %
            turbine.flow = turbine.flow * range

# Turbine efficiency and sizing

# Runner diameter for reaction turbines
class ReactionTurbines():      
    """
    Runner sizing utilities for reaction turbines.
    """

    def runnersize_calculator(self, design_flow):  
        """
        Estimate runner throat diameter for reaction turbines.

        Parameters
        ----------
        design_flow : float
            Design discharge (m³/s).

        Returns
        -------
        float
            Runner throat diameter (m).

        Notes
        -----
        Uses piecewise k coefficient (0.41 for Qd>23 m³/s, else 0.46) and
        d = k * Qd**0.473.
        """

        if design_flow > 23: # d > 1.8 - The formula in the document has an 'undefined' area
            k = 0.41
        else:
            k = 0.46
        d = k * design_flow**0.473     # runner throat diameter in m
        return d
    
# Functions to calculate turbine efficiency by turbine type (CANMET Energy Technology Center, 2004)
class Turbine(ABC):   
    """
    Abstract base class for turbine efficiency calculators.
    """

    @abstractmethod
    def turbine_calculator(self, turbine):
        """
        Compute efficiency curve and update turbine attributes.

        Parameters
        ----------
        turbine : TurbineParameters
            Input/output container with at least `head`, `design_flow`,
            `flow` or `turbine_flow`, and optional coefficients.
        """

        pass

class FrancisTurbine(Turbine):
    """
    Francis turbine efficiency calculation (CANMET, 2004).
    """

    def turbine_calculator(self, turbine):   
        """
        Populate `turbine.turbine_efficiency` across a flow range around Qd.

        Parameters
        ----------
        turbine : TurbineParameters
            Requires `head`, `design_flow`, `Rm`. Creates/uses a flow range.

        Side Effects
        ------------
        Updates:
        - `turbine.turbine_efficiency` (numpy.ndarray in [0,1]).
        - `turbine.runner_diameter` (m).

        Notes
        -----
        Uses specific speed and runner-size adjustments to peak efficiency, and
        piecewise relations above/below peak-flow `Qp`.
        """        

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
    """
    Kaplan turbine efficiency calculation (CANMET, 2004).
    """

    def turbine_calculator(self, turbine):
        """
        Compute efficiency across flow range; clip negatives to zero.

        Parameters
        ----------
        turbine : TurbineParameters
            Requires `head`, `design_flow`, `Rm`.

        Side Effects
        ------------
        Updates `turbine.turbine_efficiency` and `turbine.runner_diameter`.
        """

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
    """
    Propeller turbine efficiency calculation (CANMET, 2004).
    """
      
    def turbine_calculator(self, turbine):
        """
        Compute efficiency across flow range; clip negatives to zero.

        Parameters
        ----------
        turbine : TurbineParameters
            Requires `head`, `design_flow`, `Rm`.

        Side Effects
        ------------
        Updates `turbine.turbine_efficiency` and `turbine.runner_diameter`.
        """

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
    """
    Pelton turbine efficiency calculation (CANMET, 2004).
    """

    def turbine_calculator(self, turbine): 
        """
        Compute Pelton efficiency across the flow range.

        Parameters
        ----------
        turbine : TurbineParameters
            Requires `head`, `design_flow`; uses `pelton_n_jets` (default 3).

        Side Effects
        ------------
        Updates `turbine.turbine_efficiency` and `turbine.runner_diameter`.
        """        

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
    """
    Turgo turbine efficiency approximated from Pelton minus 0.03.
    """

    def turbine_calculator(self, turbine):
        """
        Compute Turgo efficiency by offsetting Pelton efficiency.

        Parameters
        ----------
        turbine : TurbineParameters
            Requires `head`, `design_flow`.

        Side Effects
        ------------
        Updates `turbine.turbine_efficiency` (values clipped at 0).
        """

        PeltonTurbine().turbine_calculator(turbine)       # Calculate Pelton efficiency
        turbine.turbine_efficiency = turbine.turbine_efficiency - 0.03        # Pelton efficiency - 0.03
        turbine.turbine_efficiency = np.where(turbine.turbine_efficiency <= 0 , 0, turbine.turbine_efficiency)        # Correct negative efficiencies 
          
class CrossFlowTurbine(Turbine):
    """
    Crossflow turbine efficiency calculation (empirical relation).
    """
      
    def turbine_calculator(self, turbine):
        """
        Compute crossflow efficiency across the flow range.

        Parameters
        ----------
        turbine : TurbineParameters
            Requires `design_flow`; uses empirical relation vs Qd and Q.

        Side Effects
        ------------
        Updates `turbine.turbine_efficiency` (values clipped at 0).
        """

        Qd = turbine.design_flow 
        FlowRange().flowrange_calculator(turbine= turbine)      # generate a flow range from 60% to 120% of the flow given
        Q = turbine.turbine_flow
        turbine.turbine_efficiency = 0.79 - 0.15 *((Qd - Q) / Qd) - 1.37 * ((Qd - Q) / Q)**14     # Efficiency (e_q)
        turbine.turbine_efficiency = np.where(turbine.turbine_efficiency <= 0 , 0, turbine.turbine_efficiency)        # Correct negative efficiencies

class Hydrokinetic_Turbine(Turbine):
    """
    Hydrokinetic turbine swept-area setup and related parameters.
    """    

    def turbine_calculator(self, turbine):
        """
        Ensure hydrokinetic blade geometry and swept area are populated.

        Parameters
        ----------
        turbine : TurbineParameters
            Uses/updates:
            - hk_blade_type : {'ConventionalRotor','H-DarrieusRotor','DarrieusRotor'}
            - hk_blade_diameter : float (m)
            - hk_blade_heigth : float (m) when required
            - hk_swept_area : float (m²)

        Side Effects
        ------------
        Sets defaults when missing and updates `hk_swept_area`.
        """

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
    """
    Abstract base for design-flow selection strategies.
    """

    @abstractmethod
    def designflow_calculator(self, turbine):
        """
        Compute and update `turbine.design_flow`.
        """

        pass

# Desing flow selected from the flow duration curve for a percentage of exceedance
class PercentExceedance(DesignFlow):
    """
    Design flow based on a target percent exceedance from a flow duration curve.
    """

    def designflow_calculator(self, turbine):
        """
        Select design flow from the flow duration curve at target exceedance.

        Parameters
        ----------
        turbine : TurbineParameters
            Uses:
            - pctime_runfull : float or None
                Target % exceedance (rounded to nearest integer). If None,
                defaults to 30%.
            - flow : array-like or scalar
                If array-like, computes the flow duration curve; if scalar,
                uses it directly as `design_flow`.

        Side Effects
        ------------
        Updates:
        - `turbine.design_flow`
        - `turbine.pctime_runfull` (rounded int)
        - `turbine.flowduration_curve` (pandas.DataFrame) when series provided.
        """

        pe = turbine.pctime_runfull     # percentage of time a turbine is running full
        flow = turbine.flow     # user-entered flow
        
        if pe is not None:      # user defined percent of time a turbine is running full. pe ∝ 1/(design flow)
            pe = np.round(pe)       # round to find in 'flow_percentiles' list
        else: 
            pe = 30     # default value for the percent of time a turine will run full 

        if isinstance(flow, Number):
            design_flow = flow      # when a single value of flow is provided, this is the design flow

        else:
            pc_e = np.linspace(100, 0, 101)     # sequence from 100 to 1.
            flow = flow[~np.isnan(flow)] # remove nan values
            flow_percentiles = np.percentile(flow, q = np.linspace(0, 100, 101))        # percentiles to compute, 1:100
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