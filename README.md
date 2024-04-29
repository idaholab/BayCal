# BayesianCalibration (https://baycal.readthedocs.io/en/latest/)

Bayesian Model Calibration (BayCal) toolkit is a software plugin for Risk Analysis Virtual Environment (RAVEN) framework, arming at inversely quantifying the uncertainties associated with simulation model parameters based on available experiment data. BayCal seeks statistical inference of the uncertain input parameters that are consistent with the available measurement data or observed data. The unique feature of BayCal is the capability to be linked with RAVEN to build corresponding calibration workflows for complex multi-physics simulations.

BayCal trys to resolve two critical issues existing in the Bayesian inference: 1) high-dimensional experimental data (such as time series observations at multiple locations), 2) expensive computational simulations. These issues have been studied and resolved in literature, but there is not yet a complete toolkit to resolve these issues in an efficient and automatic way. BayCal automatizes the process by coupling with RAVEN, utilizes artificial intelligence algorithms to automatically construct surrogate models for the expensive computational simulations and dimensionality reduction techniques to significantly reduce the number of simulations for convergence.

## Installation

```
conda create -n baycal_libs python=3.10
conda activate baycal_libs
pip install baycal-ravenframework
```

## Testing

```
cd BayCal/tests
raven_framework test_multiTargets.xml
```

## Analytic High-Dimensional Problem
A python analytic problem with 50 responses, three input parameters with uniform prior distributions.
<img width="1265" alt="image" src="https://github.com/idaholab/BayCal/assets/7321071/209f2a75-def5-488c-a923-7d4ac03cafb8">

## Nuclear Fuel Performance Problem
In nuclear fuel performance simulation, fission gas release (FGR) involves treatment of several complicated and interrelated physical processes, which depends on uncertaint input parameters. However, the uncertainties associated with these parameters are only known by expert judgement. In this case, Bayesian calibration can be applied to quantify the input uncertainties. In this work, a Gaussian Processing model is applied to greatly reduce the computational cost based on 100 high-fidelity simulations from fuel performance code (i.e., BISON). The FGR time series measurement data is projected to an efficient subspace constructed via Principal Component Analysis. Please refer to [1] for more detailed descriptions. The calculated posterior distributions through BayCal are illustrated in the following:

<img width="1001" alt="image" src="https://github.com/idaholab/BayCal/assets/7321071/8b8eddac-e3b4-40a1-bd08-4e70be2cf281">

<img width="1248" alt="image" src="https://github.com/idaholab/BayCal/assets/7321071/8b8bcf18-29a4-4b06-a3d0-7f7bf15880f1">



## Applications
Since BayCal is a plugin for RAVEN, it can be directly applied to the following codes:
- Generic interface with external codes
- High-fidelidty simulation codes:

    - [RELAP5-3D](https://relap53d.inl.gov/SitePages/Home.aspx)
    - [MELCOR](https://melcor.sandia.gov/about.html)
    - [MAAP5](https://www.fauske.com/nuclear/maap-modular-accident-analysis-program)
    - [MOOSE-BASED Apps](https://mooseframework.inl.gov/)
    - [SCALE](https://www.ornl.gov/onramp/scale-code-system)
    - [SERPENT](http://montecarlo.vtt.fi/)
    - [CTF - COBRA TF](https://www.ne.ncsu.edu/rdfmg/cobra-tf/)
    - [SAPHIRE](https://saphire.inl.gov/)
    - [MODELICA](https://www.modelica.org/modelicalanguage)
    - [DYMOLA](https://www.3ds.com/products-services/catia/products/dymola/)
    - [BISON](https://bison.inl.gov/SitePages/Home.aspx)

- Custom ad-hoc external models (build in python internally to RAVEN)


## References
```
1. Wu, Xu, Tomasz Kozlowski, and Hadi Meidani. "Kriging-based inverse uncertainty quantification of nuclear fuel performance code BISON fission gas release model using time series measurement data." Reliability Engineering & System Safety 169 (2018): 422-436.
2. Xie, Ziyu, Wen Jiang, Congjian Wang, and Xu Wu. "Bayesian inverse uncertainty quantification of a MOOSE-based melt pool model for additive manufacturing using experimental data." Annals of Nuclear Energy 165 (2022): 108782.
```
