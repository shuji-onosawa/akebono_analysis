import pytplot
import numpy as np
import cdflib
import akebono
from datetime import datetime
import xarray as xr
from preprocess_mgf_epoch import interpolate_mgf_epoch, convert_epoch


def calc_angle_b0_antenna(b0_dataarray,
                          component: str,
                          antenna_vector: np.ndarray):
    # antenna_vectorは大きさ1のベクトルとする
    antenna_vector = antenna_vector/np.linalg.norm(antenna_vector)
    # b0xryのB0_spinのデータを配列として取り出す。
    b0_spin = b0_dataarray.values
    # B0_spinの配列の隣同士の要素の外積を計算し、その結果の配列をつくる。配列の最後は1つ前と同じ値とする。
    b0_cross = np.cross(b0_spin[:-1], b0_spin[1:])
    b0_cross = np.append(b0_cross, b0_cross[-1].reshape(1, 3), axis=0)

    # b0_spinとantenna_vectorの外積を計算する。
    b0_cross_antenna = np.cross(b0_spin, antenna_vector)

    # b0_spinとantenna_vectorの内積を計算する。
    dot_b0_antenna = np.einsum('ij,j->i', b0_spin, antenna_vector)

    # dot_b0_Eyのarccosを計算する。
    angle_b0_antenna = np.arccos(dot_b0_antenna/np.linalg.norm(b0_spin, axis=1))

    # b0_cros sとb0_cross_antennaの内積を計算する。np.einsumは、アインシュタインの縮約記法を用いて
    # 複雑な線形代数演算を表現するための強力な関数
    dot_b0_cross_b0_cross_antenna = np.einsum('ij,ij->i', b0_cross, b0_cross_antenna)

    # dot_b0_cross_b0_cross_antennaがマイナスの時は、angle_b0_Eyをマイナスにする。
    angle_b0_antenna[dot_b0_cross_b0_cross_antenna < 0] = -angle_b0_antenna[dot_b0_cross_b0_cross_antenna < 0]

    return xr.DataArray(np.rad2deg(angle_b0_antenna), dims='Epoch', name='angle_b0_'+component)


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
    cdf_name = '../akebono_data/mgf/ak_h0_mgf_'+date+'_v01.cdf'
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
    angle_b0_Ey = calc_angle_b0_antenna(mean_b0_spin_da_replaced, 'Ey',
                                        np.array([-np.sin(np.deg2rad(35)),
                                                  np.cos(np.deg2rad(35)),
                                                  0]))
    angle_b0_sBy = calc_angle_b0_antenna(mean_b0_spin_da_replaced, 'sBy',
                                         np.array([0, -1.0, 0]))
    angle_b0_Bloop = calc_angle_b0_antenna(mean_b0_spin_da_replaced, 'Bloop',
                                           np.array([2**-0.5, -3**-0.5, 6**-0.5]))
    # make new dataset from angle_b0_Ey and angle_b0_sBy
    new_mgf_xry = xr.merge([mean_b0_spin_da_replaced, angle_b0_Ey, angle_b0_sBy, angle_b0_Bloop])

    return new_mgf_xry


def store_mca_high_time_res_data(date: str = '1990-02-25',
                                 datatype: str = 'pwr',
                                 del_invalid_data: list = ['off', 'bit rate m']):
    """
    高時間分解能のMCAスペクトルデータをtplot変数にする
    Parameters
    ----------
    date : str, optional
    datatype : str, optional
        データタイプ, by default 'pwr'
    del_invalid_data : list of string \n
        mca cdf contain data from which the interference by BDR or SMS is *not* yet removed. \n
        You can remove data contaminated by interference by passing a list containing the following words.\n
        'off': mca is off\n
        'noisy': data is noisy\n
        'sms': SMS is on\n
        'bdr': BDR is on\n
        'bit rate m': Bit rate is medium. When the bit rate is medium, the data is not reliable.\n
        'pws': PWS sounder on\n
    """
    # dateを'yyyymmdd'に変換する
    year = date[:4]
    date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')

    mca_cdf_name = '../akebono_data/vlf/mca/h1/ave0.5s/'+year+'/ak_h1_mca_'+date+'_v02.cdf'
    pytplot.cdf_to_tplot(mca_cdf_name, prefix='akb_mca_', get_metadata=True)
    akebono.mca_postprocessing(datatype=datatype, del_invalid_data=del_invalid_data)
