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

# 1時間移動平均、1 sigmaを計算する
epwrMovingAveXry = epwrXry.rolling(time=7200, center=True, min_periods=1).mean(skipna=True)
epwrMovingStdXry = epwrXry.rolling(time=7200, center=True, min_periods=1).std(skipna=True)
bpwrMovingAveXry = bpwrXry.rolling(time=7200, center=True, min_periods=1).mean(skipna=True)
bpwrMovingAstXry = bpwrXry.rolling(time=7200, center=True, min_periods=1).std(skipna=True)

# store data
epwrMatrix = epwrXry.values
print(epwrMatrix.shape)