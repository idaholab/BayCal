from scipy.io import loadmat
import pandas as pd
import matplotlib.pyplot as plt

#create scatter plot matrix for posterior distribution
from pandas.plotting import scatter_matrix

### load data
data = loadmat('BISON_data_all.mat')
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

# print(expFGR[:,1]*0.1)

# ### write to CSV for RAVEN
# fileName = {'BISON_FGR200':'Design200', 'BISON_FGR100':'Design100', 'BISON_FGR50':'Design50', 'BISON_FGR25':'Design25'}
# for outFile, inpFile in fileName.items():
#   outDat = data[outFile]
#   inpDat = data[inpFile]
#   with open(outFile+'.csv', 'w') as f:
#     f.write('temp,grainRadius,igDiffCoeff,resolution,gbDiffCoeff,prefix,filename\n')
#     for i in range(len(inpDat)):
#       outStr = ','.join(str(elem) for elem in inpDat[i,:])
#       outStr = outStr + ',' + str(i) + ',' + outFile + '_' + str(i) + '.csv\n'
#       f.write(outStr)
#   for i in range(len(inpDat)):
#     filename = outFile + '_' + str(i) + '.csv'
#     with open(filename, 'w') as f:
#       f.write('time,fgr\n')
#       for j in range(len(outDat.T)):
#         outStr = str(expFGR[j,0]) + ',' + str(outDat[i,j]) + '\n'
#         f.write(outStr)

### Plot

dfData200 = pd.DataFrame(data=bisonFGR200.T, index=expFGR[:,0])
dfData100 = pd.DataFrame(data=bisonFGR100.T, index=expFGR[:,0])
dfData50 = pd.DataFrame(data=bisonFGR50.T, index=expFGR[:,0])
dfData25 = pd.DataFrame(data=bisonFGR25.T, index=expFGR[:,0])
dfExp = pd.DataFrame(data=expFGR[:,1], index=expFGR[:,0], columns=['exp'])
# df = dfData.join(dfExp)
# plt.figure()
fig, axes = plt.subplots(nrows=2, ncols=2)
plt.subplots_adjust(wspace=0.2, hspace=0.5)
dfData25.plot(legend=False, style='b-', linewidth='0.1', ax=axes[0,0])
dfExp['exp'].plot(style='r-', ax=axes[0,0])
axes[0,0].set_title('25 LHS Samples')
dfData50.plot(legend=False, style='b-', linewidth='0.1', ax=axes[0,1])
dfExp['exp'].plot(style='r-', ax=axes[0,1])
axes[0,1].set_title('50 LHS Samples')
dfData100.plot(legend=False, style='b-', linewidth='0.1', ax=axes[1,0])
dfExp['exp'].plot(style='r-', ax=axes[1,0])
axes[1,0].set_title('100 LHS Samples')
dfData200.plot(legend=False, style='b-', linewidth='0.1', ax=axes[1,1])
dfExp['exp'].plot(style='r-', ax=axes[1,1])
axes[1,1].set_title('200 LHS Samples')
plt.show()
