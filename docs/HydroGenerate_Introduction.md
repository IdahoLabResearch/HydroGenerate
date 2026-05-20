# HydroGenerate

## Introduction

**HydroGenerate** is an open-source python library that estimates hydropower generation based on head height and flow rate for different types of hydropower:impoundment, diversion, and hydrokinetic. Additional features allow the user to retrieve instantaneous flow from United States Geological Survey (USGS) water data services stream gages where available. The tool calculates the turbine efficiency as a function of flow based on the turbine type either selected by the user or estimated based on the “head” provided by the user. Some of the additional features are:

- In the power calculation, the net hydraulic head is conisidered. Where penstock dimameter is available, the user can select from several methods (see thr **User Guide** for more details). If the penstock diameter is not known, HG will calculate a diameter that will limit head losses to 10% (default) of the available head.
- For power extraction from kinetic energy, the available head is the velocity head.
- HydroGenerate uses a simplified configuration consisting of one penstock, turbine, and generator.
- The user can specify a set of flow constraints as a proxy of hydropower operation. Otherwise, the results are the **maximum technical potential**.
- When a flow-time series is available, HydroGenerate computes at every time-step, the generated power, capacity factor, and annual energy production (AEP).
- Using publicly available CAPEX and OPEX data for hydropower, HydroGenerate performs a "light" techno-economic analysis of turbine configuration based on the nameplate capacity. Furthermore, the LCOE is computed using the wholesale electricity price as an user input.



## Giving credit

HydroGenerate was built with support from the USDOE Office of Energy Efficiency and Renewable Energy (EERE). For more information please refer to the [OSTI webpage](https://www.osti.gov/biblio/1829986).

**Authors**
```
Camilo J. Bastidas Pacheco

Juan Gallego-Calderon

Soumyadeep Nag

Bhaskar Mitra

Shiloh Elliott

Thomas M. Mosier

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
