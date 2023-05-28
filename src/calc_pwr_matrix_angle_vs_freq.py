import pytplot
from store_high_time_res_spectrum_data import store_mca_high_time_res_data, get_mgf_with_angle_xry
import pyspedas
import numpy as np
from utilities import get_idx_of_nearest_value, get_data_in_angle_range
import xarray as xr


def make_wave_mgf_dataset(date: str,
                          mca_datatype: str):
    # Datasetの作成
    # 欠損値をnanに置き換えた、B0とアンテナ間の角度を含むMGFデータのxarrayを取得する
    mgf_with_angle_dataset = get_mgf_with_angle_xry(date=date)
    mgf_epoch = mgf_with_angle_dataset['Epoch'].values

    # MCAのデータをtplot変数にする
    store_mca_high_time_res_data(date=date, datatype=mca_datatype)
    # MCAのデータを取り出す
    mca_Emax_tvar = pytplot.get_data('akb_mca_Emax_'+mca_datatype)
    mca_Bmax_tvar = pytplot.get_data('akb_mca_Bmax_'+mca_datatype)
    mca_epoch = mca_Emax_tvar.times
    mca_Emax_data = mca_Emax_tvar.y
    mca_Bmax_data = mca_Bmax_tvar.y
    
    if len(mca_epoch) == len(mgf_epoch):
        pass
    # MGFのepoch(ndarray)の長さにMCAのepoch(ndarray)の長さを合わせる
    # MCAのepochの長さがMGFのepochの長さより長い場合は、MGFのepochの長さに合わせる
    elif len(mca_epoch) > len(mgf_epoch):
        mca_epoch = mca_epoch[:len(mgf_epoch)]
        mca_Emax_data = mca_Emax_data[:len(mgf_epoch)]
        mca_Bmax_data = mca_Bmax_data[:len(mgf_epoch)]
    # MCAのepochの長さがMGFのepochの長さより短い場合は、MGFのepochの長さに合わせるために末尾にnanを追加する
    elif len(mca_epoch) < len(mgf_epoch):
        print(len(mca_epoch), len(mgf_epoch))
        mca_epoch = np.append(mca_epoch, np.full(len(mgf_epoch)-len(mca_epoch), np.nan))
        mca_Emax_data = np.append(mca_Emax_data, np.full(len(mgf_epoch)-len(mca_epoch), np.nan))
        mca_Bmax_data = np.append(mca_Bmax_data, np.full((len(mgf_epoch)-len(mca_epoch), 3), np.nan))
    # MCAのepoch配列をcoodinateにして、MCAのdatasetを作成する
    coords = {'Epoch': mgf_epoch, 'channel': mca_Emax_tvar.v}
    mca_Emax_da = xr.DataArray(mca_Emax_data, coords=coords, dims=('Epoch', 'channel'))
    mca_Bmax_da = xr.DataArray(mca_Bmax_data, coords=coords, dims=('Epoch', 'channel'))
    # MCAのepoch配列をcoodinateにして、MGFのdatasetを作成する
    mgf_with_angle_dataset['akb_mca_Emax_pwr'] = mca_Emax_da
    mgf_with_angle_dataset['akb_mca_Bmax_pwr'] = mca_Bmax_da
    wave_mgf_dataset = mgf_with_angle_dataset
    return wave_mgf_dataset


def calc_pwr_matrix_angle_vs_freq(date: str = '1990-02-11',
                                  start_time: str = '18:05:10',
                                  end_time: str = '18:09:00',
                                  mca_datatype: str = 'pwr'):
    wave_mgf_dataset = make_wave_mgf_dataset(date=date, mca_datatype=mca_datatype)
    # datasetからstart_time_epochとend_time_epochの間のsubsetを作成する
    start_time_epoch = np.datetime64(date+'T'+start_time)
    end_time_epoch = np.datetime64(date+'T'+end_time)
    sub_wave_mgf_dataset = wave_mgf_dataset.sel(Epoch=slice(start_time_epoch, end_time_epoch))

    return sub_wave_mgf_dataset

    '''    mca_Emax_pwr = mca_Emax_pwr.y[idx_start_time_epoch:idx_end_time_epoch]
    mca_Bmax_pwr = mca_Bmax_pwr.y[idx_start_time_epoch:idx_end_time_epoch]
    mgf_B0_Ey = mgf_B0_Ey.y[idx_start_time_epoch:idx_end_time_epoch]
    mgf_B0_sBy = mgf_B0_sBy.y[idx_start_time_epoch:idx_end_time_epoch]

    # 8個おきにデータを
    new_mca_Emax_pwr = np.zeros((1, 16))
    new_mca_Bmax_pwr = np.zeros((1, 16))
    new_angle_ary_Ey = np.array([])
    new_angle_ary_sBy = np.array([])
    for i in range(8):
        mca_Emax_pwr_same_angle = mca_Emax_pwr[i::8]
        mca_Bmax_pwr_same_angle = mca_Bmax_pwr[i::8]
        mgf_B0_Ey_same_angle = mgf_B0_Ey[i::8]
        mgf_B0_sBy_same_angle = mgf_B0_sBy[i::8]
        # さらに2個ずつのデータを取得する
        mgf_B0_Ey_same_angle = mgf_B0_Ey_same_angle[::2]
        mgf_B0_sBy_same_angle = mgf_B0_sBy_same_angle[::2]
        new_mca_Emax_pwr_same_angle_0 = mca_Emax_pwr_same_angle[::2]
        new_mca_Emax_pwr_same_angle_1 = mca_Emax_pwr_same_angle[1::2]
        new_mca_Bmax_pwr_same_angle_0 = mca_Bmax_pwr_same_angle[::2]
        new_mca_Bmax_pwr_same_angle_1 = mca_Bmax_pwr_same_angle[1::2]
        if len(new_mca_Emax_pwr_same_angle_0) != len(new_mca_Emax_pwr_same_angle_1):
            new_mca_Emax_pwr_same_angle_0 = new_mca_Emax_pwr_same_angle_0[:-1]
            mgf_B0_Ey_same_angle = mgf_B0_Ey_same_angle[:-1]
            mgf_B0_sBy_same_angle = mgf_B0_sBy_same_angle[:-1]
        new_mca_Emax_pwr_same_angle = (new_mca_Emax_pwr_same_angle_0 + new_mca_Emax_pwr_same_angle_1)/2
        new_mca_Bmax_pwr_same_angle = (new_mca_Bmax_pwr_same_angle_0 + new_mca_Bmax_pwr_same_angle_1)/2
        new_mca_Emax_pwr = np.append(new_mca_Emax_pwr, new_mca_Emax_pwr_same_angle, axis=0)
        new_mca_Bmax_pwr = np.append(new_mca_Bmax_pwr, new_mca_Bmax_pwr_same_angle, axis=0)
        new_angle_ary_Ey = np.append(new_angle_ary_Ey, mgf_B0_Ey_same_angle)
        new_angle_ary_sBy = np.append(new_angle_ary_sBy, mgf_B0_sBy_same_angle)
    new_mca_Emax_pwr = new_mca_Emax_pwr[1:]
    new_mca_Bmax_pwr = new_mca_Bmax_pwr[1:]

    # mgf_B0_Eyが0-22.5度, 22.5-45度, 45-67.5度, 67.5-90度, 90-112.5度, 112.5-135度, 135-157.5度, 157.5-180度の時のMCAのデータ(16*1の配列)を取得したものを平均して、角度ごとのMCAのデータ(8*16の配列)を作成する
    e_matrix = [get_data_in_angle_range(mgf_B0_Ey, new_mca_Emax_pwr, [0, 22.5]),
                get_data_in_angle_range(mgf_B0_Ey, new_mca_Emax_pwr, [22.5, 45]),
                get_data_in_angle_range(mgf_B0_Ey, new_mca_Emax_pwr, [45, 67.5]),
                get_data_in_angle_range(mgf_B0_Ey, new_mca_Emax_pwr, [67.5, 90]),
                get_data_in_angle_range(mgf_B0_Ey, new_mca_Emax_pwr, [90, 112.5]),
                get_data_in_angle_range(mgf_B0_Ey, new_mca_Emax_pwr, [112.5, 135]),
                get_data_in_angle_range(mgf_B0_Ey, new_mca_Emax_pwr, [135, 157.5]),
                get_data_in_angle_range(mgf_B0_Ey, new_mca_Emax_pwr, [157.5, 180])]
    m_matrix = [get_data_in_angle_range(mgf_B0_sBy, new_mca_Bmax_pwr, [0, 22.5]),
                get_data_in_angle_range(mgf_B0_sBy, new_mca_Bmax_pwr, [22.5, 45]),
                get_data_in_angle_range(mgf_B0_sBy, new_mca_Bmax_pwr, [45, 67.5]),
                get_data_in_angle_range(mgf_B0_sBy, new_mca_Bmax_pwr, [67.5, 90]),
                get_data_in_angle_range(mgf_B0_sBy, new_mca_Bmax_pwr, [90, 112.5]),
                get_data_in_angle_range(mgf_B0_sBy, new_mca_Bmax_pwr, [112.5, 135]),
                get_data_in_angle_range(mgf_B0_sBy, new_mca_Bmax_pwr, [135, 157.5]),
                get_data_in_angle_range(mgf_B0_sBy, new_mca_Bmax_pwr, [157.5, 180])]

    return e_matrix, m_matrix
    '''