from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
import numpy as np
from utilities import find_zero_cross_idx
from matplotlib import pyplot as plt
import os

# Input parameters
date = '1990-2-11'
startTime = date + 'T18:05:00'
endTime = date + 'T18:09:00'

# Constants
freqLabel = ['3.16 Hz', '5.62 Hz', '10 Hz', '17.8 Hz', '31.6 Hz', '56.2 Hz', '100 Hz',
             '178 Hz', '316 Hz', '562 Hz', '1 kHz', '1.78 kHz']
saveDir = '../plots/Ishigaya_events/' + date + '/' + 'each_spin/'

# Load data
ds = make_wave_mgf_dataset(date=date, mca_datatype='pwr')
subDataset = ds.sel(Epoch=slice(startTime, endTime))

angleB0EyArray = subDataset['angle_b0_Ey'].values
EpwrArray = subDataset['akb_mca_Emax_pwr'].values

angleB0sByArray = subDataset['angle_b0_sBy'].values
angleB0BloopArray = subDataset['angle_b0_Bloop'].values
BpwrArray = subDataset['akb_mca_Bmax_pwr'].values
Epoch = subDataset.coords['Epoch'].values

# Find half spin index range for E field
posToNegIdx, negToPosIdx = find_zero_cross_idx(angleB0EyArray)
halfSpinIdxRangeList = []

if posToNegIdx[0] > negToPosIdx[0]:
    for i in range(len(posToNegIdx) - 1):
        halfSpinIdxRangeList.append([negToPosIdx[i] + 1, posToNegIdx[i] + 1])
        halfSpinIdxRangeList.append([posToNegIdx[i] + 1, negToPosIdx[i + 1] + 1])
else:
    for i in range(len(posToNegIdx)):
        halfSpinIdxRangeList.append([posToNegIdx[i] + 1, negToPosIdx[i] + 1])
        halfSpinIdxRangeList.append([negToPosIdx[i] + 1, posToNegIdx[i + 1] + 1])

# Calculate pwr max and min for each channel
# Max and min are used for ylim of plot
EpwrMaxArray = subDataset['akb_mca_Emax_pwr'].max(dim='Epoch').values
EpwrMinArray = subDataset['akb_mca_Emax_pwr'].min(dim='Epoch').values
BpwrMaxArray = subDataset['akb_mca_Bmax_pwr'].max(dim='Epoch').values
BpwrMinArray = subDataset['akb_mca_Bmax_pwr'].min(dim='Epoch').values

# angle*arrayの値が負の場合は180度加算する
angleB0EyArray[angleB0EyArray < 0] += 180
angleB0sByArray[angleB0sByArray < 0] += 180
angleB0BloopArray[angleB0BloopArray < 0] += 180

# Plot angleB0Ey vs. Epwr, angleB0B vs. Bpwr for each half spin
print("Plotting...")
for j in range(len(halfSpinIdxRangeList) - 2):
    # epochs of half spin 1, 2, 3
    epoch1 = Epoch[halfSpinIdxRangeList[j][0]]
    epoch2 = Epoch[halfSpinIdxRangeList[j + 1][0]]
    epoch3 = Epoch[halfSpinIdxRangeList[j + 2][0]]
    # Plot angleB0* vs. *pwr for each channel
    for channelIdx in range(12):
        fig, axs = plt.subplots(2, 1, figsize=(12, 8))
        axs[0].plot(angleB0EyArray[halfSpinIdxRangeList[j][0]:halfSpinIdxRangeList[j][1]],
                    EpwrArray[halfSpinIdxRangeList[j][0]:halfSpinIdxRangeList[j][1], channelIdx], label=str(epoch1), marker='*', linestyle='None')
        axs[0].plot(angleB0EyArray[halfSpinIdxRangeList[j + 1][0]:halfSpinIdxRangeList[j + 1][1]],
                    EpwrArray[halfSpinIdxRangeList[j + 1][0]:halfSpinIdxRangeList[j + 1][1], channelIdx], label=str(epoch2), marker='*', linestyle='None')
        axs[0].plot(angleB0EyArray[halfSpinIdxRangeList[j + 2][0]:halfSpinIdxRangeList[j + 2][1]],
                    EpwrArray[halfSpinIdxRangeList[j + 2][0]:halfSpinIdxRangeList[j + 2][1], channelIdx], label=str(epoch3), marker='*', linestyle='None')
        axs[0].set_title('Angle between B0 and Ey vs. Power for ' + freqLabel[channelIdx] + '\n' +
                            str(Epoch[halfSpinIdxRangeList[j][0]]) + ' to ' + str(Epoch[halfSpinIdxRangeList[j + 2][1]]))
        axs[0].set_xlabel('Angle between B0 and Ey (deg)')
        axs[0].set_ylabel('Power [(mV/m)^2/Hz]')
        axs[0].set_yscale('log')
        axs[0].set_xlim(0, 180)
        axs[0].set_ylim(EpwrMinArray[channelIdx], EpwrMaxArray[channelIdx])
        axs[0].legend()
        if channelIdx == 10 or channelIdx == 11:
            axs[1].plot(angleB0BloopArray[halfSpinIdxRangeList[j][0]:halfSpinIdxRangeList[j][1]],
                        BpwrArray[halfSpinIdxRangeList[j][0]:halfSpinIdxRangeList[j][1], channelIdx], label=str(epoch1), marker='*', linestyle='None')
            axs[1].plot(angleB0BloopArray[halfSpinIdxRangeList[j + 1][0]:halfSpinIdxRangeList[j + 1][1]],
                        BpwrArray[halfSpinIdxRangeList[j + 1][0]:halfSpinIdxRangeList[j + 1][1], channelIdx], label=str(epoch2), marker='*', linestyle='None')
            axs[1].plot(angleB0BloopArray[halfSpinIdxRangeList[j + 2][0]:halfSpinIdxRangeList[j + 2][1]],
                        BpwrArray[halfSpinIdxRangeList[j + 2][0]:halfSpinIdxRangeList[j + 2][1], channelIdx], label=str(epoch3), marker='*', linestyle='None')
            axs[1].set_title('Angle between B0 and Bloop vs. Power for ' + freqLabel[channelIdx] + '\n' +
                                str(Epoch[halfSpinIdxRangeList[j][0]]) + ' to ' + str(Epoch[halfSpinIdxRangeList[j + 2][1]]))
            axs[1].set_xlabel('Angle between B0 and Bloop (deg)')
            axs[1].set_ylabel('Power [pT^2/Hz]')
            axs[1].set_yscale('log')
            axs[1].set_xlim(0, 180)
            axs[1].set_ylim(BpwrMinArray[channelIdx], BpwrMaxArray[channelIdx])
            axs[1].legend()
        else:
            axs[1].plot(angleB0sByArray[halfSpinIdxRangeList[j][0]:halfSpinIdxRangeList[j][1]],
                        BpwrArray[halfSpinIdxRangeList[j][0]:halfSpinIdxRangeList[j][1], channelIdx], label=str(epoch1), marker='*', linestyle='None')
            axs[1].plot(angleB0sByArray[halfSpinIdxRangeList[j + 1][0]:halfSpinIdxRangeList[j + 1][1]],
                        BpwrArray[halfSpinIdxRangeList[j + 1][0]:halfSpinIdxRangeList[j + 1][1], channelIdx], label=str(epoch2), marker='*', linestyle='None')
            axs[1].plot(angleB0sByArray[halfSpinIdxRangeList[j + 2][0]:halfSpinIdxRangeList[j + 2][1]],
                        BpwrArray[halfSpinIdxRangeList[j + 2][0]:halfSpinIdxRangeList[j + 2][1], channelIdx], label=str(epoch3), marker='*', linestyle='None')
            axs[1].set_title('Angle between B0 and sBy vs. Power for ' + freqLabel[channelIdx] + '\n' +
                                str(Epoch[halfSpinIdxRangeList[j][0]]) + ' to ' + str(Epoch[halfSpinIdxRangeList[j + 2][1]]))
            axs[1].set_xlabel('Angle between B0 and sBy (deg)')
            axs[1].set_ylabel('Power [pT^2/Hz]')
            axs[1].set_yscale('log')
            axs[1].set_xlim(0, 180)
            axs[1].set_ylim(BpwrMinArray[channelIdx], BpwrMaxArray[channelIdx])
            axs[1].legend()
        # Save plot
        os.makedirs(saveDir + freqLabel[channelIdx] + '/', exist_ok=True)
        plt.savefig(saveDir + freqLabel[channelIdx] + '/spin' + str(j) +'-'+ str(j + 1) +'-'+ str(j + 2) + '.jpeg')
        plt.close()
print("Finished plotting")
