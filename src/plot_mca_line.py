import pytplot
from store_high_time_res_spectrum_data import store_mca_high_time_res_data

'''
MCAスペクトルデータを読み込み、それぞれの周波数ごとに強度vs.時間のグラフを作成する
各プロットには、周波数ごとの強度とその1時間平均値、1 sigmaの値を表示する
プロットにはpytplotモジュールを使用する
'''

# Load data
date = '1990-2-11'
store_mca_high_time_res_data(date=date)

epwrXry = pytplot.get_data('akb_mca_Emax_pwr', xarray=True)
bpwrXry = pytplot.get_data('akb_mca_Bmax_pwr', xarray=True)
# 時刻を制限する
startTime = '1990-02-11T16:00:00.000'
endTime = '1990-02-11T20:00:00.000'
print(epwrXry)
epwrXry = epwrXry.sel(time=slice(startTime, endTime))
bpwrXry = bpwrXry.sel(time=slice(startTime, endTime))

# 1時間移動平均、1 sigmaを計算する
epwrMovingAveXry = epwrXry.rolling(time=7200, center=True, min_periods=1).mean(skipna=True)
epwrMovingStdXry = epwrXry.rolling(time=7200, center=True, min_periods=1).std(skipna=True)
bpwrMovingAveXry = bpwrXry.rolling(time=7200, center=True, min_periods=1).mean(skipna=True)
bpwrMovingAstXry = bpwrXry.rolling(time=7200, center=True, min_periods=1).std(skipna=True)

# store data
specBin = epwrXry.coords['spec_bins'].values

timeMovingAve = epwrMovingAveXry.coords['time'].values

epwrMovingAveMatrix = epwrMovingAveXry.values
epwrMovingStdMatrix = epwrMovingStdXry.values
bpwrMovingAveMatrix = bpwrMovingAveXry.values
bpwrMovingStdMatrix = bpwrMovingAstXry.values

for i in range(specBin.size):
    storeNameEpwrMovAve = 'akb_mca_Epwr_1h_mov_ave_ch{}'.format(i+1)
    storeNameEpwrMovStd = 'akb_mca_Epwr_1h_mov_std_ch{}'.format(i+1)
    storeNameBpwrMovAve = 'akb_mca_Bpwr_1h_mov_ave_ch{}'.format(i+1)
    storeNameBpwrMovStd = 'akb_mca_Bpwr_1h_mov_std_ch{}'.format(i+1)

    pytplot.store_data(storeNameEpwrMovAve, data={'x': timeMovingAve, 'y': epwrMovingAveMatrix[:, i].T})
    pytplot.store_data(storeNameEpwrMovStd, data={'x': timeMovingAve, 'y': epwrMovingStdMatrix[:, i].T})
    pytplot.store_data(storeNameBpwrMovAve, data={'x': timeMovingAve, 'y': bpwrMovingAveMatrix[:, i].T})
    pytplot.store_data(storeNameBpwrMovStd, data={'x': timeMovingAve, 'y': bpwrMovingStdMatrix[:, i].T})

    pytplot.options(storeNameEpwrMovAve, 'ytitle', 'Epwr ch{} \n[(mV/m)^2/Hz]'.format(i+1))
    pytplot.options(storeNameEpwrMovStd, 'ytitle', 'Epwr ch{} \n[(mV/m)^2/Hz]'.format(i+1))
    pytplot.options(storeNameBpwrMovAve, 'ytitle', 'Bpwr ch{} \n[(pT)^2/Hz]'.format(i+1))
    pytplot.options(storeNameBpwrMovStd, 'ytitle', 'Bpwr ch{} \n[(pT)^2/Hz]'.format(i+1))

# plot
pytplot.tlimit(['1990-2-11 16:00:00', '1990-2-11 20:00:00'])
pytplot.tplot(['akb_mca_Emax_pwr', 'akb_mca_Epwr_1h_mov_ave_ch1'])
