import numpy as np
import xarray as xr
import os
import pytplot
from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
from utilities import get_next_date
import akebono


def get_plot_time_range_list(ilat_mlt_ds, target_mlt_range, target_ilat_range):
    '''
    時刻データの配列とMLT、ILATの範囲を指定して、
    プロットする時刻の範囲を取得する関数
    ilat_mlt_ds: 時刻, ilat, mltのdataset. 1日分のデータを想定
    target_mlt_range: プロットするMLTの範囲 [下限値, 上限値] list
    target_ilat_range: プロットするILATの範囲 [下限値, 上限値] list
    return: プロットする時刻の範囲のリスト [開始時刻, 終了時刻] list
    '''
    # 条件を指定してデータをフィルタリング
    filtered_data = ilat_mlt_ds.where((ilat_mlt_ds['akb_orb_inv'] >= target_ilat_range[0]) &
                                      (ilat_mlt_ds['akb_orb_inv'] <= target_ilat_range[1]) &
                                      (ilat_mlt_ds['akb_orb_MLT'] >= target_mlt_range[0]) &
                                      (ilat_mlt_ds['akb_orb_MLT'] <= target_mlt_range[1]),
                                      drop=True)
    # plotのstart_timeとend_timeを取得. start_timeとend_timeの差分は5分
    start_times = filtered_data['time'].values[::5]  # 5分間隔で取得
    end_times = start_times + np.timedelta64(5, 'm')  # 5分後の時刻を取得

    return start_times, end_times
date = '1990-2-1'
next_date = get_next_date(date)

make_wave_mgf_dataset(date=date,
                      mca_datatype='pwr')
akebono.orb(trange=[date, next_date])

ilat_ds = pytplot.get_data('akb_orb_inv', xarray=True)
mlt_ds = pytplot.get_data('akb_orb_MLT', xarray=True)
ds = xr.merge([ilat_ds, mlt_ds])

# MLTとILATの範囲を指定
target_mlt_range = [10, 14]  # MLTの開始値と終了値を指定
target_ilat_range = [70, 80]  # ILATの開始値と終了値を指定

# 条件を指定してデータをフィルタリング
filtered_data = ds.where((ds['akb_orb_inv'] >= target_ilat_range[0]) &
                         (ds['akb_orb_inv'] <= target_ilat_range[1]) &
                         (ds['akb_orb_MLT'] >= target_mlt_range[0]) &
                         (ds['akb_orb_MLT'] <= target_mlt_range[1]),
                         drop=True)


# 時刻データをnumpy配列として取得
time_array = filtered_data['time'].values

# 時刻の差分を計算
time_diff = np.diff(time_array)

# 差分が30秒以上のインデックスを取得
break_indices = np.where(time_diff > np.timedelta64(30, 's'))[0] + 1

# 最初と最後の時刻のインデックスを取得
start_indices = np.insert(break_indices, 0, 0)
end_indices = break_indices - 1

# 最初と最後の時刻を取得
start_times = time_array[start_indices]
end_times = time_array[end_indices]
end_times = np.append(end_times, time_array[-1])

# 結果の表示
print("最初の時刻:", start_times)
print("最後の時刻:", end_times)

save_dir = '../plots/high_res_mca/'
os.makedirs(save_dir, exist_ok=True)

for start_time, end_time in zip(start_times, end_times):
    # start_time, end_timeを'YYYY-MM-DD HH:MM:SS'の形式に変換
    start_time = start_time.astype('M8[s]').astype(str)
    end_time = end_time.astype('M8[s]').astype(str)

    # fig_name
    fig_name = start_time.replace(':', '').replace('-', '').replace(' ', '')
    print(start_time, end_time)
    pytplot.tlimit([start_time, end_time])
    pytplot.tplot(['akb_mca_Emax_pwr', 'akb_mca_Bmax_pwr'],
                  var_label=['akb_orb_inv', 'akb_orb_MLT', 'akb_orb_ALT'],
                  xsize=14, ysize=8,
                  save_jpeg=save_dir + fig_name + '.jpg')
