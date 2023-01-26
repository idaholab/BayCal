# Copyright 2022 Battelle Energy Alliance, LLC
# ALL RIGHTS RESERVED

import scipy.stats as st
import numpy as np
from pyDOE import lhs
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
# fig = plt.figure()
# ax = fig.gca(projection='3d')

np.random.seed(123456)

def simulationModel(t, alpha=0.2, beta=5, gamma=0):
  """
  """
  out = np.tanh(t-gamma) + alpha * np.cos(beta*(t-gamma))
  return out

def discrepancyModel(t):
  """
  """
  out = 0.05*np.sin(5.*t)
  return out

def realModel(t, alpha=0.2, beta=5, gamma=0):
  """
  """
  out = simulationModel(t, alpha, beta, gamma) + discrepancyModel(t)
  return out

def observationMeasurements(t, alpha=0.2, beta=5, gamma=0):
  """
  """
  out = realModel(t, alpha, beta, gamma)
  noise = st.norm.rvs(loc=0, scale=0.04, size=len(out))
  out += noise
  return out

def observationSimulations(t, alpha=0.2, beta=5, gamma=0):
  """
  """
  out = simulationModel(t, alpha, beta, gamma)
  noise = st.norm.rvs(loc=0, scale=0.02, size=len(out))
  out += noise
  return out

numPoints = 50
numSamples = 10

t=np.linspace(-3, 3, 50)

y = observationMeasurements(t)
# plt.plot(t, y, 'ro')
# plt.show()
df = pd.DataFrame(y, index=t, columns=['Exp'])
ax = df.plot(style=['ro'], label='Exp', xlabel='t', ylabel='y')

alpha = np.linspace(0.1, 0.3, numSamples)
beta = np.linspace(4, 5, numSamples)
gamma = np.linspace(-1., 1., numSamples)

for i in range(len(alpha)):
  out = observationSimulations(t, alpha[i], beta[i], gamma[i])
  df['Sim_'+str(i)] = out

df.iloc[:,1:].plot(ax=ax)
plt.show()


### posterior testing
numSamples=120
alpha = st.norm.rvs(0.206686, 0.029962, numSamples)
beta = st.norm.rvs(5.017555, 0.076664, numSamples)
gamma = st.norm.rvs(0.033868, 0.023204, numSamples)
df_p = pd.DataFrame(y, index=t, columns=['Exp'])
ax = df.plot(style=['ro'], label='Exp', xlabel='t', ylabel='y')
for i in range(len(alpha)):
  out = observationSimulations(t, alpha[i], beta[i], gamma[i])
  df['Sim_'+str(i)] = out

df.iloc[:,1:].plot(ax=ax, label='Sim')
plt.show()

df_p = pd.DataFrame(y, index=t, columns=['Exp'])
ax = df.plot(style=['ro'], label='Exp', xlabel='t', ylabel='y')
for i in range(len(alpha)):
  out = observationSimulations(t, 0.206686, 5.017555, 0.033868)
  df['Sim_'+str(i)] = out

df.iloc[:,1:].plot(ax=ax, label='Sim')
plt.show()
# params = lhs(2, samples=numSamples, criterion='center')
# alpha, beta = params[:,0], params[:,1]
# eta = np.zeros((numPoints, numSamples))
# for i in range(numSamples):
#   eta[:,i] = observationSimulations(t, alpha=alpha[i], beta=beta[i])

# df = pd.DataFrame(eta, columns = list(range(numSamples)))
# df_exp = pd.DataFrame(y, columns=['exp'])
# df['exp'] = df_exp
# df[[10, 11, 12, 15, 16, 'exp']].plot()
# plt.show()
