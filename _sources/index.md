# HydroGenerate: Hydropower Potential Estimation

**HydroGenerate** is an open-source python library that has the estimates hydropower generation based on head height and flow rate either provided by the user or received from United States Geological Survey (USGS) water data services. The tool calculates the efficiency as a function of flow based on the turbine type either selected by the user or estimated based on the “head” provided by the user.

## Quick Start

**HydroGenerate** can be installed in your local environment using `pip install HydroGenerate`. In its most basic usage, the user needs to provide one value of flow in cubic-ft-sec (cfs) and head (ft). The function `calculate_hp_potential` is the main interface for the hydropower potential calculation using different types of inputs (float, numpy array, and pandas dataframe), and several attributes. More advance usage can be found in the user guide.

```
# Local imports
from HydroGenerate.hydropower_potential import *

# 1.1) Calculate power from a given head and flow
flow = 8000 # given flow, in cfs
head = 20 # head, in ft
power = None

hp = calculate_hp_potential(flow= flow, 
                            head= head, 
                            rated_power= power)

print("Hydropower potential is {} kW".format(round(hp.rated_power, 0)))
```

The results are returned in an object with multiple attributes. In the example above, `hp.power` gives the estimated potential for the given flow and head. If a time-series is provided, then a time-series of power will be available.

## Giving credit

HydroGenerate was built with support from the USDOE Office of Energy Efficiency and Renewable Energy (EERE). For more information please refer to the [OSTI webpage](https://www.osti.gov/biblio/1829986).

**Authors**
```
Bhaskar Mitra

Juan Gallego-Calderon

Shiloh Elliott

Thomas M. Mosier

Camilo J. Bastidas Pacheco
```

**Citation**

If you are using our repository kindly use the following citation format.

_Bibtex_
```

@misc{osti_1829986,
title = {Hydrogenerate: Open Source Python Tool To Estimate Hydropower Generation Time-series, Version 3.6 or newer},
author = {Mitra, Bhaskar and Gallego-Calderon, Juan F. and Elliott, Shiloh N and Mosier, Thomas M and Bastidas Pacheco, Camilo Jose and USDOE Office of Energy Efficiency and Renewable Energy},
abstractNote = {Hydropower is one of the most mature forms of renewable energy generation. The United States (US) has almost 103 GW of installed, with 80 GW of conventional generation and 23 GW of pumped hydropower [1]. Moreover, the potential for future development on Non-Powered Dams is up to 10 GW. With the US setting its goals to become carbon neutral [2], more renewable energy in the form of hydropower needs to be integrated with the grid. Currently, there are no publicly available tool that can estimate the hydropower potential for existing hydropower dams or other non-powered dams. The HydroGenerate is an open-source python library that has the capability of estimating hydropower generation based on flow rate either provided by the user or received from United States Geological Survey (USGS) water data services. The tool calculates the efficiency as a function of flow based on the turbine type either selected by the user or estimated based on the “head” provided by the user.},
url = {https://www.osti.gov//servlets/purl/1829986},
doi = {10.11578/dc.20211112.1},
url = {https://www.osti.gov/biblio/1829986}, year = {2021},
month = {10},
note =
}

```
