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
  bisonFGR100 = data['BISON_FGR100']
  bisonFGR200 = data['BISON_FGR200']
  bisonFGR50 = data['BISON_FGR50']
  bisonFGR25 = data['BISON_FGR25']
  # inputs: [Temperature, GrainRadius, Intra-granularGasAtomDiffusionCoefficient, Intra-granularReolutionParameter, GrainBoundaryDiffusionCoefficient]
  # range [0.95, 1.05], [0.4, 1.6], [0.1, 10], [0.1, 10], [0.1, 10]
  design200 = data['Design200']
  design100 = data['Design100']
  design50 = data['Design50']
  design25 = data['Design25']
  # experiments
  expFGR = data['EXP_FGR']

  ### GaussianProcess on the projected outputs
  inpData = design100
  outData = bisonFGR100

  ### PCA reduction
  u, s, vh = svd(outData.T)
  reduceSize = 2
  self.reduceSize = reduceSize
  ur = u[:,0:reduceSize]
  self.ur = ur
  outDataR = np.dot(outData, ur)

  kernels = [ConstantKernel(0.1, (0.01, 10.0)) * RBF(length_scale=1.0, length_scale_bounds=(1e-1, 10.0)),
             1.0 * RationalQuadratic(length_scale=1.0, alpha=0.1),
             1.0 * ExpSineSquared(length_scale=1.0, periodicity=3.0,
                                  length_scale_bounds=(0.1, 10.0),
                                  periodicity_bounds=(1.0, 10.0)),
             ConstantKernel(0.1, (0.01, 10.0))
                 * (DotProduct(sigma_0=1.0, sigma_0_bounds=(0.1, 10.0)) ** 2),
             ConstantKernel(0.1, (0.01, 10.0)) * Matern(length_scale=1.0,
                          nu=2.5)]
  kernel = kernels[4]
  self.ensembleRom = list(GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9) for _ in range(reduceSize))
  # Fit to data using Maximum Likelihood Estimation of the parameters
  for i in range(reduceSize):
    self.ensembleRom[i].fit(inpData, outDataR[:,i])

  self.time = expFGR[:,0]

def run(self, Input):
  self.temp = Input['temp']
  self.grainRadius = Input['grainRadius']
  self.igDiffCoeff = Input['igDiffCoeff']
  self.resolution = Input['resolution']
  self.gbDiffCoeff = Input['gbDiffCoeff']
  testInp = np.concatenate((self.temp, self.grainRadius, self.igDiffCoeff, self.resolution, self.gbDiffCoeff))
  Y = None
  for i in range(self.reduceSize):
    y_pred, sigma = self.ensembleRom[i].predict(testInp.reshape(1,-1), return_std=True)
    if Y is None:
      Y = y_pred
    else:
      Y = np.concatenate((Y,y_pred))
  self.fgr = np.dot(Y, self.ur.T)
