# ../execute/pyEmax_Bmax_angle_freq-*_mode-*.csvから(θEmax, θBmax)(理論値)とその時のWNA, 方位角を読みこむ
# wave_mgf_datasetから1スピンごとの(θEmax, θBmax)(観測値)の範囲を算出
# 観測値の範囲に理論値が含まれるかどうかを判定

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
saveDir = '../plots/wnaEstimation/'

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

# split dataset into half spin
halfSpinDatasetList = []
for i in range(len(halfSpinIdxRangeList)):
    halfSpinDatasetList.append(subDataset.sel(Epoch=slice(Epoch[halfSpinIdxRangeList[i][0]],
                                                          Epoch[halfSpinIdxRangeList[i][1]])))
