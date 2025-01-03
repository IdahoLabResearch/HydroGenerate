## Head Loss Estimation
The net hydraulic head is computed as the available head minus head losses:

$$H = H_e - h_l$$

Where,  

* $H$ is the net hydraulic head (m), 
* $H_e$ is the available head (m) and 
* $h_l$ is the head loss (m). 

$h_l$ is computed to account for friction losses only, or $h_l = h_f$ (other losses are more minor and hence are not included). HG includes the following options for head loss calculations: 

1. Head losses in the penstock, using the Darcy-Weisbach equation (default) as explained below, or the Hazen-Williams equation (if selected by the user). The required input for this calculation is the penstock length. Users can also select penstock material, with steel being the default if none is provided. 

2. If the penstock diameter is not known, HG will calculate a diameter that will limit head losses to 10% (default) of the available head. Users can change the penstock diameter, or the maximum percent of head loss allowed to calculate a different penstock diameter. Head losses will decrease with larger diameters while costs will increase. HG provides the flexibility to evaluate different scenarios. 

HG can calculate head losses using the Darcy-Weisbach equation (default) or the Hazen-Williams equation.  

### A. Darcy-Weisbach head loss calculation
$$h_f = f \times \frac{L \times V^2}{D \times 2g}  $$

HG computes the friction factor $f$ by using different equations, as:
1. For laminar flow (Re < 2000), f is given by (Bhave, 1991): 

$$ f = \frac{64}{Re}$$

2. For fully turbulent flow (Re > 4,000), the Swamee-Jain approximation to the Colebrook-White equation (Bhave, 1991) is used: 

$$f = \frac{.25}{\Big[log\big(\frac{\epsilon}{3.7D}+\frac{5.74}{Re^0.9}\big)\Big]^2}  $$

3. For flow in the transition zone (2,000 < Re < 4,000), f is computed using a cubic interpolation formula derived from the Moody Diagram by Dunlop (1991): 

$$f=X1+R(X2+R(X3+RX4)$$

$$R=\ \frac{Re}{2000}$$

$$X1=7FA-FB$$

$$X2=0.128-17FA+2.5FB$$

$$X3=\ -0.128+13FA-2FB$$

$$X4=0.032-3FA+0.5FB$$

$$FA=\ {Y3}^{-2}$$

$$FB=FA\left(2-\ \frac{AA\ AB}{Y2\ Y3}\right)$$

$$Y2=\ \frac{\varepsilon}{3.7D}+AB$$

$$Y3=\ -2\log(Y2)$$

$$AA=\ -1.5634601348517065795$$

$$AB=\ 0.00328895476345399058690$$

following similar methodology presented in EPANET (U.S. Environmental Protection Agency, 2020), depending on the flow’s Reynolds Number (Re), defined as $ Re = \frac{4q}{\pi Dv}$.

### B. Hazen-Williams head loss calculation

$$h_f=10.67\ast\frac{L{\ast Q}^{1.852}}{C^{1.852}\ast D^{4.87}}$$

where

* $h_f$ = head loss due to friction (m),
* $L$ = length of the pipe (m),
* $Q$ = Volumetric flow rate (m^3/s),
* $C$ = pipe roughness coefficient and
* $D$ = internal diameter of the pipe (m).

## References
U.S. Environmental Protection Agency. (2020). EPANET 2.2 User Manual. https://epanet22.readthedocs.io/en/latest/index.html 

Bhave, P. R. 1991. Analysis of Flow in Water Distribution Networks. Technomic Publishing. Lancaster, PA.

Dunlop, E. J. 1991. WADI Users Manual. Local Government Computer Services Board, Dublin, Ireland.


