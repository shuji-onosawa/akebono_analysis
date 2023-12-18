# ../execute/pyEmax_Bmax_angle_freq-*_mode-*.csvから(θEmax, θBmax)(理論値)とその時のWNA, 方位角を読みこむ
# wave_mgf_datasetから1スピンごとの(θEmax, θBmax)(観測値)の範囲を算出
# 観測値の範囲に理論値が含まれるかどうかを判定

from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
import numpy as np
from utilities import find_zero_cross_idx
import csv
import os


def split_dataset_into_half_spins(date, start_time, end_time):
    # Convert input times to datetime format
    start_time = date + 'T' + start_time
    end_time = date + 'T' + end_time

    # Load data
    ds = make_wave_mgf_dataset(date=date, mca_datatype='pwr')
    sub_dataset = ds.sel(Epoch=slice(start_time, end_time))

    angleB0EyAry = sub_dataset['angle_b0_Ey'].values

    # Find half spin index range for E field
    pos_to_neg_idx, neg_to_pos_idx = find_zero_cross_idx(angleB0EyAry)
    half_spin_idx_range_list = []

    if pos_to_neg_idx[0] > neg_to_pos_idx[0]:
        for i in range(len(pos_to_neg_idx) - 1):
            half_spin_idx_range_list.append([neg_to_pos_idx[i] + 1, pos_to_neg_idx[i] + 1])
            half_spin_idx_range_list.append([pos_to_neg_idx[i] + 1, neg_to_pos_idx[i + 1] + 1])
    else:
        for i in range(len(pos_to_neg_idx)):
            half_spin_idx_range_list.append([pos_to_neg_idx[i] + 1, neg_to_pos_idx[i] + 1])
            half_spin_idx_range_list.append([neg_to_pos_idx[i] + 1, pos_to_neg_idx[i + 1] + 1])

    # Split dataset into half spin
    half_spin_dataset_list = []
    epoch = sub_dataset.coords['Epoch'].values
    for i in range(len(half_spin_idx_range_list)):
        half_spin_dataset_list.append(sub_dataset.sel(Epoch=slice(epoch[half_spin_idx_range_list[i][0]],
                                                                  epoch[half_spin_idx_range_list[i][1]])))

    return half_spin_dataset_list


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

    # 角度のエラーを計算
    EangleErrorAry = np.ones((len(halfSpinDatasetList)))
    BangleErrorAry = np.ones((len(halfSpinDatasetList)))
    BloopangleErrorAry = np.ones((len(halfSpinDatasetList)))
    # 最初のhalfspin中、角度が何度刻みで変化するかの平均値を計算する
    firstHalfSpinDs = halfSpinDatasetList[0]
    EangleAry = firstHalfSpinDs['angle_b0_Ey'].values
    BangleAry = firstHalfSpinDs['angle_b0_sBy'].values
    BloopangleAry = firstHalfSpinDs['angle_b0_Bloop'].values
    # 角度刻みの計算
    EangleDiff = np.nanmean(np.abs(EangleAry[1:] - EangleAry[:-1]))
    BangleDiff = np.nanmean(np.abs(BangleAry[1:] - BangleAry[:-1]))
    BloopangleDiff = np.nanmean(np.abs(BloopangleAry[1:] - BloopangleAry[:-1]))
    # dictionaryに追加
    angleAtPeakPwrDict['EangleError'] = EangleErrorAry * EangleDiff
    angleAtPeakPwrDict['BangleError'] = BangleErrorAry * BangleDiff
    angleAtPeakPwrDict['BloopangleError'] = BloopangleErrorAry * BloopangleDiff

    return angleAtPeakPwrDict


def saveAngleAtPeakPwr(angleAtPeakPwrDict):
    """
    Args:
        angleAtPeakPwrDict (dict): halfSpinごと最初の時刻、各チャンネルの最大値の角度の辞書
    """
    saveDir = '../execute/wnaEstimation/'
    saveName = 'peakAngleObs.csv'
    os.makedirs(saveDir, exist_ok=True)
    with open(saveDir+saveName, 'w') as f:
        writer = csv.writer(f)
        # dictionary の key を header として書き出す
        writer.writerow(angleAtPeakPwrDict.keys())
        # dictionary の value を書き出す
        writer.writerows(zip(*angleAtPeakPwrDict.values()))


def loadSimulatedAngleAtPeakPwrByCh(freq, mode):
    """
    ../execute/pyEmax_Bmax_angle_freq-freq_mode-mode.csvからWNA列と方位角行の(θEmax, θBmax)(理論値)の行列を読み込む
    Args:
        freq (str): 周波数
        mode (str): 波動モード, l or r
    Returns:
        simResultDict (dict): wna行のheader、方位角列のheader、模擬観測値θEmaxの行列 (WNA行, 方位角列)、模擬観測値θBmaxの行列 (WNA行, 方位角列)
    """
    csvFileName = '../execute/SimulatedObservation/pyEmax_Bmax_angle_freq-'+freq+'_mode-'+mode+'.csv'

    data = []
    wnaList = []
    thetaEmaxList = []
    thetaBmaxList = []

    # csvファイルを読み込む
    with open(csvFileName, 'r') as f:
        reader = csv.reader(f)
        # headrをスキップ
        header = next(reader)
        azimathAngleList = header[1:]
        azimathAngleList = [float(angle) for angle in azimathAngleList]
        # 各行を読み込む
        for row in reader:
            wnaList.append(float(row[0]))
            row = row[1:]
            thetaEmaxRow = []
            thetaBmaxRow = []
            for cell in row:
                thetaEmax, thetaBmax = cell.split('v')
                thetaEmaxRow.append(float(thetaEmax))
                thetaBmaxRow.append(float(thetaBmax))
            thetaEmaxList.append(thetaEmaxRow)
            thetaBmaxList.append(thetaBmaxRow)
    # dictionaryに追加
    simResultDict = {}
    simResultDict['wna header'] = np.array(wnaList)
    simResultDict['azimathAngle header'] = np.array(azimathAngleList)
    simResultDict['thetaEmax'] = np.array(thetaEmaxList)
    simResultDict['thetaBmax'] = np.array(thetaBmaxList)

    return simResultDict


def wnaEstimationByCh(angleAtPeakPwrDict, ch):
    """
    Args:
        angleAtPeakPwrDict (dict): 以下を格納した辞書: halfSpinごと最初の時刻、各チャンネルの最大値の角度
        ch (int): チャンネル番号
    Returns:
        wnaDictByCh (dict): 以下を格納した辞書: L mode 仮定時のWNA、その配列長に対応する時刻、R mode 仮定時のWNA、その配列長に対応する時刻
    """
    freqList = [3.15, 5.62, 10, 17.8,
                31.6, 56.2, 100, 178,
                316, 562, 1000, 1780,
                3160, 5620, 10000, 17800]

    wnaDictByCh = {}
    timeLmode = []
    timeRmode = []
    LmodeWNA = []
    # LmodeAziAngle = [] 今後実装するかも
    RmodeWNA = []
    # RmodeAziAngle = [] 今後実装するかも

    # 観測値を配列に格納
    EpwrPeakAngle = angleAtPeakPwrDict['angleAtPeakEpwrCh{}'.format(ch)]
    BpwrPeakAngle = angleAtPeakPwrDict['angleAtPeakBpwrCh{}'.format(ch)]
    EAngleError = angleAtPeakPwrDict['EangleError']
    BAngleError = angleAtPeakPwrDict['BangleError']
    BloopAngleError = angleAtPeakPwrDict['BloopangleError']

    # WNA推定
    # 模擬観測値の読み込み
    LmodeSimuResultDict = loadSimulatedAngleAtPeakPwrByCh(str(freqList[ch]), 'l')
    RmodeSimuResultDict = loadSimulatedAngleAtPeakPwrByCh(str(freqList[ch]), 'r')
    WNAHeader = LmodeSimuResultDict['wna header']
    azimuthAngleHeader = LmodeSimuResultDict['azimathAngle header']
    LmodeThetaEmaxMatrix = LmodeSimuResultDict['thetaEmax']
    LmodeThetaBmaxMatrix = LmodeSimuResultDict['thetaBmax']
    RmodeThetaEmaxMatrix = RmodeSimuResultDict['thetaEmax']
    RmodeThetaBmaxMatrix = RmodeSimuResultDict['thetaBmax']

    # 各スピンごとにWNAを推定する
    for i in range(len(EpwrPeakAngle)):
        LmodeWNAbySpin = []
        RmodeWNAbySpin = []

        obsEpeakAngleLower = EpwrPeakAngle[i] - EAngleError[i]
        obsEpeakAngleUpper = EpwrPeakAngle[i] + EAngleError[i]
        if ch < 10:
            obsBpeakAngleLower = BpwrPeakAngle[i] - BAngleError[i]
            obsBpeakAngleUpper = BpwrPeakAngle[i] + BAngleError[i]
        else:
            obsBpeakAngleLower = BpwrPeakAngle[i] - BloopAngleError[i]
            obsBpeakAngleUpper = BpwrPeakAngle[i] + BloopAngleError[i]
        # 模擬観測値のWNA行の値を1つずつ読み込み、観測値の範囲に含まれるかどうかを判定する
        for j in range(len(WNAHeader)):
            for k in range(len(azimuthAngleHeader)):
                # L mode 仮定時のWNAを推定
                if obsEpeakAngleLower <= LmodeThetaEmaxMatrix[j, k] <= obsEpeakAngleUpper and \
                        obsBpeakAngleLower <= LmodeThetaBmaxMatrix[j, k] <= obsBpeakAngleUpper:
                    LmodeWNAbySpin.append(WNAHeader[j])
                # R mode 仮定時のWNAを推定
                if obsEpeakAngleLower <= RmodeThetaEmaxMatrix[j, k] <= obsEpeakAngleUpper and \
                        obsBpeakAngleLower <= RmodeThetaBmaxMatrix[j, k] <= obsBpeakAngleUpper:
                    RmodeWNAbySpin.append(WNAHeader[j])
        LmodeWNA+=LmodeWNAbySpin
        RmodeWNA+=RmodeWNAbySpin
        # *modeWNAbySpinが空の場合は、time*modeにはなにも追加しない
        # *modeWNAbySpinが空でない場合は、対応する時刻を*modeWNAbySpinの長さ分、time*modeに追加する
        if len(LmodeWNAbySpin) != 0:
            timeLmode += [angleAtPeakPwrDict['Epoch'][i]] * len(LmodeWNAbySpin)
        if len(RmodeWNAbySpin) != 0:
            timeRmode += [angleAtPeakPwrDict['Epoch'][i]] * len(RmodeWNAbySpin)

    # dictionaryに追加
    wnaDictByCh['LmodeWNA'] = np.array(LmodeWNA)
    wnaDictByCh['timeLmode'] = np.array(timeLmode)
    wnaDictByCh['RmodeWNA'] = np.array(RmodeWNA)
    wnaDictByCh['timeRmode'] = np.array(timeRmode)

    return wnaDictByCh


def wnaEstimationByChAll(angleAtPeakPwrDict):
    """
    Args:
        angleAtPeakPwrDict (dict): 以下を格納した辞書: halfSpinごと最初の時刻、各チャンネルの最大値の角度
    Returns:
        wnaDictByChAll (dict): 以下を格納した辞書: L mode 仮定時のWNA、その配列長に対応する時刻、R mode 仮定時のWNA、その配列長に対応する時刻
    """
    wnaDictByChAll = {}
    for ch in range(16):
        wnaDictByCh = wnaEstimationByCh(angleAtPeakPwrDict, ch)
        wnaDictByChAll['LmodeWNACh{}'.format(ch)] = wnaDictByCh['LmodeWNA']
        wnaDictByChAll['timeLmodeCh{}'.format(ch)] = wnaDictByCh['timeLmode']
        wnaDictByChAll['RmodeWNACh{}'.format(ch)] = wnaDictByCh['RmodeWNA']
        wnaDictByChAll['timeRmodeCh{}'.format(ch)] = wnaDictByCh['timeRmode']
    return wnaDictByChAll


def saveWNAEstimationByChAll(wnaDictByChAll):
    """
    Args:
        wnaDictByChAll (dict): 以下を格納した辞書: L mode 仮定時のWNA、その配列長に対応する時刻、R mode 仮定時のWNA、その配列長に対応する時刻
    """
    saveDir = '../execute/wnaEstimation/'
    saveName = 'wnaEstimationByChAll.csv'
    os.makedirs(saveDir, exist_ok=True)
    with open(saveDir+saveName, 'w') as f:
        writer = csv.writer(f)
        # dictionary の key を header として書き出す
        writer.writerow(wnaDictByChAll.keys())
        # dictionary の value を書き出す
        writer.writerows(zip(*wnaDictByChAll.values()))
