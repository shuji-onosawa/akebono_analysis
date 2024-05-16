import numpy as np
import xarray as xr
import os
import pytplot
from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
from utilities import get_next_date
import akebono
from store_mgf_data import store_angle_b0
import sys

def main(date: str):
    '''
    MCAのデータとMGFのデータをプロットする関数
    dateの日のデータをプロットする
    プロットの時間幅はget_plot_trange_list関数内のplotIntervalで指定
    Args:
        date: データをプロットする日付, 'yyyy-mm-dd'形式
    '''
    next_date = get_next_date(date)

    # データを取得、前処理
    wave_mgf_ds = make_wave_mgf_dataset(date=date,
                                        mca_datatype='pwr')
    store_angle_b0(wave_mgf_ds)
    akebono.orb(trange=[date, next_date])
    # store_gyrofreq()
    # store_Lvalue()

    ilat_ds = pytplot.get_data('akb_orb_inv', xarray=True)
    mlt_ds = pytplot.get_data('akb_orb_mlt', xarray=True)
    mlat_ds = pytplot.get_data('akb_orb_mlat', xarray=True)
    orbDataset = xr.merge([ilat_ds, mlt_ds, mlat_ds])

    # MLTとILATの範囲を指定
    mlt_range = [10, 14]  # MLTの開始値と終了値を指定
    ilat_range = [65, 80]  # ILATの開始値と終了値を指定
    mlat_range = [-90, 90]  # MLATの開始値と終了値を指定

    # プロットする時刻の範囲を取得
    plot_trange_list = get_plot_trange_list(orbDataset,
                                            mlt_range, ilat_range, mlat_range)

    # プロット
    # save path の設定
    condition_str = 'mlt_'+str(mlt_range[0])+'_'+str(mlt_range[1])+'_ilat_'+str(ilat_range[0])+'_'+str(ilat_range[1])
    save_dir = '../plots/mca_w_mgf/'+date[:4]+'/'+condition_str+'/'
    os.makedirs(save_dir, exist_ok=True)

    for plot_trange in plot_trange_list:
        print('Plotting:', plot_trange)
        pytplot.tlimit(plot_trange)
        save_path = save_dir+plot_trange[0][:10]+'_'+plot_trange[0][11:13]+plot_trange[0][14:16]
        pytplot.options('akb_mca_Bmax_pwr', 'zrange', [1e-5, 1e4])
        pytplot.tplot(['akb_mca_Emax_pwr', 'angle_b0_Ey',
                       'akb_mca_Bmax_pwr', 'angle_b0_sBy'],
                      var_label=['akb_orb_alt', 'akb_orb_inv', 'akb_orb_mlt'],
                      xsize=14, ysize=14, save_png=save_path, display=False)

def get_plot_trange_list(orbDataset, mltRange=[0, 24], ilatRange=[0, 90], mlatRange=[-90, 90]):
    '''
    時刻データの配列とMLT、ILATの範囲を指定して、
    プロットする時刻の範囲を取得する関数
    args:
        orbDataset: 時刻, ilat, mltのdataset. 1日分のデータを想定
                    orbit dataの時刻は30秒間隔であることを想定
        mltRange: プロットするMLTの範囲 [下限値, 上限値] list
        ilatRange: プロットするILATの範囲 [下限値, 上限値] list
        mlatRange: プロットするMLATの範囲 [下限値, 上限値] list
    return:
        プロットする時刻の範囲のリスト [[開始時刻, 終了時刻], ...] list
        リストが空の場合は、データが存在しないことprintして終了
    '''
    # データフィルタリング
    filteredDataset = orbDataset
    if mltRange != [0, 24]:
        assert 'akb_orb_mlt' in orbDataset.variables
        filteredDataset = filteredDataset.where((orbDataset['akb_orb_mlt'] >= mltRange[0]) &
                                                (orbDataset['akb_orb_mlt'] <= mltRange[1]), drop=True)
    if ilatRange != [0, 90]:
        assert 'akb_orb_inv' in orbDataset.variables
        filteredDataset = filteredDataset.where((orbDataset['akb_orb_inv'] >= ilatRange[0]) &
                                                (orbDataset['akb_orb_inv'] <= ilatRange[1]), drop=True)
    if mlatRange != [-90, 90]:
        assert 'akb_orb_mlat' in orbDataset.variables
        filteredDataset = filteredDataset.where((orbDataset['akb_orb_mlat'] >= mlatRange[0]) &
                                                (orbDataset['akb_orb_mlat'] <= mlatRange[1]), drop=True)

    # filteredDatasetの時刻データをnumpy配列として取得
    timeAry = filteredDataset['time'].values
    # timeAryで次の要素との時間差が30秒以上の要素のインデックスを取得. 軌道データは30秒間隔であることを想定
    breakIdxs = np.where(np.diff(timeAry) > np.timedelta64(30, 's'))[0]

    # breakIdxsが空の場合は、プログラムを終了
    if len(breakIdxs) == 0:
        print("No data in the specified range")
        sys.exit()

    # 時間差が30秒以内のブロックの開始時刻と終了時刻のリストを作成
    timeRangeList = []
    if breakIdxs[0] != 0:
        timeRangeList.append([timeAry[0], timeAry[breakIdxs[0]]])
    else:
        for i in range(len(breakIdxs)-1):
            timeRangeList.append([timeAry[breakIdxs[i]+1], timeAry[breakIdxs[i+1]]])
    timeRangeList.append([timeAry[breakIdxs[-1]+1], timeAry[-1]])

    # 各ブロックの開始時刻から4分後の時刻、さらに4分後の時刻...と計算していき、
    # 各ブロックの終了時刻を超えるまでの時刻の範囲を取得
    plotTrangeList = []
    plotInterval = np.timedelta64(30, 'm')
    for timeRange in timeRangeList:
        startTime = timeRange[0]
        endTime = timeRange[1]
        while True:
            nextTime = startTime + plotInterval
            if nextTime > endTime:
                plotTrangeList.append([startTime, endTime])
                break
            plotTrangeList.append([startTime, nextTime])
            startTime = nextTime

    # plot_time_range_listの中にはnumpy.datetime64型のデータが入っているので、
    # 'YYYY-MM-DD HH:MM:SS'の形式に変換
    for i in range(len(plotTrangeList)):
        plotTrangeList[i][0] = plotTrangeList[i][0].astype('M8[ns]').astype(str)
        plotTrangeList[i][1] = plotTrangeList[i][1].astype('M8[ns]').astype(str)
    return plotTrangeList

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


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        func = sys.argv[1]
        args = sys.argv[2:]

        if func == 'main':
            main(*args)
    else:
        print("Please provide a function name and arguments")
