import pytplot
import numpy as np
from get_antenna_angle import unit_vector, angle_between_vectors
from interpolate_mgf_epoch import interpolate_mgf_epoch
import cdflib
import akebono
import datetime


def store_mgf_data(date: str = '1990-2-25'):
    """
    高時間分解能のスペクトルデータをtplot変数にする
    Parameters
    ----------
    date : str, optional
        日付, by default '1990-2-25'
    """
    # dateを'yyyymmdd'に変換する
    date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')

    Ey_antenna_vector = np.array([-np.sin(np.deg2rad(35)),
                                  np.cos(np.deg2rad(35)),
                                  0])
    sBy_antenna_vector = np.array([0.0, -1.0, 0.0])

    cdf_name = '../akebono_data/mgf/ak_h0_mgf_'+date+'_v01.cdf'
    mgf_xary = cdflib.cdf_to_xarray(cdf_name)

    B0_epoch = mgf_xary['Epoch'].data
    B0_ary = mgf_xary['B0_spin'].data
    print(B0_epoch[10])
    print(datetime.datetime.utcfromtimestamp(B0_epoch[10]/1000))
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
                       data={'x': mgf_epoch_interp,
                             'y': angle_btwn_B0_Ey})
    pytplot.options(name='angle_btwn_B0_Ey',
                    opt_dict={'ytitle': 'angle between B0 and E1',
                              'yrange': [0, 180],
                              'line_style': 'dot'})
    pytplot.store_data(name='angle_btwn_B0_sBy',
                       data={'x': mgf_epoch_interp,
                             'y': angle_btwn_B0_sBy})
    pytplot.options(name='angle_btwn_B0_sBy',
                    opt_dict={'ytitle': 'angle between B0 and B1',
                              'yrange': [0, 180],
                              'line_style': 'dot'})
    pytplot.timebar(t=90, varname=['angle_btwn_B0_Ey', 'angle_btwn_B0_sBy'],
                    dash=True, databar=True)


def store_mca_high_time_res_data(date: str = '1990-02-25', datatype: str = 'pwr'):
    """
    高時間分解能のスペクトルデータをtplot変数にする
    Parameters
    ----------
    date : str, optional

    datatype : str, optional
        データタイプ, by default 'pwr'
    """
    # dateを'yyyymmdd'に変換する
    date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')

    mca_cdf_name = '../akebono_data/vlf/mca/h1/ave0.5s/1990/ak_h1_mca_'+date+'_v02.cdf'
    pytplot.cdf_to_tplot(mca_cdf_name, prefix='akb_mca_')
    akebono.mca_postprocessing(datatype=datatype, del_invalid_data=['off', 'sms'])
