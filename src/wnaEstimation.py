# ../execute/pyEmax_Bmax_angle_freq-*_mode-*.csvから(θEmax, θBmax)(理論値)とその時のWNA, 方位角を読みこむ
# wave_mgf_datasetから1スピンごとの(θEmax, θBmax)(観測値)の範囲を算出
# 観測値の範囲に理論値が含まれるかどうかを判定

from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
import numpy as np
from utilities import find_zero_cross_idx
import csv
import os
from plotPeakAngle import plotPeakAngle, combineImages, plotAngleHist

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
        if pos_to_neg_idx[-1] > neg_to_pos_idx[-1]:
            for i in range(len(neg_to_pos_idx) - 1):
                half_spin_idx_range_list.append([neg_to_pos_idx[i] + 1, pos_to_neg_idx[i] + 1])
                half_spin_idx_range_list.append([pos_to_neg_idx[i] + 1, neg_to_pos_idx[i + 1] + 1])
            half_spin_idx_range_list.append([neg_to_pos_idx[-1] + 1, pos_to_neg_idx[-1] + 1])
        elif pos_to_neg_idx[-1] < neg_to_pos_idx[-1]:
            for i in range(len(pos_to_neg_idx)):
                half_spin_idx_range_list.append([neg_to_pos_idx[i] + 1, pos_to_neg_idx[i] + 1])
                half_spin_idx_range_list.append([pos_to_neg_idx[i] + 1, neg_to_pos_idx[i + 1] + 1])
    elif pos_to_neg_idx[0] < neg_to_pos_idx[0]:
        if pos_to_neg_idx[-1] > neg_to_pos_idx[-1]:
            for i in range(len(neg_to_pos_idx)):
                half_spin_idx_range_list.append([pos_to_neg_idx[i] + 1, neg_to_pos_idx[i] + 1])
                half_spin_idx_range_list.append([neg_to_pos_idx[i] + 1, pos_to_neg_idx[i + 1] + 1])
        elif pos_to_neg_idx[-1] < neg_to_pos_idx[-1]:
            for i in range(len(pos_to_neg_idx) - 1):
                half_spin_idx_range_list.append([pos_to_neg_idx[i] + 1, neg_to_pos_idx[i] + 1])
                half_spin_idx_range_list.append([neg_to_pos_idx[i] + 1, pos_to_neg_idx[i + 1] + 1])
            half_spin_idx_range_list.append([pos_to_neg_idx[-1] + 1, neg_to_pos_idx[-1] + 1])

    # Split dataset into half spin
    half_spin_dataset_list = []
    epoch = sub_dataset.coords['Epoch'].values
    for i in range(len(half_spin_idx_range_list)):
        half_spin_dataset_list.append(sub_dataset.sel(Epoch=slice(epoch[half_spin_idx_range_list[i][0]],
                                                                  epoch[half_spin_idx_range_list[i][1]])))

    return half_spin_dataset_list


def selectSpin(halfSpinDatasetList, thresholdPercent):
    """
    Args:
        halfSpinDatasetList (list): halfSpinごとに分割されたxarray.datasetのリスト
        thresholdPercent (float or int): 閾値(%)
    Returns:
        selectedDatasetList (list): 閾値を満たすxarray.datasetのリスト
    """
    # halfSpinDatasetListに含まれるxarray.datasetをすべて結合したxarray.datasetを作成
    combinedDataset = halfSpinDatasetList[0]
    for i in range(1, len(halfSpinDatasetList)):
        combinedDataset = combinedDataset.combine_first(halfSpinDatasetList[i])
    # 各チャンネルごとに、最大値を算出。最大値のthesholdPercent%を閾値とする
    EmaxPwrAry = combinedDataset['akb_mca_Emax_pwr'].max(dim='Epoch').values
    BmaxPwrAry = combinedDataset['akb_mca_Bmax_pwr'].max(dim='Epoch').values
    thresholdE = EmaxPwrAry * thresholdPercent / 100
    thresholdB = BmaxPwrAry * thresholdPercent / 100

    selectedDatasetDict = {f"Ch{ch}EList": [] for ch in range(16)}
    selectedDatasetDict.update({f"Ch{ch}BList": [] for ch in range(16)})

    for i in range(len(halfSpinDatasetList)):
        for ch in range(16):
            # Emax
            EmaxPwr = halfSpinDatasetList[i]['akb_mca_Emax_pwr'].values[:, ch]
            # EmaxPwrの長さが0の場合は、このhalfSpinDatasetList[i]はスキップする
            if len(EmaxPwr) == 0:
                continue
            if np.nanmax(EmaxPwr) >= thresholdE[ch]:
                selectedDatasetDict[f"Ch{ch}EList"].append(halfSpinDatasetList[i])
            # Bmax
            BmaxPwr = halfSpinDatasetList[i]['akb_mca_Bmax_pwr'].values[:, ch]
            if np.nanmax(BmaxPwr) >= thresholdB[ch]:
                selectedDatasetDict[f"Ch{ch}BList"].append(halfSpinDatasetList[i])

    # thresholdPercentの値を追加
    selectedDatasetDict['thresholdPercent'] = thresholdPercent
    return selectedDatasetDict


def getAngleAtPeakPwr(timeAry, angleAry, pwrAry):
    """
    Args:
        timeAry (1D ndarray): 時刻の配列
        angleAry (1D ndarray): 角度の配列
        pwrAry (1D ndarray): 強度の配列
    Returns:
        angleAtPeakPwrList (List): 最大値の角度
        timeAtPeakPwrList (List): 最大値の時刻
    """
    maxValue = np.nanmax(pwrAry)
    maxIdx = np.where(pwrAry == maxValue)[0]

    # maxIdxが空の場合は、nanを返す
    if len(maxIdx) == 0:
        angleAtPeakPwr = [np.nan]
        timeAtPeakPwr = [np.nan]
        return angleAtPeakPwr, timeAtPeakPwr

    angleAtPeakPwr = angleAry[maxIdx].tolist()
    timeAtPeakPwr = timeAry[maxIdx].tolist()

    return angleAtPeakPwr, timeAtPeakPwr


def calcAngleAtPeakPwr(selectedDatasetDict):
    """
    Args:
        selectedDatasetDict (dict): 閾値を満たすxarray.datasetのリスト

    Returns:
        angleAtPeakPwrDict (dict): halfSpinごと最初の時刻、各チャンネルの最大値の角度の辞書
    """
    angleAtPeakPwrDict = {}

    for ch in range(16):
        angleAtPeakEpwr = []
        timeAtPeakEpwr = []
        angleAtPeakBpwr = []
        timeAtPeakBpwr = []

        for i in range(len(selectedDatasetDict[f"Ch{ch}EList"])):
            # Emax
            timeAry = selectedDatasetDict[f"Ch{ch}EList"][i]['Epoch'].values
            angleAry = selectedDatasetDict[f"Ch{ch}EList"][i]['angle_b0_Ey'].values
            pwrAry = selectedDatasetDict[f"Ch{ch}EList"][i]['akb_mca_Emax_pwr'].values[:, ch]
            angleAtPeakEpwrList, timeAtPeakEpwrList = getAngleAtPeakPwr(timeAry, angleAry, pwrAry)
            angleAtPeakEpwr += angleAtPeakEpwrList
            timeAtPeakEpwr += timeAtPeakEpwrList
        angleAtPeakPwrDict['timeAtPeakEpwrCh{}'.format(ch)] = timeAtPeakEpwr
        angleAtPeakPwrDict['angleAtPeakEpwrCh{}'.format(ch)] = angleAtPeakEpwr

        for j in range(len(selectedDatasetDict[f"Ch{ch}BList"])):
            # Bmax
            timeAry = selectedDatasetDict[f"Ch{ch}BList"][j]['Epoch'].values
            if ch < 10:
                angleAry = selectedDatasetDict[f"Ch{ch}BList"][j]['angle_b0_sBy'].values
            else:
                angleAry = selectedDatasetDict[f"Ch{ch}BList"][j]['angle_b0_Bloop'].values
            pwrAry = selectedDatasetDict[f"Ch{ch}BList"][j]['akb_mca_Bmax_pwr'].values[:, ch]
            angleAtPeakBpwrList, timeAtPeakBpwrList = getAngleAtPeakPwr(timeAry, angleAry, pwrAry)
            angleAtPeakBpwr += angleAtPeakBpwrList
            timeAtPeakBpwr += timeAtPeakBpwrList
        angleAtPeakPwrDict['timeAtPeakBpwrCh{}'.format(ch)] = timeAtPeakBpwr
        angleAtPeakPwrDict['angleAtPeakBpwrCh{}'.format(ch)] = angleAtPeakBpwr

    # 時刻の配列の長さを揃えるために、最大長の配列に合わせて、nanを追加する
    maxLen = 0
    for key in angleAtPeakPwrDict.keys():
        if len(angleAtPeakPwrDict[key]) > maxLen:
            maxLen = len(angleAtPeakPwrDict[key])
    for key in angleAtPeakPwrDict.keys():
        if len(angleAtPeakPwrDict[key]) < maxLen:
            angleAtPeakPwrDict[key] += [np.nan] * (maxLen - len(angleAtPeakPwrDict[key]))

    # thresholdPercentの値を追加
    angleAtPeakPwrDict['thresholdPercent'] = selectedDatasetDict['thresholdPercent'] * np.ones(maxLen)

    return angleAtPeakPwrDict


def saveAngleAtPeakPwr(angleAtPeakPwrDict, date, startTime, endTime):
    """
    Args:
        angleAtPeakPwrDict (dict): halfSpinごと最初の時刻、各チャンネルの最大値の角度の辞書
        date (str): 日付, yyyy-mm-dd
        startTime (str): 開始時刻, hh:mm:ss
        endTime (str): 終了時刻, hh:mm:ss
    """
    saveDir = '../execute/wnaEstimation/'+date+'_'+startTime[0:2]+startTime[3:5]+startTime[6:8]+'-'+endTime[0:2]+endTime[3:5]+endTime[6:8]+'/'
    saveName = 'peakAngleObs.csv'
    os.makedirs(saveDir, exist_ok=True)
    with open(saveDir+saveName, 'w') as f:
        writer = csv.writer(f)
        # dictionary の key を header として書き出す
        writer.writerow(angleAtPeakPwrDict.keys())
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



def main(date, startTime, endTime):
    print('Split dataset into half spins...')
    halfSpinDatasetList = split_dataset_into_half_spins(date, startTime, endTime)
    print('Select spin...')
    selectedSpinDict = selectSpin(halfSpinDatasetList, 0)
    print('Calculate angle at peak power...')
    angleAtPeakPwrDict = calcAngleAtPeakPwr(selectedSpinDict)
    print('Save angle at peak power...')
    saveAngleAtPeakPwr(angleAtPeakPwrDict, date, startTime, endTime)

    print('Plot histogram...')
    plotAngleHist(date, startTime, endTime)

dateList = ['1990-02-11', '1990-02-17', '1990-02-25', '1990-03-02', '1990-03-06']

'''
    print("Plotting angle at peak power...")
    plotPeakAngle(date, startTime, endTime, fold=True)
    plotPeakAngle(date, startTime, endTime, fold=False)
'''
'''
print('Split dataset into half spins...')
halfSpinDatasetList = split_dataset_into_half_spins(date, startTime, endTime)
print('Select spin...')
selectedSpinDict = selectSpin(halfSpinDatasetList, thresholdPercent)
print('Calculate angle at peak power...')
angleAtPeakPwrDict = calcAngleAtPeakPwr(selectedSpinDict)
print('Save angle at peak power...')
saveAngleAtPeakPwr(angleAtPeakPwrDict)
print('Plot histogram...')
plotAngleHist(date, startTime, endTime)


print("Plotting angle at peak power...")
plotPeakAngle(date, startTime, endTime, fold=True, color='r')
plotPeakAngle(date, startTime, endTime, fold=False, color='r')

freqLabel = ['3.16', '5.62', '10', '17.8',
             '31.6', '56.2', '100', '178',
             '316', '562', '1000', '1780',
             '3160', '5620', '10000', '17800']
saveFolder = '../plots/peakAngles/'+ date + '_' \
        + startTime[0:2] + startTime[3:5] + startTime[6:8] + '-' \
        + endTime[0:2] + endTime[3:5] + endTime[6:8] + '/'
for freq in freqLabel:
    combineImages(saveFolder+'angleAtPeakPwr'+freq+'Hz_threshold0.0folded.jpeg',
                  saveFolder+'angleAtPeakPwr'+freq+'Hz_threshold'+str(float(thresholdPercent))+'folded.jpeg',
                  saveFolder+'angleAtPeakPwr'+freq+'Hz_threshold'+str(thresholdPercent)+'_combined.png')
                  '''