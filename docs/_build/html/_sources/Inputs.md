## Table 1:  List of HydroGenerate inputs, definition, variable types, option, and units.



|	#	|	Variable Name	|	Definition	|	Type	|	Options	|	Required	|	Needed to calculate	|	Units (US)	|	Units (SI)	|
|	:---	|	:---:	|	:---:	|	:---:	|	:---:	|	:---:	|	:---:	|	:---:	|	---:	|
|	1	|	flow	|	Volume of water over time. Flow rate.	|	Numerical, series, pandas dataframe with DateTime index	|	-	|	yes	|	All calculations	|	cfs	|	m3/s	|
|	2	|	head	|	A measure of liquid pressure, expressed in terms of the height of a column of water. Change in water levels between the intake and the discharge point.	|	Numerical	|	-	|	yes	|	All calculations	|	ft	|	m	|
|	3	|	rated_power	|	Power output at design flow, nameplace capacity	|	Numerical	|	-	|	no	|	-	|	kW	|	kW	|
|	4	|	Hydropower_type	|	Type of hydropower calculation	|	String	|	Basic, Diversion, Hydrokinetics	|	yes, has default	|	All calculations	|	-	|	-	|
|	5	|	units	|	Units system	|	String	|	US, IS	|	yes, has default	|	All calculations	|	-	|	-	|
|	6	|	penstock_headloss_method	|	Method for allowing users to select a specific method for head loss	|	String	|	Darcy-Weisbach (default), Hazen-Williams.	|	yes, has default	|	Net head	|	-	|	-	|
|	7	|	design_flow	|	The flow rate for which the hydro turbine is designed	|	Numerical	|	-	|	no	|	Power calculation	|	cfs	|	m3/s	|
|	8	|	system_efficiency_o	|	Overal efficiency of the system	|	Percent	|	1 - 100	|	-	|	-	|		DL		|
|	9	|	generator_efficiency	|	Efficiency of the hydroelectric generator.	|	Percent	|	1 - 100	|	yes, has default	|	Power calculation	|		DL		|
|	10	|	turbine_type	|	Type of turbine used in the system.	|	String	|	Kaplan, Francis, Propellor, Pelton, Turgo, Crossflow	|	no	|	Efficiency	|	-	|	-	|
|	11	|	head_loss	|	Energy lost as water flow.	|	Numerical	|	-	|	no	|	Net head	|	ft	|		|
|	12	|	penstock_headloss_calculation	|	Variable used to indicate when to calculate head loss in the penstock	|	Boolean	|	-	|	yes, has default	|	Net head	|	-	|	-	|
|	13	|	penstock_length	|	Penstock length	|	Numerical	|	-	|	yes, if calculating head loss in the penstock.	|	Net head	|	ft	|	m	|
|	14	|	penstock_diameter	|	Penstock diameter	|	Numerical	|	-	|	no	|	Net head	|	ft	|	m	|
|	15	|	penstock_material	|	Penstock material	|	String	|	CastIron, Concrete, GalvanizedIron, Plastic, Steel	|	no	|	Net head	|	-	|	-	|
|	16	|	penstock_frictionfactor	|	Penstock friction factor	|	Numerical	|	-	|	no	|	Net head	|		DL		|
|	17	|	pctime_runfull	|	Percent of time a turbine runs full	|	Numerical / Percent	|		|	no	|	Design flow	|		|	-	|
|	18	|	max_headloss_allowed	|	Maximum head loss allowed in the penstock	|	Percent	|	1 - 100	|	yes, has default	|	Net head	|	ft	|	-	|
|	19	|	turbine_Rm	|	Turbine manufacture/design coefficient	|	Numerical	|		|	no	|	Turbine efficiency	|	-	|	-	|
|	20	|	pelton_n_jets	|	Number of jets in a Pelton turbine	|	Numerical	|	-	|	no	|	Turbine efficiency	|	-	|	-	|
|	21	|	flow_column	|	Name of the column that contains the flow data, if reading from a CSV file	|	String	|	-	|	yes, if reading flow data from a CSV	|	All calculations	|	-	|	-	|
|	22	|	channel_average_velocity	|	Channel average cross section velocity	|	Numerical	|		|	yes, for hydrokinetics	|	Hydrokinetics	|	-	|	-	|
|	23	|	hk_blade_diameter	|	Hydrokinetic turbine blade diameter	|	Numerical	|	-	|	no	|	Hydrokinetics	|	-	|	-	|
|	24	|	hk_blade_heigth	|	Hydrokinetic turbine blade height	|	Numerical	|	-	|	no	|	Hydrokinetics	|	-	|	-	|
|	25	|	hk_blade_type	|	Hydrokinetic turbine blade type	|	Numerical	|	ConventionalRotor, H-DarrieusRotor, DarrieusRotor	|	no	|	Hydrokinetics	|	-	|	-	|
|	26	|	hk_swept_area	|	Hydrokinetic turbine blades swept area	|	Numerical	|	-	|	no	|	Hydrokinetics	|	-	|	-	|
|	27	|	annual_caclulation	|	Method for allowing users to turn off annual parameter’s calculation	|	Boolean	|		|	no	|	Annual energy generated / Revenue	|	-	|	-	|
|	28	|	resource_category	|	Type of hydroelectryc project category	|	String	|	NewStream-reach, Non-PoweredDam, CanalConduit, UnitAddition, GeneratorRewind	|	yes, has default	|	Initial capital cost / O&M	|	-	|	-	|
|	29	|	electricity_sell_price	|	Electricity sell price	|	Numerical	|	-	|	yes, has default	|	Revenue	|	$/KW	|	$/KW	|
|	30	|	cost_calculation_method	|	Method for selecting between cost calculation methods	|	String	|	ORNL_HBCM	|		|		|	-	|	-	|
|	31	|	capacity_factor	|	Hydropower plant capacity factor	|	Numeric	|	0 - 1	|	-	|	-	|	-	|	-	|
|	32	|	n_operation_days	|	Number of days a year a hydroelectric plant operates	|	Numerical	|	1 - 365	|	no	|	Annual energy generated / Revenue	|	-	|	-	|

* DL: dimensionless.


