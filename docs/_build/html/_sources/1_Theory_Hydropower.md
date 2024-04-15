# Hydropower Calculation

Hydrogenerate (HG) canculates hydropower potential using 

$$P = n \times \gamma \times Q \times H$$

where,  

* $P$ is the hydropower potential (watt),  
* $n$ is the overall system efficiency (dimensionless),  
* $\gamma$ is the specific weight of water (9,810 N/m^3), 
* $Q$ is the flow (m^3/s), and  
* $H$ is the net hydraulic head (m). 

HG uses a simplified configuration, consisting of one penstock, turbine, and generator. The turbine type is selected based on head and the elements are sized for a design flow that can be entered by the user or computed in HG, using flow data. The efficiency of the turbine at flows below or above the design flow is then computed using a set of empirical equations for each turbine type (CANMET, 2004). 

HG considers the streamflow provided by the user to be the flow routed through the hydropower plant. In some instances, e.g., multi-purpose operation reservoir, the amount of flow routed through the power system, and its operation, obey different priorities and must be analyzed outside HG to compute the flow available for hydropower generation. The considerations and analyses needed to generate the available-for-hydropower flow are outside the scope of the current version of HG. 
For hydrokinetic generation, HG will estimate the potential of installing a single turbine. Users can use this single turbine estimate as a reference value for single installations or understand the type of setup needed to meet their energy needs. Computing the power available in hydrokinetic assessment requires data on the velocity of water. 
In HG, the user can set the units to United States Customary (US), the default, or metric (IS) depending on the data available. However, all internal computations in HG are conducted using the metric system for units and values are converted accordingly.

### HG Workflow. Traditional hydropower. 
HG can currently compute hydropower under three hydropower types: Basic, Diversion, and Hydrokinetic. The file HydroGenerate_Workflow.ipynb included in the HG’s GitHub repository (https://github.com/IdahoLabResearch/HydroGenerate/blob/main/examples/HydroGenerate_Workflow.ipynb) walks used through these three calculations. 

### Basic hydropower calculation:
Required inputs: Hydraulic head, flow, rated power. In the basic calculation mode, users can input two of these three variables and HG will calculate the third. 

### Diversion
Required inputs: Hydraulic head, flow.
Optional inputs: all the inputs listed in Table 1, except those used only for hydrokinetic estimations.

Computation Steps: 
1. Compute head losses
2. Select the turbine type: Based on the net hydraulic head, HG will suggest a recommended turbine type by following step 3. 
3. Define the design flow ($Q_d$). 
4. Compute the efficiency of the turbine at flows above and below the design flow and estimate power for the value (s) of flow provided the user. Turbine efficiency is calculated following the methodology presented in the Clean Energy Project Analysis electronic textbook (CANMET Energy Technology Center, 2004) 
5. Compute the overall efficiency of the system. The overall efficiency of the system is computed as the turbine efficiency (calculated in step 4) times the Generator efficiency. 
6. Compute estimated power potential using Equation 1.
7. Compute all economic parameters (O&M, initial capital cost, revenue).

Output: the list of outputs will depend on the inputs used. In the most complete case, the output list includes all the variables listed in Table 2, except for those resulting from hydrokinetic calculations.

### Hydrokinetics
For hydrokinetic assessments the only required input is the average velocity in the river section. Additionally, the users can select among different hydrokinetic turbine types and vary the dimensions to evaluate energy potential.
For hydrokinetic estimations, when replacing the net hydraulic head by the velocity head, we obtain:

$$P=n\ast\rho\ast Q\ast\ \frac{V^2}{2}$$

Replacing $Q=V\times\ A_b$, we obtain:

$$P=\frac{1}{2}n\ast\rho\ast A_b\ast V^3$$

Where 
* $\rho$ is the density of water, in Kg/m^3,
* A_b is the swept area of blades, in m^2, and 
* V is the velocity of water, in m/s. 

The maximum energy that can be removed from flow is limited to approximately 59%; this value is commonly known as the Betz limit (Betz, 2014). Replacing n with 0.59 allow us to compute the maximum energy that could be generated for a turbine of a given area:

$$P=0.295\ast\rho\ast A_b\ast V^3$$

The average channel velocity value introduced by the user is directly used in this equation. The swept area of blades is computed for each turbine type and dimensions given. Niebuhr et al., (2019) provides a review of existing hydrokinetic turbine types. The turbine types and default sizes included in HG were derived from Niebuhr et al., (2019) and brochures of existing hydrokinetic turbines.

## References 
DOE. (2023). Types of Hydropower Plants | Department of Energy. https://www.energy.gov/eere/water/types-hydropower-plants 

Hadjerioua, Boualem, Wei, Yaxing, and Kao, Shih-Chieh. An Assessment of Energy Potential at Non-Powered Dams in the United States. United States: N. p., 2012. Web. https://doi.org/10.2172/1039957 

U.S. Bureau of Reclamation. (2011). Hydropower Resource Assessment at Existing Reclamation Facilities. https://www.usbr.gov/power/AssessmentReport/USBRHydroAssessmentFinalReportMarch2011.pdf 

U.S. DOI. (2007). Potential Hydroelectric Development at Existing Federal Facilities For Section 1834 of the Energy Policy Act of 2005. https://www.usbr.gov/power/data/1834/Sec1834_EPA.pdf 

CANMET Energy Technology Center. (2004). Clean Energy Project Analysis: Retscreen Engineering & Cases Textbook. https://www.ieahydro.org/media/1ccb8c33/RETScreen%C2%AE-Engineering-Cases-Textbook%E2%80%93-PDF.pdf 

Betz, A. (2014). Introduction to the theory of flow machines. Elsevier. eBook ISBN: 9781483180908. https://shop.elsevier.com/books/introduction-to-the-theory-of-flow-machines/betz/978-0-08-011433-0 

Niebuhr, C.M., Van Dijk, M., Neary, V.S. and Bhagwan, J.N., 2019. A review of hydrokinetic turbines and enhancement techniques for canal installations: Technology, applicability and potential. Renewable and Sustainable Energy Reviews, 113, p.109240. https://doi.org/10.1016/j.rser.2019.06.047 