# Quick Start

**HydroGenerate** can be installed in your local environment using `pip install HydroGenerate`. 

## Basic usage

In its most basic usage, the user needs to provide one value of flow in cubic-ft-sec (cfs) and head (ft). The function `calculate_hp_potential` is the main interface for the hydropower potential calculation using different types of inputs (float, numpy array, and pandas dataframe), and several attributes. More advance usage can be found in the user guide.

```
# Local imports
from HydroGenerate.hydropower_potential import *

# Calculate power from a given head and flow
flow = 8000 # given flow, in cfs
head = 20 # head, in ft
power = None

hp = calculate_hp_potential(flow= flow, 
                            head= head, 
                            rated_power= power)

print("Hydropower potential is {} kW".format(round(hp.rated_power, 0)))
```

The results are returned in an object with multiple attributes. In the example above, `hp.power` gives the estimated potential for the given flow and head. If a time-series is provided, then a time-series of power will be available.

## Time-series usage

HydroGenerate truly shines when used with a time-series. The tool can be used in several applications such as dispatch optimization of hydropower hybrids, techno-economic assessment, nation-wide resource assesment, etc. The best way to utilize the time-series capabilities is through a **pandas dataframe**.

```
# Local imports
from HydroGenerate.hydropower_potential import *
import pandas as pd

flow_df = pd.read_csv('./examples/test_flow.csv')
head = 20 # head, in ft
power = None

hp = calculate_hp_potential(flow=flow_df.copy(),  
                            rated_power= power, 
                            head= head,
                            hydropower_type= 'Diversion',
                            flow_column= 'discharge_cfs', 
                            annual_caclulation= True)

# Get the rated power from the hp object
name_plate_capacity = round(hp.rated_power, 0)
print(name_plate_capacity)

# Print the resulting time-series
print(hp.dataframe_output)
```