import pytplot
import numpy as np
from get_antenna_angle import unit_vector, angle_between_vectors
from interpolate_mgf_epoch import interpolate_mgf_epoch
import cdflib
import akebono

date = '19900225'
trange = [date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' 12:20:00',
          date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' 12:30:00']
Ey_antenna_vector = np.array([-np.sin(np.deg2rad(35)),
                              np.cos(np.deg2rad(35)),
                              0])
sBy_antenna_vector = np.array([0.0, -1.0, 0.0])

cdf_name = '../akebono_data/mgf/ak_h0_mgf_'+date+'_v01.cdf'
mgf_xary = cdflib.cdf_to_xarray(cdf_name)

B0_epoch = mgf_xary['Epoch'].data
B0_ary = mgf_xary['B0_spin'].data

angle_btwn_B0_Ey = np.empty(int(B0_ary.shape[0]))
angle_btwn_B0_sBy = np.empty(int(B0_ary.shape[0]))
angle_btwn_B0_antenna_epoch = np.empty(int(B0_ary.shape[0]))

for i in range(int(B0_ary.shape[0])):

    if B0_epoch[i] == 0.0:
        angle_btwn_B0_antenna_epoch[i] = 0.0
        angle_btwn_B0_Ey[i] = np.nan
        angle_btwn_B0_sBy[i] = np.nan
    else:
        # mgfのデータ構造
        # epoch: 長さ172799の1次元配列 (1日/0.5秒=172800)
        # b0_spin: 172799*3*16の3次元配列
        # 0.5sごとに3軸の16個のデータがあり、各軸の平均値を取る
        angle_btwn_B0_antenna_epoch[i] = B0_epoch[i]
        B0_vector = np.array([np.average(B0_ary[i][0]),
                              np.average(B0_ary[i][1]),
                              np.average(B0_ary[i][2])])

        B0_unit_vector = unit_vector(B0_vector)
        angle_btwn_B0_Ey[i] = angle_between_vectors(B0_unit_vector, Ey_antenna_vector)
        angle_btwn_B0_sBy[i] = angle_between_vectors(B0_unit_vector, sBy_antenna_vector)

mgf_epoch_interp = interpolate_mgf_epoch(angle_btwn_B0_antenna_epoch)

pytplot.store_data(name='angle_btwn_B0_Ey',
                   data={'x': cdflib.cdfepoch.to_datetime(mgf_epoch_interp),
                         'y': angle_btwn_B0_Ey})
pytplot.options(name='angle_btwn_B0_Ey',
                opt_dict={'ytitle': 'angle between B0 and E1',
                          'yrange': [-180, 180]})
pytplot.store_data(name='angle_btwn_B0_sBy',
                   data={'x': cdflib.cdfepoch.to_datetime(mgf_epoch_interp),
                         'y': angle_btwn_B0_sBy})
pytplot.options(name='angle_btwn_B0_sBy',
                opt_dict={'ytitle': 'angle between B0 and B1',
                          'yrange': [-180, 180]})

akebono.vlf_mca(trange=['1990-2-25', '1990-2-26'], datatype='pwr')

pytplot.tlimit(trange)
pytplot.tplot(['akb_mca_Emax_pwr', 'angle_btwn_B0_Ey', 'akb_mca_Bmax_pwr', 'angle_btwn_B0_sBy'],
              save_png='../plots/mca_spin_modulation/mca_spec_ave0.5s_wide')
