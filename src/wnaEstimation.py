from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
import numpy as np
from utilities import find_zero_cross_idx as findZeroCrossIdx
import csv
import os
from plotPeakAngle import plotPeakAngle, combineImages, plotAngleHist


def main(date, startTime, endTime, EpwrRatioThreshold, BpwrRatioThreshold, fold=True, color='k'):
    """
    Args:
        date (str): 日付, yyyy-mm-dd
        startTime (str): 開始時刻, hh:mm:ss
        endTime (str): 終了時刻, hh:mm:ss
        EpwrRatioThreshold (float): 電力比率しきい値
        BpwrRatioThreshold (float): 磁場電力比率しきい値
        fold (bool): 角度を0~180度に折り返すか否か
        color (str): マーカーの色
    """
    print('Processing date: {}, startTime: {}, endTime: {}'.format(date, startTime, endTime))
    #データを格納する辞書を作成
    angleAtPeakPwrDict = {
        "date": date,
        "startTime": startTime,
        "endTime": endTime}
    for ch in range(16):  # 16ch
        angleAtPeakPwrDict['timeAtPeakEpwrCh{}'.format(ch)] = []
        angleAtPeakPwrDict['angleAtPeakEpwrCh{}'.format(ch)] = []
        angleAtPeakPwrDict['timeAtPeakBpwrCh{}'.format(ch)] = []
        angleAtPeakPwrDict['angleAtPeakBpwrCh{}'.format(ch)] = []

    # データの読み込み
    ds = make_wave_mgf_dataset(date=date, mca_datatype='pwr')
    subDataset = ds.sel(Epoch=slice(date+'T'+startTime, date+'T'+endTime))

    # 1スピンごとにデータを分割
    halfSpinDatasetList = splitDatasetIntoHalfSpins(subDataset)

    # 各チャンネルの最大値の角度、その時の時刻を取得
    angleAtPeakPwrDict = makePeakAnglePowerTimeSeries(angleAtPeakPwrDict, halfSpinDatasetList,
                                                      EpwrRatioThreshold, BpwrRatioThreshold)

    # csvファイルに保存
    saveAngleAtPeakPwr(angleAtPeakPwrDict)

    # プロット
    print('Plotting...')
    plotPeakAngle(date, startTime, endTime,
                  EpwrRatioThreshold, BpwrRatioThreshold, fold, color)


def splitDatasetIntoHalfSpins(dataSet):
    angleB0EyAry = dataSet['angle_b0_Ey'].values

    # Find half spin index range for E field
    posToNegIdx, negToPosIdx = findZeroCrossIdx(angleB0EyAry)
    halfSpinIdxRangeList = []

    if posToNegIdx[0] > negToPosIdx[0]:
        if posToNegIdx[-1] > negToPosIdx[-1]:
            for i in range(len(negToPosIdx) - 1):
                halfSpinIdxRangeList.append([negToPosIdx[i] + 1, posToNegIdx[i] + 1])
                halfSpinIdxRangeList.append([posToNegIdx[i] + 1, negToPosIdx[i + 1] + 1])
            halfSpinIdxRangeList.append([negToPosIdx[-1] + 1, posToNegIdx[-1] + 1])
        elif posToNegIdx[-1] < negToPosIdx[-1]:
            for i in range(len(posToNegIdx)):
                halfSpinIdxRangeList.append([negToPosIdx[i] + 1, posToNegIdx[i] + 1])
                halfSpinIdxRangeList.append([posToNegIdx[i] + 1, negToPosIdx[i + 1] + 1])
    elif posToNegIdx[0] < negToPosIdx[0]:
        if posToNegIdx[-1] > negToPosIdx[-1]:
            for i in range(len(negToPosIdx)):
                halfSpinIdxRangeList.append([posToNegIdx[i] + 1, negToPosIdx[i] + 1])
                halfSpinIdxRangeList.append([negToPosIdx[i] + 1, posToNegIdx[i + 1] + 1])
        elif posToNegIdx[-1] < negToPosIdx[-1]:
            for i in range(len(posToNegIdx) - 1):
                halfSpinIdxRangeList.append([posToNegIdx[i] + 1, negToPosIdx[i] + 1])
                halfSpinIdxRangeList.append([negToPosIdx[i] + 1, posToNegIdx[i + 1] + 1])
            halfSpinIdxRangeList.append([posToNegIdx[-1] + 1, negToPosIdx[-1] + 1])

    # Split dataset into half spin
    halfSpinDatasetList = []
    epoch = dataSet.coords['Epoch'].values
    for i in range(len(halfSpinIdxRangeList)):
        halfSpinDatasetList.append(dataSet.sel(Epoch=slice(epoch[halfSpinIdxRangeList[i][0]],
                                                                  epoch[halfSpinIdxRangeList[i][1]-1])))
    return halfSpinDatasetList


def getAngleAtPeakPwr(timeAry, angleAry, pwrAry):
    """
    pwrが最大値をとる時の角度と時刻を取得する。
    pwrが最大となる角度、時刻が複数ある場合は、すべての角度、時刻を取得する。
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


def makePeakAnglePowerTimeSeries(angleAtPeakPwrDict, halfSpinDatasetList, EpwrRatioThreshold, BpwrRatioThreshold):
    """
    Args:
        halfSpinDatasetList (list): halfSpinごとに分割されたxarray.datasetのリスト
        EpwrRatioThreshold (float): 1スピン内での電場最大強度と最小強度の比の閾値
        BpwrRatioThreshold (float): 1スピン内での磁場最大強度と最小強度の比の閾値
    Returns:
        angleAtPeakPwrDict (dict): halfSpinごと最初の時刻、各チャンネルの最大値の角度の辞書
    """
    # angleAtPeakPwrDictにEpwrRatioThreshold, BpwrRatioThresholdを追加
    angleAtPeakPwrDict['EpwrRatioThreshold'] = EpwrRatioThreshold
    angleAtPeakPwrDict['BpwrRatioThreshold'] = BpwrRatioThreshold
    # チャンネルごとに最大値の角度、時刻を取得
    for ch in range(16):
        angleAtPeakEpwr = []
        timeAtPeakEpwr = []
        angleAtPeakBpwr = []
        timeAtPeakBpwr = []
        
        # Emax
        for i in range(len(halfSpinDatasetList)):
            timeAry = halfSpinDatasetList[i]['Epoch'].values
            angleExAry = halfSpinDatasetList[i]['angle_b0_Ex'].values
            angleEyAry = halfSpinDatasetList[i]['angle_b0_Ey'].values
            pwrAry = halfSpinDatasetList[i]['akb_mca_Emax_pwr'].values[:, ch]
            EaxisAry = halfSpinDatasetList[i]['E_axis'].values
            # １スピン中の電場強度の最大値と最小値の比がEpwrRatioThreshold未満であれば、このhalfspinDatasetList[i]はスキップする
            EmaxInSpin = np.nanmax(pwrAry)
            EminInSpin = np.nanmin(pwrAry)
            if EmaxInSpin / EminInSpin < EpwrRatioThreshold:
                continue
            # EmaxPwrの長さが0の場合は、このhalfSpinDatasetList[i]はスキップする
            if len(pwrAry) == 0:
                continue
            # E_axisすべて同じ値でない場合は、このhalfSpinDatasetList[i]はスキップする
            if len(set(EaxisAry)) != 1: # set()で重複を削除. 重複を削除した配列の長さが１のとき、E_axisはすべて同じ値
                continue
            # E_axisが0, 3を含む場合は、このhalfSpinDatasetList[i]はスキップする
            if 0 in EaxisAry or 3 in EaxisAry:
                continue
            
            # 最大値の角度、時刻を取得
            E_axis_flag = EaxisAry[0]
            if E_axis_flag == 1:
                angleAtPeakEpwrList, timeAtPeakEpwrList = getAngleAtPeakPwr(timeAry, angleExAry, pwrAry)
            elif E_axis_flag == 2:
                angleAtPeakEpwrList, timeAtPeakEpwrList = getAngleAtPeakPwr(timeAry, angleEyAry, pwrAry)

            angleAtPeakEpwr += angleAtPeakEpwrList
            timeAtPeakEpwr += timeAtPeakEpwrList
        # 最大値の角度、時刻を辞書に追加
        angleAtPeakPwrDict['timeAtPeakEpwrCh{}'.format(ch)] = timeAtPeakEpwr
        angleAtPeakPwrDict['angleAtPeakEpwrCh{}'.format(ch)] = angleAtPeakEpwr
        
        # Bmax
        for j in range(len(halfSpinDatasetList)):
            timeAry = halfSpinDatasetList[j]['Epoch'].values
            if ch < 10:
                angleAry = halfSpinDatasetList[j]['angle_b0_sBy'].values
            else:
                angleAry = halfSpinDatasetList[j]['angle_b0_Bloop'].values
            pwrAry = halfSpinDatasetList[j]['akb_mca_Bmax_pwr'].values[:, ch]
            # １スピン中の磁場強度の最大値と最小値の比がBpwrRatioThreshold未満であれば、このhalfspinDatasetList[j]はスキップする
            BmaxInSpin = np.nanmax(pwrAry)
            BminInSpin = np.nanmin(pwrAry)
            if BmaxInSpin / BminInSpin < BpwrRatioThreshold:
                continue
            # BmaxPwrの長さが0の場合は、このhalfSpinDatasetList[j]はスキップする
            if len(pwrAry) == 0:
                continue

            # 最大値の角度、時刻を取得
            angleAtPeakBpwrList, timeAtPeakBpwrList = getAngleAtPeakPwr(timeAry, angleAry, pwrAry)
            
            angleAtPeakBpwr += angleAtPeakBpwrList
            timeAtPeakBpwr += timeAtPeakBpwrList
        # 最大値の角度、時刻を辞書に追加
        angleAtPeakPwrDict['timeAtPeakBpwrCh{}'.format(ch)] = timeAtPeakBpwr
        angleAtPeakPwrDict['angleAtPeakBpwrCh{}'.format(ch)] = angleAtPeakBpwr

    # 時刻の配列の長さを揃えるために、最大長の配列に合わせて、nanを追加する
    # 最大の長さを求める. 'date', 'startTime', 'endTime', 'EpwrRatioThreshold', 'BpwrRatioThreshold'は除く
    maxLen = 0
    for key in angleAtPeakPwrDict.keys():
        if key not in ['date', 'startTime', 'endTime', 'EpwrRatioThreshold', 'BpwrRatioThreshold']:
            if len(angleAtPeakPwrDict[key]) > maxLen:
                maxLen = len(angleAtPeakPwrDict[key])

    # 最大の長さに合わせる
    for key in angleAtPeakPwrDict.keys():
        if key not in ['date', 'startTime', 'endTime', 'EpwrRatioThreshold', 'BpwrRatioThreshold']:
            if len(angleAtPeakPwrDict[key]) < maxLen:
                angleAtPeakPwrDict[key] += [np.nan] * (maxLen - len(angleAtPeakPwrDict[key]))

    return angleAtPeakPwrDict


def saveAngleAtPeakPwr(angleAtPeakPwrDict):
    """
    angleAtPeakPwrDictをcsvファイルに保存する.
    csvファイルの名前は、yyyymmdd_hhmmss-hhmmss_EpwrRatioThreshold-BpwrRatioThreshold.csv
    Args:
        angleAtPeakPwrDict (dict): halfSpinごと最初の時刻、各チャンネルの最大値の角度の辞書
    """
    # ファイル名を作成
    date = angleAtPeakPwrDict['date'].replace('-', '')
    startTime = angleAtPeakPwrDict['startTime'].replace(':', '')
    endTime = angleAtPeakPwrDict['endTime'].replace(':', '')
    EpwrRatioThreshold = angleAtPeakPwrDict['EpwrRatioThreshold']
    BpwrRatioThreshold = angleAtPeakPwrDict['BpwrRatioThreshold']

    saveDir = '../execute/peakAngleObs/'
    saveName = date+'_'+startTime+'-'+endTime+'_'+str(EpwrRatioThreshold)+'-'+str(BpwrRatioThreshold)+'.csv'
    
    # angleAtPeakPwrDictからdate, startTime, endTime, EpwrRatioThreshold, BpwrRatioThresholdを削除
    del angleAtPeakPwrDict['date']
    del angleAtPeakPwrDict['startTime']
    del angleAtPeakPwrDict['endTime']
    del angleAtPeakPwrDict['EpwrRatioThreshold']
    del angleAtPeakPwrDict['BpwrRatioThreshold']

    # csvファイルに保存
    os.makedirs(saveDir, exist_ok=True)
    with open(saveDir+saveName, mode='w') as f:
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


dateList = ['1990-02-11', '1990-02-17', '1990-02-25', '1990-02-25']
startTimeList = ['18:05:00', '03:45:00', '12:22:00', '15:49:00']
endTimeList = ['18:10:00', '03:50:00', '12:27:00', '15:54:00']


for date, startTime, endTime in zip(dateList, startTimeList, endTimeList):
    main(date, startTime, endTime, 5.0, 5.0, fold=True, color='k')

