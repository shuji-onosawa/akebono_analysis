import pytplot
import numpy as np
import cdflib
from datetime import datetime
import xarray as xr
from preprocess_mgf_epoch import interpolate_mgf_epoch, convert_epoch

def calc_angle_b0_antenna(b0_array,
                          antenna_vector: np.ndarray):
    # document: ../doc/kvectorEstimation.md
    # antenna_vectorは大きさ1のベクトルとする
    antenna_vector = antenna_vector/np.linalg.norm(antenna_vector)
    # b0_spinの大きさを1にする
    b0_spin_norm = np.linalg.norm(b0_array, axis=1)
    b0SpinNormalized = b0_array/b0_spin_norm[:, np.newaxis]
    # b0_spinとantenna_vectorの内積を計算する
    b0CdotAntenna = np.dot(b0SpinNormalized, antenna_vector)
    # angleB0Antenna を計算する
    angleB0Antenna = np.arccos(b0CdotAntenna)

    # angleB0Antennaは-pi~piの範囲で求めたいので、正負を決めるためにベクトル計算をする
    # b0SpinNormalizedとアンテナベクトルの外積を計算する
    b0CrossAntenna = np.cross(b0SpinNormalized, antenna_vector)
    # b0CrossAntennaとスピン軸方向の単位ベクトル(0, 0, 1)の内積を計算する
    b0CrossAntennaCdotZ = np.dot(b0CrossAntenna, np.array([0, 0, 1]))
    # b0CrossAntennaCdotZが負ならangleB0Antennaはそのまま、正なら-angleB0Antennaとする
    angleB0AntennaSigned = np.where(b0CrossAntennaCdotZ < 0, angleB0Antenna, -angleB0Antenna) # -pi~pi, rad

    return angleB0AntennaSigned

def get_mgf_with_angle_xry(date: str = '1990-2-25'):
    """
    MGFデータを読み込み、電磁場のアンテナとB0の内積を追加したxarrayを返す関数
    Parameters
    ----------
    date : str, optional
        日付, by default '1990-2-25'
    """
    # dateを'yyyymmdd'に変換する
    date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
    # cdfファイルを読み込む
    cdf_name = '../akebono_data/mgf/'+date[:4]+'/ak_h0_mgf_'+date+'_v01.cdf'
    mgf_xary = cdflib.cdf_to_xarray(cdf_name)

    b0_spin_da = mgf_xary['B0_spin']
    # mean over dim1
    mean_b0_spin_da = b0_spin_da.mean(dim='dim1')
    # replace B0_spin data at epoch=0.0 with (nan, nan, nan)
    mean_b0_spin_da_replaced = mean_b0_spin_da.where(mean_b0_spin_da['Epoch'] != 0.0,
                                                     np.array([np.nan, np.nan, np.nan]))
    # interpolate epoch
    epoch = mean_b0_spin_da_replaced['Epoch'].data
    epoch = interpolate_mgf_epoch(epoch)
    # apply convert_epoch to coordinate "Epoch"
    mean_b0_spin_da_replaced['Epoch'] = convert_epoch(epoch)

    # calculate angle between B0 and antennas
    b0Ary = mean_b0_spin_da_replaced.values
    angleB0EyAry = calc_angle_b0_antenna(b0Ary,
                                        np.array([-np.sin(np.deg2rad(35)),
                                                  np.cos(np.deg2rad(35)),
                                                  0]))
    angleB0EyXry = xr.DataArray(np.rad2deg(angleB0EyAry), dims='Epoch', name='angle_b0_Ey')
    angleB0sByAry = calc_angle_b0_antenna(b0Ary,
                                         np.array([0, -1.0, 0]))
    angleB0sByXry = xr.DataArray(np.rad2deg(angleB0sByAry), dims='Epoch', name='angle_b0_sBy')
    angleB0BloopAry = calc_angle_b0_antenna(b0Ary,
                                           np.array([2**-0.5, -3**-0.5, 6**-0.5]))
    angleB0BloopXry = xr.DataArray(np.rad2deg(angleB0BloopAry), dims='Epoch', name='angle_b0_Bloop')
    # make new dataset from angle_b0_Ey and angle_b0_sBy
    new_mgf_xry = xr.merge([mean_b0_spin_da_replaced, angleB0EyXry, angleB0sByXry, angleB0BloopXry])

    return new_mgf_xry


def preprocess_mgf_angle(angleAry: np.ndarray):
    """
    Args:
        angleAry (np.ndarray): angle between B0 and antenna
    Returns:
        foldedAngleAry (np.ndarray): folded angle between B0 and antenna. 0 <= foldedAngleAry <= 180
    """
    foldedAngleAry = np.where(angleAry > 0, angleAry, angleAry+180)
    return foldedAngleAry


def store_angle_b0(wave_mgf_ds: xr.Dataset):
    angleB0EyDs = wave_mgf_ds['angle_b0_Ey']
    angleB0EyAry = angleB0EyDs.values
    angleB0sByDs = wave_mgf_ds['angle_b0_sBy']
    angleB0sByAry = angleB0sByDs.values
    angleB0BloopDs = wave_mgf_ds['angle_b0_Bloop']
    angleB0BloopAry = angleB0BloopDs.values

    angleB0EyFolded = preprocess_mgf_angle(angleB0EyAry)
    angleB0sByFolded = preprocess_mgf_angle(angleB0sByAry)
    angleB0BloopFolded = preprocess_mgf_angle(angleB0BloopAry)

    pytplot.store_data('angle_b0_Ey',
                       data={'x': angleB0EyDs['Epoch'].data,
                             'y': angleB0EyFolded})
    pytplot.store_data('angle_b0_sBy',
                       data={'x': angleB0sByDs['Epoch'].data,
                             'y': angleB0sByFolded})
    pytplot.store_data('angle_b0_Bloop',
                       data={'x': angleB0BloopDs['Epoch'].data,
                             'y': angleB0BloopFolded})

    yrange = [0, 180]
    ymajor_ticks = [0, 90, 180]
    yminor_tick_interval = 10
    opt_dict = {'yrange': yrange, 'y_major_ticks': ymajor_ticks, 'y_minor_tick_interval': yminor_tick_interval,
                'color': 'k', 'marker': '.', 'line_style': ' '}
    pytplot.options('angle_b0_Ey',
                    opt_dict=opt_dict)
    pytplot.options('angle_b0_sBy',
                    opt_dict=opt_dict)
    pytplot.options('angle_b0_Bloop',
                    opt_dict=opt_dict)
    pytplot.timebar(t=90,
                    varname=['angle_b0_Ey', 'angle_b0_sBy', 'angle_b0_Bloop'],
                    databar=True)
    pytplot.store_data('angle_b0_B', data=['angle_b0_Bloop', 'angle_b0_sBy'])
    pytplot.options('angle_b0_B', 'color', ['k', 'r']) # red: sBy, black: Bloop
    pytplot.options(['angle_b0_Ey', 'angle_b0_B'], 'panel_size', 0.5)
