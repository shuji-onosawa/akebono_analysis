import cdflib
import pytplot
from store_high_time_res_spectrum_data import store_mca_high_time_res_data, store_mgf_data
import datetime

start_time = '1990-02-11 18:05:10'
end_time = '1990-02-11 18:09:00'

# 1. データを取得する
# 1.1. MGFのデータを取得する
store_mgf_data(date = start_time[:8])
# 1.2. MCAのデータを取得する
store_mca_high_time_res_data(date = start_time[:8], datatype = 'pwr')
pytplot.tplot_names()
mgf_tvar_Ey = pytplot.get_data('angle_btwn_B0_Ey')
mca_tvar = pytplot.get_data('akb_mca_Emax_pwr')

# 2. データを切り出す
# 2.1. 時間をepochに変換する
star_time_epoch = pytplot.time_double(start_time)
end_time_epoch = pytplot.time_double(end_time)
# 2.2. MGFのデータを切り出す
