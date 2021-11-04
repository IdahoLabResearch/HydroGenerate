# HydropGenerate

## Installation Instructions

The HydroGenerate is offered as a python package. This means that the classes and utilities can be used anywhere in your system, without risks of making unwanted changes to the core code in the repo, issues with finsing the module in path, etc.

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
conda activate hat_env
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
