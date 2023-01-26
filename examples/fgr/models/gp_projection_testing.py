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

### load data
data = loadmat('BISON_data_all.mat')
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
expFGR = data['EXP_FGR'][:,1]
expFGRCov = (expFGR * 0.1)**2
print(data.keys())
print('exp len:', data['EXP_FGR'].shape)
print('fgr100:', bisonFGR100.shape)
print('fgr200:', bisonFGR200.shape)
print('fgr50:', bisonFGR50.shape)
print('fgr25:', bisonFGR25.shape)
print('design100', design100.shape)
print('design200', design200.shape)
print('design50', design50.shape)
print('design25', design25.shape)
numOut = len(data['EXP_FGR'])

df = pd.DataFrame(data['EXP_FGR'][:,1], index=data['EXP_FGR'][:,0], columns=['Exp'])
ax = df.plot(style=['ro'], label='Exp', xlabel='t', ylabel='FGR')
df_sim = pd.DataFrame(bisonFGR100, index=data['EXP_FGR'][:,0])
df_sim.plot(ax=ax)
# plt.show()
df_inp = pd.DataFrame(design100, columns=['temp', 'grainRadius', 'igDiffCoeff', 'resolution', 'gbDiffCoeff'])
print(df_inp.describe())

inpData = design100
outData = bisonFGR100
testInp = design25
testOut = bisonFGR25

###### PCA reduction
outDataMean = np.mean(outData, axis=1)
outDiff = outData - outDataMean.reshape(-1,1)
expFGRDiff = expFGR - outDataMean
testOutDiff = testOut - outDataMean.reshape(-1,1)
romSize = 2
Ur, Sr, Vr = svd(outDiff)
Ur = Ur[:, 0:romSize]
outDiffR = np.matmul(Ur.T, outDiff)
expFGRDiffR = np.matmul(Ur.T, expFGRDiff)
testOutDiffR = np.matmul(Ur.T, testOutDiff)
outDataMeanR = np.matmul(Ur.T, outDataMean)

df_exp_R = pd.DataFrame(outDataMeanR+ expFGRDiffR, columns=['exp'])
ax = df_exp_R.plot(style=['ro'], label='Exp', xlabel='t', ylabel='FGR')
df_sim_R = pd.DataFrame(outDiffR+outDataMeanR.reshape(-1,1))
df_sim_R.plot(ax=ax)
plt.show()

expFGRCovR = np.matmul(Ur.T, np.matmul(np.diag(expFGRCov), Ur))
print('Reduced Experiment Data:')
print(outDataMeanR + expFGRDiffR)
print('Reduced Experiment Cov:')
print(expFGRCovR)

# kernels = [ConstantKernel(0.1, (0.01, 10.0)) * RBF(length_scale=10, length_scale_bounds=(1e-2, 100)),
#            1.0 * RationalQuadratic(length_scale=1.0, alpha=0.1),
#            1.0 * ExpSineSquared(length_scale=1.0, periodicity=3.0,
#                                 length_scale_bounds=(0.1, 10.0),
#                                 periodicity_bounds=(1.0, 10.0)),
#            ConstantKernel(0.1, (0.01, 10.0))
#                * (DotProduct(sigma_0=1.0, sigma_0_bounds=(0.1, 10.0)) ** 2),
#            ConstantKernel(1., (1E-3, 1000.0)) * Matern(length_scale=1., length_scale_bounds=(1e-1, 10.0),
#                         nu=2.5),
#            1.0 * Matern(length_scale=1., length_scale_bounds=(1e-1, 10.0),
#                          nu=2.5)]
# kernel = kernels[4]
#
# ensembleRom = list(GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=20) for _ in range(romSize))
# # # Fit to data using Maximum Likelihood Estimation of the parameters
# for i in range(romSize):
#   ensembleRom[i].fit(inpData, outDataR[i,:])
#
# Y = None
# Y_cov = None
# for i in range(romSize):
#   y_pred, cov = ensembleRom[i].predict(testInp, return_std=True)
#   if Y is None:
#     Y = y_pred
#     Y_cov = cov
#   else:
#     Y = np.vstack((Y,y_pred))
#     Y_cov = np.vstack((Y_cov, cov))
#   # print(cov)
#
# score = 0.
# for i in range(testOutR.shape[-1]):
#   err = r2_score(Y[:,i], testOutR[:,i])
#   print(err)
#   score += err
# print('r2_score:', score/testOutR.shape[-1])
#
# print(Y)
# print(testOutR)
# print(Y-testOutR)

# df_predict = pd.DataFrame(Y, index = data['EXP_FGR'][:,0])
# ax = df.plot(style=['ro'], label='Exp', xlabel='t', ylabel='FGR')
# df_predict.plot(ax=ax)
# plt.show()
