# Installation

**HydroGenerate** is offered as a python package. This means that the classes and utilities can be used anywhere in your system, without risks of making unwanted changes to the core code in the repo, issues with finding the module in path, etc.

## For basic usage

**HydroGenerate** can be installed by downloading the source code from GitHub or via the PyPI package manager using pip.

For those interested only in using the code, the simplest way to obtain it is with pip by using this command:

```
pip install HydroGenerate
```

For a quick start guide, follow the steps in the **Quick start** page. 

## For developers

1. Clone the repo:

```
git clone git@github.com:IdahoLabResearch/HydroGenerate.git
cd HydroGenerate
```

2. It is recommended that a dedicated conda environment be created for developing/using this repo and prior to the installation below. 

```
conda create --name hydro-gen python=3.6
```

To activate the environment, execute the following command:

```
conda activate hydro-gen
```

3. Install the package in your environment:

```
cd HydroGenerate
pip install -e .
```

**Optional**

4. Install jupyter lab in your new environment to run the examples provided in `./examples`
```
conda install -c conda-forge jupyterlab
```

5. Install the package `dataretrieval` in your new environment to use streamflow data from a USGS stream gauge.

```
pip install dataretrieval
```