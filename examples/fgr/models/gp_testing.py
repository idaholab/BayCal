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


def predict(testInp, ensembleRom):
  Y = None
  Y_cov = None
  for i in range(len(ensembleRom)):
    y_pred, cov = ensembleRom[i].predict(testInp, return_cov=True)
    if Y is None:
      Y = y_pred
      Y_cov = cov
    else:
      Y = np.vstack((Y,y_pred))
      Y_cov = np.vstack((Y_cov, cov))
    # print(cov)
  return Y, Y_cov

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
print(expFGRCov)
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

kernels = [ConstantKernel(0.1, (0.01, 10.0)) * RBF(length_scale=10, length_scale_bounds=(1e-2, 100)),
           1.0 * RationalQuadratic(length_scale=1.0, alpha=0.1),
           1.0 * ExpSineSquared(length_scale=1.0, periodicity=3.0,
                                length_scale_bounds=(0.1, 10.0),
                                periodicity_bounds=(1.0, 10.0)),
           ConstantKernel(0.1, (0.01, 10.0))
               * (DotProduct(sigma_0=1.0, sigma_0_bounds=(0.1, 10.0)) ** 2),
           ConstantKernel(1.) * Matern(length_scale=1.,nu=2.5),
           Matern(length_scale=1.,nu=2.5)+ConstantKernel(1.)]
kernel = kernels[5]

ensembleRom = list(GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=20) for _ in range(numOut))
# # Fit to data using Maximum Likelihood Estimation of the parameters
for i in range(numOut):
  ensembleRom[i].fit(inpData, outData[i,:])

Y, Y_cov = predict(testInp, ensembleRom)
print(Y_cov)

score = 0.
for i in range(testOut.shape[-1]):
  err = r2_score(Y[:,i], testOut[:,i])
  print(err)
  score += err
print('r2_score:', score/testOut.shape[-1])

# df_predict = pd.DataFrame(Y, index = data['EXP_FGR'][:,0])
# ax = df.plot(style=['ro'], label='Exp', xlabel='t', ylabel='FGR')
# df_predict.plot(ax=ax)
# plt.show()


### test best value
testInp = np.asarray([0.9985, 0.4903, 6.4707, 5.7717, 2.4686])
Y, Y_cov = predict(testInp.reshape(1,-1), ensembleRom)
print(Y_cov)
# testInpFull = np.asarray([0.9763, 1.56746, 8.593076, 7.443521, 5.435424])
# testInpFull = np.asarray([1.024972,     1.587199,     8.268945,     8.270110,     6.424983])
# testInpFull = np.asarray([1.002193,     1.175592,     9.637261,     8.937706,     4.760015])
testInpFull = np.asarray([1.000177, 0.984510,    9.436257,    2.684452,     4.404000])
test = np.asarray([1.024972,     0.4903,     8.268945,     8.270110,     6.424983])
Yp, _ = predict(testInpFull.reshape(1,-1), ensembleRom)
Yt, _ = predict(test.reshape(1,-1), ensembleRom)
df_predict = pd.DataFrame(Y, index = data['EXP_FGR'][:,0], columns=['literature'])
df_p_predict = pd.DataFrame(Yp, index = data['EXP_FGR'][:,0], columns=['calculation'])
df_p_t = pd.DataFrame(Yt, index = data['EXP_FGR'][:,0], columns=['test'])
print('Literature:', abs(df.iloc[:,0]-df_predict.iloc[:,0]).sum())
print('Calculation:', abs(df.iloc[:,0]-df_p_predict.iloc[:,0]).sum())
print('Testing', abs(df.iloc[:,0]-df_p_t.iloc[:,0]).sum())
ax = df.plot(style=['ro'], label='Exp', xlabel='t', ylabel='FGR')
df_predict.plot(ax=ax)
df_p_predict.plot(ax=ax, style=['k+'])
# df_p_t.plot(ax=ax, style=['bo'])
plt.show()
