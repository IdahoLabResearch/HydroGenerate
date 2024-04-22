## Design Flow Estimation

1.	If less than three or less flow values are entered, HG will use the average flow to compute all turbine parameters following the procedure described in the Turbine Parameters Calculation section. A constant flow can be used to represent scenarios where a fixed flow is guaranteed during the entire operation of the power system, e.g., when a fixed water right will be used to generate hydropower. 
2.	If a time series, containing at least 3 data points of flow is provided by the user, then a design flow can be calculated using the flow-duration curve. HG will build the flow-duration relationship (i.e., calculating the percent of time a flow value is exceeded) and users can select the percent exceedance desired (i.e., the percent of time the turbines will be flowing full). 
3.	If the user has no initial information on the percent of exceedance needed for the estimation, HG will use a default of 30%, in the range of existing recommendations and applications (Alonso-Tristán et al., 2011; Barelli et al., 2013; CANMET Energy Technology Center, 2004; Gulliver & Arndt, 1991). {numref}`DesignFlow` shows how design flow is calculated when 'pctime_runfull = 30'. A percent of exceedance of 30% means the turbine will be flowing full 30% of the time, and while this value is in range with multiple applications and recommendations, there are many factors that will impact the selection of a design flow, e.g., construction cost, purpose (base load or peak demand), off-grid versus grid tied, turbine efficiency curve. Users can vary the percent of exceedance and compare the outputs for each simulation to understand possible configurations for a specific site.


```{figure} DesignFlow.SVG
---
name: DesignFlow
---
Sample Flow-Duration plot using the data from the USGS NWIS example indluded in the [USER GUIDE section](UserGuide_4_QueryingDataUSGS-NWIS.md).
```


> **Note**: Flow-duration plots depict specific flow-statistic values selected from flow-duration curves. 
> The flow-duration curve is a cumulative frequency curve that shows the percent of values that specified 
> discharges were equaled or less than (percentile), or the percent of values that specified discharges 
> were equaled or exceeded (percent exceedance). Percent exceedance is 100 minus the percentile. 
> Example: the 30th percent exceedance (the value that 30 percent of the flows are equal to or greater than)
> is the 70th percentile (the value that 70 percent of the flows are equal to or less than). 
> While the flow-duration curve does not show the chronological sequence of flows, it is an important means 
> of representing flow characteristics of a stream throughout the range of flow on a single curve. 
> The flow-duration figure presented here represent the flow-duration curves of daily streamflow data for 
>  the [period downloaded](UserGuide_4_QueryingDataUSGS-NWIS.md). In the example, using the default ['pctime_runfull = 30' leads to a design flow of 200 cfs](UserGuide_4_QueryingDataUSGS-NWIS.md).


In cases where there are significant variations of flow throughout the year, selecting more than one turbine can be a more effective scenario, over selecting a single larger turbine that will operate full a smaller time of the year. In contrast, some turbine types can operate at relatively high efficiency for low flows (Yildiz & Vrugt, 2019), allowing the selection of a larger percent of exceedance (larger design flow) without compromising efficiency. Each configuration will have associated costs and specific details that need to be evaluated.

Note: It is recommended, under ideal conditions, to include 10 years of flow record at a site to capture existing hydrological variability and obtain a more realistic power estimation (Hadjerioua et al., 2012). Also, it is important to simulate the response of the system during wet and dry years. In HG, users can select a design flow and input a time-series of flow to evaluate the system’s response for the data entered.

## References 
Alonso-Tristán, C., González-Peña, D., Díez-Mediavilla, M., Rodríguez-Amigo, M., & García-Calderón, T. (2011). Small hydropower plants in Spain: A case study. Renewable and Sustainable Energy Reviews, 15(6), 2729–2735. https://doi.org/10.1016/j.rser.2011.03.029 

Barelli, L., Liucci, L., Ottaviano, A., & Valigi, D. (2013). Mini-hydro: A design approach in case of torrential rivers. Energy, 58, 695–706. https://doi.org/10.1016/j.energy.2013.06.038 

CANMET Energy Technology Center. (2004). Clean Energy Project Analysis: Retscreen Engineering & Cases Textbook. https://www.ieahydro.org/media/1ccb8c33/RETScreen%C2%AE-Engineering-Cases-Textbook%E2%80%93-PDF.pdf 

Gulliver, John S.; Arndt, Roger E.A.. (1991). Hydropower Engineering Handbook. McGraw-Hill, Inc.. Retrieved from the University of Minnesota Digital Conservancy, https://hdl.handle.net/11299/195476. 

Yildiz, V., & Vrugt, J. A. (2019). A toolbox for the optimal design of run-of-river hydropower plants. Environmental Modelling & Software, 111, 134–152. https://doi.org/10.1016/j.envsoft.2018.08.018 

Hadjerioua, Boualem, Wei, Yaxing, and Kao, Shih-Chieh. An Assessment of Energy Potential at Non-Powered Dams in the United States. United States: N. p., 2012. Web. https://doi.org/10.2172/1039957 

