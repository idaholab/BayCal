# Copyright 2022 Battelle Energy Alliance, LLC
# ALL RIGHTS RESERVED
import numpy as np
import scipy.stats as st
import seaborn as sns
import matplotlib.pyplot as plt
#import corner
import pandas as pd

### control
fname = 'dumpExport.csv'
### thining of the chain
interval = 20
### load data
df = pd.read_csv(fname, index_col='traceID')
index = df.index
x = range(index[0], index[-1], interval)
df = df.loc[x]
print(df.describe())
### Histgram plot
df.hist(alpha=0.5, bins=50)
### trace plot
df.plot(subplots=True)
### Autocorrelation plot
"""
Autocorrelation plots are often used for checking randomness in time series.
This is done by computing autocorrelations for data values at varying time lags.
If time series is random, such autocorrelations should be near zero for any and
all time-lag separations. If time series is non-random then one or more of the
autocorrelations will be significantly non-zero. The horizontal lines displayed
in the plot correspond to 95% and 99% confidence bands. The dashed line is 99%
confidence band.
"""

for var in df.columns:
  plt.figure()
  acPlot = pd.plotting.autocorrelation_plot(df[var])
  plt.title(var)
#### Joint Distribution Plots
g = sns.PairGrid(df)
# g.map(sns.scatterplot)
# g.map(sns.histplot)
# g.map_offdiag(sns.scatterplot)
g.map_diag(sns.histplot, stat='density')
g.map_diag(sns.kdeplot, color='.3')
g.map_upper(sns.scatterplot)
g.map_lower(sns.kdeplot)

plt.show()
