from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
import numpy as np
from utilities import find_zero_cross_idx
from matplotlib import pyplot as plt
import os

# input parameters
date = '1990-2-11'
start_time = date+'T18:05:00'
end_time = date+'T18:09:00'

# constants
freq_label = ['3.16 Hz', '5.62 Hz', '10 Hz', '17.8 Hz', '31.6 Hz', '56.2 Hz', '100 Hz',
              '178 Hz', '316 Hz', '562 Hz', '1 kHz', '1.78 kHz']
save_dir = '../plots/Ishigaya_events/'+date+'/'+'each_spin/'

# load data
ds = make_wave_mgf_dataset(date=date, mca_datatype='pwr')
sub_dataset = ds.sel(Epoch=slice(start_time, end_time))

angle_b0_Ey_ary = sub_dataset['angle_b0_Ey'].values
Epwr_ary = sub_dataset['akb_mca_Emax_pwr'].values
Epoch = sub_dataset.coords['Epoch'].values

# find half spin index range
pos_to_neg_idx, neg_to_pos_idx = find_zero_cross_idx(angle_b0_Ey_ary)
print(pos_to_neg_idx)
print(neg_to_pos_idx)
half_spin_idx_range_list = []
for i in range(len(pos_to_neg_idx)-1):
    half_spin_idx_range_list.append([neg_to_pos_idx[i]+1, pos_to_neg_idx[i]+1])
    half_spin_idx_range_list.append([pos_to_neg_idx[i]+1, neg_to_pos_idx[i+1]+1])

# calc Epwr max and min for each channel
# max and min are used for ylim of plot
Epwr_max_ary = sub_dataset['akb_mca_Emax_pwr'].max(dim='Epoch').values
Epwr_min_ary = sub_dataset['akb_mca_Emax_pwr'].min(dim='Epoch').values

# plot angle_b0_Ey vs. pwr
for j in range(len(half_spin_idx_range_list)-2):
    if angle_b0_Ey_ary[half_spin_idx_range_list[j][0]] < 0:
        angle_b0_Ey_ary[half_spin_idx_range_list[j][0]:half_spin_idx_range_list[j][1]] = \
            angle_b0_Ey_ary[half_spin_idx_range_list[j][0]:half_spin_idx_range_list[j][1]] + 180
    if angle_b0_Ey_ary[half_spin_idx_range_list[j+1][0]] < 0:
        angle_b0_Ey_ary[half_spin_idx_range_list[j+1][0]:half_spin_idx_range_list[j+1][1]] = \
            angle_b0_Ey_ary[half_spin_idx_range_list[j+1][0]:half_spin_idx_range_list[j+1][1]] + 180
    if angle_b0_Ey_ary[half_spin_idx_range_list[j+2][0]] < 0:
        angle_b0_Ey_ary[half_spin_idx_range_list[j+2][0]:half_spin_idx_range_list[j+2][1]] = \
            angle_b0_Ey_ary[half_spin_idx_range_list[j+2][0]:half_spin_idx_range_list[j+2][1]] + 180
        
    # plot angle_b0_Ey vs. pwr for each channel
    for channel_idx in range(12):
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        ax.plot(angle_b0_Ey_ary[half_spin_idx_range_list[j][0]:half_spin_idx_range_list[j][1]],
                Epwr_ary[half_spin_idx_range_list[j][0]:half_spin_idx_range_list[j][1], channel_idx], label='half spin 1')
        ax.plot(angle_b0_Ey_ary[half_spin_idx_range_list[j+1][0]:half_spin_idx_range_list[j+1][1]],
                Epwr_ary[half_spin_idx_range_list[j+1][0]:half_spin_idx_range_list[j+1][1], channel_idx], label='half spin 2')
        ax.plot(angle_b0_Ey_ary[half_spin_idx_range_list[j+2][0]:half_spin_idx_range_list[j+2][1]],
                Epwr_ary[half_spin_idx_range_list[j+2][0]:half_spin_idx_range_list[j+2][1], channel_idx], label='half spin 3')
        ax.set_title('Angle between B0 and Ey vs. Power for '+freq_label[channel_idx]+'\n' +
                     str(Epoch[half_spin_idx_range_list[j][0]])+' to '+str(Epoch[half_spin_idx_range_list[j+2][1]]))
        ax.set_xlabel('Angle between B0 and Ey (deg)')
        ax.set_ylabel('Power [(mV/m)^2/Hz]')
        ax.set_xlim(0, 180)
        ax.set_ylim(Epwr_min_ary[channel_idx], Epwr_max_ary[channel_idx])
        ax.legend()

        # save plot
        os.makedirs(save_dir+'/Efiled/'+freq_label[channel_idx]+'/', exist_ok=True)
        plt.savefig(save_dir+'/Efiled/'+freq_label[channel_idx]+'/spin'+str(j)+str(j+1)+str(j+2) + '.jpeg')