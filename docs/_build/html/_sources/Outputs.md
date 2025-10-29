## Table 2: List of HydroGenerate outputs, definition, variable type, and units.

|	#	|	Variable Name	|	Definition	|	Type	|	Options	|	Units (US)	|	Units (SI)	|
|	:---	|	:---:	|	:---:	|	:---:	|	:---:	|	:---:	|	---:	|
|	1	|	annual_dataframe_output	|	Dataframe with annual summary	|	Pandas dataframe	|	-	|	-	|	-	|
|	2	|	annual_om	|	Annual operation and maintennance cost	|	Numeric	|		|	Million $	|	Million $	|
|	3	|	capacity_factor	|	Hydropower plant capacity factor	|	Numeric	|	0 - 1	|	-	|	-	|
|	4	|	channel_average_velocity	|	Average water velocity in a channel. 	|	numeric	|	-	|	ft/s	|	-	|
|	5	|	dataframe_output	|	Dataframe with power and efficiency for each value of flow	|	Pandas dataframe	|	-	|	-	|	-	|
|	6	|	design_flow	|	Flow used for designing the hydropower system	|		|	-	|	cfs	|	m3/s	|
|	7	|	electricity_sell_price	|	Electricity sell price	|	Numerical	|	-	|	$/KW	|	$/KW	|
|	8	|	flow	|	Volume of water over time. Flow rate.	|	Numerical, series.	|	-	|	cfs	|	m3/s	|
|	9	|	flow_column	|	Name of the column that contains the flow data, if reading from a CSV file	|	String	|	-	|	-	|	-	|
|	10	|	flowduration_curve	|	Cumulative frequency curve that shows the percent of time specified discharges were equaled or exceeded during a given period	|	Pandas dataframe	|	-	|	cfs	|	m3/s	|
|	11	|	generator_efficiency	|	Efficiency of the hydroelectric generator.	|	Numerical / Percent	|	1 - 100	|		DL		|
|	12	|	head	|	A measure of liquid pressure, expressed in terms of the height of a column of water. Change in water levels between the intake and the discharge point.	|	Numerical	|	-	|	ft	|	m	|
|	13	|	head_loss	|	Energy lost as water flow.	|	Numerical	|	-	|	ft	|	m	|
|	14	|	hk_blade_diameter	|	Hydrokinetic turbine blade diameter	|	Numerical	|	-	|	ft	|	m	|
|	15	|	hk_blade_heigth	|	Hydrokinetic turbine blade height	|	Numerical	|	-	|	ft	|	m	|
|	16	|	hk_blade_type	|	Hydrokinetic turbine blade type	|	Numerical	|	ConventionalRotor, H-DarrieusRotor, DarrieusRotor	|	-	|	-	|
|	17	|	hk_swept_area	|	Hydrokinetic turbine blades swept area	|	Numerical	|	-	|	ft2	|	m2	|
|	18	|	hydropower_type	|		|		|		|		|		|
|	19	|	icc	|	Initial capital cost	|	Numeric	|		|	Million $	|	Million $	|
|	20	|	max_headloss_allowed	|	Maximum head loss allowed in the penstock	|	Numerical / Percent	|	1 - 100	|	-	|	-	|
|	21	|	n_operation_days	|	Number of days a year a hydroelectric plant operates	|	Numerical	|	1 - 365	|	-	|	-	|
|	22	|	net_head	|	Net hydraulic head	|	Numerical	|	-	|	ft	|	m	|
|	23	|	pctime_runfull	|	Percent of time a turbine runs full	|	Numerical / Percent	|	-	|	-	|	-	|
|	24	|	pelton_n_jets	|	Number of jets in a Pelton turbine	|	Numerical	|	-	|	-	|	-	|
|	25	|	penstock_design_diameter	|	Diameter of the penstock, calculated for the design flow	|	Numerical	|	-	|	ft	|	m	|
|	26	|	penstock_design_headloss	|	Head losses in the penstock at design flow.	|	Numerical	|	-	|	ft	|	m	|
|	27	|	penstock_diameter	|	Penstock diameter	|	Numerical	|	-	|	ft	|	m	|
|	28	|	penstock_frictionfactor	|	Penstock friction factor	|	Numerical	|	-	|	-	|	-	|
|	29	|	penstock_headloss_calculation	|	Indicator of whether head lossess in the penstock were calculated or not.	|	Boolean	|	-	|	-	|	-	|
|	30	|	penstock_headloss_method	|	Method for allowing users to select a specific method for head loss	|	String	|	Darcy-Weisbach (default), Hazen-Williams.	|	-	|	-	|
|	31	|	penstock_length	|	Penstock length	|	Numerical	|	-	|	ft	|	m	|
|	32	|	penstock_material_o	|	Penstock material	|	String	|	CastIron, Concrete, GalvanizedIron, Plastic, Steel	|	-	|	-	|
|	33	|	power	|	Power output for different values of flow	|	Series	|		|	KW	|	KW	|
|	34	|	rated_power	|	Power output at design flow, nameplace capcity	|	Numerical	|	-	|	kW	|	kW	|
|	35	|	resource_category	|	Type of hydroelectryc project category	|	String	|	NewStream-reach, Non-PoweredDam, CanalConduit, UnitAddition, GeneratorRewind	|	-	|	-	|
|	36	|	runner_diameter	|	Turbine runner diameter	|	Numeric	|	-	|	ft	|	m	|
|	37	|	system_efficiency	|	Total efficiency of the system. Total efficiency = turbine efficieincy * generator efficiency	|	Numerical / Percent	|	1 - 100	|		DL*		|
|	38	|	turbine_efficiency	|	Efficiency of the turbine for different flow values	|	Numerical / Percent	|	1 - 100	|		DL		|
|	39	|	turbine_flow	|	Flow that passed through the turbine	|	Series	|	-	|	cfs	|	m3/s	|
|	40	|	turbine_type_o	|	Type of turbine used in the system.	|	String	|	Kaplan, Francis, Propellor, Pelton, Turgo, Crossflow	|	-	|	-	|


* DL: dimensionless. 