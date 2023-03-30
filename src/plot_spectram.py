import pytplot
import numpy as np
from get_antenna_angle import unit_vector, angle_between_vectors
import cdflib
from load import mca_h1cdf_dB_to_absolute
import matplotlib.pyplot as plt
import datetime as dt

date = '19900225'
trange = [date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' 12:20:00',
          date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' 12:30:00']
Ey_antenna_vector = np.array([-np.sin(np.deg2rad(35)),
                              np.cos(np.deg2rad(35)),
                              0])
sBy_antenna_vector = np.array([0.0, -1.0, 0.0])

cdf_name = './akebono_data/mgf/ak_h0_mgf_'+date+'_v01.cdf'
mgf_xary = cdflib.cdf_to_xarray(cdf_name)

B0_epoch = mgf_xary['Epoch'].data / 1000
B0_ary = mgf_xary['B0_spin'].data

angle_btwn_B0_Ey = np.empty(int((B0_ary.shape[0]+1)/2-1))
angle_btwn_B0_sBy = np.empty(int((B0_ary.shape[0]+1)/2-1))
angle_btwn_B0_antenna_epoch = np.empty(int((B0_ary.shape[0]+1)/2-1))

for i in range(int((B0_ary.shape[0]+1)/2-1)):
    # 1秒値データを想定しています。
    if B0_epoch[2*i] == 0.0:
        angle_btwn_B0_antenna_epoch[i] = 0.0
        angle_btwn_B0_Ey[i] = np.nan
        angle_btwn_B0_sBy[i] = np.nan
    else:
        # mgfのデータ構造
        # epoch: 長さ172799の1次元配列 (1日/0.5秒=172800)
        # b0_spin: 172799*3*16の3次元配列
        # 1秒値にするために2つの連続する3*16の配列の最後と最初の値をとってきて平均
        angle_btwn_B0_antenna_epoch[i] = B0_epoch[2*i]
        B0_vector = np.array([(B0_ary[2*i][0][15]+B0_ary[2*i+1][0][0])/2,
                              (B0_ary[2*i][1][15]+B0_ary[2*i+1][1][0])/2,
                              (B0_ary[2*i][2][15]+B0_ary[2*i+1][2][0])/2])

        B0_unit_vector = unit_vector(B0_vector)
        angle_btwn_B0_Ey[i] = angle_between_vectors(B0_unit_vector, Ey_antenna_vector)
        angle_btwn_B0_sBy[i] = angle_between_vectors(B0_unit_vector, sBy_antenna_vector)

pytplot.store_data(name='angle_btwn_B0_Ey',
                   data={'x': angle_btwn_B0_antenna_epoch,
                         'y': angle_btwn_B0_Ey})
pytplot.options(name='angle_btwn_B0_Ey',
                opt_dict={'ytitle': 'angle between B0 and E1',
                          'yrange': [-180, 180]})
pytplot.store_data(name='angle_btwn_B0_sBy',
                   data={'x': angle_btwn_B0_antenna_epoch,
                         'y': angle_btwn_B0_sBy})
pytplot.options(name='angle_btwn_B0_sBy',
                opt_dict={'ytitle': 'angle between B0 and B1',
                          'yrange': [-180, 180]})


pytplot.cdf_to_tplot('./akebono_data/vlf/mca/h1/ave8s/ak_h1_mca_'+date+'_v02.cdf')
mca_h1cdf_dB_to_absolute(spec_type='pwr')
Emax_tvar = pytplot.get_data('Emax')
pytplot.tlimit(trange)
pytplot.tplot(['Emax_pwr', 'Bmax_pwr'], save_png='./plots/mca_spin_modulation/mca_spec_ave8s_wide')
