<img align="right" width = 300 src="docs/images/HG_horizontal.png" alt="HydroGenerate">

# HydroGenerate <br>


## About

**HydroGenerate** is an open-source python library that has the capability of estimating hydropower generation based on flow rate either provided by the user or received from United States Geological Survey (USGS) water data services. The tool calculates the efficiency as a function of flow based on the turbine type either selected by the user or estimated based on the “head” provided by the user.

For more information please refer to the [OSTI webpage](https://www.osti.gov/biblio/1829986).

## Installation Instructions

**HydroGenerate** is offered as a python package. This means that the classes and utilities can be used anywhere in your system, without risks of making unwanted changes to the core code in the repo, issues with finsing the module in path, etc.

### For Basic Usage

**HydroGenerate** can be installed by downloading the source code from GitHub or via the PyPI package manager using pip.

For those interested only in using the code, the simplest way to obtain it is with pip by using this command:

```
pip install HydroGenerate
```

### For developers

1. Clone the repo:

```
git clone git@github.com:IdahoLabResearch/HydroGenerate.git
cd HydroGenerate
```

2. It is recommended that a dedicated conda environment be created for developing/using this repo and prior to the installation below. 

```
conda create --name hat-env python=3.6
```

To activate the environment, execute the following command:

```
conda activate hat-env
```

3. Install the package in your environment:

```
pip install -e .
```

**Optional**

4. Install jupyter lab in your new environment
```
conda install -c conda-forge jupyterlab
```

**Authors**
```
Juan Gallego-Calderon

Camilo J. Bastidas Pacheco

Soumyadeep Nag

Bhaskar Mitra

Shiloh Elliott

Thomas M. Mosier
```

**Citation**

If you are using our repository kindly use the following citation format(s).

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

_Chicago_

```

Mitra, Bhaskar, Gallego-Calderon, Juan F., Elliott, Shiloh N, Mosier, Thomas M, Bastidas Pacheco, Camilo Jose, and USDOE Office of Energy Efficiency and Renewable Energy. Hydrogenerate: Open Source Python Tool To Estimate Hydropower Generation Time-series. Computer software. Version 3.6 or newer. October 19, 2021. https://www.osti.gov//servlets/purl/1829986. doi:https://doi.org/10.11578/dc.20211112.1.

```

_APA_

```

Mitra, Bhaskar, Gallego-Calderon, Juan F., Elliott, Shiloh N, Mosier, Thomas M, Bastidas Pacheco, Camilo Jose, & USDOE Office of Energy Efficiency and Renewable Energy. (2021, October 19). Hydrogenerate: Open Source Python Tool To Estimate Hydropower Generation Time-series (Version 3.6 or newer) [Computer software]. https://www.osti.gov//servlets/purl/1829986. https://doi.org/10.11578/dc.20211112.1

```

_MLA_

```

Mitra, Bhaskar, Gallego-Calderon, Juan F., Elliott, Shiloh N, Mosier, Thomas M, Bastidas Pacheco, Camilo Jose, and USDOE Office of Energy Efficiency and Renewable Energy. Hydrogenerate: Open Source Python Tool To Estimate Hydropower Generation Time-series. Computer software. https://www.osti.gov//servlets/purl/1829986. Vers. 3.6 or newer. USDOE Office of Energy Efficiency and Renewable Energy (EERE). 19 Oct. 2021. Web. doi:10.11578/dc.20211112.1.

```


