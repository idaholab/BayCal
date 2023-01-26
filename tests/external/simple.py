# Copyright 2017 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
  # np.random.seed(1086)
  self.sigma = 1.0
  self.rand = np.random.randn()

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
  mu = self.alpha + self.beta * self.rand
  self.zout = mu + self.sigma * np.random.randn()
  #print(self.zout)
