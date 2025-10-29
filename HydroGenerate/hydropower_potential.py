"""
03-2023
@author: Camilo J. Bastidas Pacheco, MITRB, J. Gallego-Calderon

This module calculates hydropower potential for different types of installations.

Overview
--------
- Core pipeline wiring across flow preprocessing, hydraulic losses, turbine
  selection/efficiency, energy/revenue, and (optional) costs.
- Supports BASIC, DIVERSION (run-of-river), and HYDROKINETIC modes.
- Handles unit conversion (US↔SI) and DataFrame vs scalar inputs.

Key Constants
-------------
rho : float
    Water density (kg/m³).
g : float
    Acceleration of gravity (m/s²).

Notes
-----
- US units are converted to SI internally for calculations.
- For DIVERSION projects, turbine choice and efficiency curves depend on
  (head, design_flow) in SI units.
"""

import numpy as np
import math
# from numpy.core.fromnumeric import mean
# from numpy.lib.function_base import median
import pandas as pd
from datetime import datetime
import os
from abc import ABC, abstractmethod
from numbers import Number
from math import exp

from HydroGenerate.hydraulic_processing import *
from HydroGenerate.turbine_calculation import *
from HydroGenerate.flow_preprocessing import *
from HydroGenerate.summary_results import *

# Constant definition / unit conversion
rho = 1000 # water density in Kg/m^3
g = 9.81 # acceleration of gravity (m/s^2)
cfs_to_cms = 0.0283168 # 1 cubic feet per second to cubic meter per second
ft_to_m = 0.3048 # 1 feet to meters
nu = 0.0000011223 # Kinematic viscosity of water (m2/s) at 60F (~15.6C) - prevalent stream water temperature 
wholesale_elecprice_2023 = 0.0582       # Weigthed average wholesale electricity price in 2023 ($/kWh): https://www.eia.gov/electricity/wholesale/

# Economic Parameters
class EconomicParameters:
    """
    Container for simple economic inputs.

    Parameters
    ----------
    resource_category : str or None
        Category for cost model (e.g., 'Non-PoweredDam', 'NewStream-reachDevelopment').
    capacity_factor : float or None
        Capacity factor as a fraction (0–1) or percent (0–100) depending on use;
        see revenue calculators for interpretation.
    electricity_sell_price : float or None
        Electricity price ($/kWh). If None, a 2023 wholesale default is used.
    n_operation_days : int or None
        Days per year the plant operates (<= 365) when capacity factor is not supplied.

    Attributes
    ----------
    resource_category : str or None
    electricity_sell_price : float or None
    capacity_factor : float or None
    n_operation_days : int or None
    """

    def __init__(self, resource_category, 
                 capacity_factor, electricity_sell_price, n_operation_days):

        '''
        This class initializes the calculation of hydropower potential for a specific turbine type
        Input variables:
        - sell_price: Selects the particular turbine based on available head

        Returns: None
        '''

        self.resource_category = resource_category      # Options: 'Non-PoweredDam', 'NewStream-reachDevelopment', 
        self.electricity_sell_price = electricity_sell_price       # selling price of electricity, $/kWh
        self.capacity_factor = capacity_factor      # capcity factor, %
        self.n_operation_days = n_operation_days        # number of days the plant operates in a year

# Function to combine multiple instances
def merge_instances(ob1, *args):
    """
    Merge attributes from multiple objects into the first object.

    Parameters
    ----------
    ob1 : object
        Target object to be updated in-place.
    *args : object
        One or more objects whose `__dict__` will be merged into `ob1`.

    Returns
    -------
    object
        The updated `ob1` reference.

    Notes
    -----
    Later objects in `*args` may overwrite attributes from earlier ones.
    """

    for d in args:
        ob1.__dict__.update(d.__dict__)
    return ob1

# function to calculated head 
def calculate_head(rated_flow, rated_power):
    """
    Compute net head (m) from rated flow and power.

    Parameters
    ----------
    rated_flow : float
        Flow at rated conditions (m³/s).
    rated_power : float
        Electrical power (W).

    Returns
    -------
    float
        Net head in meters computed as `P / (rho * g * Q)`.
    """

    return rated_power/(rho*g*rated_flow) 

# Function to check if a pandas dataframe is used and extract flow values
def pd_checker(flow, flow_column):
    """
    Normalize flow input and detect pandas DataFrame usage.

    Parameters
    ----------
    flow : float or array-like or pandas.DataFrame
        Flow input. If DataFrame, must include the column named by `flow_column`.
    flow_column : str or None
        Column name containing flow values when `flow` is a DataFrame.

    Returns
    -------
    tuple
        (flow_data, pandas_dataframe) where:
        - flow_data : float or numpy.ndarray
            Scalar/array extracted from the DataFrame or the original value.
        - pandas_dataframe : bool
            True if DataFrame input was used.

    Raises
    ------
    ValueError
        If `flow` is a DataFrame but `flow_column` is not provided.
    """

    pandas_dataframe = False        # flag to track if a pandas dataframe is used outside of this function
    
    if isinstance(flow, pd.DataFrame):      # check if a pandas dataframe is used
            
        if flow_column is None:
            raise ValueError("When using a pandas dataframe, users must indicate what column" \
                             " has the flow values using 'flow_column = \"Name\"'")
        else:         
            flow_data = flow[flow_column].to_numpy()        # Extract flow from a pandas dataframe column
            pandas_dataframe = True
        
    else:       # if flow is not a pandas dataframe
        flow_data = flow

    return flow_data, pandas_dataframe

# Unit transformation
class Units:
    """
    Convert selected attributes on `self` from US to SI units.

    Side Effects
    ------------
    Converts in place (when present):
    - flow, design_flow, minimum_turbineflow : cfs → m³/s
    - head, head_loss, penstock_length, hk_blade_diameter, hk_blade_heigth : ft → m
    - channel_average_velocity : ft/s → m/s
    - penstock_diameter : ft → m
    """

    def us_to_si_conversion(self):
        """
        Convert selected attributes on `self` from US to SI units.

        Side Effects
        ------------
        Converts in place (when present):
        - flow, design_flow, minimum_turbineflow : cfs → m³/s
        - head, head_loss, penstock_length, hk_blade_diameter, hk_blade_heigth : ft → m
        - channel_average_velocity : ft/s → m/s
        - penstock_diameter : ft → m
        """

        if self.flow is not None:
            self.flow = self.flow * cfs_to_cms      # cfs to m3/s

        if self.design_flow is not None:
            self.design_flow = self.design_flow * cfs_to_cms        # cfs to m3/s

        if self.minimum_turbineflow is not None:
            self.minimum_turbineflow = self.minimum_turbineflow * cfs_to_cms        # cfs to m3/s

        if self.head is not None:
            self.head = self.head * ft_to_m     # ft to m

        if self.head_loss is not None:
            self.head_loss = self.head_loss * ft_to_m       # ft to m

        if self.penstock_length is not None:
            self.penstock_length = self.penstock_length * ft_to_m       # ft to m

        if self.channel_average_velocity is not None:
            self.channel_average_velocity = self.channel_average_velocity * ft_to_m       # ft to m

        if self.penstock_diameter is not None:
            self.penstock_diameter = self.penstock_diameter * ft_to_m       # ft/s to m/s

        if self.hk_blade_diameter is not None:
            self.hk_blade_diameter= self.hk_blade_diameter * ft_to_m       # ft to m

        if self.hk_blade_heigth is not None:
            self.hk_blade_heigth = self.hk_blade_heigth * ft_to_m       # ft to m

    def si_to_us_conversion(self):
        """
        Convert selected attributes on `self` from SI to US units.

        Side Effects
        ------------
        Converts in place (when present):
        - flow, turbine_flow, design_flow, minimum_turbineflow : m³/s → cfs
        - dataframe_output['turbine_flow_cfs'] : m³/s → cfs
        - head, head_loss, penstock_design_headloss, net_head, max_headloss_allowed,
          penstock_length, penstock_diameter, hk_blade_diameter, hk_blade_heigth,
          runner_diameter : m (or m-derived) → ft
        - channel_average_velocity : m/s → ft/s

        Notes
        -----
        Net head is only converted for non-hydrokinetic modes.
        """

        if self.flow is not None:
            self.flow = self.flow / cfs_to_cms      # m3/s tp cfs

        if self.turbine_flow is not None:
            self.turbine_flow = self.turbine_flow / cfs_to_cms      # m3/s tp cfs

        if self.design_flow is not None:
            self.design_flow = self.design_flow / cfs_to_cms        # m3/s tp cfs

        if self.minimum_turbineflow is not None:
            self.minimum_turbineflow = self.minimum_turbineflow / cfs_to_cms        # cfs to m3/s

        if self.dataframe_output is not None:
            self.dataframe_output['turbine_flow_cfs'] =  self.dataframe_output['turbine_flow_cfs'] / cfs_to_cms        # m3/s tp cfs

        if self.head is not None:
            self.head = self.head / ft_to_m     # m to ft 

        if self.head_loss is not None:
            self.head_loss = self.head_loss / ft_to_m       # m to ft

        if self.penstock_design_headloss is not None:
            self.penstock_design_headloss = self.penstock_design_headloss / ft_to_m       # m to ft

        if self.hydropower_type != 'Hydrokinetic':
            if self.net_head is not None:
                self.net_head = self.net_head / ft_to_m #       m to ft
    
        if self.max_headloss_allowed is not None:
            self.max_headloss_allowed = self.max_headloss_allowed / ft_to_m     # m to ft 

        if self.penstock_length is not None:
            self.penstock_length = self.penstock_length / ft_to_m       # m to ft 

        if self.penstock_diameter is not None:
            self.penstock_diameter = self.penstock_diameter / ft_to_m       # m to ft

        if self.channel_average_velocity is not None:
            self.channel_average_velocity = self.channel_average_velocity / ft_to_m       # m/s to ft/s

        if self.hk_blade_diameter is not None:
            self.hk_blade_diameter= self.hk_blade_diameter / ft_to_m       # m to ft

        if self.hk_blade_heigth is not None:
            self.hk_blade_heigth = self.hk_blade_heigth / ft_to_m       # m to ft

        if self.runner_diameter is not None:
            self.runner_diameter = self.runner_diameter /  ft_to_m       # m to ft

# Hydropower calculation
class Hydropower(ABC):
    """
    Abstract base class for hydropower calculators.
    """

    @abstractmethod
    def hydropower_calculation(self, hp_params):
        """
        Compute hydropower for the given parameter container.

        Parameters
        ----------
        hp_params : object
            Parameter object updated in place with results.
        """

        pass

# Basic calculation
class Basic(Hydropower):      
    def hydropower_calculation(self, hp_params):
        """
        Solve for the missing variable among {flow, head, rated_power} and compute power.

        Parameters
        ----------
        hp_params : object
            Must supply at least two of {flow (m³/s), head (m), rated_power (kW)}.
            May include `head_loss` (m) and `system_efficiency` (0–1).

        Raises
        ------
        ValueError
            If fewer than two of {flow, head, rated_power} are provided.

        Side Effects
        ------------
        Updates `hp_params.flow`, `hp_params.head`, `hp_params.rated_power`,
        `hp_params.net_head`, `hp_params.penstock_design_headloss` as needed.

        Notes
        -----
        Default overall efficiency is 0.85 if not provided.
        Power formula: `P[kW] = n * rho * g * Q * H / 1000`.
        """

        flow = hp_params.flow       # flow, m3/s
        head = hp_params.head       # head, m
        rated_power = hp_params.rated_power     # rated power, KW
        system_efficiency = hp_params.system_efficiency     # system afficiency
                
        if len([i for i in [flow, head, rated_power] if i is None]) > 1:
            raise ValueError('Missing inputs. Users must provide flow and head to compute power, flow and power' \
                             ' to compute head, or power and head to compute flow')

        # Overal system efficiency
        if system_efficiency is not None:
            n = system_efficiency
        else: 
            n = 0.85

        # Compute head
        if head is not None: 
            if hp_params.head_loss is not None:
                h = head - hp_params.head_loss
            else:
                h = head
        else:
            P = rated_power
            h = P * 1000 / (n * g * rho * flow) # Net head, in m
            hp_params.head = h      # update

        # Compute Flow 
        if flow is None:
           P = rated_power
           flow = P  * 1000 / (n * g * rho * h)
           hp_params.flow = flow      # update

        # Compute hydropower
        if rated_power is None:
            P = n * g * rho * flow * h / 1000 # HP potential in kilowatts
            hp_params.rated_power = P      # update

        hp_params.penstock_design_headloss = None        # update - for using the same Unit function
        hp_params.net_head = h        # update - for using the same Unit function
     
# Diversion - Run-of-river
class Diversion(Hydropower):
    def hydropower_calculation(self, hp_params):
        """
        Run full run-of-river (diversion) workflow from design flow to power.

        Parameters
        ----------
        hp_params : object
            Requires:
            - flow/design_flow and head (SI inside the routine)
            - penstock settings if head-loss calculation is enabled
            - turbine selection inputs (e.g., Rm, pelton_n_jets)
            - flags for annual/major maintenance when time series present

        Raises
        ------
        ValueError
            If unsupported turbine or head-loss method is requested, or when
            required values for head-loss calculations are missing.

        Side Effects
        ------------
        - Selects turbine type and computes efficiency curve.
        - Applies flow min/max limits, maintenance outages (if flagged).
        - Computes head loss (design and time series) for DW/HW as configured.
        - Updates rated power, per-step power, net head, and related fields.

        Notes
        -----
        Turbine types supported: Kaplan, Francis, Pelton, Turgo, Crossflow, Propeller.
        Head-loss methods supported: Darcy–Weisbach, Hazen–Williams.
        """

        # Calculate design flow
        if hp_params.design_flow is None:
            PercentExceedance().designflow_calculator(hp_params)

        # Select turbine type
        if hp_params.turbine_type is None:
            turbine_type_selector(hp_params)        # Turbine type

        # Add flow range for turbine evaluation if a sinlge flow value is given
        FlowRange().flowrange_calculator(hp_params)

        # Set max flow to the design flow and minimum flow passing throught the turbine
        FlowPreProcessing().max_turbineflow_checker(hp_params)      # max flow check
        FlowPreProcessing().min_turbineflow_checker(hp_params)      # min flow check

        # Run major maintenance and annual maintenance
        if hp_params.pandas_dataframe: 
            if hp_params.major_maintenance_flag:            # Major
                FlowPreProcessing().major_maintenance_implementer(hp_params)

            if hp_params.annual_maintenance_flag:           # Annual
                FlowPreProcessing().annual_maintenance_implementer(hp_params)
     
        # Turbine parameters calculation by turbine type
        turbine_type = hp_params.turbine_type.upper()

        # Check if a turbine type is acceped by HG
        tt_list = ['KAPLAN', 'FRANCIS', 'PELTON', 'TURGO','CROSSFLOW', 'PROPELLER']
        
        if turbine_type not in tt_list:
            raise ValueError('The following turbine types are currently supported in HydroGenerate', tt_list)
        
        if turbine_type == 'KAPLAN':
                KaplanTurbine().turbine_calculator(hp_params)

        elif turbine_type == 'FRANCIS':
                FrancisTurbine().turbine_calculator(hp_params)

        elif turbine_type == 'PELTON':
                PeltonTurbine().turbine_calculator(hp_params)

        elif turbine_type == 'TURGO':
                TurgoTurbine().turbine_calculator(hp_params)

        elif turbine_type == 'CROSSFLOW':
                CrossFlowTurbine().turbine_calculator(hp_params)
            
        elif turbine_type == 'PROPELLER':
                PropellerTurbine().turbine_calculator(hp_params)

        # Head loss calculation 
        if hp_params.penstock_headloss_calculation: # If head loss in the penstock are calculated

            if hp_params.penstock_length is None:
                raise ValueError("Penstock length is required for head loss computations if" \
                                 " penstock_headloss_calculation is True")
            
            if hp_params.penstock_headloss_method == None:
                hp_params.penstock_headloss_method = 'DARCY-WEISBACH'

            hl_method = hp_params.penstock_headloss_method.upper()

            # Check if a turbine type is acceped by HG
            hl_list = ['DARCY-WEISBACH', 'HAZEN-WILLIAMS']
        
            if hl_method not in hl_list:
                raise ValueError('The following head loss methods are currently supported in HydroGenerate', hl_list)

            if hl_method == 'DARCY-WEISBACH': # Darcy-Weisbach
                DarcyWeisbach().penstock_headloss_calculator(hp_params)       # head loss at design parameters
                DarcyWeisbach().penstock_headloss_calculator_ts(hp_params)        # head loss for a range of flow values

            elif hl_method == 'HAZEN-WILLIAMS': # Hazen-Williams
                HazenWilliamns().penstock_headloss_calculator(hp_params)       # head loss at design parameters
                HazenWilliamns().penstock_headloss_calculator_ts(hp_params)        # head loss for a range of flow values

        else:  
            hp_params.head_loss = 0
            hp_params.penstock_headloss_method = None        # penstock head losses are not calculated

        # Generator efficiency
        if hp_params.generator_efficiency is None:
            hp_params.generator_efficiency = 0.98       # Default
        else:
             hp_params.generator_efficiency =  hp_params.generator_efficiency / 100 # percent to proportion

        # remove negatives and > 1 from turbine effiency
        hp_params.turbine_efficiency = np.where(hp_params.turbine_efficiency < 0, 0, hp_params.turbine_efficiency) # remove negatives
        hp_params.turbine_efficiency = np.where(hp_params.turbine_efficiency > 1, 1, hp_params.turbine_efficiency) # remove > 1

        
        n = hp_params.turbine_efficiency * hp_params.generator_efficiency       # overal system efficiency
        n_max = np.nanmax(hp_params.turbine_efficiency) * hp_params.generator_efficiency      # maximum system efficiency
        
        if hp_params.penstock_design_headloss:        # if design head loss was calculated for penstock only
            hd = hp_params.head - hp_params.penstock_design_headloss  # net hydraulic head at design flows

        else:
            hd = hp_params.head

        h = hp_params.head - hp_params.head_loss        # net hydraulic head
        Qd = hp_params.design_flow      # Design flow
        Q = hp_params.turbine_flow      # Flow passing by the turbine

        P = n_max * g * rho * Qd * hd / 1000        # HP potential in kilowatts for design flow
        hp_params.rated_power = P       # update - Kw

        hp_params.power = n * g * rho * Q * h / 1000        # HP potential in kilowatts
        hp_params.net_head = hd        # update

        hp_params.head = h        # update
        
class Hydrokinetic(Hydropower):
    def hydropower_calculation(self, hp_params):
        """
        Compute hydrokinetic power from swept area and channel velocity.

        Parameters
        ----------
        hp_params : object
            Uses/updates:
            - system_efficiency : percent if not None, otherwise defaults to 59 (Betz limit)
            - hk_swept_area or geometry fields to compute it
            - channel_average_velocity : m/s

        Side Effects
        ------------
        Updates `hp_params.rated_power` (kW).
        """

        # System efficiency
        if hp_params.system_efficiency:         # if the user provides an efficiency value
            n = hp_params.system_efficiency

        else:       # If the efficiency is not provided, HG will caclulate the maximum HK potential 
            n = hp_params.system_efficiency = 59        # Efficiency [percentage] - Betz Limit - Maximum 

        n = n /100      # efficiency 

        # Area of blades
        if hp_params.hk_swept_area is None:     # If the user does not input swept area of blades
            Hydrokinetic_Turbine().turbine_calculator(hp_params)        # calculate swept area of blades
        
        A = hp_params.hk_swept_area     # Swept Area of blades, m2
        V = hp_params.channel_average_velocity      # cross sectional average velocity m/s

        P = 0.5 * n * rho * A * (V**3) / 1000       # Power in KW
        hp_params.rated_power = P       # update

# Hydropower economic analysis: Cost
class Cost(ABC):
    """
    Abstract base for cost models.
    """

    @abstractmethod
    def cost_calculation(self, hp_params):
        """
        Compute and update capital and O&M cost fields on `hp_params`.
        """

        pass

# ORNL_HBCM methods obtained from: https://info.ornl.gov/sites/publications/files/Pub58666.pdf
class ONRL_BaselineCostModeling_V2(Cost):
    def cost_calculation(self, hp_params):
        """
        Estimate initial capital cost (ICC) and annual O&M via ORNL HBCM (2014).

        Parameters
        ----------
        hp_params : object
            Requires:
            - rated_power : float (kW)
            - net_head : float (m)
            - resource_category : str (mapped to model cases)

        Returns
        -------
        None

        Side Effects
        ------------
        Sets:
        - `hp_params.icc` : float
            ICC in million 2014 USD.
        - `hp_params.annual_om` : float
            Annual O&M in million 2014 USD (min of model curve and 2.5% of ICC
            for categories other than GENERATORREWIND).

        Notes
        -----
        Internally converts head to ft and power to MW per model definitions.
        """

        P = hp_params.rated_power / 1000       # rated power, mW
        H = hp_params.net_head / ft_to_m        # net head, ft

        if hp_params.resource_category is None:
            hp_params.resource_category = 'NEWSTREAM-REACH'

        res_category = hp_params.resource_category.upper()

        rc_list = ['NEWSTREAM-REACH', 'NON-POWEREDDAM', 'NPD', 'CANALCONDUIT','PSH_ EXISTINGINFRAESTRUCTURE',
                    'PSH_GREENFIELD', 'UNITADDITION', 'GENERATORREWIND']
        
        if res_category not in rc_list:
            raise ValueError('The resource category must be in the following list', rc_list)

        # icc = initial capital cost = f(H, P) in $2014. H in ft, P in MW
        if hp_params.resource_category == 'NEWSTREAM-REACH':
            icc = 9605710 * 𝑃**0.977 * 𝐻**-0.126        # New Stream-reach Development
           
        if res_category == 'NON-POWEREDDAM':
             icc = 11489245 * P**0.976 * 𝐻**-0.240        # Non-Powered Dam

        if res_category == 'NPD':
             icc = 11489245 * P**0.976 * 𝐻**-0.240        # Non-Powered Dam

        if res_category == 'CANALCONDUIT':
            icc = 9297820 * 𝑃**0.810 * 𝐻**-0.10     # Canal / Conduit Project

        if res_category == 'PSH_ EXISTINGINFRAESTRUCTURE':
            icc = 3008246 * 𝑃 * exp(-0.000460 * P)      # Pumped Storage Hydropower Projects - Existing Infrastructure

        if res_category == 'PSH_GREENFIELD':
            icc = 4882655 * 𝑃 * exp(-0.000776 * P)      #  Pumped Storage Hydropower Projects - Greenfield Sites

        if res_category == 'UNITADDITION':
            icc = 4163746 * 𝑃**0.741        # Unit Addition Projects

        if res_category == 'GENERATORREWIND':
            icc = 250147 * 𝑃**0.817     # Generator Rewind Projects
        
        icc = icc / 1000000     # icc, million $

        # Annual Operation and Maintennance 
        annual_om = 225417 * 𝑃**0.54 / 1000000 # Annual Operation Maintennance, million $

        # ORNL_HBCM predicts higher costs for smaller plants, the authors sugges using the lesser between Annual OP&M and 2.5% of ICC 
        if res_category != 'GENERATORREWIND':
            if annual_om > 0.025 * icc:
                annual_om = 0.025 * icc

        hp_params.icc = icc     # update. ICC, 2014 million dollar        
        hp_params.annual_om = annual_om     # update, Annual O&M, 2014 million $

# Hydropower economic analysis: evenue
class Revenue(ABC):
    """
    Abstract base for revenue models.
    """

    @abstractmethod
    def revenue_calculation(self, hp_params):
        """
        Compute and update energy and revenue fields on `hp_params`.
        """

        pass

# Constant electricty price for single / multiple values of flow - not a time series
class ConstantEletrictyPrice(Revenue):
     def revenue_calculation(self, hp_params):
        """
        Annual energy/revenue from mean power and capacity factor or days/year.

        Parameters
        ----------
        hp_params : object
            Uses:
            - power : array-like of kW (time series)
            - capacity_factor : float or None
            - n_operation_days : int or None
            - electricity_sell_price : float ($/kWh) or None

        Side Effects
        ------------
        Sets:
        - `hp_params.annual_energy_generated` : float (kWh)
        - `hp_params.annual_revenue` : float (million $)
        - Harmonizes `capacity_factor` and `n_operation_days` when one is given.

        Raises
        ------
        ValueError
            If `n_operation_days` > 365 when capacity factor is not provided.
        """

        mean_power = np.mean(hp_params.power)       # mean of the power provided for a time series of flow

        if hp_params.n_operation_days is None:
            hp_params.n_operation_days = 365

        if hp_params.capacity_factor:
            annual_energy = hp_params.capacity_factor * mean_power * 365        # annual energy generated, killowatt day 
            hp_params.n_operation_days = hp_params.capacity_factor * 365        # update  
        
        else:
            if hp_params.n_operation_days > 365:
                raise ValueError('The number of days in a year a plant operates cannot exceed 365')

            annual_energy = hp_params.n_operation_days * mean_power        # annual energy generatedkillowatt day
            hp_params.capacity_factor = hp_params.n_operation_days * 100/ 365        # update
        
        if  hp_params.electricity_sell_price is None:
             hp_params.electricity_sell_price = wholesale_elecprice_2023       # electricity sell price, defined above

        hp_params.annual_energy_generated = annual_energy * 24      # units from Kw day to KWh
        hp_params.annual_revenue =  hp_params.annual_energy_generated * hp_params.electricity_sell_price / 1000000       # annual revenue, M$

# Constant electricty price for a pandas dataframe with a dateTime index. 
class ConstantEletrictyPrice_pd(Revenue):
    def revenue_calculation(self, hp_params, flow):
        """
        Annual energy/revenue from a time-indexed pandas DataFrame.

        Parameters
        ----------
        hp_params : object
            Uses/updates: power (kW), turbine_flow (m³/s or cfs depending on mode),
            turbine_efficiency (0–1), rated_power (kW), electricity_sell_price ($/kWh).
        flow : pandas.DataFrame
            Time-indexed DataFrame; index frequency determines hourly energy step.

        Side Effects
        ------------
        - Populates `hp_params.dataframe_output` with power/flow/efficiency/energy.
        - Populates `hp_params.annual_dataframe_output` with annual KPIs
          (energy, revenue, capacity factor).

        Notes
        -----
        Capacity factor is clipped to ≤ 1. Hours are computed from index diffs.
        """

        if  hp_params.electricity_sell_price is None:
            hp_params.electricity_sell_price = wholesale_elecprice_2023       # electricity sell price, defined above

        output = flow.copy()
        output['power_kW'] = hp_params.power      # Power, kW
        output['turbine_flow_cfs'] = hp_params.turbine_flow     # Flow passing by the turbine, cfs

        # remove negatives and > 1 from turbine effiency
        hp_params.turbine_efficiency = np.where(hp_params.turbine_efficiency < 0, 0, hp_params.turbine_efficiency) # remove negatives
        hp_params.turbine_efficiency = np.where(hp_params.turbine_efficiency > 1, 1, hp_params.turbine_efficiency) # remove > 1
        
        output['efficiency'] = hp_params.turbine_efficiency     # efficiency 

        hours = flow.index.to_series().diff().values / pd.Timedelta('1 hour')       # time difference in hours
        output['energy_kWh'] = output['power_kW'] * hours       # energy = power * hours (kWh)

        # Generate annual energy, mean efficiency, and flow.
        flow_md = output.groupby([output.index.year]).agg(annual_turbinedvolume_ft3= ('turbine_flow_cfs', 'sum'),
                                                      mean_annual_effienciency = ('efficiency', 'mean'),
                                                      total_annual_energy_KWh = ('energy_kWh', 'sum'))
        
        # flow_md['total_annual_energy_MWh'] = flow_md['total_annual_energy_MWh'] / 1000
        
        flow_md['revenue_M$'] = flow_md['total_annual_energy_KWh'] * hp_params.electricity_sell_price / 1000000  
        flow_md['capacity_factor'] = flow_md['total_annual_energy_KWh'] / (hp_params.rated_power * 8760)        # energy generater / max energy. 1 year = 8760 hours
        flow_md.loc[flow_md['capacity_factor'] > 1, 'capacity_factor'] = 1

        hp_params.dataframe_output = output
        hp_params.annual_dataframe_output = flow_md

# Function to calculate hydropower potential - function users will call 
def calculate_hp_potential(flow= None,
                           head= None, 
                           rated_power= None, 
                           hydropower_type= 'BASIC', 
                           units= 'US',

                           penstock_headloss_method= 'Darcy-Weisbach',
                           design_flow= None, 
                           system_efficiency = None,
                           generator_efficiency= None,
                           turbine_type= None,   
                           head_loss= None, 

                           penstock_headloss_calculation= False,
                           penstock_length= None, 
                           penstock_diameter= None, 
                           penstock_material= None, 
                           penstock_frictionfactor= None,

                           pctime_runfull= None, 
                           max_headloss_allowed= None,
                           turbine_Rm= None,
                           pelton_n_jets= None,
                           flow_column= None,

                           channel_average_velocity= None,
                           hk_blade_diameter= None, 
                           hk_blade_heigth= None, 
                           hk_blade_type= None, 
                           hk_swept_area= None,

                           annual_caclulation = False,
                           resource_category= None, 
                           electricity_sell_price= None,
                           cost_calculation_method= 'ORNL_HBCM',
                           capacity_factor= None, 
                           n_operation_days= None,
                           
                           minimum_turbineflow = None,
                           minimum_turbineflow_percent = None, 
                           annual_maintenance_flag = False,
                           major_maintenance_flag = False): 
    """
    End-to-end hydropower potential calculation and (optionally) revenue/costs.

    Parameters
    ----------
    flow : float or array-like or pandas.DataFrame, optional
        Input flow. If DataFrame, provide `flow_column` with the column name.
    head : float, optional
        Gross head (ft or m depending on `units`).
    rated_power : float, optional
        Rated power (kW). Used with `flow`/`head` to solve missing variables in BASIC.
    hydropower_type : {'BASIC','DIVERSION','HYDROKINETIC'} or None, default 'BASIC'
        Calculation mode. If None, skips hydro calc but enables cost if requested.
    units : {'US','SI'}, default 'US'
        Input/output unit system. Internally converted to SI for calculations.
    penstock_headloss_method : {'Darcy-Weisbach','Hazen-Williams'}, default 'Darcy-Weisbach'
        Method for head-loss estimation when `penstock_headloss_calculation` is True.
    design_flow : float, optional
        Design flow (same units as `flow`). If None, estimated from percent exceedance when available.
    system_efficiency : float, optional
        Overall efficiency (0–1 or 0–100% depending on context).
    generator_efficiency : float, optional
        Generator efficiency (0–1 or 0–100%). Defaults to 0.98 if None.
    turbine_type : str, optional
        Fixed turbine type; if None, selected automatically in DIVERSION mode.
    head_loss : float, optional
        Known head loss (same units as `head`).
    penstock_headloss_calculation : bool, default False
        Whether to compute penstock head-loss (design and time series).
    penstock_length, penstock_diameter : float, optional
        Penstock geometry (length, diameter).
    penstock_material : str, optional
        Material key for roughness tables (e.g., 'Steel').
    penstock_frictionfactor : float, optional
        DW friction factor or HW C value; if None, computed/selected.
    pctime_runfull : float, optional
        Target percent exceedance used to derive `design_flow` from FDC.
    max_headloss_allowed : float, optional
        Max allowed head loss as percent of head.
    turbine_Rm : float, optional
        Manufacturer/design coefficient for reaction turbines.
    pelton_n_jets : int, optional
        Pelton jet count.
    flow_column : str, optional
        Column name when `flow` is a pandas.DataFrame.
    channel_average_velocity : float, optional
        Cross-sectional mean velocity (m/s) for hydrokinetic mode.
    hk_blade_diameter, hk_blade_heigth : float, optional
        Hydrokinetic rotor geometry (m).
    hk_blade_type : {'ConventionalRotor','H-DarrieusRotor','DarrieusRotor'}, optional
    hk_swept_area : float, optional
        Hydrokinetic swept area (m²); computed if not provided.
    annual_caclulation : bool, default False
        If True, compute annual energy and revenue (DataFrame-based if available).
    resource_category : str, optional
        Cost model category used by ORNL HBCM.
    electricity_sell_price : float, optional
        Price of electricity ($/kWh) for revenue.
    cost_calculation_method : {'ORNL_HBCM'}, default 'ORNL_HBCM'
        Cost model selector.
    capacity_factor : float, optional
        Capacity factor (0–1 or 0–100%) for revenue if not using DataFrame timing.
    n_operation_days : int, optional
        Days/year the plant operates when `capacity_factor` not supplied.
    minimum_turbineflow : float, optional
        Absolute minimum turbine flow (same units as `flow`).
    minimum_turbineflow_percent : float, optional
        Minimum turbine flow as percent of design flow when absolute min not given.
    annual_maintenance_flag, major_maintenance_flag : bool, default False
        Zero-flow outages (7 days/year, 14 days/5 years) applied in DIVERSION
        when a DataFrame with a datetime index is provided.

    Returns
    -------
    object
        A merged parameter/result object containing inputs and computed fields,
        including (as available) `rated_power`, `power`, `net_head`, `head_loss`,
        `turbine_efficiency`, `dataframe_output`, `annual_dataframe_output`,
        and cost/revenue summaries.

    Raises
    ------
    ValueError
        For invalid unit choices, unsupported hydro types, bad inputs for
        DataFrame flow, or missing values required by selected sub-methods.

    Notes
    -----
    - US inputs are converted to SI internally; results are converted back to US
      when `units == 'US'`.
    - In DIVERSION mode, turbine selection and performance are computed before
      penstock head-loss if enabled.
    """
    
    # Check if a pandas dataframe
    flow_data, pandas_dataframe = pd_checker(flow, flow_column)       # check if a dataframe is used and extract flow values

    # initialize all instances: HydraulicDesign, Turbine, and Economic parameters.
    hyd_pm = HydraulicDesignParameters(flow= flow_data, design_flow= design_flow, head= head, #net_head= net_head,
                                       penstock_length= penstock_length, penstock_diameter= penstock_diameter, 
                                       penstock_material= penstock_material, 
                                       head_loss= head_loss, 
                                       penstock_frictionfactor= penstock_frictionfactor,
                                       penstock_headloss_calculation= penstock_headloss_calculation,
                                       max_headloss_allowed= max_headloss_allowed,
                                       penstock_headloss_method = penstock_headloss_method,
                                       channel_average_velocity= channel_average_velocity)

    turb_pm = TurbineParameters(turbine_type= turbine_type, 
                                flow= flow_data, design_flow= design_flow, flow_column = flow_column,
                                head= head, 
                                rated_power= rated_power,
                                system_efficiency= system_efficiency,
                                generator_efficiency= generator_efficiency,
                                Rm= turbine_Rm, pctime_runfull= pctime_runfull, pelton_n_jets= pelton_n_jets,
                                hk_blade_diameter= hk_blade_diameter, hk_blade_heigth= hk_blade_heigth, hk_blade_type= hk_blade_type, 
                                hk_swept_area= hk_swept_area)        # Initialize
    
    cost_pm = EconomicParameters(resource_category= resource_category, 
                                 electricity_sell_price= electricity_sell_price, 
                                 capacity_factor= capacity_factor, n_operation_days= n_operation_days)
    
    flow_preproc_pm = FlowPreProcessingParameters(minimum_turbineflow = minimum_turbineflow, minimum_turbineflow_percent = minimum_turbineflow_percent, 
                                         annual_maintenance_flag = annual_maintenance_flag, major_maintenance_flag = major_maintenance_flag)
    
    all_params = merge_instances(hyd_pm, turb_pm, cost_pm, flow_preproc_pm)       # merge parameters into a single instance
    
    all_params.pandas_dataframe = pandas_dataframe          # update 
    all_params.hydropower_type = hydropower_type        # update
    all_params.units = units

    if pandas_dataframe:
        all_params.datetime_index = flow.index        # Obtain index from flow data for annual calculation

    # check if units are in list
    if units not in ['SI', 'US']:
        raise ValueError('Units can only be \"US\" or \"SI\", see HydroGenerate for additional information')


    # units conversion - US to Si
    if units == 'US':       
        Units.us_to_si_conversion(all_params)       # convert imputs from US units to SI units
    
    # Check if hydropower type is valid
    hpt_list = ['BASIC', 'DIVERSION', 'HYDROKINETIC']

    # No hydropower calculation
    if hydropower_type is None:
        all_params.net_head = all_params.head       # update for cost calculation.

    elif hydropower_type.upper() not in hpt_list:
        raise ValueError('Hydropower type can only be:', hpt_list)

    # Basic hydropower calculation 
    elif hydropower_type.upper() == 'BASIC':
        Basic().hydropower_calculation(all_params)

    # Diversion projects
    elif hydropower_type.upper() == 'DIVERSION':
        Diversion().hydropower_calculation(all_params)
    
    elif hydropower_type.upper() == 'HYDROKINETIC':
        Hydrokinetic().hydropower_calculation(all_params)

    # Cost calculation
    if hydropower_type is None:
        if cost_calculation_method == 'ORNL_HBCM':
                ONRL_BaselineCostModeling_V2().cost_calculation(all_params)

    elif hydropower_type.upper() != 'HYDROKINETIC':
            if cost_calculation_method == 'ORNL_HBCM':
                ONRL_BaselineCostModeling_V2().cost_calculation(all_params)

    # Annual energy and revenue calculation
    
    # TODO: calculate pandas output when annual_calculation = False

    if annual_caclulation:
        if pandas_dataframe:        # If a pandas dataframe is used
            ConstantEletrictyPrice_pd().revenue_calculation(all_params, flow= flow)     # calculate revenue when a time-indexed pd.dataframe is given.
        
        else:
            ConstantEletrictyPrice().revenue_calculation(all_params)

    # units conversion - SI to US
    if units == 'US':
        Units.si_to_us_conversion(all_params)       # convert imputs from US units to SI units

    return all_params
  
# Examples are provided in the 'HydroGenerate_Workflow.ipynb' file.  