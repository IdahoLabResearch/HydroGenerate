"""
03-2023
@author: Camilo J. Bastidas Pacheco
This script handles head loss calculations and penstock sizing.

Functionality
-------------
- Compute Reynolds number and select/compute friction factors.
- Estimate head loss via Darcy–Weisbach or Hazen–Williams.
- Size penstocks to respect a maximum allowable head loss.
"""

import numpy as np
from abc import ABC, abstractmethod

g = 9.81        # acceleration of gravity (m/s^2)
nu = 0.0000011223       # Kinematic viscosity of water (m2/s) at 60F (~15.6C) - prevalent stream water temperature 

# Hydraulic design parameters
class HydraulicDesignParameters:

    """Hydraulic design parameter container.

    This class stores input values needed for penstock head-loss calculations
    and provides helper methods for computing Reynolds number and a starting
    design diameter for iterative sizing.

    Parameters
    ----------
    flow : float or array-like
        Flow values (m³/s). This may represent a single value or a time series,
        depending on the calling context.
    design_flow : float
        Design flow (m³/s).
    head : float
        Available (gross) head (m).
    head_loss : float or numpy.ndarray or None
        Head loss for the provided ``flow`` values (m). This may be provided by
        the user or computed by head-loss calculators in this module.
    max_headloss_allowed : float or None
        Maximum head loss allowed as a percentage of head (%, 1–100). If
        ``None``, method-specific defaults may be applied.
    penstock_headloss_method : str or None
        Name of the head-loss method. Current options in this module include
        ``"Darcy-Weisbach"`` and ``"Hazen-Williams"``. (Manning is referenced
        but not implemented in this file.)
    penstock_headloss_calculation : bool
        Whether to calculate head loss in the penstock. If net head is already
        available externally, set to ``False``.
    penstock_length : float or None
        Penstock length (m). Required for head-loss calculations that depend on
        length.
    penstock_diameter : float or None
        Penstock diameter (m). If ``None``, some methods may size diameter to
        meet the allowed head-loss constraint.
    penstock_material : str or None
        Penstock material key used for roughness selection. Expected options include: ``CastIron``, ``Concrete``, ``GalvanizedIron``, ``Plastic``, ``Steel``.
    penstock_frictionfactor : float or None
        Friction parameter for the chosen method:
        - Darcy–Weisbach: friction factor ``f`` (if provided), or roughness
          ``epsilon`` used to compute ``f``.
        - Hazen–Williams: coefficient ``C``.
        - Manning: ``n`` (not used in this file).
    channel_average_velocity : float or None
        Average cross-sectional water velocity in the channel (Q/A), if
        applicable.

    Notes
    -----
    Many algorithms in this module mutate attributes on a shared
    :class:`HydraulicDesignParameters` instance (e.g., updating
    ``penstock_design_diameter`` during iterations).
    """
    def __init__(self, flow, design_flow,       # Flow parameters
                 head, head_loss, 
                 max_headloss_allowed, penstock_headloss_method, penstock_headloss_calculation,    # head / head loss 
                 penstock_length, penstock_diameter, penstock_material, penstock_frictionfactor,        # penstock parameters  
                 channel_average_velocity):

        # Inputs
        self.flow = flow        # flow values (m3/s)     
        self.design_flow = design_flow      # design flow (m3/s)    
        self.head = head        # available head (m)
        self.head_loss = head_loss      # head loss for the flow values given or computed
        self.max_headloss_allowed = max_headloss_allowed        # maximum head loss allowed (%, 1-100)
        self.penstock_headloss_method = penstock_headloss_method      # headloss method, currently: (Darcy-Weisbach, Hazen-Williams) -  TODO: add Manning
        self.penstock_length = penstock_length      # lenght of the penstock (m)
        self.penstock_diameter = penstock_diameter      # penstock diameter (m)
        self.penstock_material = penstock_material      # penstock material, current options are:  (CastIron, Concrete, GalvanizedIron, Plastic, Steel), default: Steel
        self.penstock_frictionfactor = penstock_frictionfactor      # Hazen-Williams C, Darcy Weisbach Epsilon, Manning's n
        self.channel_average_velocity = channel_average_velocity        # average cross sectional water velocity (Q/A)

        # Additional parameters
        self.Re = []        # Reynolds number (unitless / dimensionless)
        self.penstock_design_diameter = None     # placeholder for the estimated penstock diameter (m) during calculations.
        self.penstock_design_headloss = None     # placeholder for design head_loss in iterations of multiple flow values
        self.channel_design_headloss = None     # placeholder for channel head loss
        self.channel_headloss = None     # placeholder for channel head loss
        self.penstock_headloss_calculation = penstock_headloss_calculation      # Calculate head_loss in the penstock? (boolean) - if net head is available set to False

    # Reynolds number calculation
    def reynoldsnumber_calculator(self):
        """Compute and store the Reynolds number for the design condition.

        Notes
        -----
        This method updates ``self.penstock_design_diameter`` (if needed) and
        writes the resulting Reynolds number to ``self.Re``.

        The Reynolds number is computed as::

            Re = 4 * Q / (pi * D * nu)

        where ``Q`` is ``self.design_flow``, ``D`` is the (design) diameter, and
        ``nu`` is the kinematic viscosity constant defined in this module.
        """
        self.designdiameter_calculator()        # calculate diameter
        self.Re = 4 * self.design_flow / (np.pi * self.penstock_design_diameter * nu)        # Reynolds number, update  

    # Design diameter calculator - initial assumed diameter
    def designdiameter_calculator(self):
        """Initialize ``penstock_design_diameter`` for calculations.

        Notes
        -----
        - If ``self.penstock_diameter`` is provided, it becomes the design
          diameter.
        - Otherwise, the method initializes ``self.penstock_design_diameter`` to
          a small starting value (0.01 m) the first time it is needed.
        """

        if self.penstock_diameter is not None:      # penstock diameter is known
            self.penstock_design_diameter = self.penstock_diameter       # update

        else:   # penstock diameter will be calculated
            if self.penstock_design_diameter is None:    # if design diameter is also none (not chekcking diameter) 
                self.penstock_design_diameter = 0.01     # starting value for iteration

# Roughness coefficients
class RoughnessCoefficients:
    """Roughness coefficient record for a penstock material.

    Parameters
    ----------
    material : str
        Material identifier key (e.g., ``"Steel"``).
    darcyweisbach_epsilon : float
        Absolute roughness ``epsilon`` for Darcy–Weisbach calculations (m).
    hazenwiliams_c : float
        Hazen–Williams coefficient ``C`` (dimensionless).
    mannings_n : float
        Manning roughness coefficient ``n`` (s/m^(1/3)).
    """
    def __init__(self, material, darcyweisbach_epsilon, hazenwiliams_c, mannings_n):        # Epsilon, C, n
        self.material = material
        self.darcyweisbach_epsilon = darcyweisbach_epsilon
        self.hazenwiliams_c = hazenwiliams_c
        self.mannings_n = mannings_n
    
    class Values:       # roughness values from Epanet documentation 
        """Catalog of default roughness values.

        This nested class provides a dictionary mapping material keys to
        :class:`RoughnessCoefficients` instances. Values are sourced from EPANET
        documentation as indicated in the original code comments.
        """
        def __init__(self):
            self.roughnesscoefficients = { }
            self.add_roughnesscoefficient_values("CastIron", 0.00025908, 135, 0.0135)       # Cast Iron. Epsilon, C, n
            self.add_roughnesscoefficient_values("Concrete", 0.0016764, 130, 0.0145)        # Concrete. Epsilon, C, n
            self.add_roughnesscoefficient_values("GalvanizedIron", 0.0001524, 120, 0.016)   # Galvanized Iron. Epsilon, C, n
            self.add_roughnesscoefficient_values("Plastic", 0.000001524, 145, 0.013)        # Plastic. Epsilon, C, n
            self.add_roughnesscoefficient_values("Steel", 0.00004572, 145, 0.016)           # Steel. Epsilon, C, n

        def add_roughnesscoefficient_values(self, material, darcyweisbach_epsilon, hazenwiliams_c, mannings_n):     # method for adding roughness values
            """Add a roughness coefficient record for a material key.

            Parameters
            ----------
            material : str
                Material identifier key.
            darcyweisbach_epsilon : float
                Darcy–Weisbach roughness (m).
            hazenwiliams_c : float
                Hazen–Williams coefficient.
            mannings_n : float
                Manning ``n``.

            Notes
            -----
            This method mutates ``self.roughnesscoefficients`` in place.
            """
            self.roughnesscoefficients[material] = RoughnessCoefficients(material, darcyweisbach_epsilon, hazenwiliams_c, mannings_n)
       
# Roughness selection
class Roughness(ABC):
    """Abstract base class for roughness selection."""
    @abstractmethod
    def roughness_selector(self, material):
        """Select a roughness parameter for the given material.

        Parameters
        ----------
        material : str or None
            Material identifier key. If ``None``, implementations should apply
            a method-specific default.

        Returns
        -------
        float
            The selected roughness parameter (e.g., ``epsilon``, ``C``, or
            ``n`` depending on the implementation).
        """
        pass

class DW_RoughnessSelector(Roughness):      # Darcy-Weisbach roughness selector
    """Darcy–Weisbach roughness selector.

    Selects absolute roughness ``epsilon`` (m) based on material.
    """     
    def roughness_selector(self, material):
        """Select Darcy–Weisbach absolute roughness ``epsilon``.

        Parameters
        ----------
        material : str or None
            Material identifier key. Defaults to ``"Steel"`` when ``None``.

        Returns
        -------
        float
            Absolute roughness ``epsilon`` (m).
        """
        roughness_coefficients = RoughnessCoefficients.Values()     # read existing roughness coefficient values
        if material is not None:        # user provided material
            epsilon = roughness_coefficients.roughnesscoefficients[material].darcyweisbach_epsilon
        else:       # the default material is steel
            epsilon = roughness_coefficients.roughnesscoefficients['Steel'].darcyweisbach_epsilon
        return epsilon
    
class HW_RoughnessSelector(Roughness):      # Hazen-Williams roughness selector
    """Hazen–Williams roughness selector.

    Selects Hazen–Williams coefficient ``C`` based on material.
    """
    def roughness_selector(self, material):
        """Select Hazen–Williams coefficient ``C``.

        Parameters
        ----------
        material : str or None
            Material identifier key. Defaults to ``"Steel"`` when ``None``.

        Returns
        -------
        float
            Hazen–Williams coefficient ``C``.
        """
        roughness_coefficients = RoughnessCoefficients.Values()     # read existing roughness coefficient values
        if material is not None:        # user provided material
            C = roughness_coefficients.roughnesscoefficients[material].hazenwiliams_c
        else:       # the default material is steel
            C = roughness_coefficients.roughnesscoefficients['Steel'].hazenwiliams_c        # defaul to steel
        return C

class Manning_RoughnessSelector(Roughness):
    """Manning roughness selector.

    Selects Manning coefficient ``n`` based on material.
    """
    def roughness_selector(self, material):
        """Select Manning roughness coefficient ``n``.

        Parameters
        ----------
        material : str or None
            Material identifier key. Defaults to ``"Concrete"`` when ``None``.

        Returns
        -------
        float
            Manning roughness coefficient ``n``.
        """
        roughness_coefficients = RoughnessCoefficients.Values()     # read existing roughness coefficient values
        if material is not None:        # user provided material
            n = roughness_coefficients.roughnesscoefficients[material].mannings_n
        else:       # the default material is concrete
            n = roughness_coefficients.roughnesscoefficients['Concrete'].mannings_n       # defaul to concrete
        return n

class DW_FrictionFactor():      # Darcy-Weisbach friction factor calculator 
    """Darcy–Weisbach friction factor calculator.

    Computes a Darcy friction factor using regime-dependent formulas:
    Swamee–Jain approximation (turbulent), 
    Cubic interpolation (transitional), 
    Laminar expression (laminar), 

    References are preserved from the original inline comments.
    """
    def frictionfactor_calculator(self, hydraulic_parameters):
        """Compute Darcy–Weisbach friction factor ``f``.

        Parameters
        ----------
        hydraulic_parameters : HydraulicDesignParameters
            Hydraulic parameters containing:
            ``penstock_material`` (str or None), 
            ``Re`` (float), 
            ``penstock_design_diameter`` (float)

        Returns
        -------
        float
            Darcy friction factor ``f`` (dimensionless).

        Notes
        -----
        This method does not mutate ``hydraulic_parameters``; it reads from it.
        """

        epsilon = DW_RoughnessSelector().roughness_selector(material = hydraulic_parameters.penstock_material)      # DW roughness factor
        Re = hydraulic_parameters.Re # Reynolds number
        D = hydraulic_parameters.penstock_design_diameter # Design diameter
        
        if Re > 4000:
            ff = 0.25 / (np.log10((epsilon / (3.7 * D)) + (5.74 / Re**0.9)))**2     # Swamee-Jain approximation to the Colebrook-White equation (Bhave, 1991)
        
        elif Re > 2000:     # Cubic interpolation formula derived from the Moody Diagram (Dunlop, 1991)
            AA= -1.5634601348517065795
            AB= 0.00328895476345399058690
            Y2 = (epsilon / 3.7 * D) + AB
            Y3 = -2 * np.log10(Y2)
            FA = Y3**-2
            FB = FA * (2 - (AA * AB / (Y2 * Y3)))
            X1 = 7*FA - FB
            X2 = 0.128 - 17*FA + 2.5*FB
            X3 = -0.128 + 13*FA - 2*FB
            X4 = 0.032 - 3*FA + 0.5*FB
            R =  Re/2000
            ff = X1 + R * (X2 + R * (X3 + R * X4))
        
        else:
            ff = 64/Re      # Laminar flow (Bhave, 1991)

        return ff

# Head loss calculation
class HeadLoss(ABC):   
    """Abstract base class for penstock head-loss calculators."""
    @abstractmethod
    def penstock_headloss_calculator(self, hydraulic_parameters):
        """Compute (or size) penstock head loss for the design condition.

        Parameters
        ----------
        hydraulic_parameters : HydraulicDesignParameters
            The parameter container to read inputs from and update outputs on.

        Notes
        -----
        Implementations typically update ``hydraulic_parameters`` in place.
        """
        pass
     
class DarcyWeisbach(HeadLoss):      # Head loss calculator using Darcy-Weisbach
    """Penstock head-loss calculator using Darcy–Weisbach."""
    def penstock_headloss_calculator(self, hydraulic_parameters):     
        """Compute Darcy–Weisbach head loss at design flow and update parameters.

        Parameters
        ----------
        hydraulic_parameters : HydraulicDesignParameters
            Parameter container. This method reads (at minimum) ``design_flow``,
            ``head``, ``penstock_length``, ``penstock_diameter`` and updates
            working values such as ``penstock_design_diameter``,
            ``penstock_design_headloss``, and ``penstock_frictionfactor``.

        Notes
        -----
        This method mutates ``hydraulic_parameters`` in place.

        If ``hydraulic_parameters.penstock_diameter`` is ``None``, the method
        will iteratively increase diameter until the computed head loss is less
        than or equal to the allowed fraction of head (see
        :meth:`diameter_check`).
        """
        hydraulic_parameters.reynoldsnumber_calculator()        # calculate Reynolds number
        D = hydraulic_parameters.penstock_design_diameter        # Design diameter
        L = hydraulic_parameters.penstock_length        # Penstock lenght
        V = hydraulic_parameters.design_flow / (np.pi * (D/2)**2)      # V = Q/A
        
        if hydraulic_parameters.penstock_frictionfactor is None:        # if a value of ff is not given
            ff = DW_FrictionFactor().frictionfactor_calculator(hydraulic_parameters)        # DW friction factor   

        else:       # if penstock friction factor is given
            ff = hydraulic_parameters.penstock_frictionfactor

        head_loss =  ff * L * V**2 / (D * 2*g)      # DW head loss
        hydraulic_parameters.penstock_frictionfactor = ff       # update
        hydraulic_parameters.penstock_design_headloss = head_loss        # update
        
        if hydraulic_parameters.penstock_diameter is None:
            DarcyWeisbach().diameter_check(hydraulic_parameters)        # Check: head loss does not exceed the max allowed head loss - increase D until reached

    def diameter_check(self, hydraulic_parameters):
        """Iteratively increase diameter until head-loss constraint is met.

        Parameters
        ----------
        hydraulic_parameters : HydraulicDesignParameters
            Parameter container updated in place. The method reads
            ``max_headloss_allowed``, ``head``, ``penstock_length`` and updates
            ``penstock_design_diameter``, ``penstock_design_headloss``, and
            finally ``penstock_diameter``.

        Notes
        -----
        This method mutates ``hydraulic_parameters`` in place.

        - If ``max_headloss_allowed`` is ``None``, a default of 10% is used.
        - If ``penstock_length`` is ``None``, the method sets design head loss
          to ``head * max_headloss_allowed`` and skips diameter iteration.
        - Otherwise, the method uses recursion via
          :meth:`penstock_headloss_calculator` while incrementing diameter by
          0.1 m until the constraint is satisfied.
        """
        # max head loss allowes 
        max_headloss_allowed = hydraulic_parameters.max_headloss_allowed
        
        if max_headloss_allowed is None:
            max_headloss_allowed = 10      # If a maximum head loss allowed is not used, the default is 10%
        
        max_headloss_allowed = max_headloss_allowed / 100        # Transform from percentage

        # if a penstcok lenght is not provided, head loss = head * max allowed losses
        if hydraulic_parameters.penstock_length is None: 
            hydraulic_parameters.penstock_design_headloss = hl = hydraulic_parameters.head * max_headloss_allowed      # update
        
        else:
            hl = hydraulic_parameters.penstock_design_headloss     # head loss 
            h = hydraulic_parameters.head       # head
 
            if hl > max_headloss_allowed * h:       # head loss larger than maximum allowed
                while hl > max_headloss_allowed * h:        # iterate until head loss is less than the max allowed
                    hydraulic_parameters.penstock_design_diameter = hydraulic_parameters.penstock_design_diameter + 0.1       # increase by 0.1
                    DarcyWeisbach().penstock_headloss_calculator(hydraulic_parameters)       # Recursion to solve until head loss = desired head loss
                    hl = hydraulic_parameters.penstock_design_headloss       # update after each step
        
        hydraulic_parameters.penstock_diameter = hydraulic_parameters.penstock_design_diameter       # update     
    
    def penstock_headloss_calculator_ts(self, hydraulic_parameters):
        """Compute Darcy–Weisbach head loss for a flow time series.

        Parameters
        ----------
        hydraulic_parameters : HydraulicDesignParameters
            Parameter container with:
            ``turbine_flow`` (array-like): flow values (m³/s), 
            ``penstock_length`` (float): required, 
            ``penstock_design_diameter`` (float), 
            ``penstock_frictionfactor`` (float): Darcy friction factor

        Raises
        ------
        ValueError
            If ``hydraulic_parameters.penstock_length`` is ``None``.

        Notes
        -----
        This method mutates ``hydraulic_parameters.head_loss`` in place by
        computing head loss for each time-series flow value.
        """
        if hydraulic_parameters.penstock_length is None:        # penstock lenght not provided
            raise ValueError("The penstock lenght is required for head loss calculations")
        
        else:
            D = hydraulic_parameters.penstock_design_diameter
            V = hydraulic_parameters.turbine_flow / (np.pi * (D/2)**2)      # V = Q/A
            ff = hydraulic_parameters.penstock_frictionfactor       # DW friction factor 
            L = hydraulic_parameters.penstock_length # 
            hydraulic_parameters.head_loss = ff * L * V**2 / (D * 2*g)      # D-W head loss for flow != design_flow - update

class HazenWilliamns(HeadLoss):     # Head loss calculator using Hazen-Williams
    """Penstock head-loss calculator using Hazen–Williams.

    Notes
    -----
    The class name is kept as in the source (``HazenWilliamns``), though the
    standard spelling is "HazenWilliams".
    """
    def penstock_headloss_calculator(self, hydraulic_parameters):
        """Compute Hazen–Williams head loss and update parameters.

        Parameters
        ----------
        hydraulic_parameters : HydraulicDesignParameters
            Parameter container. This method reads (at minimum) ``design_flow``,
            ``head``, ``penstock_length``, ``penstock_diameter`` and updates
            ``penstock_frictionfactor`` (as Hazen–Williams ``C``),
            ``penstock_design_headloss``, and potentially ``penstock_diameter``.

        Notes
        -----
        This method mutates ``hydraulic_parameters`` in place.

        - If ``penstock_diameter`` is provided, head loss is computed directly.
        - If ``penstock_diameter`` is ``None``, diameter is computed to satisfy
          a head-loss allowance (default 10% of head if not provided).
        """
        if hydraulic_parameters.penstock_frictionfactor is None:        # if a value of C is not given
            C = HW_RoughnessSelector().roughness_selector(material = hydraulic_parameters.penstock_material) # HW roughness factor (C)
        
        else:
            C = hydraulic_parameters.penstock_frictionfactor
        
        L = hydraulic_parameters.penstock_length # Penstock lenght
        Q = hydraulic_parameters.design_flow 
                
        if hydraulic_parameters.penstock_diameter is not None:      # Penstock diameter is known
            D = hydraulic_parameters.penstock_diameter # Design diameter
            head_loss = 10.67 * L * Q**1.852 / (C**1.852 * D**4.87)     # HW head loss 

        else:          
            if hydraulic_parameters.max_headloss_allowed is not None:       # user-entered max head loss allowed
                head_loss = hydraulic_parameters.max_headloss_allowed * hydraulic_parameters.head / 100
            else:
                head_loss = 0.1 * hydraulic_parameters.head     # default to 10% of head loss

            D = (10.67 * L * Q**1.852 / (C**1.852 * head_loss))**(1/4.87)       # Calculated diameter
            hydraulic_parameters.penstock_design_headloss = head_loss      # update
            hydraulic_parameters.penstock_diameter = D      # update
        
        hydraulic_parameters.penstock_frictionfactor = C        # update
        hydraulic_parameters.reynoldsnumber_calculator()        # update
        hydraulic_parameters.penstock_design_headloss = head_loss        # update

        return None        

    def penstock_headloss_calculator_ts(self, hydraulic_parameters):
        """Compute Hazen–Williams head loss for a flow time series.

        Parameters
        ----------
        hydraulic_parameters : HydraulicDesignParameters
            Parameter container with:
            ``turbine_flow`` (array-like): flow values (m³/s), 
            ``penstock_length`` (float or None), 
            ``penstock_design_diameter`` (float), 
            ``penstock_frictionfactor`` (float): Hazen–Williams ``C``

        Notes
        -----
        This method mutates ``hydraulic_parameters.head_loss`` in place.

        If ``penstock_length`` is ``None``, the method returns immediately
        without modification.
        """
        if hydraulic_parameters.penstock_length is None:
            return
            
        else:
            D = hydraulic_parameters.penstock_design_diameter
            C = hydraulic_parameters.penstock_frictionfactor
            L = hydraulic_parameters.penstock_length # 
            Q = hydraulic_parameters.turbine_flow
            hydraulic_parameters.head_loss = 10.67 * L * Q**1.852 / (C**1.852 * D**4.87)     # HW head loss 



if __name__ == "__main__":
        
# Head loss
    hyd_param = HydraulicDesignParameters(flow= 1000, design_flow= 1000,
                                          channel_average_velocity= None,
                                          head = 100, penstock_length = 115, penstock_diameter = 10, 
                                          head_loss= None, max_headloss_allowed = None, penstock_headloss_method = None,
                                          penstock_material = None, penstock_frictionfactor = None, penstock_headloss_calculation= True)
        

    hl = DarcyWeisbach()
    hl.penstock_headloss_calculator(hyd_param)
    print(hyd_param.penstock_design_headloss)
