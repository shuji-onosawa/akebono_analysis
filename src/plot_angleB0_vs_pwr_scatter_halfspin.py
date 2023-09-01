from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
import os
import matplotlib.pyplot as plt
import numpy as np
from utilities import find_zero_cross_idx

# input
date = '1990-2-11'
start_time = date+'T18:05:20'
end_time = date+'T18:08:40'

freq_label = ['3.16 Hz', '5.62 Hz', '10 Hz', '17.8 Hz', '31.6 Hz', '56.2 Hz', '100 Hz',
              '178 Hz', '316 Hz', '562 Hz', '1 kHz', '1.78 kHz']
angle_list = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180]
angle_label_list = [11.25, 33.75, 56.25, 78.75, 101.25, 123.75, 146.25, 168.75]
threshold_percent = 0.3
# output
output_dir = '../plots/Ishigaya_events/'+date+'/'
os.makedirs(output_dir, exist_ok=True)

# calc
# load data
wave_mgf_dataset = make_wave_mgf_dataset(date, mca_datatype='pwr')
sub_dataset = wave_mgf_dataset.sel(Epoch=slice(start_time, end_time))

angle_b0_Ey_ary = sub_dataset['angle_b0_Ey'].values
Epwr_ary = sub_dataset['akb_mca_Emax_pwr'].values

angle_b0_sBy_ary = sub_dataset['angle_b0_sBy'].values
angle_b0_Bloop_ary = sub_dataset['angle_b0_Bloop'].values
Bpwr_ary = sub_dataset['akb_mca_Bmax_pwr'].values

# initialize lists
Epwr_list = []
Bpwr_list = []
angle_b0_Ey_list = []
angle_b0_sBy_list = []
angle_b0_Bloop_list = []

mean_Epwr_list = []
mean_Bpwr_list = []
mean_Bloop_list = []
std_Epwr_list = []
std_Bpwr_list = []
std_Bloop_list = []

# find half spin indices ranges for E field
E_pos_to_neg_idx, E_neg_to_pos_idx = find_zero_cross_idx(angle_b0_Ey_ary)
half_spin_idx_range_list_E = []

if E_pos_to_neg_idx[0] > E_neg_to_pos_idx[0]:
    for i in range(len(E_pos_to_neg_idx)-1):
        half_spin_idx_range_list_E.append([E_neg_to_pos_idx[i]+1, E_pos_to_neg_idx[i]+1])
        half_spin_idx_range_list_E.append([E_pos_to_neg_idx[i]+1, E_neg_to_pos_idx[i+1]+1])
else:
    for i in range(len(E_pos_to_neg_idx)):
        half_spin_idx_range_list_E.append([E_pos_to_neg_idx[i]+1, E_neg_to_pos_idx[i]+1])
        half_spin_idx_range_list_E.append([E_neg_to_pos_idx[i]+1, E_pos_to_neg_idx[i+1]+1])

# find half spin indices ranges for M field
B_pos_to_neg_idx, B_neg_to_pos_idx = find_zero_cross_idx(angle_b0_sBy_ary)
half_spin_idx_range_list_B = []

if B_pos_to_neg_idx[0] > B_neg_to_pos_idx[0]:
    for i in range(len(B_pos_to_neg_idx)-1):
        half_spin_idx_range_list_B.append([B_neg_to_pos_idx[i]+1, B_pos_to_neg_idx[i]+1])
        half_spin_idx_range_list_B.append([B_pos_to_neg_idx[i]+1, B_neg_to_pos_idx[i+1]+1])
else:
    for i in range(len(B_pos_to_neg_idx)):
        half_spin_idx_range_list_B.append([B_pos_to_neg_idx[i]+1, B_neg_to_pos_idx[i]+1])
        half_spin_idx_range_list_B.append([B_neg_to_pos_idx[i]+1, B_pos_to_neg_idx[i+1]+1])

# calc Epwr max and min for each channel
Epwr_max_ary = sub_dataset['akb_mca_Emax_pwr'].max(dim='Epoch').values
Epwr_min_ary = sub_dataset['akb_mca_Emax_pwr'].min(dim='Epoch').values

# plot
# E field
# scatter plot
fig = plt.figure(figsize=(16, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.scatter(angle_b0_Ey_list[i], Epwr_list[i],
               label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('Ey [(mV/m)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_Ey_list[i])}')
# set title for the whole figure
fig.suptitle('Ey over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Epwr_vs_angle_scatter.jpeg', dpi=300)

# mean and std
fig = plt.figure(figsize=(16, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.errorbar(angle_label_list, mean_Epwr_list[i], yerr=std_Epwr_list[i],
                label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('Ey [(mV/m)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_Ey_list[i])}')
# set title for the whole figure
fig.suptitle('mean Ey over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Epwr_vs_angle_mean.jpeg', dpi=300)

# M field
# scatter plot
fig = plt.figure(figsize=(16, 10))
for i in range(10):
    ax = fig.add_subplot(4, 3, i+1)
    ax.scatter(angle_b0_sBy_list[i], Bpwr_list[i],
               label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('B search coil [(nT)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    # legend at upper right
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_sBy_list[i])}')
for j in range(2):
    ax = fig.add_subplot(4, 3, j+11)
    ax.scatter(angle_b0_Bloop_list[j+10], Bpwr_list[j+10],
               label=freq_label[j+10])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('B loop [(nT)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{j+10}, samples={len(angle_b0_Bloop_list[j+10])}')
# set title for the whole figure
fig.suptitle('B over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Bpwr_vs_angle_scatter.jpeg', dpi=300)

# mean and std
fig = plt.figure(figsize=(16, 10))
for i in range(10):
    ax = fig.add_subplot(4, 3, i+1)
    ax.errorbar(angle_label_list, mean_Bpwr_list[i], yerr=std_Bpwr_list[i],
                label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('B search coil [(nT)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_sBy_list[i])}')
for j in range(2):
    ax = fig.add_subplot(4, 3, j+11)
    ax.errorbar(angle_label_list, mean_Bloop_list[j+10], yerr=std_Bloop_list[j+10],
                label=freq_label[j+10])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('B loop [(nT)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{j+10}, samples={len(angle_b0_Bloop_list[j+10])}')
# set title for the whole figure
fig.suptitle('mean B over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Bpwr_vs_angle_mean.jpeg', dpi=300)

# plot normalized
# E field
# mean and std
fig = plt.figure(figsize=(16, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.errorbar(angle_label_list, mean_Epwr_list[i]/np.nanmax(mean_Epwr_list[i]), yerr=std_Epwr_list[i]/np.nanmax(mean_Epwr_list[i]),
                label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('Ey/Ey_max')
    # limit y axis to 0-1.1
    ax.set_ylim(0, 1.1)
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_Ey_list[i])}')
# set title for the whole figure
fig.suptitle('Normarized mean Ey over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Epwr_vs_angle_mean_normalized.jpeg', dpi=300)

# M field
# mean and std
fig = plt.figure(figsize=(16, 10))
for i in range(10):
    ax = fig.add_subplot(4, 3, i+1)
    ax.errorbar(angle_label_list, mean_Bpwr_list[i]/np.nanmax(mean_Bpwr_list[i]), yerr=std_Bpwr_list[i]/np.nanmax(mean_Bpwr_list[i]),
                label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('sBy/sBy_max')
    # limit y axis to 0-1.1
    ax.set_ylim(0, 1.1)
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_sBy_list[i])}')
for j in range(2):
    ax = fig.add_subplot(4, 3, j+11)
    ax.errorbar(angle_label_list, mean_Bloop_list[j+10]/np.nanmax(mean_Bloop_list[j+10]), yerr=std_Bloop_list[j+10]/np.nanmax(mean_Bloop_list[j+10]),
                label=freq_label[j+10])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('Bloop/Bloop_max')
    # limit y axis to 0-1.1
    ax.set_ylim(0, 1.1)
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{j+10}, samples={len(angle_b0_Bloop_list[j+10])}')
# set title for the whole figure
fig.suptitle('Normarized mean B over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Bpwr_vs_angle_mean_normalized.jpeg', dpi=300)
