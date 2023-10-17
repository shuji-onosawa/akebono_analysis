import pytplot
import numpy as np
'''
MCAスペクトルデータを読み込み、それぞれの周波数ごとに強度vs.時間のグラフを作成する
各プロットには、周波数ごとの強度(Todo:とその1時間平均値、1 sigmaの値を表示する)
プロットにはpytplotモジュールを使用する
'''


def calcMovingAverage(xarray, timeWindow):
    '''
    時間移動平均を計算する
    :param xarray: xarray.DataArray
    :param timeWindow: int
    :return: xarray.DataArray
    '''
    return xarray.rolling(time=timeWindow, center=True, min_periods=1).mean(skipna=True)


def calcMovingStd(xarray, timeWindow):
    '''
    時間移動標準偏差を計算する
    :param xarray: xarray.DataArray
    :param timeWindow: int
    :return: xarray.DataArray
    '''
    return xarray.rolling(time=timeWindow, center=True, min_periods=1).std(skipna=True)


def storeMovAverage(xarray, timeWindow, storeName):
    '''
    時間移動平均を計算し、pytplotに格納する
    :param xarray: xarray.DataArray
    :param timeWindow: int
    :param storeName: str
    :return: None
    '''
    movingAveXry = calcMovingAverage(xarray, timeWindow)
    movingAveMatrix = movingAveXry.values
    timeMovingAve = movingAveXry.coords['time'].values
    for i in range(movingAveMatrix.shape[1]):
        pytplot.store_data(storeName, data={'x': timeMovingAve, 'y': movingAveMatrix[:, i].T})
        pytplot.options(storeName, 'ytitle', 'Moving Average ch{} \n[(mV/m)^2/Hz]'.format(i+1))


def storeMovStd(xarray, timeWindow, storeName):
    '''
    時間移動標準偏差を計算し、pytplotに格納する
    :param xarray: xarray.DataArray
    :param timeWindow: int
    :param storeName: str
    :return: None
    '''
    movingStdXry = calcMovingStd(xarray, timeWindow)
    movingStdMatrix = movingStdXry.values
    timeMovingStd = movingStdXry.coords['time'].values
    for i in range(movingStdMatrix.shape[1]):
        pytplot.store_data(storeName, data={'x': timeMovingStd, 'y': movingStdMatrix[:, i].T})
        pytplot.options(storeName, 'ytitle', 'Moving Std ch{} \n[(mV/m)^2/Hz]'.format(i+1))


def storeEpwrLines(xarray):
    '''
    xarray.DataArrayをpytplotに格納する
    :param xarray: xarray.DataArray
    :param storeName: str
    :return: None
    '''
    pwrMatrix = xarray.values
    timePwr = xarray.coords['time'].values
    specBin = xarray.coords['spec_bins'].values
    # 各周波数の最大値、最小値を取得
    pwrMax = np.nanmax(pwrMatrix, axis=0)
    pwrMin = np.nanmin(pwrMatrix, axis=0)
    print(pwrMax.shape, pwrMin.shape)
    for i in range(pwrMatrix.shape[1]):
        storeName = 'akb_mca_Epwr_ch{}'.format(i+1)
        pytplot.store_data(storeName, data={'x': timePwr, 'y': pwrMatrix[:, i].T})
        pytplot.options(storeName, 'ytitle', '{} \n[(mV/m)^2/Hz]'.format(str(specBin[i])))
        pytplot.options(storeName, 'yrange', [0.9*pwrMin[i], 1.1*pwrMax[i]])


def storeBpwrLines(xarrary):
    '''
    xarray.DataArrayをpytplotに格納する
    :param xarrary: xarray.DataArray
    :param storeName: str
    :return: None
    '''
    pwrMatrix = xarrary.values
    timePwr = xarrary.coords['time'].values
    specBin = xarrary.coords['spec_bins'].values
    # 各周波数の最大値、最小値を取得
    pwrMax = np.nanmax(pwrMatrix, axis=0)
    pwrMin = np.nanmin(pwrMatrix, axis=0)
    for i in range(pwrMatrix.shape[1]):
        storeName = 'akb_mca_Bpwr_ch{}'.format(i+1)
        pytplot.store_data(storeName, data={'x': timePwr, 'y': pwrMatrix[:, i].T})
        pytplot.options(storeName, 'ytitle', '{} \n[(pT)^2/Hz]'.format(str(specBin[i])))
        pytplot.options(storeName, 'yrange', [0.9*pwrMin[i], 1.1*pwrMax[i]])
