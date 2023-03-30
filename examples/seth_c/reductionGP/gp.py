import pandas as pd
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, RationalQuadratic, ExpSineSquared, DotProduct, ConstantKernel
from numpy.linalg import svd
import os

import threading
localLock = threading.RLock()

def initialize(self, runInfo, inputs):
  self.reduceSize = 12

  ### load data
  seth_tests = ['C'] # Only read in SETH-C data
  filenames = ['bisona_toptan']
  dataType = ['inputs', 'outputs', 'exp']
  data = {}
  cwd = os.path.dirname(os.path.abspath(__file__))
  for e in seth_tests:
      for m in filenames:
          for t in dataType:
              name = e + '_' + m + '_' + t + '.pkl'
              name = os.path.join(cwd, '..', 'models', name)
              df = pd.read_pickle(name)
              data[t] = df

  inpData = data['inputs'].to_numpy()
  outData = data['outputs'].to_numpy()
  # expData = data['exp'].to_numpy().ravel()

  outDataMean = np.mean(outData, axis=1)
  outDiff = outData - outDataMean.reshape(-1,1)
  ### PCA reduction
  u, _, _ = svd(outDiff)
  ur = u[:,0:self.reduceSize]
  outDiffR = np.matmul(ur.T, outDiff)
  self.outDataMeanR = np.matmul(ur.T, outDataMean)

  kernels = [ConstantKernel(0.1, (0.01, 10.0)) * RBF(length_scale=1.0, length_scale_bounds=(1e-1, 10.0)),
             1.0 * RationalQuadratic(length_scale=1.0, alpha=0.1),
             1.0 * ExpSineSquared(length_scale=1.0, periodicity=3.0,
                                  length_scale_bounds=(0.1, 10.0),
                                  periodicity_bounds=(1.0, 10.0)),
             ConstantKernel(0.1, (0.01, 10.0))
                 * (DotProduct(sigma_0=1.0, sigma_0_bounds=(0.1, 10.0)) ** 2),
             ConstantKernel(0.1, (0.01, 10.0)) * Matern(length_scale=1.0,
                          nu=2.5)]
  kernel = kernels[1]
  self.ensembleRom = list(GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9) for _ in range(self.reduceSize))
  # Fit to data using Maximum Likelihood Estimation of the parameters
  for i in range(self.reduceSize):
    self.ensembleRom[i].fit(inpData, outDiffR[i,:])

  # self.time = data['exp'].index.to_numpy()
  self.time = np.asarray(list(range(self.reduceSize)))
  self._params = ['pcf_scale', 'fuel_k_scale', 'fuel_cp_scale', 'clad_k_scale', 'clad_cp_scale', 'fuel_roughness', 'clad_roughness', 'emissivity_primary', 'emissivity_secondary', 'contact_coef', 'gap_cond', 'kennard_coef']

  import pickle
  for i in range(self.reduceSize):
     with open('gp_'+str(i)+'.pkl', 'wb') as f:
        pickle.dump(self.ensembleRom[i], f)


def run(self, Input):
  testInp = [Input[var] for var in self._params]
  testInp = np.asarray(testInp)
  Y = None
  for i in range(self.reduceSize):
    y_pred, cov = self.ensembleRom[i].predict(testInp.reshape(1,-1), return_cov=True)
    if Y is None:
      Y = y_pred
      yCov = cov
    else:
      Y = np.concatenate((Y,y_pred))
      yCov = np.concatenate((yCov, cov))
  self.clad_temp_OD = Y + self.outDataMeanR
  self.clad_temp_OD_cov = yCov.flatten()
