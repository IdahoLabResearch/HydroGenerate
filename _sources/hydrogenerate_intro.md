# Getting started

HG can currently compute hydropower under three hydropower types: Basic, Diversion, and Hydrokinetic. The file HydroGenerate_Workflow.ipynb included in the HG’s GitHub repository (https://github.com/IdahoLabResearch/HydroGenerate/blob/main/examples/HydroGenerate_Workflow.ipynb) walks used through these three calculations.  

Basic hydropower calculation: 

Required inputs: Hydraulic head, flow, rated power. In the basic calculation mode, users can input two of these three variables and HG will calculate the third.  

Diversion 

Required inputs: Hydraulic head, flow. 

Optional inputs: all the inputs listed in Table 1, except those used only for hydrokinetic estimations. 

Computation Steps:  

Compute head losses: the procedure and available options for head loss calculation in HG for each type of hydropower estimation is described in Appendix A Head Loss Calculations. 

Select the turbine type: Based on the net hydraulic head, HG will suggest a recommended turbine type by following 3.  

Define the design flow (Qd). The procedure for this step is explained in Appendix B Design Flow Selection. 

Compute the efficiency of the turbine at flows above and below the design flow and estimate power for the value (s) of flow provided the user. Turbine efficiency is calculated following the methodology presented in the Clean Energy Project Analysis electronic textbook ​(CANMET Energy Technology Center, 2004)​ (included in Appendix C Turbine Efficiency Calculation) 

Compute the overall efficiency of the system. The overall efficiency of the system is computed as the turbine efficiency (calculated in step 4) times the Generator efficiency.  

Compute estimated power potential using Equation 1. 

Compute all economic parameters (O&M, initial capital cost, revenue). 

Output: the list of outputs will depend on the inputs used. In the most complete case, the output list includes all the variables listed in Table 2, except for those resulting from hydrokinetic calculations. 