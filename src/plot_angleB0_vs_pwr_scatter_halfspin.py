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
threshold_percent = 0.5
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
std_Epwr_list = []
std_Bpwr_list = []

# find half spin indices ranges for E field
E_pos_to_neg_idx, E_neg_to_pos_idx = find_zero_cross_idx(angle_b0_Ey_ary)
half_spin_idx_range_list_E = []

if E_pos_to_neg_idx[0] > E_neg_to_pos_idx[0]:
    for i in range(len(E_pos_to_neg_idx)-1):
        half_spin_idx_range_list_E.append([E_neg_to_pos_idx[i]+1, E_pos_to_neg_idx[i]+1])
        half_spin_idx_range_list_E.append([E_pos_to_neg_idx[i]+1, E_neg_to_pos_idx[i+1]+1])
    if len(E_pos_to_neg_idx) == len(E_neg_to_pos_idx):
        half_spin_idx_range_list_E.append([E_neg_to_pos_idx[-1]+1, E_pos_to_neg_idx[-1]+1])
else:
    for i in range(len(E_pos_to_neg_idx)-1):
        half_spin_idx_range_list_E.append([E_pos_to_neg_idx[i]+1, E_neg_to_pos_idx[i]+1])
        half_spin_idx_range_list_E.append([E_neg_to_pos_idx[i]+1, E_pos_to_neg_idx[i+1]+1])
    if len(E_pos_to_neg_idx) == len(E_neg_to_pos_idx):
        half_spin_idx_range_list_E.append([E_pos_to_neg_idx[-1]+1, E_neg_to_pos_idx[-1]+1])

# find half spin indices ranges for M field
B_pos_to_neg_idx, B_neg_to_pos_idx = find_zero_cross_idx(angle_b0_sBy_ary)
half_spin_idx_range_list_B = []

if B_pos_to_neg_idx[0] > B_neg_to_pos_idx[0]:
    for i in range(len(B_pos_to_neg_idx)-1):
        half_spin_idx_range_list_B.append([B_neg_to_pos_idx[i]+1, B_pos_to_neg_idx[i]+1])
        half_spin_idx_range_list_B.append([B_pos_to_neg_idx[i]+1, B_neg_to_pos_idx[i+1]+1])
    if len(B_pos_to_neg_idx) == len(B_neg_to_pos_idx):
        half_spin_idx_range_list_B.append([B_neg_to_pos_idx[-1]+1, B_pos_to_neg_idx[-1]+1])
else:
    for i in range(len(B_pos_to_neg_idx)-1):
        half_spin_idx_range_list_B.append([B_pos_to_neg_idx[i]+1, B_neg_to_pos_idx[i]+1])
        half_spin_idx_range_list_B.append([B_neg_to_pos_idx[i]+1, B_pos_to_neg_idx[i+1]+1])
    if len(B_pos_to_neg_idx) == len(B_neg_to_pos_idx):
        half_spin_idx_range_list_B.append([B_pos_to_neg_idx[-1]+1, B_neg_to_pos_idx[-1]+1])

Bl_pos_to_neg_idx, Bl_neg_to_pos_idx = find_zero_cross_idx(angle_b0_Bloop_ary)
half_spin_idx_range_list_Bl = []

if Bl_pos_to_neg_idx[0] > Bl_neg_to_pos_idx[0]:
    for i in range(len(Bl_pos_to_neg_idx)-1):
        half_spin_idx_range_list_Bl.append([Bl_neg_to_pos_idx[i]+1, Bl_pos_to_neg_idx[i]+1])
        half_spin_idx_range_list_Bl.append([Bl_pos_to_neg_idx[i]+1, Bl_neg_to_pos_idx[i+1]+1])
    if len(Bl_pos_to_neg_idx) == len(Bl_neg_to_pos_idx):
        half_spin_idx_range_list_Bl.append([Bl_neg_to_pos_idx[-1]+1, Bl_pos_to_neg_idx[-1]+1])
else:
    for i in range(len(Bl_pos_to_neg_idx)-1):
        half_spin_idx_range_list_Bl.append([Bl_pos_to_neg_idx[i]+1, Bl_neg_to_pos_idx[i]+1])
        half_spin_idx_range_list_Bl.append([Bl_neg_to_pos_idx[i]+1, Bl_pos_to_neg_idx[i+1]+1])
    if len(Bl_pos_to_neg_idx) == len(Bl_neg_to_pos_idx):
        half_spin_idx_range_list_Bl.append([Bl_pos_to_neg_idx[-1]+1, Bl_neg_to_pos_idx[-1]+1])

# calc pwr max and min for each channel
Epwr_max_ary = sub_dataset['akb_mca_Emax_pwr'].max(dim='Epoch').values
Bpwr_max_ary = sub_dataset['akb_mca_Bmax_pwr'].max(dim='Epoch').values

# judge whether to use half spin or not
# criteria: if there are any values over threshold_percent*Epwr_max_ary[ch], use half spin
for ch in range(12):
    # initialize lists
    Epwr_list.append([])
    angle_b0_Ey_list.append([])
    for i in range(len(half_spin_idx_range_list_E)):
        # if there are any values over threshold_percent*Epwr_max_ary[ch], use half spin
        if np.nanmax(Epwr_ary[half_spin_idx_range_list_E[i][0]:half_spin_idx_range_list_E[i][1], ch]) > threshold_percent*Epwr_max_ary[ch]:
            Epwr_list[ch] += Epwr_ary[half_spin_idx_range_list_E[i][0]:half_spin_idx_range_list_E[i][1], ch].tolist()
            halfspin_angle_ary_E = angle_b0_Ey_ary[half_spin_idx_range_list_E[i][0]:half_spin_idx_range_list_E[i][1]]
            # halfspin_angle_ary_Eの値で負の値の場合は180を足す
            halfspin_angle_ary_E[halfspin_angle_ary_E < 0] += 180
            angle_b0_Ey_list[ch] += halfspin_angle_ary_E.tolist()

for ch in range(12):
    # initialize lists
    Bpwr_list.append([])
    angle_b0_sBy_list.append([])
    angle_b0_Bloop_list.append([])
    if ch < 10:
        for i in range(len(half_spin_idx_range_list_B)):
            # if there are any values over threshold_percent*Bpwr_max_ary[ch], use half spin
            if np.nanmax(Bpwr_ary[half_spin_idx_range_list_B[i][0]:half_spin_idx_range_list_B[i][1], ch]) > threshold_percent*Bpwr_max_ary[ch]:
                Bpwr_list[ch] += Bpwr_ary[half_spin_idx_range_list_B[i][0]:half_spin_idx_range_list_B[i][1], ch].tolist()
                halfspin_angle_ary_B = angle_b0_sBy_ary[half_spin_idx_range_list_B[i][0]:half_spin_idx_range_list_B[i][1]]
                # halfspin_angle_ary_Bの値で負の値の場合は180を足す
                halfspin_angle_ary_B[halfspin_angle_ary_B < 0] += 180
                angle_b0_sBy_list[ch] += halfspin_angle_ary_B.tolist()
    if ch >= 10:
        for i in range(len(half_spin_idx_range_list_Bl)):
            # if there are any values over threshold_percent*Bpwr_max_ary[ch], use half spin
            if np.nanmax(Bpwr_ary[half_spin_idx_range_list_Bl[i][0]:half_spin_idx_range_list_Bl[i][1], ch]) > threshold_percent*Bpwr_max_ary[ch]:
                Bpwr_list[ch] += Bpwr_ary[half_spin_idx_range_list_Bl[i][0]:half_spin_idx_range_list_Bl[i][1], ch].tolist()
                halfspin_angle_ary_Bl = angle_b0_Bloop_ary[half_spin_idx_range_list_Bl[i][0]:half_spin_idx_range_list_Bl[i][1]]
                # halfspin_angle_ary_Blの値で負の値の場合は180を足す
                halfspin_angle_ary_Bl[halfspin_angle_ary_Bl < 0] += 180
                angle_b0_Bloop_list[ch] += halfspin_angle_ary_Bl.tolist()

angle_b0_sBy_list[10] = angle_b0_Bloop_list[10]
angle_b0_sBy_list[11] = angle_b0_Bloop_list[11]

angle_b0_B_list = angle_b0_sBy_list

# calc mean and std
for ch in range(12):
    Epwr_each_ch_ary = np.array(Epwr_list[ch])
    Bpwr_each_ch_ary = np.array(Bpwr_list[ch])
    angle_b0_Ey_each_ch_ary = np.array(angle_b0_Ey_list[ch])
    angle_b0_B_each_ch_ary = np.array(angle_b0_B_list[ch])
    # initialize lists
    mean_Epwr_list.append([])
    mean_Bpwr_list.append([])
    std_Epwr_list.append([])
    std_Bpwr_list.append([])
    for angle_idx in range(len(angle_list)-1):
        condition_for_E = (angle_b0_Ey_each_ch_ary >= angle_list[angle_idx]) &\
                          (angle_b0_Ey_each_ch_ary < angle_list[angle_idx+1])
        condition_for_B = (angle_b0_B_each_ch_ary >= angle_list[angle_idx]) &\
                          (angle_b0_B_each_ch_ary < angle_list[angle_idx+1])

        mean_Epwr_list[ch].append(np.nanmean(Epwr_each_ch_ary[condition_for_E]))
        mean_Bpwr_list[ch].append(np.nanmean(Bpwr_each_ch_ary[condition_for_B]))
        std_Epwr_list[ch].append(np.nanstd(Epwr_each_ch_ary[condition_for_E]))
        std_Bpwr_list[ch].append(np.nanstd(Bpwr_each_ch_ary[condition_for_B]))

# plot
# E field
# scatter plot
fig = plt.figure(figsize=(16, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.scatter(angle_b0_Ey_list[i], Epwr_list[i],
               label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('E_wave [(mV/m)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_Ey_list[i])}')
# set title for the whole figure
fig.suptitle('E_wave over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Epwr_vs_angle_scatter.jpeg', dpi=300)

# mean and std line plot
fig = plt.figure(figsize=(16, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.errorbar(angle_label_list, mean_Epwr_list[i], yerr=std_Epwr_list[i],
                label=freq_label[i], marker='o', capthick=1, capsize=5)
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

# mean and std normalized by max
fig = plt.figure(figsize=(16, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.errorbar(angle_label_list, mean_Epwr_list[i]/np.nanmax(mean_Epwr_list[i]), yerr=std_Epwr_list[i]/np.nanmax(mean_Epwr_list[i]),
                label=freq_label[i], marker='o', capthick=1, capsize=5)
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
# scatter plot
fig = plt.figure(figsize=(16, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.scatter(angle_b0_B_list[i], Bpwr_list[i],
               label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('B_wave [(nT)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    # legend at upper right
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_B_list[i])}')
# set title for the whole figure
fig.suptitle('B_wave over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Bpwr_vs_angle_scatter.jpeg', dpi=300)

# mean and std line plot
fig = plt.figure(figsize=(16, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.errorbar(angle_label_list, mean_Bpwr_list[i], yerr=std_Bpwr_list[i],
                label=freq_label[i], marker='o', capthick=1, capsize=5)
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('B_wave [(nT)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_B_list[i])}')
# set title for the whole figure
fig.suptitle('mean B over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Bpwr_vs_angle_mean.jpeg', dpi=300)

# mean and std normalized by max
fig = plt.figure(figsize=(16, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.errorbar(angle_label_list, mean_Bpwr_list[i]/np.nanmax(mean_Bpwr_list[i]), yerr=std_Bpwr_list[i]/np.nanmax(mean_Bpwr_list[i]),
                label=freq_label[i], marker='o', capthick=1, capsize=5)
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('sBy/sBy_max')
    # limit y axis to 0-1.1
    ax.set_ylim(0, 1.1)
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
    # set title for each subplot
    ax.set_title(f'ch{i+1}, samples={len(angle_b0_B_list[i])}')
# set title for the whole figure
fig.suptitle('Normarized mean B over {threshold_percent}% of max vs angle'.format(threshold_percent=threshold_percent))
plt.tight_layout()
plt.savefig(output_dir+'Bpwr_vs_angle_mean_normalized.jpeg', dpi=300)
