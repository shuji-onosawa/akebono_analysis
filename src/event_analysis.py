# イベントの日付、開始時刻、終了時刻を入力
# ダイナミックスペクトル&アンテナとB0の角度のプロット、角度vs波動強度のプロット、各周波数で波動強度のラインプロットを作成
from plot_high_res_mca import store_angle_b0, store_gyrofreq, get_next_date
from plot_angleB0_vs_pwr_scatter_halfspin import plotAngleB0Vspwr
from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
from store_mca_line import storeEpwrLines, storeBpwrLines
import pytplot
import akebono
import os

# イベントの日付、開始時刻、終了時刻を入力
date = '1990-02-17'  # イベントの日付. yyyy-mm-dd
nextDate = get_next_date(date)
startTime = '03:45:00'  # イベントの開始時刻. hh:mm:ss
endTime = '03:55:00'  # イベントの終了時刻. hh:mm:ss
saveDir = '../plots/enent_analysis/' +\
    date[0:4]+date[5:7]+date[8:] + '_' +\
    startTime[0:2]+startTime[3:5]+startTime[6:] + '-' +\
    endTime[0:2]+endTime[3:5]+endTime[6:]+'/'  # プロットを保存するディレクトリ
os.makedirs(saveDir, exist_ok=True)

# データロード
ds = make_wave_mgf_dataset(date, 'pwr', del_invalid_data=['off', 'bit rate m', 'sms', 'bdr', 'noisy'])
akebono.orb(trange=[date, nextDate])

store_angle_b0(ds)
store_gyrofreq()

Exry = pytplot.get_data('akb_mca_Emax_pwr', xarray=True)
Bxry = pytplot.get_data('akb_mca_Bmax_pwr', xarray=True)
storeEpwrLines(Exry, date + ' ' + startTime, date + ' ' + endTime)
storeBpwrLines(Bxry, date + ' ' + startTime, date + ' ' + endTime)

# プロット
# ダイナミックスペクトル&アンテナとB0の角度のプロット
pytplot.tlimit([date + ' ' + startTime, date + ' ' + endTime])
pytplot.options('akb_mca_Emax_pwr', 'zrange', [1e-7, 1e2])
pytplot.options('akb_mca_Bmax_pwr', 'zrange', [1e-5, 1e6])
pytplot.tplot(['akb_mca_Emax_pwr', 'angle_b0_Ey', 'akb_mca_Bmax_pwr', 'angle_b0_B'],
              var_label=['akb_orb_inv', 'akb_orb_mlt', 'akb_orb_alt'],
              xsize=14, ysize=14, save_jpeg=saveDir+'spec_angleB0', display=False)
# 角度vs波動強度のプロット
plotAngleB0Vspwr(date, startTime, endTime, saveDir)

# 各周波数で波動強度のラインプロットを作成
pytplot.tplot(['akb_mca_Epwr_ch1', 'akb_mca_Epwr_ch2', 'akb_mca_Epwr_ch3', 'akb_mca_Epwr_ch4',
               'akb_mca_Epwr_ch5', 'akb_mca_Epwr_ch6', 'akb_mca_Epwr_ch7', 'akb_mca_Epwr_ch8',
               'akb_mca_Epwr_ch9', 'akb_mca_Epwr_ch10', 'akb_mca_Epwr_ch11', 'akb_mca_Epwr_ch12'],
              xsize=14, ysize=14, save_jpeg=saveDir+'Epwr_lines', display=False)
pytplot.tplot(['akb_mca_Bpwr_ch1', 'akb_mca_Bpwr_ch2', 'akb_mca_Bpwr_ch3', 'akb_mca_Bpwr_ch4',
               'akb_mca_Bpwr_ch5', 'akb_mca_Bpwr_ch6', 'akb_mca_Bpwr_ch7', 'akb_mca_Bpwr_ch8',
               'akb_mca_Bpwr_ch9', 'akb_mca_Bpwr_ch10', 'akb_mca_Bpwr_ch11', 'akb_mca_Bpwr_ch12'],
              xsize=14, ysize=14, save_jpeg=saveDir+'Bpwr_lines', display=False)
