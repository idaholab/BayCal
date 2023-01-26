# Copyright 2022 Battelle Energy Alliance, LLC
# ALL RIGHTS RESERVED

import scipy.stats as st
import numpy as np

def initialize(self, runInfoDict, inputFiles):
  """
    Method to generate the observed data
    Assume alpha = 1.0, beta = 2.5, sigma = 1.0.
    and zout = alpha + beta * random + random * sigma
    @ In, runInfoDict, dict, the dictionary containing the runInfo
    @ In, inputFiles, list, the list of input files
    @ Out, None
  """
  numPoints = 50
  self.time = np.atleast_1d(np.linspace(-3, 3, 50))

def run(self, inputDict):
  """
    Method required by RAVEN to run this as an external model.
    log likelihood function
    @ In, self, object, object to store members on
    @ In, inputDict, dict, dictionary containing inputs from RAVEN
    @ Out, None
  """
  self.alpha = inputDict['alpha']
  self.beta = inputDict['beta']
  self.gamma = inputDict['gamma']
  out = np.tanh(self.time-self.gamma) + self.alpha * np.cos(self.beta*(self.time-self.gamma))
  noise = st.norm.rvs(loc=0, scale=0.02, size=len(out))
  self.eta = np.atleast_1d(out + noise)
