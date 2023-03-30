import numpy as np
import pandas as pd
import load
from pytplot import get_data
from pyspedas import tinterpol
import matplotlib.pyplot as plt


def count_sum_saturation(field_tvar, freq_ch_idx, sat_value,
                         input_pos_value, input_pos_range):

    count_array = np.zeros(input_pos_range.size-1)
    for i in range(input_pos_range.size-1):
        sat_dB_idx = np.where(field_tvar.y.T[freq_ch_idx] == sat_value
                              & input_pos_value.y >= input_pos_range[i]
                              & input_pos_value.y <= input_pos_range[i+1])
        count_array[i] = sat_dB_idx[0].size

    return count_array


def count_sum_sat_by_alt(freq_ch_idx, sat_value):

    MIN_ALT, MAX_ALT, DALT = 0, 12000, 1000
    alt_range = np.arange(MIN_ALT, MAX_ALT, DALT)
    Efield_tvar = get_data('Emax')
    tinterpol('akb_ALT', 'Emax')
    alt_tvar = get_data('akb_ALT-itrp')
    return count_sum_saturation(Efield_tvar, freq_ch_idx,
                                sat_value, alt_tvar.y, alt_range)


def count_sum_obs(field_tvar, input_pos_value, input_pos_range):
    count_array = np.zeros(input_pos_range.size-1)
    for i in range(input_pos_range.size-1):
        in_range_idx = np.where(input_pos_value.y >= input_pos_range[i] & input_pos_value.y <= input_pos_range[i+1])


def plot_distribution(x, y, title, save_name):
    fig = plt.figure(figsize=(6, 6))
    fig.subplots_adjust(bottom=0.2)
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.set_xlabel('Altitude [km]')
    for tick in ax.get_xticklabels():
        tick.set_rotation(30)
    ax.set_ylabel('Count')
    ax.set_title(title)

    plt.savefig(save_name)


START_DATE, END_DATE = '1990-03-01', '1990-04-01'
date_list = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
date_list = np.datetime_as_string(date_list, unit='D')
date_list = date_list.astype(object)

FREQ_CH_IDX = 0
FREQ_SAT_VALUE = 96

alt_range = np.arange(0, 12000, 1000)
count_sat_by_alt_array = np.zeros(alt_range.size-1)

for i in range(date_list.size-1):
    print(date_list[i])

    load.mca([date_list[i], date_list[i+1]])
    load.orb([date_list[i], date_list[i+1]])

    count_sat_by_alt_array += count_sum_sat_by_alt(FREQ_CH_IDX, FREQ_SAT_VALUE)

alt_label_array = np.empty(alt_range.size-1).tolist()
for i in range(alt_range.size-1):
    alt_label_array[i] = str(alt_range[i+1]) + '-' + str(alt_range[i])

plot_distribution(alt_label_array, obs_alt_distribution, title='Altitude Coverage',
                  save_name='plots/mca_saturation_alt_distribution/alt_coverage.png')
plot_distribution(alt_label_array, alt_distribution_array(0, 96), title='3.16 Hz  96 dB',
                  save_name='plots/mca_saturation_alt_distribution/alt_distribution_3.16Hz_96dB.png')
