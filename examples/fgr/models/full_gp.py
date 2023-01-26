from scipy.io import loadmat
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, RationalQuadratic, ExpSineSquared, DotProduct, ConstantKernel
from sklearn.metrics import r2_score
from numpy.linalg import svd

#create scatter plot matrix for posterior distribution
from pandas.plotting import scatter_matrix
import threading
localLock = threading.RLock()

def initialize(self, runInfo, inputs):
  ### load data
  data = loadmat('../models/BISON_data_all.mat')
  # outputs
  bisonFGR100 = data['BISON_FGR100'].T
  bisonFGR200 = data['BISON_FGR200'].T
  bisonFGR50 = data['BISON_FGR50'].T
  bisonFGR25 = data['BISON_FGR25'].T
  # inputs: [Temperature, GrainRadius, Intra-granularGasAtomDiffusionCoefficient, Intra-granularReolutionParameter, GrainBoundaryDiffusionCoefficient]
  # range [0.95, 1.05], [0.4, 1.6], [0.1, 10], [0.1, 10], [0.1, 10]
  design200 = data['Design200']
  design100 = data['Design100']
  design50 = data['Design50']
  design25 = data['Design25']
  # experiments
  expFGR = data['EXP_FGR']
  self.numOut = len(expFGR)
  inpData = design100
  outData = bisonFGR100
  kernels = [ConstantKernel(0.1, (0.01, 10.0)) * RBF(length_scale=10, length_scale_bounds=(1e-2, 100)),
             1.0 * RationalQuadratic(length_scale=1.0, alpha=0.1),
             1.0 * ExpSineSquared(length_scale=1.0, periodicity=3.0,
                                  length_scale_bounds=(0.1, 10.0),
                                  periodicity_bounds=(1.0, 10.0)),
             ConstantKernel(0.1, (0.01, 10.0))
                 * (DotProduct(sigma_0=1.0, sigma_0_bounds=(0.1, 10.0)) ** 2),
             ConstantKernel(1.) * Matern(length_scale=1., nu=2.5),
             Matern(length_scale=1.,nu=2.5)+ConstantKernel(1.)]
  kernel = kernels[5]

  self.ensembleRom = list(GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=20) for _ in range(self.numOut))
  # Fit to data using Maximum Likelihood Estimation of the parameters
  for i in range(self.numOut):
    self.ensembleRom[i].fit(inpData, outData[i,:])

  self.time = expFGR[:,0]

def run(self, Input):
  self.temp = Input['temp']
  self.grainRadius = Input['grainRadius']
  self.igDiffCoeff = Input['igDiffCoeff']
  self.resolution = Input['resolution']
  self.gbDiffCoeff = Input['gbDiffCoeff']
  testInp = np.concatenate((self.temp, self.grainRadius, self.igDiffCoeff, self.resolution, self.gbDiffCoeff))
  y = None
  yCov = None
  for i in range(self.numOut):
    yp, cov = self.ensembleRom[i].predict(testInp.reshape(1,-1), return_cov=True)
    if y is None:
      y = yp
      yCov = cov
    else:
      y = np.concatenate((y,yp))
      yCov = np.concatenate((yCov, cov))
  self.fgr = y
  self.fgrCov = yCov.flatten()
