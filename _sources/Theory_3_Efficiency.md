# Turbine Selection & Efficiency Calculation


## Turbine Selection 

Turbine selection for a particular site is performed based on the design flow and the hydraulic head. {numref}`TurbineSelection` shows the turbine selection graph (Gulliver & Arndt, 1991). The figure shows multiple overlapping regions. When a site is located in a overlapping region, the distance from the point to the centroid of each figure are calculated and the turbine type with the smallest centroid distance is is selected for computation. Turbine types can be manually entered by users and, when more than one turbine type is suitable, than information is stored in the output. A python package called "Shapely" (Gillies et al., 2024) is imported to perform the area selection, centroid and distance to centroids calculations. 

{numref}`TurbineSelection` shows the turbine selection graph (Gulliver & Arndt, 1991).
```{figure} Turbine_Selection.SVG
---
name: TurbineSelection
---
Sample Flow-Duration plot using the data from the USGS NWIS example indluded in the [USER GUIDE section](UserGuide_4_QueryingDataUSGS-NWIS.md).
```



## Turbine Efficiency Calculation

The turbine efficiency calculation follows the same methodology and equations included in (CANMET, 2004). For further details on turbine efficiency, refer to CANMET, (2004). Turbine efficiency computations are conducted using the following equations:

### Reaction turbines (Francis, Kaplan and Propellor). 
Turbine runner size (d) 

$$d=kQ_d^{0.473}$$

where:
* $d$ = runner diameter (m),
* $k$ = 0.46 for d < 1.8, or 0.41 for d ≥ 1.8 (dimensionless) and
* $Q_d$ = Design flow (m^3/s).

Specific speed ($n_q$)

$$n_q=kh^{-0.5}$$

where: 
* $n_q$ = specific speed based on flow,
* $k$ = 800 for Propeller and Kaplan turbines, 600 for Francis turbines and
* $h$ = rated head on turbine in m (gross head less maximum head loss).

### Francis Turbines:
Specific speed adjustment to peak efficiency ($\land e_{nq}$)

$$\land e_{nq}\ =\ \left(\frac{n_q-56}{256}\right)^2$$

Runner size adjustment to peak efficiency ($\land e_d$)

$$\land e_d\ \ =(0.081+\ \land e_{nq}\ )(1-0.789\ d^{-0.2})\ \ $$

Turbine peak efficiency ($e_p$) is calculated using 

$$e_p=\left(0.919-\ \land e_{nq}+\ \land e_d\right)-0.0305+0.005\ R_m\ ,$$

where: 

$R_m$ = turbine manufacture/design coefficient. (2.8 to 6.1; default = 4.5)


Peak efficiency flow ($Q_p$)

$$Q_p=0.65\ Q_d\ n_q^{0.05}$$

Efficiencies at flows below peak efficiency flow ($e_q$)

$$e_q=\ \left\{1-\left[1.25\left(\frac{Q_p-Q}{Q_p}\right)^{3.94-0.0195\ n_q}\right]\right\}\ e_p$$

Drop in efficiency at full load ($\land e_p$)

$$\land e_p=0.0072\ n_q^{0.4}$$

Efficiency at full load ($e_r$)

$$e_r=\left(1-\ \land e_p\right) e_p$$

Efficiencies at flows above peak efficiency flow ($e_q$)

$$e_q=\ e_p-\ \left[\left(\frac{Q-\ Q_p}{Q_d-Q_p}\right)^2\left(e_p-e_r\right)\right]$$

### Kaplan and Propellor turbines
Specific speed adjustment to peak efficiency ($\land e_{nq}$)

$$\land e_{nq}\ =\ \left(\frac{n_q-170}{700}\right)^2$$

Runner size adjustment to peak efficiency ($\land e_d$)

$$\land e_d\ \ =(0.095+\ \land e_{nq}\ )(1-0.789\ d^{-0.2})\ \ $$

Turbine peak efficiency ($e_p$)

$$e_p=\left(0.905-\ \land e_{nq}+\ \land e_d\right)-0.0305+0.005{\ R}_m\ $$

### Kaplan turbines
Peak efficiency flow ($Q_p$)

$$Q_p=0.75\ Q_d\ $$

Efficiencies at flows above peak efficiency flow ($e_q$)

$$e_q=\ \ \left[1-3.5\ \left(\frac{Q_p-Q}{Q_p}\right)^6\right]e_p$$

### Propellor turbines
Peak efficiency flow ($Q_p$)

$$Q_p=Q_d\ $$

Efficiencies at flows above peak efficiency flow ($e_q$)

$$e_q=\ \ \left[1-1.25\ \left(\frac{Q_p-Q}{Q_p}\right)^{1.13}\right]e_p$$

### Pelton Turbines
Rotational Speed ($n$)

$$n=31\ \left(h\ \frac{Q_d}{j}\right)^{0.5}$$

Where:

$j$ = number of jets (ranging from 1 to 6)

Outside diameter of runner ($d$) 

$$d=\frac{49.4\ h^{0.5}\ j^{0.02}}{n}$$

Turbine peak efficiency ($e_p$)

$$e_p=0.864\ d^{0.04}\ $$


Peak efficiency flow ($Q_p$)

$$Q_p=\ \left(0.662+0.001\ j\right)\ Q_d\ $$

Efficiencies at flows above peak efficiency flow ($e_q$)

$$e_q=\ \ \left[1-\ \left\{\left(1.31+0.025\ j\right)\ \left(\frac{Q_p-Q}{Q_p}\right)^{5.6+0.4\ j}\right\}\ \right]e_p$$

### Turgo Turbines
Efficiencies at flows above peak efficiency flow ($e_q$)

$$e_q=Pelton\ Turbines\ e_q-0.03\ \ $$

### Crossflow turbines
Peak efficiency flow ($Q_p$)

$$Q_p=Q_d\ $$

Efficiencies at flows above peak efficiency flow ($e_q$)

$$e_q=\ \ 0.79-0.15\left(\frac{Q_d-Q}{Q_p}\right)-1.37\left(\frac{Q_d-Q}{Q_p}\right)^{14}$$

## References
CANMET Energy Technology Center. (2004). Clean Energy Project Analysis: Retscreen Engineering & Cases Textbook. https://www.ieahydro.org/media/1ccb8c33/RETScreen%C2%AE-Engineering-Cases-Textbook%E2%80%93-PDF.pdf 

Gulliver, John S.; Arndt, Roger E.A.. (1991). Hydropower Engineering Handbook. McGraw-Hill, Inc.. Retrieved from the University of Minnesota Digital Conservancy, https://hdl.handle.net/11299/195476.

Gillies, S., van der Wel, C., Van den Bossche, J., Taves, M. W., Arnott, J., Ward, B. C., & others. (2024). Shapely (Version 2.0.6) [Computer software]. https://doi.org/10.5281/zenodo.5597138