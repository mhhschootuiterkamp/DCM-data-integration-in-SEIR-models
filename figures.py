"""
Create figures from the paper, base on initalization.py.
"""

import matplotlib.pyplot as plt

from initalization import *

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df_SEIR['Date'][14:],(df_SEIR['Rep only contacts'][14:] / df_SEIR['Rep'][14:] - 1),label = 'Based on COVID RADAR data',color = 'darkblue')
ax.plot(df_SEIR_m['Date'][14:],(df_SEIR_m['Rep only contacts'][14:] / df_SEIR_m['Rep'][14:] - 1),label = 'Based on COVID RADAR and CoronaMelder data',color = 'darkred')
ax.axhline(y = 0, color = 'black', linestyle = 'dotted')
ax.set_xlabel('Date')
ax.set_ylabel('Relative difference')
ax.set_title('Relative difference between estimates of effective reproduction number')
ax.legend()
plt.show()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df_SEIR['Date'],df_SEIR['I'],label = 'Based on COVID RADAR data',color = 'blue')
ax.plot(df_SEIR_m['Date'],df_SEIR_m['I'],label = 'Based on COVID RADAR and CoronaMelder data',color = 'red')
ax.plot(df_SEIR['Date'],df_SEIR['prev'],label = 'Estimate of RIVM',color = 'black')
ax.fill_between(df_SEIR['Date'], df_SEIR['prev_up'],df_SEIR['prev_low'],alpha=.3)
ax.set_xlabel('Date')
ax.set_ylabel('Number of individuals')
ax.set_title('Estimates of the number of infectious individuals')
ax.legend(loc = 'upper left')
plt.show()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df_SEIR['Date'],df_SEIR['I'] / df_SEIR['prev'],label = 'Based on COVID RADAR data',color = 'darkblue')
ax.plot(df_SEIR_m['Date'],df_SEIR_m['I'] / df_SEIR_m['prev'],label = 'Based on COVID RADAR and CoronaMelder data',color = 'darkred')
ax.axhline(y = 1, color = 'black', linestyle = 'dotted')
ax.set_xlabel('Date')
ax.set_ylabel('Ratio')
ax.set_title('Ratio between different estimates of the number of infectious individuals')
ax.legend(loc = 'upper left')
plt.show()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df_SEIR['Date'][14:],df_SEIR['Rep only contacts'][14:],label = 'Based on COVID RADAR data',color = 'blue')
ax.plot(df_SEIR_m['Date'][14:],df_SEIR_m['Rep only contacts'][14:],label = 'Based on COVID RADAR and CoronaMelder data',color = 'red')
ax.plot(df_SEIR['Date'][14:],df_SEIR['Rep_rivm'][14:],label = 'Estimate of RIVM',color = 'black')
ax.axhline(y = 1, color = 'black', linestyle = 'dotted')
ax.set_xlabel('Date')
ax.set_ylabel('Effective reproduction number')
ax.set_title('Estimates of the effective reproduction number')
ax.legend()
plt.show()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df_SEIR['Date'][14:],df_SEIR['Rep only contacts'][14:] / df_SEIR['Rep_rivm'][14:],label = 'Based on COVID RADAR data',color = 'darkblue')
ax.plot(df_SEIR_m['Date'][14:],df_SEIR_m['Rep only contacts'][14:] / df_SEIR_m['Rep_rivm'][14:],label = 'Based on COVID RADAR and CoronaMelder data',color = 'darkred')
ax.axhline(y = 1, color = 'black', linestyle = 'dotted')
ax.set_xlabel('Date')
ax.set_ylabel('Ratio')
ax.set_title('Ratio between different estimates of the effective reproduction number')
ax.legend()
plt.show()