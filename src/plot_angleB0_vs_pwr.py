from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
import numpy as np

date = '1990-2-11'
start_time = date+'T18:05:00'
end_time = date+'T18:09:00'

ds = make_wave_mgf_dataset(date=date, mca_datatype='pwr')
sub_dataset = ds.sel(Epoch=slice(start_time, end_time))

angle_b0_Ey_ary = sub_dataset['angle_b0_Ey'].values
Epwr_ary = sub_dataset['akb_mca_Emax_pwr'].values


