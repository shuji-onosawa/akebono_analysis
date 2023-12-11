# ../execute/pyEmax_Bmax_angle_freq-*_mode-*.csvから(θEmax, θBmax)(理論値)とその時のWNA, 方位角を読みこむ
# wave_mgf_datasetから1スピンごとの(θEmax, θBmax)(観測値)の範囲を算出
# 観測値の範囲に理論値が含まれるかどうかを判定

from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
import numpy as np
from utilities import find_zero_cross_idx
from matplotlib import pyplot as plt
import csv
import os

# Input parameters
date = '1990-02-11'
startTime = date + 'T18:05:00'
endTime = date + 'T18:09:00'

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
epwrArySubDS = halfSpinDatasetList[0]['akb_mca_Emax_pwr'].values


def getAngleAtPeakPwr(angleAry, pwrAry):
    """
    Args:
        angleAry (1D ndarray): 角度の配列
        pwrAry (1D ndarray): 強度の配列
    Returns:
        angleAtPeakPwr (float): 最大値の角度
    """
    # pwrAry にnanが含まれる場合は、nanを返す
    if np.isnan(pwrAry).any():
        angleAtPeakPwr = np.nan
        return angleAtPeakPwr
    # pwrAry にnanが含まれない場合は、最大値の角度を返す
    maxValue = np.max(pwrAry)
    maxIdx = np.where(pwrAry == maxValue)[0]
    # もしmaxIdxが1つの場合は、そのインデックスの角度を返す
    if len(maxIdx) == 1:
        angleAtPeakPwr = angleAry[maxIdx]
    # もしmaxIdxが複数の場合は、nanを返す
    else:
        angleAtPeakPwr = np.nan
    return angleAtPeakPwr


def calcAngleAtPeakPwr(halfSpinDatasetList):
    """
    Args:
        halfSpinDatasetList (list): halfSpinごとに分割されたDatasetのリスト

    Returns:
        angleAtPeakPwrDict (dict): halfSpinごと最初の時刻、各チャンネルの最大値の角度の辞書
    """
    angleAtPeakPwrDict = {}

    epochAry = np.zeros(len(halfSpinDatasetList))
    EangleMatrix = np.zeros((len(halfSpinDatasetList), 16)) # mcaのチャンネルは全部で16個
    BangleMatrix = np.zeros((len(halfSpinDatasetList), 16)) # mcaのチャンネルは全部で16個
    for i in range(len(halfSpinDatasetList)):
        epoch = halfSpinDatasetList[i].coords['Epoch'].values[0]
        epochAry[i] = epoch

        EpwrAry = halfSpinDatasetList[i]['akb_mca_Emax_pwr'].values
        BpwrAry = halfSpinDatasetList[i]['akb_mca_Bmax_pwr'].values
        EangleAry = halfSpinDatasetList[i]['angle_b0_Ey'].values
        sByangleAry = halfSpinDatasetList[i]['angle_b0_sBy'].values
        BloopangleAry = halfSpinDatasetList[i]['angle_b0_Bloop'].values
        for ch in range(16):
            if ch < 10:
                EangleMatrix[i, ch] = getAngleAtPeakPwr(EangleAry, EpwrAry[:, ch])
                BangleMatrix[i, ch] = getAngleAtPeakPwr(sByangleAry, BpwrAry[:, ch])
            else:
                EangleMatrix[i, ch] = getAngleAtPeakPwr(BloopangleAry, EpwrAry[:, ch])
                BangleMatrix[i, ch] = getAngleAtPeakPwr(BloopangleAry, BpwrAry[:, ch])
    angleAtPeakPwrDict['Epoch'] = epochAry
    for ch in range(16):
        # 角度が負の場合は180度足して正にする
        EangleMatrix[:, ch][EangleMatrix[:, ch] < 0] += 180
        BangleMatrix[:, ch][BangleMatrix[:, ch] < 0] += 180
        # dictionaryに追加
        angleAtPeakPwrDict['angleAtPeakEpwrCh{}'.format(ch)] = EangleMatrix[:, ch]
        angleAtPeakPwrDict['angleAtPeakBpwrCh{}'.format(ch)] = BangleMatrix[:, ch]

    return angleAtPeakPwrDict


def saveAngleAtPeakPwr(angleAtPeakPwrDict):
    """
    Args:
        angleAtPeakPwrDict (dict): halfSpinごと最初の時刻、各チャンネルの最大値の角度の辞書
    """
    saveDir = '../execute/'+date+'/'
    saveName = 'peakAngleObs.csv'
    os.makedirs(saveDir, exist_ok=True)
    with open(saveDir+saveName, 'w') as f:
        writer = csv.writer(f)
        # dictionary の key を header として書き出す
        writer.writerow(angleAtPeakPwrDict.keys())
        # dictionary の value を書き出す
        writer.writerows(zip(*angleAtPeakPwrDict.values()))

'''
def wnaEstimation(angleAtPeakPwrDict):
    """
    Args:
        angleAtPeakPwrDict (dict): halfSpinごと最初の時刻、各チャンネルの最大値の角度の辞書

    Returns:
        wnaDict (dict): halfSpinごと最初の時刻、L mode 仮定時の各チャンネルのWNAの辞書、 R mode 仮定時の各チャンネルのWNAの辞書
    """
    wnaDict = {}
    wnaDict['Epoch'] = angleAtPeakPwrDict['Epoch']
    for ch in range(16):
        EpwrPeakAngle = angleAtPeakPwrDict['angleAtPeakEpwrCh{}'.format(ch)]
        BpwrPeakAngle = angleAtPeakPwrDict['angleAtPeakBpwrCh{}'.format(ch)]
        wnaDict['angleAtPeakEpwrCh{}'.format(ch)] = EpwrPeakAngle
        wnaDict['angleAtPeakBpwrCh{}'.format(ch)] = BpwrPeakAngle
        # L mode 仮定時のWNA推定
        LmodeWNA = np.zeros(len(EpwrPeakAngle))
'''

angleAtPeackPwr = calcAngleAtPeakPwr(halfSpinDatasetList)
# csvファイルに書き出す
saveAngleAtPeakPwr(angleAtPeackPwr)
