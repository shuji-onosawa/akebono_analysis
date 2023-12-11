import numpy as np
import xarray as xr
import os
import pytplot
from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
from utilities import get_next_date
import akebono


def get_plot_trange_list(ilat_mlt_ds, mlt_range, ilat_range, mlat_range=[-90, 90]):
    '''
    時刻データの配列とMLT、ILATの範囲を指定して、
    プロットする時刻の範囲を取得する関数
    args:
        ilat_mlt_ds: 時刻, ilat, mltのdataset. 1日分のデータを想定
                    orbit dataの時刻は30秒間隔であることを想定
        mlt_range: プロットするMLTの範囲 [下限値, 上限値] list
        ilat_range: プロットするILATの範囲 [下限値, 上限値] list
    return:
        プロットする時刻の範囲のリスト [[開始時刻, 終了時刻], ...] list
    '''
    # ilat_mlt_dsが'akb_orb_inv'と'akb_orb_MLT'の2つの変数を持っていることを確認
    assert 'akb_orb_inv' in ilat_mlt_ds.variables
    assert 'akb_orb_mlt' in ilat_mlt_ds.variables
    # 条件を指定してデータをフィルタリング
    condition = ((ilat_mlt_ds['akb_orb_inv'] >= ilat_range[0]) &
                 (ilat_mlt_ds['akb_orb_inv'] <= ilat_range[1]) &
                 (ilat_mlt_ds['akb_orb_mlt'] >= mlt_range[0]) &
                 (ilat_mlt_ds['akb_orb_mlt'] <= mlt_range[1]))
    if mlat_range == [-90, 90]:
        pass
    else:
        condition = condition & ((ilat_mlt_ds['akb_orb_mlat'] >= mlat_range[0]) &
                                 (ilat_mlt_ds['akb_orb_mlat'] <= mlat_range[1]))
    filtered_data = ilat_mlt_ds.where(condition, drop=True)
    # filtered_dataの時刻データをnumpy配列として取得
    time_ary = filtered_data['time'].values
    # time_arrayで時間差が30秒以上のインデックスを取得
    break_indices = np.where(np.diff(time_ary) > np.timedelta64(30, 's'))[0] + 1

    # break_indicesが空の場合は、データが存在しないことを示すために空のリストを返す
    if len(break_indices) == 0:
        return []

    # 時間差が30秒以内のブロックの開始時刻と終了時刻のリストを作成
    time_range_list = []
    for i in range(len(break_indices)+1):
        if i == 0:
            start_index = 0
        else:
            start_index = break_indices[i-1]
        if i == len(break_indices):
            end_index = len(time_ary)
        else:
            end_index = break_indices[i]
        time_range_list.append([time_ary[start_index], time_ary[end_index-1]])

    # 各ブロックの開始時刻から4分後の時刻、さらに4分後の時刻...と計算していき、
    # 各ブロックの終了時刻を超えるまでの時刻の範囲を取得
    plot_trange_list = []
    for time_range in time_range_list:
        start_time = time_range[0]
        end_time = time_range[1]
        while True:
            next_time = start_time + np.timedelta64(4, 'm')
            if next_time > end_time:
                break
            plot_trange_list.append([start_time, next_time])
            start_time = next_time

    # plot_time_range_listの中にはnumpy.datetime64型のデータが入っているので、
    # 'YYYY-MM-DD HH:MM:SS'の形式に変換
    for i in range(len(plot_trange_list)):
        plot_trange_list[i][0] = plot_trange_list[i][0].astype('M8[ns]').astype(str)
        plot_trange_list[i][1] = plot_trange_list[i][1].astype('M8[ns]').astype(str)
    return plot_trange_list


def preprocess_mgf_angle(wave_mgf_ds: xr.Dataset):
    '''
    wave_mgf_dsに含まれる角度データを前処理する関数
    '''
    angle_b0_Ey = wave_mgf_ds['angle_b0_Ey']
    angle_b0_sBy = wave_mgf_ds['angle_b0_sBy']
    angle_b0_Bloop = wave_mgf_ds['angle_b0_Bloop']

    angle_b0_Ey = angle_b0_Ey.where(angle_b0_Ey.values > 0, angle_b0_Ey.values+180)
    angle_b0_sBy = angle_b0_sBy.where(angle_b0_sBy.values > 0, angle_b0_sBy.values+180)
    angle_b0_Bloop = angle_b0_Bloop.where(angle_b0_Bloop.values> 0, angle_b0_Bloop.values+180)

    return angle_b0_Ey, angle_b0_sBy, angle_b0_Bloop


def store_angle_b0(wave_mgf_ds: xr.Dataset):
    angleB0Ey, angleB0sBy, angleB0Bloop = preprocess_mgf_angle(wave_mgf_ds)
    pytplot.store_data('angle_b0_Ey',
                       data={'x': angleB0Ey['Epoch'].data,
                             'y': angleB0Ey.data})
    pytplot.store_data('angle_b0_sBy',
                       data={'x': angleB0sBy['Epoch'].data,
                             'y': angleB0sBy.data})
    pytplot.store_data('angle_b0_Bloop',
                       data={'x': angleB0Bloop['Epoch'].data,
                             'y': angleB0Bloop.data})

    pytplot.options('angle_b0_Ey',
                    opt_dict={'yrange': [0, 180], 'color': 'k', 'marker': '.', 'line_style': None})
    pytplot.options('angle_b0_sBy',
                    opt_dict={'yrange': [0, 180], 'marker': '.', 'line_style': None})
    pytplot.options('angle_b0_Bloop',
                    opt_dict={'yrange': [0, 180], 'marker': '.', 'line_style': None})
    pytplot.timebar(t=90,
                    varname=['angle_b0_Ey', 'angle_b0_sBy', 'angle_b0_Bloop'],
                    databar=True)
    pytplot.store_data('angle_b0_B', data=['angle_b0_Bloop', 'angle_b0_sBy'])
    pytplot.options('angle_b0_B', 'color', ['k', 'r']) # red: sBy, black: Bloop
    pytplot.options(['angle_b0_Ey', 'angle_b0_B'], 'panel_size', 0.5)


def store_gyrofreq():
    '''
    akebonoの軌道データに含まれる磁場モデルの磁場の大きさからgyrofrequencyを計算してtplot変数として保存する関数
    '''
    # 定数
    q = 1.60217662e-19  # 電気素量
    me = 9.10938356e-31  # 電子の質量
    mh = 1.6726219e-27  # 水素原子の質量
    mhe = 6.6464764e-27  # ヘリウム原子の質量
    mo = 2.7e-26  # 酸素原子の質量

    # akebonoの軌道データに含まれる磁場モデルの磁場の大きさを取得
    bmdl_scaler = pytplot.get_data('akb_orb_bmdl_scaler')
    bmdl_scaler_ary = bmdl_scaler.y  # 単位はnT
    bmdl_scaler_ary = bmdl_scaler_ary*1e-9  # 単位をTに変換
    # gyrofrequencyを計算
    fco = q*bmdl_scaler_ary/mo/2/np.pi
    fche = q*bmdl_scaler_ary/mhe/2/np.pi
    fch = q*bmdl_scaler_ary/mh/2/np.pi
    fce = q*bmdl_scaler_ary/me/2/np.pi
    # tplot変数として保存
    pytplot.store_data('fco', data={'x': bmdl_scaler.times, 'y': fco})
    pytplot.options('fco',
                    opt_dict={'ylog': 1, 'color': 'k', 'yrange': [1, 2e4]})
    pytplot.store_data('fche', data={'x': bmdl_scaler.times, 'y': fche})
    pytplot.options('fche',
                    opt_dict={'ylog': 1, 'color': 'r', 'yrange': [1, 2e4]})
    pytplot.store_data('fch', data={'x': bmdl_scaler.times, 'y': fch})
    pytplot.options('fch',
                    opt_dict={'ylog': 1, 'color': 'b', 'yrange': [1, 2e4]})
    pytplot.store_data('fce', data={'x': bmdl_scaler.times, 'y': fce})
    pytplot.options('fce',
                    opt_dict={'ylog': 1, 'color': 'g', 'yrange': [1, 2e4]})


def store_Lvalue():
    '''
    akebonoの軌道データに含まれる不変緯度の値からLvalueを計算してtplot変数として保存する関数
    '''
    # akebonoの軌道データに含まれる不変緯度の値を取得
    inv = pytplot.get_data('akb_orb_inv')
    invAry = inv.y
    # Lvalueを計算
    Lvalue = 1 / np.cos(np.deg2rad(invAry))**2
    # tplot変数として保存
    pytplot.store_data('Lvalue', data={'x': inv.times, 'y': Lvalue})
    pytplot.options('Lvalue',
                    opt_dict={'ylable': 'L'})


def plot_mca_w_mgf_1day(date: str):
    '''
    MCAのデータとMGFのデータをプロットする関数
    dateの日のデータをプロットする
    1プロットの時間範囲は4分(general_plot.pyのplot_trange_listの設定に依存)
    '''
    next_date = get_next_date(date)

    # データを取得、前処理
    wave_mgf_ds = make_wave_mgf_dataset(date=date,
                                        mca_datatype='pwr')
    store_angle_b0(wave_mgf_ds)
    akebono.orb(trange=[date, next_date])
    store_gyrofreq()
    # store_Lvalue()

    ilat_ds = pytplot.get_data('akb_orb_inv', xarray=True)
    mlt_ds = pytplot.get_data('akb_orb_mlt', xarray=True)
    mlat_ds = pytplot.get_data('akb_orb_mlat', xarray=True)
    ilat_mlt_ds = xr.merge([ilat_ds, mlt_ds, mlat_ds])

    # MLTとILATの範囲を指定
    mlt_range = [18, 22]  # MLTの開始値と終了値を指定
    ilat_range = [65, 80]  # ILATの開始値と終了値を指定
    mlat_range = [-90, 90]  # MLATの開始値と終了値を指定

    # プロットする時刻の範囲を取得
    plot_trange_list = get_plot_trange_list(ilat_mlt_ds,
                                            mlt_range, ilat_range, mlat_range)

    # プロット
    # save path の設定
    condition_str = 'mlt_'+str(mlt_range[0])+'_'+str(mlt_range[1])+'_ilat_'+str(ilat_range[0])+'_'+str(ilat_range[1])
    save_dir = '../plots/mca_w_mgf/'+date[:4]+'/'+condition_str+'/'
    os.makedirs(save_dir, exist_ok=True)
    # plot_trange_listの中身が空の場合は、データが存在しないことを表示して終了
    if len(plot_trange_list) == 0:
        print("No data in the specified range")
        return

    for plot_trange in plot_trange_list:
        pytplot.tlimit(plot_trange)
        save_path = save_dir+plot_trange[0][:10]+'_'+plot_trange[0][11:13]+plot_trange[0][14:16]
        pytplot.options('akb_mca_Bmax_pwr', 'zrange', [1e-4, 1e2])
        pytplot.tplot(['akb_mca_Emax_pwr', 'angle_b0_Ey',
                       'akb_mca_Bmax_pwr', 'angle_b0_B',
                       'fce'],
                      var_label=['akb_orb_alt', 'akb_orb_inv', 'akb_orb_mlt'],
                      xsize=14, ysize=14, save_png=save_path, display=False)
