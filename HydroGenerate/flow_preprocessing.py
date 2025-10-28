'''
Copyright 2023, Battelle Energy Alliance, LLC
'''

"""
07-2024 
@author: Soumyadeep Nag, Camilo J. Bastidas Pacheco, J. Gallego-Calderon

This module applies the flow limit constraints and incorporates the impact
of annual and major maintenance activities on turbine flow.

It provides utilities to:
1) Cap turbine flow at design limits.
2) Enforce minimum turbine flow thresholds (absolute or % of design flow).
3) Set turbine flow to zero during annual and major maintenance windows.

Expected `flow_obj` interface (used by functions here)
-----------------------------------------------------
Attributes
----------
flow : numpy.ndarray
    Raw inflow time series (m³/s), same length as `datetime_index`.
design_flow : float or numpy.ndarray
    Turbine design flow (m³/s). If array, must align with `flow`.
turbine_flow : numpy.ndarray
    Turbine flow (m³/s); created/updated by the functions in this module.
datetime_index : pandas.DatetimeIndex
    Timestamps for `flow`. Weekly grouping assumes this index (or a level)
    is named "dateTime" when using pandas.Grouper(level="dateTime", ...).

Notes
-----
- Annual maintenance zeros 7 consecutive days once per year, selecting the week
  with the lowest weekly mean flow.
- Major maintenance zeros 14 consecutive days every 5 years (skipping the first),
  selecting the two-week period with the lowest bi-weekly mean flow.
"""


import numpy as np
import pandas as pd
from datetime import datetime
   

# Hydraulic design parameters
class FlowPreProcessingParameters:

    """
    Container for flow pre-processing options used by flow limit and
    maintenance logic.

    Parameters
    ----------
    minimum_turbineflow : float or None
        Absolute minimum turbine flow (m^3/s). If None, a percentage of
        `design_flow` is used (see `minimum_turbineflow_percent`).
    minimum_turbineflow_percent : float or None
        Minimum turbine flow as a percentage of `design_flow` (1–100). Used
        only when `minimum_turbineflow` is None. If both are None, a default
        of 10% is applied.
    annual_maintenance_flag : bool
        If True, enforce a 7-day annual maintenance outage (flow set to 0).
    major_maintenance_flag : bool
        If True, enforce a 14-day major maintenance outage every 5 years
        (flow set to 0).

    Attributes
    ----------
    minimum_turbineflow : float or None
    minimum_turbineflow_percent : float or None
    annual_maintenance_flag : bool
    major_maintenance_flag : bool

    Notes
    -----
    This class only stores configuration; calculations are performed by
    methods in `FlowPreProcessing`.
    """        

    def __init__(self, minimum_turbineflow, minimum_turbineflow_percent,       # Flow parameters
                 annual_maintenance_flag, major_maintenance_flag): 

# Inputs
        self.minimum_turbineflow = minimum_turbineflow        # minimum flow through the turbine (m3/s)     
        self.minimum_turbineflow_percent = minimum_turbineflow_percent      # Set minimum flow by using a percent of design flow, deault is 10  (%, 1-100)
        self.annual_maintenance_flag = annual_maintenance_flag        # Boolean to include annual maintenance or not
        self.major_maintenance_flag = major_maintenance_flag      # Boolean to include major maintenance or not



class FlowPreProcessing():

    """
    Apply design flow limits and scheduled maintenance to a flow object.

    The methods in this class expect a `flow_obj` with, at minimum, the
    attributes described in the module docstring. Methods update
    `flow_obj.turbine_flow` in place and do not return values.

    See Also
    --------
    max_turbineflow_checker : Cap turbine flow at design flow.
    min_turbineflow_checker : Enforce minimum turbine flow threshold.
    annual_maintenance_implementer : Zero 7 days/year at lowest-flow week.
    major_maintenance_implementer : Zero 14 days/5 years at lowest bi-weekly mean.
    """

    # Function that sets max turbine flow to the design flow
    def max_turbineflow_checker(self, flow_obj):
        """
        Cap turbine flow at the design flow.

        Parameters
        ----------
        flow_obj : object
            Object with attributes:
            - flow : numpy.ndarray
                Raw inflow time series (m^3/s).
            - design_flow : float or numpy.ndarray
                Turbine design flow (m^3/s). If array, must align with `flow`.

        Side Effects
        ------------
        Updates `flow_obj.turbine_flow` (numpy.ndarray), where each element is
        `min(flow, design_flow)`.

        Examples
        --------
        >>> # flow_obj.flow = [12, 8], design_flow = 10
        >>> # turbine_flow becomes [10, 8]
        """

        flow = flow_obj.flow            # this is a numpy array
        design_flow = flow_obj.design_flow
        flow_obj.turbine_flow = np.where(flow > design_flow, design_flow, flow)         # turbine_flow is created here as this code is always active and runs 1st. flow is < design flow

    # Function that sets min turbine flow to the design flow
    def min_turbineflow_checker(self, flow_obj):
        """
        Enforce a minimum turbine flow threshold; set values below it to zero.

        Logic
        -----
        - If `flow_obj.minimum_turbineflow` is provided, use it (m^3/s).
        - Else, compute min flow as
        (`minimum_turbineflow_percent` or 10 by default) × `design_flow` / 100.
        The computed value is stored back into `flow_obj.minimum_turbineflow`.

        Parameters
        ----------
        flow_obj : object
            Object with attributes:
            - turbine_flow : numpy.ndarray
                Turbine flow series (m^3/s), typically after max-capping.
            - design_flow : float or numpy.ndarray
                Turbine design flow (m^3/s).
            - minimum_turbineflow : float or None
            - minimum_turbineflow_percent : float or None

        Side Effects
        ------------
        Updates `flow_obj.turbine_flow`, replacing values `< min_flow` with 0.

        Notes
        -----
        - If `design_flow` is an array, elementwise percentages are applied.
        - Default minimum percent is 10 if neither absolute nor percentage is given.

        Examples
        --------
        >>> # design_flow = 20 m^3/s, minimum_turbineflow_percent = 10
        >>> # min_flow = 2.0; turbine_flow < 2.0 becomes 0
        """
        
        flow = flow_obj.turbine_flow # this is a numpy array        
        design_flow = flow_obj.design_flow

        # check if the user entered a min flow value
        if flow_obj.minimum_turbineflow is not None:
            min_flow = flow_obj.minimum_turbineflow
        else:
            if flow_obj.minimum_turbineflow_percent is not None:         # Check if a user entered min flow percentage if not, use 10% as default
                min_flow_percent =  flow_obj.minimum_turbineflow_percent
            else:
                min_flow_percent = 10           # Default   
     
            min_flow = (min_flow_percent / 100) * design_flow           # Compute minimum flow that passes through the turbine
            flow_obj.minimum_turbineflow = min_flow            # update

        flow_obj.turbine_flow = np.where(flow < min_flow, 0, flow)          # replace flows less than min flow with 0

    def annual_maintenance_implementer(self, flow_obj):
        """
        Zero turbine flow for 7 consecutive days once per calendar year.

        Procedure
        ---------
        1) Compute weekly mean flow and identify the week with the lowest mean
        (excluding first/last partial weeks).
        2) For each year in the time span, zero out the 7-day window starting on
        the Monday of that lowest-flow week.

        Parameters
        ----------
        flow_obj : object
            Object with attributes:
            - turbine_flow : numpy.ndarray
                Turbine flow series (m^3/s).
            - datetime_index : pandas.DatetimeIndex
                Timestamps aligned with `turbine_flow`.

        Side Effects
        ------------
        Updates `flow_obj.turbine_flow`, setting the 7 chosen days per year to 0.

        Assumptions
        -----------
        - `datetime_index` covers multiple years or at least one full year.
        - Weekly grouping uses `pd.Grouper(level="dateTime", freq='W')`. Ensure your
        index (or a MultiIndex level) is named "dateTime" or adjust the grouper
        accordingly.

        Examples
        --------
        >>> # After applying, each year has a 7-day zero-flow outage at the
        >>> # statistically lowest weekly mean period.
        """

        # Function to set annual maintennace - i.e., make the flow 0 for a week a year

        turbine_flow = flow_obj.turbine_flow            # turbine flow series with max and min (if on) limits implemented
        datetime_index = flow_obj.datetime_index            # datetime index of the user flow
        flow = pd.DataFrame(data= turbine_flow, index= datetime_index, columns=['flow_cms'])            # create dataframe with date and flow in m3/s
        
        # Create series with maintennance years
        start_date = datetime_index[0].year         # Start Year
        end_date = datetime_index[-1].year          # End year
        maint_years = list(range(start_date, end_date, 1))          # Years where there will be maintenance - every year

        # Find minimum week - maintennance week
        weekly = flow .groupby(pd.Grouper(level="dateTime", freq='W')).mean().iloc[1:-1]             # compute the two-weekly mean and drop first and last
        weekly['week'] = weekly.index.strftime('%W')
        week_maint = weekly.groupby('week').mean().idxmin()[0]
        
        # Generate a series with the monday of every maintenance week
        start_days = []
        for m in maint_years:
            start_days.append(datetime.strptime(str(m) + str(week_maint) + '1', "%Y%W%w"))          # Monday of the week where maintenance starts

        # Generate a date series of maintenance from start date
        dates_maint = []        # maintenance dates
        for d in start_days:
            # for day in range(7):
            dates_maint.append(pd.date_range(d, periods= 7).date)           # generate 7 days for each year
            #  dates_maint.append((sd + datetime.timedelta(days=day)).strftime("%Y-%m-%d"))

        dates_maint = np.concatenate(dates_maint, axis= 0)      # generate single array
        flow['date'] = flow.index.date          # add date to dataframe
        flow.loc[flow.date.isin(dates_maint), 'flow_cms'] = 0           # replace flow in minimum weeks with 0

        flow_obj.turbine_flow = flow['flow_cms'].to_numpy()         # update

    # Function that schedules the major maintennace
    def major_maintenance_implementer(self, flow_obj):

        """
        Zero turbine flow for 14 consecutive days every 5 years (skip first year).

        Procedure
        ---------
        1) Compute bi-weekly (2W) mean flow and identify the bi-weekly window with
        the lowest mean (excluding first/last partial windows).
        2) For maintenance years spaced every 5 years (starting after the first),
        zero out the 14-day window starting on the Monday of the selected week.

        Parameters
        ----------
        flow_obj : object
            Object with attributes:
            - turbine_flow : numpy.ndarray
                Turbine flow series (m^3/s).
            - datetime_index : pandas.DatetimeIndex
                Timestamps aligned with `turbine_flow`.

        Side Effects
        ------------
        Updates `flow_obj.turbine_flow`, setting the selected 14 days to 0 in each
        maintenance year (every 5 years; first year excluded).

        Assumptions
        -----------
        - Sufficient span to include one or more 5-year intervals.
        - Bi-weekly grouping uses `pd.Grouper(level="dateTime", freq='2W')`. Ensure
        your index (or a MultiIndex level) is named "dateTime" or adjust the
        grouper accordingly.

        Examples
        --------
        >>> # In a 10-year record, days 1–14 of the lowest 2-week flow window
        >>> # are zeroed in years 5 and 10 (year 0 excluded).
        """
        
        # Major maintenance will happend on the month with lowest flow a year - during the first 15 days of this month.

        turbine_flow = flow_obj.turbine_flow            # turbine flow series with max and min (if on) limits implemented
        datetime_index = flow_obj.datetime_index            # datetime index of the user flow
        flow = pd.DataFrame(data= turbine_flow, index= datetime_index, columns=['flow_cms']) # create dataframe with date and flow in m3/s
        
        # Find maintennance years
        start_date = datetime_index[0].year         # Start Year
        end_date = datetime_index[-1].year          # End year
        maint_years = list(range(start_date, end_date, 5))          # Years where there will be maintenance - every 5 years
        del maint_years[0]          # remove the first year

        # Find minimum two-week period - maintennance week
        weekly = flow .groupby(pd.Grouper(level="dateTime", freq='2W')).mean().iloc[1:-1]             # compute the two-weekly mean and drop first and last
        weekly['week'] = weekly.index.strftime('%W')
        week_maint = weekly.groupby('week').mean().idxmin()[0]

        # Generate a series with the monday of every maintenance week
        start_days = []
        for m in maint_years:
            start_days.append(datetime.strptime(str(m) + str(week_maint) + '1', "%Y%W%w"))          # Monday of the week where maintenance starts
            
        # Generate a date series of maintenance from start date
        dates_maint = []
        for d in start_days:
            dates_maint.append(pd.date_range(d, periods= 14).date)           # generate 14 days for each year
        
        dates_maint = np.concatenate(dates_maint, axis= 0)

        # Make flow 0 during those days
        flow['date'] = flow.index.date
        flow.loc[flow.date.isin(dates_maint), 'flow_cms'] = 0           # replace flow in minimum weeks with 0
        
        flow_obj.turbine_flow = flow['flow_cms'].to_numpy()         # update


