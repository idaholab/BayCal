.. _quickstart:

Quick Start
============

BayCal is a RAVEN plugin, it utilizes RAVEN input structure to design the
workflow calculation, and contains the following XML blocks.

Root XML block:
+++++++++++++++++++++++++++++++++++++

.. code:: xml

    <?xml version="1.0" ?>
    <Simulation verbosity="quiet">
      ...
    </Simulation>

Prior distribution block:
+++++++++++++++++++++++++++++++++++++++
Many distributions can be defined through the XML block, such as Beta, Exponential,
Gamma, Lapace, Logistic, LogNormal, LogUniform, Normal, Triangular, Uniform, Weibull,
or custom defined distributions. For example:

.. code:: xml

    <Distributions>
      <Normal name="normal">
        <mean>0</mean>
        <sigma>10</sigma>
      </Normal>
      <Normal name="propDist">
        <mean>0</mean>
        <sigma>1</sigma>
      </Normal>
    </Distributions>

Bayesian inference via Markov Chain Monte Carlo
+++++++++++++++++++++++++++++++++++++++++++++++++
Both Metropolis method and AdaptiveMetropolis method can be used to perform Bayesian inference.
The posterior distribution can be computed through these methods.

.. code:: xml

    <Samplers>
      <Metropolis name="Metropolis">
        <samplerInit>
          <limit>1000</limit>
          <initialSeed>070419</initialSeed>
          <burnIn>500</burnIn>
        </samplerInit>
        <likelihood log="True">likelihood</likelihood>
        <variable name="alpha">
          <distribution>normal</distribution>
          <initial>0</initial>
          <proposal class="Distributions" type="Normal">propDist</proposal>
        </variable>
        <variable name="beta">
          <distribution>normal</distribution>
          <initial>0</initial>
          <proposal class="Distributions" type="Normal">propDist</proposal>
        </variable>
        <TargetEvaluation class="DataObjects" type="PointSet">outSet</TargetEvaluation>
      </Metropolis>
    </Samplers>

Likelihood Model
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
A BayCal likelihood model can be defined, both simulation output and experimental data
are integrated into the likelihood model to compute the posterior distribution. For example,
An ExternalModel "simple" is used to represent the simulation model, while an ExternalModel
"likelihood" is used to integrate simulation output and experimental data. An EnsembleModel is
used to couple simulation model with BayCal LikelihoodModel.

.. code:: xml

    <Models>
      <ExternalModel name="likelihood" subType="BayCal.LikelihoodModel">
        <variables>likelihood, zout</variables>
        <LikelihoodModel type="normal">
          <!-- targets of interest from simulation
          Multiple targets can be provided, and they will be stacked together based on
          their provided orders.
          -->
          <simTargets>zout</simTargets>
          <expTargets shape="" computeCov='True' correlation='False'>
            2.11500008,  0.14946724, -1.65039824,  4.35404944,  2.81822947,
            6.54820123, -1.75704173,  2.25129699, -1.19830637,  3.76461502,
            0.386274  ,  0.3026495 ,  1.6467714 , -0.18838893, -0.40815504,
            2.11830326,  2.08114549,  2.4998607 ,  2.79584898,  3.88973006,
          -2.7575892 , -0.04385282,  0.05381042, -1.46692956,  1.70190605,
          -1.57171388,  4.11788556, -1.63605661,  3.80630774,  2.84303567,
          -1.38054778, -1.21978835, -0.22892141,  4.32828596,  1.43980194,
            3.2975833 ,  2.50307962,  3.99509689, -0.04558891, -2.93355096,
            1.54869592,  0.82694381, -2.27505536,  2.10192782, -0.02294763,
            1.36074938, -0.69042317,  1.80091876,  0.03907101, -2.38166576,
            1.563129  ,  1.20795836,  2.29019786,  2.65269473,  0.85751374,
          -0.59481231,  1.80102222,  0.02886628,  6.45080851,  4.07795272,
            7.16290259,  1.35855176, -0.75228632,  1.65880613,  2.4717668 ,
            1.10216817, -0.44061435, -1.92342245,  3.05321389,  0.89013387,
          -1.05614164,  0.33685368,  1.65889606, -0.49594808,  6.63155206,
            3.70915947, -0.46757349,  0.75459259, -0.87910652,  2.84513982,
          -2.27714018,  2.16478883, -0.31847088,  5.61444774, -1.28556545,
            2.6697912 ,  0.84654927,  8.2436798 ,  1.80816732,  3.72230814,
            3.36955247,  0.72882023, -3.85778293, -1.2840472 ,  1.65360275,
          -0.48916641,  2.25437166,  1.28519366, -3.07200649,  1.02090558
          </expTargets>
          <reduction>
            <type>pca</type>
            <!-- -1: no truncation
                0: optimal rank is computed
                >1: user-defined truncation rank
                >0 and < 1: computed rank is the number of the biggest single value needed
                to reach the energy identified by truncationRank-->
            <truncationRank>0</truncationRank>
          </reduction>
          <!--
          <expCov diag="False"></expCov>
          <biasTargets></biasTargets>
          <biasCov diag="False"></biasCov>
          <romCov diag="False"></romCov>
          -->
        </LikelihoodModel>
      </ExternalModel>
      <!-- External Model -->
      <ExternalModel ModuleToLoad="simple" name="simple" subType="">
        <variables>alpha, beta, zout</variables>
      </ExternalModel>
      <!-- EnsembleModel -->
      <EnsembleModel name="EnsembleLH" subType="">
        <Model class="Models" type="ExternalModel">
            simple
          <Input class="DataObjects" type="PointSet">inputHolderSimple</Input>
          <TargetEvaluation class="DataObjects" type="PointSet">simData</TargetEvaluation>
        </Model>
        <Model class="Models" type="ExternalModel">
            likelihood
          <Input class="DataObjects" type="PointSet">inputHolderLikelihood</Input>
          <TargetEvaluation class="DataObjects" type="PointSet">lhData</TargetEvaluation>
        </Model>
      </EnsembleModel>
    </Models>

DataObjects as internal data container
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
DataObjects are required to store the inputs/outputs.

.. code:: xml

    <DataObjects>
      <PointSet name="inputHolderLikelihood">
        <Input>zout</Input>
        <Output>OutputPlaceHolder</Output>
      </PointSet>
      <PointSet name="inputHolder">
        <Input>alpha, beta, zout</Input>
        <Output>OutputPlaceHolder</Output>
      </PointSet>
      <PointSet name="inputHolderSimple">
        <Input>alpha, beta</Input>
        <Output>OutputPlaceHolder</Output>
      </PointSet>
      <PointSet name="outSet">
        <Input>alpha, beta</Input>
        <Output>zout, likelihood</Output>
      </PointSet>
      <PointSet name="out_export">
        <Input>traceID</Input>
        <Output>alpha, beta</Output>
      </PointSet>
      <PointSet name="simData">
        <!-- calibrated parameters -->
        <Input>alpha, beta</Input>
        <!-- simulation targets that will be passed to likelihood model -->
        <Output>zout</Output>
      </PointSet>
      <PointSet name="lhData">
        <!-- simulation targets -->
        <Input>zout</Input>
        <Output>likelihood</Output>
      </PointSet>
    </DataObjects>

OutStreams can be used to save the calculations into CSV files
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code:: xml

    <OutStreams>
      <Print name="dumpOut">
        <type>csv</type>
        <source>outSet</source>
        <what>input, output</what>
      </Print>
      <Print name="dumpExport">
        <type>csv</type>
        <source>out_export</source>
        <what>input, output</what>
      </Print>
    </OutStreams>

Steps to control the calculation flows:
+++++++++++++++++++++++++++++++++++++++
MultiRun is used to perform the Metropolis/AdaptiveMetropolis sampling.
IOStep is used to manage the inputs/outputs streams.

.. code:: xml

    <Steps>
      <MultiRun name="BayesianInference">
        <Input class="DataObjects" type="PointSet">inputHolderLikelihood</Input>
        <Input class="DataObjects" type="PointSet">inputHolderSimple</Input>
        <Model class="Models" type="EnsembleModel">EnsembleLH</Model>
        <Sampler class="Samplers" type="Metropolis">Metropolis</Sampler>
        <SolutionExport class="DataObjects" type="PointSet">out_export</SolutionExport>
        <Output class="DataObjects" type="PointSet">simData</Output>
        <Output class="DataObjects" type="PointSet">lhData</Output>
        <Output class="DataObjects" type="PointSet">outSet</Output>
      </MultiRun>
      <IOStep name="print">
        <Input class="DataObjects" type="PointSet">out_export</Input>
        <Input class="DataObjects" type="PointSet">outSet</Input>
        <Output class="OutStreams" type="Print">dumpExport</Output>
        <Output class="OutStreams" type="Print">dumpOut</Output>
      </IOStep>
    </Steps>

RunInfo to define the global settings for the calculations
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code:: xml

  <RunInfo>
    <WorkingDir>external</WorkingDir>
    <Sequence>BayesianInference, print</Sequence>
    <batchSize>1</batchSize>
    <internalParallel>False</internalParallel>
  </RunInfo>




