# Methods, Functions, Classes, and Input Handling
This section includes detials on input handling, and describes all exisitng funcitons, methods, and classes to inform future contributors.

## Input Handling
{numref}`HG_InputH` shows how input parameters are handled in **_HydroGenerate_**. For details on inputs and outputs, data types, units, and a general view of the workflow visit [](UserGuide_7_HydroGenerateWorkflow.md). 

```{figure} HG_Inputs.SVG
---
name: HG_InputH
---
Input Handling
```

## Computations Workflow, methods, functions, and classes
{numref}`DetWorkflow` shows methods, functions, and classes avaliable in **_HydroGenerate_**.

```{figure} DetailedWorkflow.SVG
---
name: DetWorkflow
---
Computations Workflow, methods, functions, and classes
```

## Classes, methods, and functions implemented in HydroGenerate

##### Table 4: Description of classes, methods, and functions implemented in HydroGenerate. 

|	Name	|	Type	|	Functionality	|
|	:---	|	:---:	|	:---:	|
|	TurbineParameters	|	Class	|	Initializes parameters needed for turbine calculation	|
|	turbine_type_selector	|	Function	|	Selects a turbine type based on head.	|
|	FlowRange:	|	Class	|		|
|	flowrange_calculator	|	Method in FlowRange	|	Creates a flow range from half the value of flow to the flow provided. This flow range is used to evaluate the efficiency of a turbine for flows below the design flow when a time series is not available	|
|	ReactionTurbines	|	Class	|		|
|	Runnersize_calculator	|	Method in reaction turbines	|	Computes the runner diameter for reaction turbines	|
|	Turbine	|	Abstract class	|	Enforces the method turbine_calculator	|
|	FrancisTurbine, KaplanTurbine, PropellorTurbine, TurgoTurbine, CrossFlowTurbine,	|	Class Turbine	|	Compute all parameters related to each turbine type	|
|	Hydrokinetic_turbine	|		|		|
|	DesignFlow	|	Abstract class	|	Enforces the designflow_calculator method	|
|	PercentExceedance	|	Class DesignFlow	|	Computes the design flow for a series of flow and a given percent of exceedance	|
|	HydraulicDesignParameters	|	Class	|	Initializes parameters needed for hydraulic computations	|
|	RoughnessCoefficients	|	Class	|	Contains the roughness coefficients for a selected set of materials.	|
|	add_roughnesscoefficient_values	|	Method in RoughnessCoefficiencts	|	Allows adding additional roughness coefficients	|
|	Roughness	|	Abstract class	|	Enforces the roughness_selector method	|
|	DW_RoughnessSelector, HW_RoughnessSelector,	|	Class Roughness	|	Select roughness coefficient for a given material and head loss method. DW: Darcy-Weisbach. HW: Hazen-Williams.	|
|	Manning_ RoughnessSelector	|		|		|
|	DW_FrictionFactor	|	Class	|		|
|	frictionfactor_calculator	|	Method in DW_FrictionFactor	|	Computes Darcy-Weisbach friction factor depending on Reynolds number.	|
|	HeadLoss	|	Abstract class	|	Enforces the penstock_headloss_calculator method	|
|	DarcyWeisbach, HazenWilliamns	|	Method	|	Computes head losses in the	|
|	EconomicParameters	|	Class	|	Initializes parameters needed for economic computations	|
|	merge_instances	|	Function	|	Merges the parameters of multiple classes	|
|	calculate_head	|	Function	|	Calculates the head required for certain power and flow value	|
|	pd_checker	|	Function	|	Checks if flow is a pandas dataframe	|
|	Units	|	Class	|	Contains methods for unit conversion	|
|	us_to_si_conversion, si_to_us_conversion	|	Methods in Units	|	Convert units from US to international system (SI).	|
|	Hydropower	|	Abstract class	|	Enforces the hydropower_calculation method	|
|	Basic,	|	Method in Hydropower	|	Computes hydropower potential under each onfiguration	|
|	Diversion,	|		|		|
|	Hydrokinetic	|		|		|
|	Cost	|	Abstract class	|	Enforces the cost_calculation method	|
|	ONRL_BaselineCostModeling_V2	|	Method in Cost	|	Computes cost using the Oak Ridge National Laboratory Baseline Cost modelling equations	|
|	Revenue	|	Abstract class	|	Enforces the revenue_calculation method	|
|	ConstantEletrictyPrice,	|		|	Compute revenue	|
|	ConstantEletrictyPrice_pd	|		|		|
|	calculate_hp_potential	|	Function	|	Performs all computation and executes existing functions depending on parameters	|
|	flow_efficiency_plot	|	Function	|	Plot turbine efficiency as a function of flow	|
|	flow_efficiency_power_plot	|	Function	|	Plot power and turbine efficiency as a function of flow	|
|	turbine_type_plot	|	Function	|	Plot turbine selection information	|
|	flow_duration_curve_plot	|	Function	|	Plot the flow-duration curve	|
|	plant_capfactor_plot	|	Function	|	Plot monthly capacity fator summary	|
|	plant_turbineflow_plot	|	Function	|	Plot monthly turbine flow summary	|
|	plant_elecgeneration_plot	|	Function	|	Plot monthly electricity generation summary |
|	FlowPreProcessingParameters	|	Class	|	Initializes parameters needed for flow preprocessing |
|   FlowPreProcessing	|	Class	|	Contains methods for flwo preprocessing	|
|	max_turbineflow_checker	|	Function	|	Checks that flow is not larger than design flow	|
|	min_turbineflow_checker	|	Function	|	Checks that flow is not less than minimum turbine flow	|
|   annual_maintenance_implementer	|	Function	|	Implements annual maintenance   |
|   major_maintenance_implementer	|	Function	|	Implements major maintenance    |