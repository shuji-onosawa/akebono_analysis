import pytplot
from store_high_time_res_spectrum_data import store_mca_high_time_res_data, store_mgf_data
import pyspedas
import numpy as np
import utilities

date = '1990-02-11'
start_time = '18:05:10'
end_time = '18:09:00'
mca_datatype = 'pwr'

# データを取得する
# MGFのデータをtplot変数にする
store_mgf_data(date=date)

# MCAのデータをtplot変数にする
store_mca_high_time_res_data(date=date, datatype=mca_datatype)

# データを切り出す
# start_time, end_timeをepochに変換する
star_time_epoch = pyspedas.time_double(date+' '+start_time)
end_time_epoch = pyspedas.time_double(date+''+end_time)

# MCAのepoch配列とMGFのepoch配列を取得する
mgf_B0_Ey = pytplot.get_data('angle_btwn_B0_Ey')
mgf_B0_sBy = pytplot.get_data('angle_btwn_B0_sBy')
mca_Emax_pwr = pytplot.get_data('akb_mca_Emax_'+mca_datatype)
mca_Bmax_pwr = pytplot.get_data('akb_mca_Bmax_'+mca_datatype)
epoch_mgf_B0_Ey = mgf_B0_Ey.times
epoch_mgf_B0_sBy = mgf_B0_sBy.times
epoch_mca_Emax_pwr = mca_Emax_pwr.times
epoch_mca_Bmax_pwr = mca_Bmax_pwr.times

# MCAのepoch配列とMGFのepoch配列を比較して、start_time_epochとend_time_epochの間のデータを取得する
# MCAのepoch配列の長さとMGFのepoch配列の長さを確認する
# 長さが違う場合は長いほうの配列の後ろを切って短くして、長さが同じになるようにする
if len(epoch_mca_Emax_pwr) != len(epoch_mgf_B0_Ey):
    if len(epoch_mca_Emax_pwr) > len(epoch_mgf_B0_Ey):
        epoch_mca_Emax_pwr = epoch_mca_Emax_pwr[:len(epoch_mgf_B0_Ey)]
    else:
        epoch_mgf_B0_Ey = epoch_mgf_B0_Ey[:len(epoch_mca_Emax_pwr)]
# MCAのepoch配列とMGFのepoch配列の差が-250~250であることを確認する
if not np.all(np.logical_and(epoch_mca_Emax_pwr - epoch_mgf_B0_Ey >= -250,
                             epoch_mca_Emax_pwr - epoch_mgf_B0_Ey <= 250)):
    raise ValueError('epoch_mca_Emax_pwr - epoch_mgf_B0_Ey is not in the range of -250 to 250.')
# MCAのepoch配列からstart_time_epochとend_time_epochの間のデータを取得する
idx_start_time_epoch = utilities.get_idx_of_nearest_value(epoch_mca_Emax_pwr, star_time_epoch)
idx_end_time_epoch = utilities.get_idx_of_nearest_value(epoch_mca_Emax_pwr, end_time_epoch)

# データを切り出す
mca_Emax_pwr = mca_Emax_pwr.y[idx_start_time_epoch:idx_end_time_epoch+1]
mca_Bmax_pwr = mca_Bmax_pwr.y[idx_start_time_epoch:idx_end_time_epoch+1]
mgf_B0_Ey = mgf_B0_Ey.y[idx_start_time_epoch:idx_end_time_epoch+1]
mgf_B0_sBy = mgf_B0_sBy.y[idx_start_time_epoch:idx_end_time_epoch+1]

# mgf_B0_Eyが0-22.5度, 22.5-45度, 45-67.5度, 67.5-90度, 90-112.5度, 112.5-135度, 135-157.5度, 157.5-180度の時のMCAのデータ(16*1の配列)を取得する

# mgf_B0_Eyが0-22.5度の時のMCAのデータ(16*1の配列)を取得して、2次元配列を作成する
test = utilities.get_data_in_angle_range(mgf_B0_Ey, mca_Emax_pwr, [0, 22.5])
print(test)





