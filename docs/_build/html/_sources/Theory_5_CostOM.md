# Cost, O&M, and Revenue Calculation

## Cost and O&M
Cost and O&M are calculated using the _Hydropower Baseline Cost Modeling, Version 2_ models (ORNL, 2015).


##### Initial Capital Cost (ICC)
Cost for hydropower project is calcualted using the following equations (ORNL, 2015):

|	#	|	Resource Category (HG)   |	Cost Model Equation *	|
|	:---	|	:---:	|	:---:	|
|	1	|	'Non-PoweredDam'	|	$ICC = 11,489,245 P^{0.976} H^{-0.240}$	|	
|	2	|	'NewStream-reach'	|	$ICC = 9,605,245 P^{0.977} H^{-0.126}$	|	
|	3	|	'CanalConduit'	|	$ICC = 9,297,820 P^{0.810} H^{-0.102}$	|	
|	4	|	'PSH_ExistingInfrastructure'	|	$ICC = 3,008,246 P e^{-0.000460P}$	|	
|	5	|	'PSH_Greenfield'	|	$ICC = 8,882,655 P e^{-0.000776P}$	|	
|	6	|	'UnitAddition'	|	$ICC = 4,163,746 P^{0.741}$	|	
|	7	|	'GeneratorRewind'	|	$ICC = 250,147 P^{0.817}$	|	

* ICC in 2014$; P in MW; H in ft. 

Taken from ORNL, (2015). 


##### Operation and Maintennance (O&M)

O&M costs are calcualted using the following equation:

$$Annual O\&M (2014\$) = 225,417 P^{0.547}$$

The _Hydropower Baseline Cost Modeling, Version 2_ report (ORNL, 2015) recommends using the lesser of 2.5% of ICC or the result of the equation above. This recommendation is implemented in HG. 

## Revenue
Revenue is computed assuming a unique electricty price. The default is 0.0582 $/kW, which is the average wholesale electricity price in 2023 https://www.eia.gov/electricity/wholesale/

## References
Oak Ridge Natiional Laboratory, 2015. Hydropower Baseline Cost Modeling, Version 2. https://info.ornl.gov/sites/publications/files/Pub58666.pdf