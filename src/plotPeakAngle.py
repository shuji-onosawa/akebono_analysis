# wnaEstimation.pyの中で、作成したdictionary.csvを読み込んで、グラフを作成する
import pandas as pd
import matplotlib.pyplot as plt

# constant
freqLabel = ['3.16 Hz', '5.62 Hz', '10 Hz', '17.8 Hz', '31.6 Hz', '56.2 Hz', '100 Hz',
             '178 Hz', '316 Hz', '562 Hz', '1 kHz', '1.78 kHz']
# Read the CSV file
df = pd.read_csv('../execute/1990-2-11/peakAngleObs.csv')

# Convert 'Epoch' to datetime
epochAry = pd.to_datetime(df['Epoch'], unit='ns').values

# Plot the graph
fig, axs = plt.subplots(6, 2, figsize=(10, 6), sharex='col')
axs = axs.flatten()
for i in range(len(freqLabel)):
    axs[i].scatter(epochAry, df['angleAtPeakEpwrCh'+str(i)], marker='*', s=5, label = 'E', color='b')
    axs[i].scatter(epochAry, df['angleAtPeakBpwrCh'+str(i)], marker='*', s=5, label = 'B', color='r')
    axs[i].errorbar(epochAry, df['angleAtPeakEpwrCh'+str(i)], yerr=df['EangleError'], fmt='*', ecolor='b', elinewidth=0.5, capsize=3)
    if i < 10:
        axs[i].errorbar(epochAry, df['angleAtPeakBpwrCh'+str(i)], yerr=df['BangleError'], fmt='*', ecolor='r', elinewidth=0.5, capsize=3)
    else:
        axs[i].errorbar(epochAry, df['angleAtPeakBpwrCh'+str(i)], yerr=df['BloopangleError'], fmt='*', ecolor='r', elinewidth=0.5, capsize=3)
    axs[i].set_xlabel('time [UT]')
    axs[i].set_ylabel('Angle [deg]\n@'+freqLabel[i])
    axs[i].set_ylim(0, 180)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()
