from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset, make_1ch_Epwr_thresholded_by_max_ds, make_1ch_Bpwr_thresholded_by_max_ds
import os
import matplotlib.pyplot as plt
import numpy as np

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
wave_mgf_dataset = make_wave_mgf_dataset(date, mca_datatype='pwr')
sub_dataset = wave_mgf_dataset.sel(Epoch=slice(start_time, end_time))

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

for ch in range(12):
    Epwr_over0p3_ds = make_1ch_Epwr_thresholded_by_max_ds(sub_dataset, ch, threshold_percent)
    Bpwr_over0p3_ds = make_1ch_Bpwr_thresholded_by_max_ds(sub_dataset, ch, threshold_percent)

    angle_b0_Ey = Epwr_over0p3_ds['angle_b0_Ey'].values
    angle_b0_sBy = Bpwr_over0p3_ds['angle_b0_sBy'].values
    angle_b0_Bloop = Bpwr_over0p3_ds['angle_b0_Bloop'].values
    angle_b0_Ey = np.where(angle_b0_Ey < 0, angle_b0_Ey+180, angle_b0_Ey)
    angle_b0_sBy = np.where(angle_b0_sBy < 0, angle_b0_sBy+180, angle_b0_sBy)
    angle_b0_Bloop = np.where(angle_b0_Bloop < 0,
                              angle_b0_Bloop+180, angle_b0_Bloop)

    Epwr_list.append(Epwr_over0p3_ds['akb_mca_Emax_pwr'].values)
    Bpwr_list.append(Bpwr_over0p3_ds['akb_mca_Bmax_pwr'].values)
    angle_b0_Ey_list.append(angle_b0_Ey)
    angle_b0_sBy_list.append(angle_b0_sBy)
    angle_b0_Bloop_list.append(angle_b0_Bloop)

    # calc mean and std for each freq and angle bin
    mean_Epwr_list_perch = []
    mean_Bpwr_list_perch = []
    mean_Bloop_list_perch = []
    std_Epwr_list_perch = []
    std_Bpwr_list_perch = []
    std_Bloop_list_perch = []

    for angle_idx in range(len(angle_list)-1):
        condition_pos_Ey = (angle_b0_Ey >= angle_list[angle_idx]) &\
                           (angle_b0_Ey < angle_list[angle_idx+1])
        condition_pos_sBy = (angle_b0_sBy >= angle_list[angle_idx]) &\
                            (angle_b0_sBy < angle_list[angle_idx+1])
        condition_pos_Bloop = (angle_b0_Bloop >= angle_list[angle_idx]) &\
                              (angle_b0_Bloop < angle_list[angle_idx+1])

        Epwr_in_angle = Epwr_over0p3_ds['akb_mca_Emax_pwr'].values[condition_pos_Ey]
        Bpwr_in_angle = Bpwr_over0p3_ds['akb_mca_Bmax_pwr'].values[condition_pos_sBy]
        Bloop_in_angle = Bpwr_over0p3_ds['akb_mca_Bmax_pwr'].values[condition_pos_Bloop]

        mean_Epwr_in_angle = np.nanmean(Epwr_in_angle)
        mean_Bpwr_in_agnle = np.nanmean(Bpwr_in_angle)
        mean_Bloop_in_angle = np.nanmean(Bloop_in_angle)
        std_Epwr_in_angle = np.nanstd(Epwr_in_angle)
        std_Bpwr_in_angle = np.nanstd(Bpwr_in_angle)
        std_Bloop_in_angle = np.nanstd(Bloop_in_angle)

        mean_Epwr_list_perch.append(mean_Epwr_in_angle)
        mean_Bpwr_list_perch.append(mean_Bpwr_in_agnle)
        mean_Bloop_list_perch.append(mean_Bloop_in_angle)
        std_Epwr_list_perch.append(std_Epwr_in_angle)
        std_Bpwr_list_perch.append(std_Bpwr_in_angle)
        std_Bloop_list_perch.append(std_Bloop_in_angle)

    mean_Epwr_list.append(mean_Epwr_list_perch)
    mean_Bpwr_list.append(mean_Bpwr_list_perch)
    mean_Bloop_list.append(mean_Bloop_list_perch)
    std_Epwr_list.append(std_Epwr_list_perch)
    std_Bpwr_list.append(std_Bpwr_list_perch)
    std_Bloop_list.append(std_Bloop_list_perch)


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
