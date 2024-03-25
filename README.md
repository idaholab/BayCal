# BayesianCalibration (https://baycal.readthedocs.io/en/latest/)

Bayesian Model Calibration (BayCal) toolkit is a software plugin for Risk Analysis Virtual Environment (RAVEN) framework, arming at inversely quantifying the uncertainties associated with simulation model parameters based on available experiment data. BayCal seeks statistical inference of the uncertain input parameters that are consistent with the available measurement data or observed data. The unique feature of BayCal is the capability to be linked with RAVEN to build corresponding calibration workflows for complex multi-physics simulations. 

BayCal trys to resolve two critical issues existing in the Bayesian inference: 1) high-dimensional experimental data (such as time series observations at multiple locations), 2) expensive computational simulations. These issues have been studied and resolved in literature, but there is not yet a complete toolkit to resolve these issues in an efficient and automatic way. BayCal automatizes the process by coupling with RAVEN, utilizes artificial intelligence algorithms to automatically construct surrogate models for the expensive computational simulations and dimensionality reduction techniques to significantly reduce the number of simulations for convergence.

## Analytic High-Dimensional Problem
A python analytic problem with 50 responses, three input parameters with uniform prior distributions.
<img width="1265" alt="image" src="https://github.com/idaholab/BayCal/assets/7321071/209f2a75-def5-488c-a923-7d4ac03cafb8">
