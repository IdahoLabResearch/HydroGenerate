'''
Copyright 2023, Battelle Energy Alliance, LLC
'''

"""
Created on 03-2023
@author: Camilo J. Bastidas Pacheco
This script handles head loss calculations and penstock sizing 
"""

import numpy as np
from abc import ABC, abstractmethod
from numbers import Number
   
# TODO: add documentation along the class: reference equations, describe the inputs, outputs, constants.
# TODO: validate that the method implemented is correct. Juan to cross-check the equations

g = 9.81 # acceleration of gravity (m/s^2)
nu = 0.0000011223 # Kinematic viscosity of water (m2/s) at 60F (~15.6C) - prevalent stream water temperature 

# Hydraulic design parameters
class HydraulicDesignParameters:
    def __init__(self, flow, design_flow, head, penstock_length, penstock_diameter, penstock_material,
                 head_loss, max_headloss_allowed, headloss_method):
        '''
        This class initializes hydraulic parameters needed for multiple calculations 
        Input variables:
        Returns: None
        '''
        # Inputs
        self.flow = flow
        self.design_flow = design_flow
        self.head = head
        self.penstock_length = penstock_length
        self.penstock_diameter = penstock_diameter
        self.penstock_material = penstock_material
        self.head_loss = head_loss       
        self.max_headloss_allowed = max_headloss_allowed
        self.headloss_method = headloss_method

        # internal parameters
        self.Re = []
        self.penstock_frictionfactor = None
        self.design_diameter = None

        
    # Reynolds number calculator 
    def reynoldsnumber_calculator(self):

        self.designdiameter_calculator()
        self.Re = 4 * self.design_flow / (np.pi * self.design_diameter * nu) # Reynolds number  

    # Design diameter calculator - initial assumed diameter
    def designdiameter_calculator(self):
        
        if self.penstock_diameter is not None:  # penstock diameter is known
            self.design_diameter = self.penstock_diameter    

        else:   # penstock diameter calculation based on head, flow, and length
            if self.design_diameter is None:    # if design diameter is also none (not chekcking diameter) 
                # self.design_diameter = 1.517 * self.design_flow**0.5 / self.head**0.25  # USBR 1986 equation
                self.design_diameter = 0.01

# Design flow

# Roughness
class RoughnessCoefficients:
    def __init__(self, material, darcyweisbach_epsilon, hazenwiliams_c, mannings_n):
        self.material = material
        self.darcyweisbach_epsilon = darcyweisbach_epsilon
        self.hazenwiliams_c = hazenwiliams_c
        self.mannings_n = mannings_n
    
    class Values:       # Values from Epanet documentation
        def __init__(self):
            self.roughnesscoefficients = { }
            self.add_roughnesscoefficient_values("CastIron", 0.00025908, 135, 0.0135)
            self.add_roughnesscoefficient_values("Concrete", 0.0016764, 130, 0.0145)
            self.add_roughnesscoefficient_values("GalvanizedIron", 0.0001524, 120, 0.016)
            self.add_roughnesscoefficient_values("Plastic", 0.000001524, 145, 0.013)
            self.add_roughnesscoefficient_values("Steel", 0.00004572, 145, 0.016)

        def add_roughnesscoefficient_values(self, material, darcyweisbach_epsilon, hazenwiliams_c, mannings_n):
            self.roughnesscoefficients[material] = RoughnessCoefficients(material, darcyweisbach_epsilon, hazenwiliams_c, mannings_n)
       
# Methods for roughness calculation
class Roughness(ABC):
    @abstractmethod
    def roughness_selector(self, material):
        pass

class DW_RoughnessSelector(Roughness):      # Darcy-Weisbach roughness selector
    
    def roughness_selector(self, material):
        roughness_coefficients = RoughnessCoefficients.Values()
        if material is not None:
            epsilon = roughness_coefficients.roughnesscoefficients[material].darcyweisbach_epsilon
        else:
            epsilon = roughness_coefficients.roughnesscoefficients['Steel'].darcyweisbach_epsilon
        return epsilon
    
class HW_RoughnessSelector(Roughness):      # Hazen-Williams roughness selector
    def roughness_selector(self, material):
        roughness_coefficients = RoughnessCoefficients.Values()
        if material is not None:
            C = roughness_coefficients.roughnesscoefficients[material].hazenwiliams_c
        else:
            C = roughness_coefficients.roughnesscoefficients['Steel'].hazenwiliams_c        # defaul to steel
        return C

class DW_FrictionFactor():      # Darcy-Weisbach friction factor calculator 
    
    def frictionfactor_calculator(self, hydraulic_parameters):

        epsilon = DW_RoughnessSelector().roughness_selector(material = hydraulic_parameters.penstock_material)      # DW roughness factor
        Re = hydraulic_parameters.Re # Reynolds number
        D = hydraulic_parameters.design_diameter # Design diameter
        
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
    
    @abstractmethod
    def headloss_calculator(self, hydraulic_parameters):
        pass
     
class DarcyWeisbach(HeadLoss):

    def headloss_calculator(self, hydraulic_parameters):     
        
        hydraulic_parameters.reynoldsnumber_calculator()
        D = hydraulic_parameters.design_diameter        # Design diameter
        L = hydraulic_parameters.penstock_length        # Penstock lenght
        V = hydraulic_parameters.design_flow / (np.pi * (D/2)**2)      # V = Q/A
        ff = DW_FrictionFactor().frictionfactor_calculator(hydraulic_parameters)        # DW friction factor   
        head_loss =  ff * L * V**2 / (D * 2*g)      # DW head loss
        hydraulic_parameters.penstock_frictionfactor = ff       # update
        hydraulic_parameters.head_loss = head_loss      # update
        
        if hydraulic_parameters.penstock_diameter is None:
            DarcyWeisbach().diameter_check(hydraulic_parameters)        # Check: head loss does not exceed the max allowed head loss - increase D until reached

    def diameter_check(self, hydraulic_parameters):

        # max head loss allowes 
        max_headloss_allowed = hydraulic_parameters.max_headloss_allowed
        
        if max_headloss_allowed is None:
            max_headloss_allowed = 10      # If a maximum head loss allowed is not used, the default is 10%
        
        max_headloss_allowed = max_headloss_allowed / 100        # Transform from percentage

        # if a penstcok lenght is not provided head loss = head * max allowed losses
        if hydraulic_parameters.penstock_length is None: 
            hydraulic_parameters.head_loss = hl = hydraulic_parameters.head * max_headloss_allowed      # update
        
        else:
            hl = hydraulic_parameters.head_loss     # head loss 
            h = hydraulic_parameters.head       # head
 
            if hl > max_headloss_allowed * h:       # head loss larger than maximum allowed
                while hl > max_headloss_allowed * h:
                    hydraulic_parameters.design_diameter = hydraulic_parameters.design_diameter + 0.1
                    DarcyWeisbach().headloss_calculator(hydraulic_parameters)
                    hl = hydraulic_parameters.head_loss
        
        hydraulic_parameters.penstock_diameter = hydraulic_parameters.design_diameter       # update     
    
    # head loss for a time series of flow using DW
    def headloss_calculator_ts(self, hydraulic_parameters):
            
            if hydraulic_parameters.penstock_length is None:
                return
            
            else:
                D = hydraulic_parameters.design_diameter
                V = hydraulic_parameters.flow / (np.pi * (D/2)**2)      # V = Q/A
                ff = hydraulic_parameters.penstock_frictionfactor       # DW friction factor 
                L = hydraulic_parameters.penstock_length # 
                head_loss = ff * L * V**2 / (D * 2*g)      # DW head loss for flow != design_flow
                head_loss = head_loss.to_numpy()
                return head_loss

class HazenWilliamns(HeadLoss):

    def headloss_calculator(self, hydraulic_parameters):

        C = HW_RoughnessSelector().roughness_selector(material = hydraulic_parameters.penstock_material) # HW roughness factor (C)
        L = hydraulic_parameters.penstock_length # Penstock lenght
        Q = hydraulic_parameters.design_flow 
                
        if hydraulic_parameters.penstock_diameter is not None:  # Penstock diameter is known
            D = hydraulic_parameters.penstock_diameter # Design diameter
            head_loss = 10.67 * L * Q**1.852 / (C**1.852 * D**4.87)   # HW head loss 

        else:          
            if hydraulic_parameters.max_headloss_allowed is not None:
                head_loss = hydraulic_parameters.max_headloss_allowed * hydraulic_parameters.head
            else:
                head_loss = 0.1 * hydraulic_parameters.head

            D = (10.67 * L * Q**1.852 / (C**1.852 * head_loss))**(1/4.87) # Calculated diameter
            hydraulic_parameters.head_loss = head_loss
            hydraulic_parameters.penstock_diameter = D  # update
        
        hydraulic_parameters.penstock_frictionfactor = C    # update
        hydraulic_parameters.reynoldsnumber_calculator()    # update
        hydraulic_parameters.head_loss = head_loss  # update
        
        # if hydraulic_parameters.penstock_diameter is None: 
        #     diametercheck = DiameterCheck(head_loss)
        #     head_loss = diametercheck.maxheadloss_checker(hydraulic_parameters)
        #     hydraulic_parameters.head_loss = head_loss

        return None        



if __name__ == "__main__":
        
    # Example 1. penstock diameter is not known. Maximum head loss allowed is not specified
    hyd_param = HydraulicDesignParameters(flow = 20, design_flow = 20, head = 50, penstock_length = 50, penstock_diameter = None, 
                                          penstock_material = None, head_loss= None, max_headloss_allowed = None, headloss_method= 'a')
        
    # Darcy Weisbach 
    hl = DarcyWeisbach()
    hl.headloss_calculator(hyd_param)

    print("\nPenstockDiameter:",hyd_param.penstock_diameter)
    print("Head Loss:",hyd_param.head_loss)
    print("FrictionFactor",hyd_param.penstock_frictionfactor)
    
    # # Example 2. penstock diameter is not known. Maximum head loss is set to 5%
    # hyd_param = HydraulicDesignParameters(flow= 2, design_flow= 2, head= 50, penstock_length= 50, penstock_diameter= None, 
    #                                       penstock_material= None, head_loss= None, max_headloss_allowed= 0.05)
        
    # # Darcy Weisbach 
    # hl = DarcyWeisbach()
    # hl.headloss_calculator(hydraulic_parameters = hyd_param)

    # print("\nPenstockDiameter:",hyd_param.penstock_diameter)
    # print("Head Loss:",hyd_param.head_loss)
    
    # # Example 3. penstock diameter is not known. Maximum head loss allowed is not specified. 
    # # Hazen-Williams is used for head loss calculations
    # hyd_param = HydraulicDesignParameters(flow = 20, design_flow= 20, head= 50, penstock_length= 50, penstock_diameter= None, 
    #                                       penstock_material= None, head_loss= None, max_headloss_allowed= None)
    # # HazenWilliamns()
    # hl = HazenWilliamns()
    # hl.headloss_calculator(hydraulic_parameters = hyd_param)

    # print("\nFrictionFactor",hyd_param.penstock_frictionfactor)
    # print("PenstockDiameter:",hyd_param.penstock_diameter)
    # print("Head Loss:",hyd_param.head_loss)

