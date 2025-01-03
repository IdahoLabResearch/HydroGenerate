---
title: 'HydroGenerate: Techno-economic potential analysis of small hydro'
tags:
  - Python
  - Hydro Power
  - Techno-economic assesment
  - 
  - 
authors:
  - name: Soumyadeep Nag
    orcid: 0000-0000-0000-0000
    equal-contrib: true
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: CCamilo Jose Bastidas Pacheco
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
  - name: Juan Felipe Gallego Calderon
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 1
affiliations:
 - name: Idaho National Laboratory, Idaho Falls, ID, United States
   index: 1
   ror: 00hx57361
date: 11 November 2024
bibliography: HydroGenerate.bib
---

# Summary

The growth of hydropower, as compared to other renewable energy resources, has decreased in the past decades, especially due to high development cost and permiting challenges. Consequently, realistic foresight into a chosen site's performance can help developers make decisions confidently and inturn boost hydropower potential. HydroGenerate is a python library for estimating the hydropower generation potential at a user-chosen geographical site. Apart from developers, this tool can also aid hydropower researchers evaluate the potential of their developed hydropower technology or operating policy for a given site. HydroGenerate fetches historical flow and head data from USGS for the user-chosen site, and evaluates different technical options to estimate the maximum power generation potential. 

# Statement of need

Features:
HydroGenerate incorporates characteristics of Francis, Kaplan, Pelton and Hydrokinetic turbines. All of these turbine types have different efficiency curves and efficiencies vary with flow conditions. Hydrogenerate incorporates this variable efficiency feature with each turbine type thereby allowing for a more realistic estimation of hydropower potential. Furthermore, turbine selection for a site is crucial as there could be multiple turbine types that are suitable for the site. HydroGenerate uses geometric properties for the turbine characteristics to select turbines.

Flow etching and pre-processing:
Flow and head data can be fed to HydroGenerate in the form of time-series data or as constants. The time series data can be procured by using the API from USGS and fed directly to HydroGenerate. This data is then processed to check for turbine minimum and maximum flow limits as well as maintenance periods to add to the practical considerations of the systems. CAMILLO: When USGS data is not complete how does HG process that? 

Different head-loss calculation methods
Furthermore, HydroGenerate offers several two methods to perform penstock head-loss calculations, Darcy-Weisbach and Hazen-Williams. 

Different types of new hydro power constructions
HydroGenerate also has an internal cost model that can estimate the total capital cost of the project based on the type of construction, such as, non-powered dam, new stream-reach, canal-conduit, pumped storage hydro with existing infrastructure, new pumped storage hydro, unit addition to an existing hydro power unit, and generator rewind. 

Benefits to researchers:
HG provides an open-source, free, modular, customizable, and well-documented tool for hydropower potential estimation, predesign, and evaluation of different types of projects. Researchers can directly use HG for multiple hydropower assessments, by taking advantage of the examples included in the documentation. 

For example, power and energy system researchers need power system models of different seasons (or hydrological conditions) to understand power reserves and other capabilities of hydropower generation assets. HydroGenerate (using real historical data) can estimate the potential for multiple sites and thereby help in creating a more realistic power system model. Environmental researchers can use the tool determine the impact of sedimentation or drought or glacier recession (among others) on the hydro power production by feeding appropriate head and flow data. 

One other feature of HydroGenerate is the modularity. Each section of the code is modular in nature which allows a researcher to be able to develop and insert his his/her own module to evaluate the benefits of the same.  For example, turbine design researchers can use this feature to develop new turbine modules. If a new turbine type is available, its power generation potential with real data and its revenue from the market can be estimated to gain a more realistic view of the benefits of the new turbine design. Also, market analysis researchers can use this feature to include new operational constraints to suite price profiles or other requirements. 

Energy system planners rely heavily on system models to perform optimal planning. Hydrogenerate provides the hydropower generation models that fit well into multi-objective optimization problems, providing both, technical as well as economic potential for planning. 

Poitive points:
The above features make HydroGenerate a complete tool that is open-source and publicly available. Other similar open source tools are .....
Once the flow data is taken as input
Similar tools and comparative statements:
 One similar but closed and membership based platform is the The RETScreen (https://natural-resources.canada.ca/maps-tools-and-publications/tools/modelling-tools/retscreen/7465) Clean Energy Management Software platform that includes hydropower potential estimation. RETScreen implements similar efficiency equations but doesn’t include functionality for flow data analysis and constraints, head loss calculation in the penstock, and has limited capabilities for initial capital cost and operation and maintenance estimations. 

Additional research has proposed automated approaches for identifying sites with hydropower potential by using GIS in combination with summaries of flow data (Arefiev et al. 2015). These approaches are useful for estimating existing hydropower potential across large study areas. HydroGenerate can be used in combination with tool implementing this functionality, to analyze generation and plant characteristics once sites have been identified and expand their usability. For example, HydroGenerate was used to assess hydropower potential across multiple non-powered dams where head data was available or was estimated using remote sensing data (Hansen et al. 2024a; Hanset et al. 2024b).

# The HydroGenerate Workflow: Design and Implementation
The user has a choice to input flow in the form of time-series or constant. Including flow and head data, there are 32 inputs available to the user. Upon execution HydroGenerate, generates an object which contains cost and performance data as its attributes. The workflow of HydroGenerate can be divideed into the following steps:

* Step 1 Input data processing: This step involves conversion of inputs to SI units. (CAMILO)


* Step 2a Design flow computation: If less than three or less flow values are entered, HG will use the average flow to compute all turbine parameters following the procedure described in the Turbine Parameters Calculation section. If a time series, containing at least 3 data points of flow is provided by the user, then a design flow can be calculated using the flow-duration curve. HG will build the flow-duration relationship (i.e., calculating the percent of time a flow value is exceeded) and users can select the percent exceedance desired (i.e., the percent of time the turbines will be flowing full). f the user has no initial information on the percent of exceedance needed for the estimation, HG will use a default of 30%, in the range of existing recommendations and applications (Alonso-Tristán et al., 2011; Barelli et al., 2013; CANMET Energy Technology Center, 2004; Gulliver & Arndt, 1991). The figure below shows how design flow is calculated when ‘pctime_runfull = 30’. 
<img src="flow_duration_curve.png" alt="drawing" width="500" style="display: block; margin: 0 auto"  caption="fgh"/>


* Step 2b Head loss calculation: The net hydraulic head is computed as the available head minus head losses: $$H = H_e - h_l$$ where, $H$ is the net hydraulic head (m), $H_e$ is the available head (m) and $h_l$ is the head loss (m). $h_l$ is computed to account for friction losses only, or $h_l = h_f$ (other losses are more minor and hence are not included). HG includes the following options for head loss calculations: 1. Head losses in the penstock, using the Darcy-Weisbach equation (default) as explained below, or the Hazen-Williams equation (if selected by the user). The required input for this calculation is the penstock length. Users can also select penstock material, with steel being the default if none is provided, 2. If the penstock diameter is not known, HG will calculate a diameter that will limit head losses to 10% (default) of the available head. Users can change the penstock diameter, or the maximum percent of head loss allowed to calculate a different penstock diameter. Head losses will decrease with larger diameters while costs will increase. HG provides the flexibility to evaluate different scenarios. HG can calculate head losses using the Darcy-Weisbach equation (default) or the Hazen-Williams equation. 


* Step 2c Turbine selection is performed: Using 'Shapely' and [1] predefined polygons in (flow,head) coordinate system are created and the polygon centroids are precalculated within HydroGenerate. The following steps are used to perform turbine selection: a) Step 1: Using user-provided data and shapely, a point in cartesian space using flow and head as coordinates, is defined b) Step 2: The shapes that encompass the design flow and head are determined using shapely. This process requires the projection of the point onto the boundaries of the polygon. The number of boundaries intersected by the projection determines wether the point is within a polygon or not. Odd and even number indicated boundaries indicate, inside or outside the polygon, respectively, c) Step 3: Compute the distance between the the defined point and the centroid of the shapes identified in steps 1 and 2 using eucledian distance, d) Step 4: Select the best turbine type as the one with minimum distance from its centroid to the desired point (derived form user data) e) Step 5: Generate plots to vizualise the selection. If the program finds multiple suitable turbines, HydroGenerate computes potential for the best suitable turbine (step 3) to serve the purpose of the program . However, for the user's convenience HydroGenerate also returns other suitable turbine types.  

<img src="turb_sel.png" alt="drawing" width="500" style="display: block; margin: 0 auto"/>

* Step 2d Turbine parameter calculation: This step calculates the runner diameter, specific speed  of the turbine. These are then used to calculate the efficiency curve. For example, consider that a particular site needs a Francis turbine. The parameters and the efficiency curve are calculated as follows: Turbine runner size (d) $$d=kQ_d^{0.473}$$ where $d$ = runner diameter (m), $k$ = 0.46 for d < 1.8, or 0.41 for d ≥ 1.8 (dimensionless) and $Q_d$ = Design flow (m^3/s). Specific speed ($n_q$) $$n_q=kh^{-5}$$ where $n_q$ = specific speed based on flow, $k$ = 800 for Propeller and Kaplan turbines, 600 for Francis turbines and $h$ = rated head on turbine in m (gross head less maximum head loss). Specific speed adjustment to peak efficiency ($\land e_{nq}$) $$\land e_{nq}\ =\ \left(\frac{n_q-56}{256}\right)^2$$ Runner size adjustment to peak efficiency ($\land e_d$) $$\land e_d\ \ =(0.081+\ \land e_{nq}\ )(1-0.789\ d^{-0.2})\ \ $$ Turbine peak efficiency ($e_p$) is calculated using $$e_p=\left(0.919-\ \land e_{nq}+\ \land e_d\right)-0.0305+0.005\ R_m\ ,$$ where $R_m$ = turbine manufacture/design coefficient. (2.8 to 6.1; default = 4.5) Peak efficiency flow ($Q_p$) $$Q_p=0.65\ Q_d\ n_q^{0.05}$$ Efficiencies at flows below peak efficiency flow ($e_q$) $$e_q=\ \left\{1-\left[1.25\left(\frac{Q_p-Q}{Q_p}\right)^{3.94-0.0159\ n_q}\right]\right\}\ e_p$$ Drop in efficiency at full load ($\land e_p$) $$\land e_p=0.0072\ n_q^{0.4}$$ Efficiency at full load ($e_r$) $$e_r=\left(1-\ \land e_p\right)\land e_p$$ Efficiencies at flows above peak efficiency flow ($e_q$) $$e_q=\ e_p-\ \left[\left(\frac{Q-\ Q_p}{Q_d-Q_p}\right)^2\left(e_p-e_r\right)\right]$$


* Step 3 Power and energy calculation: Hydrogenerate canculates hydropower potential using  $$        P = \eta \times \gamma \times Q \times H$$   where,  $P$ is the hydropower potential (watt),  $\eta$ is the overall system efficiency (dimensionless),  $\gamma$ is the specific weight of water (9,810 N/m^3), $Q$ is the flow (m^3/s), and $H$ is the net hydraulic head (m). For hydrokinetic applications, the hydropower potential is calculated using $$        P=0.295\ast\rho\ast A_b\ast V^3$$ where, $\rho$ is the density of water, in Kg/m^3, $A_b$ is the swept area of blades, in m^2, and $V$ is the velocity of water, in m/s, while also considering the maximum energy that can be extracted from flow is limited to approximately 59% (Betz limit [Betz, 2014]). The average channel velocity value introduced by the user is directly used in this equation. The swept area of blades is computed for each turbine type and dimensions given. Niebuhr et al., (2019) provides a review of existing hydrokinetic turbine types. HG uses a simplified configuration, consisting of one penstock, turbine, and generator. The turbine type is selected based on head and the elements are sized for a design flow that can be entered by the user or computed in HG, using flow data. The overall efficiency of the system is calculated as $\eta = e_{turb}*e_{gen}$, where $e_{turb}$ and $e_{gen}$ are turbine and generator efficiencies. Turbine efficiencies at flows below or above the design flow is then computed using a set of empirical equations for each turbine type (CANMET, 2004), while considering constant generator efficiency. 

* Step 4 Economic calculations: HG currently uses empirical equations to calculate the capital and O&M cost of the plant [https://info.ornl.gov/sites/publications/files/Pub58666.pdf]. The capital cost calculation equations are separated based on type of plant. Revenue is calculated using an average wholesale electricity market price [https://www.eia.gov/electricity/wholesale/]. For example for a Non-Powered Dam, the initial capital cost is given as: $$ ICC = 11,489,245P^{0.976}H^{-0.24}$$ where, $ICC, P$ and $H$ are the initial capital cost, Rated electrical power and net available water head, respectively.

<img src="HG_workflow.png" alt="drawing" width="1000" style="display: block; margin: 0 auto"/>

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References