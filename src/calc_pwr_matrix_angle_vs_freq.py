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
    store_mca_high_time_res_data(date=date,
                                 datatype=mca_datatype,
                                 del_invalid_data=['off', 'bit rate m', 'sms', 'bdr', 'noisy'])
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


def calc_pwr_matrix_angle_vs_freq(dataset: xr.Dataset,
                                  data_name: str,
                                  angle_name: str):
    '''
    Parameters
    ----------
    date : str, optional
        日付, yyyy-mm-dd
    data_name : str, optional
        例: 'akb_mca_Emax_pwr'
    angle_name : str, optional
        例: 'angle_b0_Ey'
    '''
    angle_list = [-180, -157.5, -135, -112.5, -90, -67.5, -45, -22.5, 0,
                  22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180]
    mean_pwr_matrix = np.zeros((len(angle_list)-1, 16))
    for i in range(len(angle_list)-1):
        condition = (dataset[angle_name] >= angle_list[i]) &\
                    (dataset[angle_name] < angle_list[i+1])
        dataset_in_angle_range = dataset.where(condition, drop=True)
        if dataset_in_angle_range[angle_name].size == 0:
            mean_pwr_matrix[i, :] = 0
        else:
            mean_pwr_matrix[i] = dataset_in_angle_range[data_name].mean(dim='Epoch')
    return mean_pwr_matrix


def calc_pwr_matrix_angle_vs_freq_halfspin(dataset: xr.Dataset,
                                           data_name: str,
                                           angle_name: str):
    '''
    Parameters
    ----------
    data_name : str, optional
        例: 'akb_mca_Emax_pwr'
    angle_name : str, optional
        例: 'angle_b0_Ey'
    '''
    angle_list = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180]

    mean_pwr_matrix = np.zeros((len(angle_list)-1, 16))
    std_matrix = np.zeros((len(angle_list)-1, 16))

    for i in range(len(angle_list)-1):
        condition_pos = (dataset[angle_name] >= angle_list[i]) &\
                        (dataset[angle_name] < angle_list[i+1])
        condition_neg = (dataset[angle_name] >= -180+angle_list[i]) &\
                        (dataset[angle_name] < -180+angle_list[i+1])
        condition = condition_pos | condition_neg
        dataset_in_angle_range = dataset.where(condition, drop=True)
        if dataset_in_angle_range[angle_name].size == 0:
            mean_pwr_matrix[i, :] = np.nan
            std_matrix[i, :] = np.nan
        else:
            print(dataset_in_angle_range[angle_name].mean(dim='Epoch').size)
            mean_pwr_matrix[i] = dataset_in_angle_range[data_name].mean(dim='Epoch')
            std_matrix[i] = dataset_in_angle_range[data_name].std(dim='Epoch', skipna=True)

    return mean_pwr_matrix, std_matrix


def make_1ch_Epwr_over0p3max_ds(dataset: xr.Dataset,
                                ch_idx: int):
    ds_1ch = dataset.isel(channel=ch_idx)

    max_Epwr_value = ds_1ch.max(dim='Epoch')['akb_mca_Emax_pwr'].values
    ds_1ch_over_0p3 = ds_1ch.where(ds_1ch['akb_mca_Emax_pwr'] > 0.3*max_Epwr_value, drop=True)

    return ds_1ch_over_0p3


def make_1ch_Bpwr_over0p3max_ds(dataset: xr.Dataset,
                                ch_idx: int):
    ds_1ch = dataset.isel(channel=ch_idx)

    max_Bpwr_value = ds_1ch.max(dim='Epoch')['akb_mca_Bmax_pwr'].values
    ds_1ch_over_0p3 = ds_1ch.where(ds_1ch['akb_mca_Bmax_pwr'] > 0.3*max_Bpwr_value, drop=True)

    return ds_1ch_over_0p3
