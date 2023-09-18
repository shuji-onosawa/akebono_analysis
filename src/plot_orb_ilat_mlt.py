import pytplot
import akebono
import matplotlib.pyplot as plt
import numpy as np
from utilities import get_next_date


def plot_orb_ilat_mlt(start_time, end_time, save_path=None):
    '''
    start_time: プロットする開始時刻. 'yyyy-mm-dd hh:mm:ss.nnnnnn'
    end_time: プロットする終了時刻. 'yyyy-mm-dd hh:mm:ss.nnnnnn'
    '''
    # データを取得
    date = start_time[:10]
    next_date = get_next_date(date)
    akebono.orb(trange=[date, next_date])

    # データをフィルタリング
    ilat_ds = pytplot.get_data('akb_orb_inv', xarray=True)
    ilat_sel = ilat_ds.sel(time=slice(start_time, end_time))
    mlt_ds = pytplot.get_data('akb_orb_mlt', xarray=True)
    mlt_sel = mlt_ds.sel(time=slice(start_time, end_time))

    # プロット
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection='polar')

    colorlist = []
    for i in range(len(mlt_sel)):
        colorlist.append('k')
    colorlist[0] = 'r'

    # プロット
    ax.scatter(mlt_sel/12*np.pi, 90-ilat_sel, s=10, marker='x', color=colorlist)

    # ラベルの位置とフォーマット設定
    ax.set_rlabel_position(150)

    ax.set_theta_zero_location("S")  # theta=0 at the top
    ax.set_theta_direction(1)  # theta increasing clockwise
    ax.set_title('Akebono orbit \n' + start_time[:19] + '\n' + end_time[:19], fontsize=10)
    # ラベルの値を指定
    ax.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2], ['0 hr', '6 hr', '12 hr', '18 hr'], fontsize=10)
    ax.set_yticks([0, 10, 20], ['90°', '80°', '70°'], fontsize=10)

    ax.set_ylim(0, 30)
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=300)
    plt.show()
