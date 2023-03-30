import numpy as np
from abc import ABC, abstractmethod
   
# TODO: add documentation along the class: reference equations, describe the inputs, outputs, constants.
# TODO: validate that the method implemented is correct. Juan to cross-check the equations

# Constant definition / unit conversion
rho = 1000 # water density in Kg/m^3
g = 9.81 # acceleration of gravity (m/s^2)
cfs_to_cms = 0.0283168 # cubic feet per second to cubic meter per second
ft_to_m = 0.3048 # feet to meters
nu = 0.0000011223 # Kinematic viscosity of water (m2/s) at 60F (~15.6C) - prevalent stream water temperature 


# Hydraulic design parameters
### This class will contain all the hydraulic-related parameters
### I'll modify the turbine class so that it only contains parameter needed for turbine related calculations
class HydraulicDesignParameters:
    def __init__(self, flow, design_flow, head, 
                 penstock_length, penstock_diameter, penstock_material, penstock_slope, penstock_frictionfactor,
                 head_loss):
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
        self.penstock_slope = penstock_slope
        self.penstock_frictionfactor = penstock_frictionfactor
        self.Re = []
        self.head_loss = head_loss
        
        # Reynolds number calculator 
    def reynoldsnumber_calculator(self):
        if self.penstock_diameter is not None: # penstock diameter is known
            self.design_diameter = self.penstock_diameter 
        else: # penstock diameter calculation based on head, flow, and length
            self.design_diameter = (4 * self.design_flow / (0.125 * 3.14 * (2 * g * self.head)**0.5))**0.5 # USBR 1986 equation
        
        self.Re = 4 * self.design_flow / (np.pi * self.design_diameter * nu)   


# Roughness

### I added this in this format because a user might want to add his/her own coefficientvalues

# Roughness
class RoughnessCoefficients:
    def __init__(self, material, darcyweisbach_epsilon, hazenwiliams_c, mannings_n):
        self.material = material
        self.darcyweisbach_epsilon = darcyweisbach_epsilon
        self.hazenwiliams_c = hazenwiliams_c
        self.mannings_n = mannings_n
    
    class Values:
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

class DW_RoughnessSelector(Roughness): # Darcy-Weisbach roughness selector
    def roughness_selector(self, material):
        roughness_coefficients = RoughnessCoefficients.Values()
        if material is not None:
            epsilon = roughness_coefficients.roughnesscoefficients[material].darcyweisbach_epsilon
        else:
            epsilon = roughness_coefficients.roughnesscoefficients['Steel'].darcyweisbach_epsilon
        return epsilon
    
class HW_RoughnessSelector(Roughness): # Hazen-Williams roughness selector
    def roughness_selector(self, material):
        roughness_coefficients = RoughnessCoefficients.Values()
        if material is not None:
            C = roughness_coefficients.roughnesscoefficients[material].hazenwiliams_c
        else:
            C = roughness_coefficients.roughnesscoefficients['Steel'].hazenwiliams_c
        return C

class DiameterCheck:
    def __init__(self, head_loss):
        self.head_loss = head_loss

    def maxheadloss_checker(self, hydraulic_parameters):
        if hydraulic_parameters.penstock_diameter is None:
            if self.head_loss > 0.1 * hydraulic_parameters.head:
                while self.head_loss > 0.1 * hydraulic_parameters.head:
                    hydraulic_parameters.design_diameter = hydraulic_parameters.design_diameter + 0.1 
                    hl = DarcyWeisbach()
                    hl.headloss_calculator(hydraulic_parameters)
                    hydraulic_parameters.penstock_diameter = hydraulic_parameters.design_diameter
                    self.head_loss = hydraulic_parameters.head_loss
        return self.head_loss


# Head loss calculation
class HeadLoss(ABC):   
    
    @abstractmethod
    def headloss_calculator(self, hydraulic_parameters):
        pass
     
class DarcyWeisbach(HeadLoss):

    def headloss_calculator(self, hydraulic_parameters):
                   
        epsilon = DW_RoughnessSelector().roughness_selector(material = hydraulic_parameters.penstock_material) # DW roughness factor
        D = hydraulic_parameters.design_diameter # Design diameter
        Re = hydraulic_parameters.Re # Reynolds number
        L = hydraulic_parameters.penstock_length # Penstock lenght
        V = hydraulic_parameters.flow / (np.pi * (D/2)**2) # V = Q/A

        if hydraulic_parameters.Re > 4000:
            ff = 0.25 / (np.log10((epsilon / 3.7 * D) + (5.74 / Re**0.9)))**2 # (Bhave, 1991)
        
        elif hydraulic_parameters.Re > 2000:
            AA= -1.5634601348517065795
            AB= 0.00328895476345399058690
            Y2 = (epsilon / 3.7 * D) + AB
            Y3 = -2 * np.log10(Y2)
            FA = Y3**-2
            FB = FA * (2 - (AA * AB / Y2 * Y3))
            X1 = 7*FA - FB
            X2 = 0.128 - 17*FA + 2.5*FB
            X3 = -0.128 + 13*FA - 2*FB
            X4 = 0.032 - 3*FA + 0.5*FB
            R =  Re/2000
            ff = X1 + R * (X2 + R * (X3 + R*X4)) # (Dunlop, 1991)
        else:
            ff = 64/Re # (Bhave, 1991)
        
        hydraulic_parameters.penstock_frictionfactor = ff
        head_loss =  ff * L * V**2 / D * 2 * g
        hydraulic_parameters.head_loss = head_loss

        # check that head loss does not exceed 10% of total head
        if hydraulic_parameters.penstock_diameter is None: 
            diametercheck = DiameterCheck(head_loss)
            head_loss = diametercheck.maxheadloss_checker(hydraulic_parameters)
            hydraulic_parameters.head_loss = head_loss
        
        # hydraulic_parameters.reynoldsnumber_calculator() # Calculate the Reynolds number again 
        # DarcyWeisbachPenstock().headloss_calculator(hydraulic_parameters)     
        # hydraulic_parameters.design_diameter = hydraulic_parameters.penstock_diameter

        return None        

class HazenWilliamns(HeadLoss):

    def headloss_calculator(self, hydraulic_parameters):
        C = HW_RoughnessSelector().roughness_selector(material = hydraulic_parameters.penstock_material) # HW roughness factor (C)
        D = hydraulic_parameters.design_diameter # Design diameter
        L = hydraulic_parameters.penstock_length # Penstock lenght
        Q = hydraulic_parameters.flow 
        
        head_loss = 10.67 * L * Q**1.852 / C**1.852 * D**4.87
        hydraulic_parameters.head_loss = head_loss
        
        if hydraulic_parameters.penstock_diameter is None:
            if head_loss > 0.1 * hydraulic_parameters.head:
                head_loss = 0.1 * hydraulic_parameters.head
                hydraulic_parameters.head_loss = head_loss
                D = (10.67 * L * Q**1.852 / (C**1.852 * head_loss))**(1 / 4.87) # D for head losses = 10% head
                hydraulic_parameters.penstock_diameter = D
        
        

        # if hydraulic_parameters.penstock_diameter is None: 
        #     diametercheck = DiameterCheck(head_loss)
        #     head_loss = diametercheck.maxheadloss_checker(hydraulic_parameters)
        #     hydraulic_parameters.head_loss = head_loss

        return None        

if __name__ == "__main__":
        
    hyd_param = HydraulicDesignParameters(flow = 2, design_flow = 2, head = 9, penstock_length = 150, penstock_diameter = None, 
                                          penstock_material = None, penstock_slope = None, penstock_frictionfactor = None,
                                          head_loss= None)
        
    hyd_param.reynoldsnumber_calculator() # Calculate the Reynolds number
    
    rc = RoughnessCoefficients.Values().roughnesscoefficients['Steel'].darcyweisbach_epsilon # Roughness coefficient

    # hl = DarcyWeisbach()
    # hl.headloss_calculator(hydraulic_parameters = hyd_param)
    
    hl = HazenWilliamns()
    hl.headloss_calculator(hydraulic_parameters = hyd_param)

    print("ReynoldsNumber:",hyd_param.Re)
    print("FrictionFactor",hyd_param.penstock_frictionfactor)
    print("PenstockDiameter:",hyd_param.penstock_diameter)
    print("Head Loss:",hyd_param.head_loss)
    # print("Head Loss:", turbine.h_f)

    # TODO: if penstock_diameter is None we need to call the function again with the updated parametes
    # to obtain the actual head_loss
    # I'm trying to set the following recursion inside the function
    
    # hl = DarcyWeisbachPenstock()
    # hyd_param.reynoldsnumber_calculator() # Calculate the Reynolds number
    # rc = RoughnessCoefficients.Values().roughnesscoefficients['Steel'].darcyweisbach_epsilon # Roughness coefficient
    # hl.headloss_calculator(hydraulic_parameters = hyd_param)
    # print("\nReynoldsNumber:",hyd_param.Re)
    # print("FrictionFactor",hyd_param.penstock_frictionfactor)
    # print("PenstockDiameter:",hyd_param.penstock_diameter)
    # print("Head Loss:",hyd_param.head_loss)
