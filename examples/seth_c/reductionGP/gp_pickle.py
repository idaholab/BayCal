import pandas as pd
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, RationalQuadratic, ExpSineSquared, DotProduct, ConstantKernel
from numpy.linalg import svd
import os
import pickle

import threading
localLock = threading.RLock()

def initialize(self, runInfo, inputs):
  self.reduceSize = 12
  self.time = np.asarray(list(range(self.reduceSize)))
  self._params = ['pcf_scale', 'fuel_k_scale', 'fuel_cp_scale', 'clad_k_scale', 'clad_cp_scale', 'fuel_roughness', 'clad_roughness', 'emissivity_primary', 'emissivity_secondary', 'contact_coef', 'gap_cond', 'kennard_coef']
  self.ensembleRom = []
  self.outDataMeanR = np.asarray([-73777.83300882,   7240.669854,    4165.34502144,   -872.86185406, 2287.84436974,   1058.49402228,   -570.58932593,    314.52333594, -277.95012659,   -173.24443402,    425.17291697,   -159.83675214])
  cwd = os.path.dirname(os.path.abspath(__file__))
  # ### load data
  # seth_tests = ['C'] # Only read in SETH-C data
  # filenames = ['bisona_toptan']
  # dataType = ['inputs', 'outputs', 'exp']
  # data = {}

  # for e in seth_tests:
  #     for m in filenames:
  #         for t in dataType:
  #             name = e + '_' + m + '_' + t + '.pkl'
  #             name = os.path.join(cwd, '..', 'models', name)
  #             df = pd.read_pickle(name)
  #             data[t] = df

  # inpData = data['inputs'].to_numpy()
  # outData = data['outputs'].to_numpy()
  # # expData = data['exp'].to_numpy().ravel()

  # outDataMean = np.mean(outData, axis=1)
  # outDiff = outData - outDataMean.reshape(-1,1)
  # ### PCA reduction
  # u, _, _ = svd(outDiff)
  # ur = u[:,0:self.reduceSize]
  # outDiffR = np.matmul(ur.T, outDiff)
  # self.outDataMeanR = np.matmul(ur.T, outDataMean)
  # print(self.outDataMeanR)

  for i in range(self.reduceSize):
     name = os.path.join(cwd, 'gp_'+str(i)+'.pkl')
     with open(name, 'rb') as f:
        self.ensembleRom.append(pickle.load(f))

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
