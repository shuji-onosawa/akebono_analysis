from pytplot import get_data
from pyspedas import tinterpol
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import akebono
import os
import datetime

start = time.time()


def get_date_list(start_date, end_date):
    date_list = pd.date_range(start=start_date, end=end_date, freq='D')
    date_list = np.datetime_as_string(date_list, unit='D')
    date_list = date_list.astype(object)
    return date_list


def convert_dB_to_pwr(dB, center_freq):
    DB_0 = 1e-6
    pwr = DB_0**2 * 10**(dB/10) / (0.3*center_freq)
    return pwr


def count_mca_intensity(trange,
                        postgap=['off', 'noisy', 'bdr', 'sms', 'bit rate m', 'pws'],
                        alt_range=[0, 12000],
                        mlt_range=[10, 14],
                        ilat_range=[60, 90]):
    start_date, end_date = trange[0], trange[1]
    date_list = get_date_list(start_date, end_date)

    E_matrix = np.zeros((16, 255))
    B_matrix = np.zeros((16, 255))

    freq_array = np.array([3.16, 5.62, 10.0, 17.8,
                           31.6, 56.2, 100,  178,
                           316,  562,  1000, 1780,
                           3160, 5620, 10000, 17800])
    intensity_array = np.arange(0, 255)  # 0 - 254 dB

    for i in range(date_list.size-1):
        print(date_list[i])
        akebono.vlf_mca([date_list[i], date_list[i+1]], datatype='dB', del_invalid_data=postgap)
        try:
            akebono.orb([date_list[i], date_list[i+1]])
        except Exception as e:
            print('No orbit data')
            print(e)
            continue
        try:
            tinterpol('akb_orb_inv', interp_to='akb_mca_Emax', newname='ILAT')
        except Exception as e:
            print('data lack in orbit data')
            print(e)
            continue
        # tinterpol('akb_orb_MLAT', interp_to='akb_mca_Emax', newname='MLAT')
        tinterpol('akb_orb_MLT', interp_to='akb_mca_Emax', newname='MLT', method='nearest')
        tinterpol('akb_orb_ALT', interp_to='akb_mca_Emax', newname='ALT')

        E_tvar = get_data('akb_mca_Emax')
        E_array = E_tvar.y
        E_array_T = E_array.T
        B_tvar = get_data('akb_mca_Bmax')
        B_array = B_tvar.y
        B_array_T = B_array.T

        ilat = get_data('ILAT')
        mlt = get_data('MLT')
        alt = get_data('ALT')

        E_matrix_per_day = np.empty((16, 255), dtype=int)
        B_matrix_per_day = np.empty((16, 255), dtype=int)

        # count the number of an intensity value
        for ch in range(freq_array.size):
            for intensity in intensity_array:
                E_matrix_per_day[ch][intensity] = \
                    np.count_nonzero((E_array_T[ch] == intensity) &
                                     (ilat.y >= ilat_range[0]) &
                                     (ilat.y <= ilat_range[1]) &
                                     (mlt_range[0] <= mlt.y) &
                                     (mlt.y <= mlt_range[1]) &
                                     (alt_range[0] <= alt.y) &
                                     (alt.y <= alt_range[1]))
                B_matrix_per_day[ch][intensity] = \
                    np.count_nonzero((B_array_T[ch] == intensity) &
                                     (ilat.y >= ilat_range[0]) &
                                     (ilat.y <= ilat_range[1]) &
                                     (mlt_range[0] <= mlt.y) &
                                     (mlt.y <= mlt_range[1]) &
                                     (alt.y >= alt_range[0]) &
                                     (alt.y <= alt_range[1]))

        E_matrix = E_matrix + E_matrix_per_day
        B_matrix = B_matrix + B_matrix_per_day

    E_dict = {'field': 'electric',
              'matrix': E_matrix,
              'trange': trange,
              'alt_range': alt_range,
              'mlt_range': mlt_range,
              'ilat_range': ilat_range}
    M_dict = {'field': 'magnetic',
              'matrix': B_matrix,
              'trange': trange,
              'alt_range': alt_range,
              'mlt_range': mlt_range,
              'ilat_range': ilat_range}

    return E_dict, M_dict


def distribution_plot(channel: list,
                      dict_list: list):
    '''
    channel: 0: 3.16, 1: 5.62, 2: 10.0, 3: 17.8, 4: 31.6, 5: 56.2, 6: 100, 7: 178, 8: 316, 9: 562, 10: 1000,
            11: 1780, 12: 3160, 13: 5620, 14: 10000, 15: 17800 unit Hz
    dict_list: list of dictionary
    '''
    # check the field
    field = dict_list[0]['field']
    if field == 'electric':
        save_dir = '../plots/mca_intensity_distribution/Efield/'
        # if there is no directory, make it
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    elif field == 'magnetic':
        save_dir = '../plots/mca_intensity_distribution/Mfield/'
        # if there is no directory, make it
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    title = field + ' field ' + '\n'
    plot_save_name = save_dir + 'mca_' + field + '_'

    for k in range(len(dict_list)):
        trange = dict_list[k]['trange']
        # trangeはlist型、長さ2。trange[1]の日付を1日前の日付にする
        trange[1] = (datetime.datetime.strptime(trange[1], '%Y-%m-%d') - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        alt_range = dict_list[k]['alt_range']
        mlt_range = dict_list[k]['mlt_range']
        
        title += trange[0]+'_'+trange[1]+'_' +\
            'alt'+str(alt_range[0])+'_'+str(alt_range[1]) +\
            'mlt'+str(mlt_range[0])+'_'+str(mlt_range[1]) + '\n'
        plot_save_name += trange[0]+'_'+trange[1]+'_' +\
            'alt'+str(alt_range[0])+'_'+str(alt_range[1]) +\
            'mlt'+str(mlt_range[0])+'_'+str(mlt_range[1])
        if k != len(dict_list) - 1:
            plot_save_name += '_'

    pwr_ary = np.empty((16, 255), dtype=float)
    intensity_array = np.arange(0, 255)
    freq_array = np.array([3.16, 5.62, 10.0, 17.8,
                           31.6, 56.2, 100,  178,
                           316,  562,  1000, 1780,
                           3160, 5620, 10000, 17800])
    for ch in range(16):
        pwr_ary[ch] = convert_dB_to_pwr(intensity_array, freq_array[ch])

    fig, axs = plt.subplots(nrows=len(channel), ncols=1,
                            figsize=(10, 2+4*len(channel)))
    fig.suptitle(title)
    for i, ch in zip(range(len(channel)), channel):
        for j in range(len(dict_list)):
            axs[i].plot(pwr_ary[ch],
                        dict_list[j]['matrix'][ch]/sum(dict_list[j]['matrix'][ch]),
                        label=dict_list[j]['trange'],
                        marker='.')
        axs[i].set_yscale('log')
        axs[i].set_ylim(bottom=1e-4, top=1e-1)
        axs[i].set_xscale('log')
        if field == 'electric':
            axs[i].set_xlim(left=1e-12, right=1e2)
        axs[i].set_ylabel(str(freq_array[ch])+' Hz \n %')
        axs[i].legend()
        if i == len(channel) - 1:
            if field == 'electric':
                axs[i].set_xlabel('mV/m/Hz^0.5')
            if field == 'magnetic':
                axs[i].set_xlabel('pT/Hz^0.5')
    plot_save_name = save_dir + 'mca_' + field + '_pwr_dist_solarmin_per_alt.png'
    plt.savefig(plot_save_name)
    plt.clf()
    plt.close()

date_range = ['1993-1-1', '1998-1-1']
mlt_range = [11, 13]
ilat_range = [77, 79]

e_dict1, _ = count_mca_intensity(trange=date_range, alt_range=[0, 1000], mlt_range=mlt_range, ilat_range=ilat_range)
e_dict2, _ = count_mca_intensity(trange=date_range, alt_range=[1000, 2000], mlt_range=mlt_range, ilat_range=ilat_range)
e_dict3, _ = count_mca_intensity(trange=date_range, alt_range=[2000, 3000], mlt_range=mlt_range, ilat_range=ilat_range)
e_dict4, _ = count_mca_intensity(trange=date_range, alt_range=[3000, 4000], mlt_range=mlt_range, ilat_range=ilat_range)
e_dict5, _ = count_mca_intensity(trange=date_range, alt_range=[4000, 5000], mlt_range=mlt_range, ilat_range=ilat_range)
e_dict6, _ = count_mca_intensity(trange=date_range, alt_range=[5000, 6000], mlt_range=mlt_range, ilat_range=ilat_range)

elapsed_time = time.time() - start
print("elapsed_time:{:.3f}".format(elapsed_time) + "[sec]")

distribution_plot(channel=[1, 3, 5], dict_list=[e_dict1, e_dict2, e_dict3, e_dict4, e_dict5, e_dict6])
