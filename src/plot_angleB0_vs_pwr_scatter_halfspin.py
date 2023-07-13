from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
import os
import matplotlib.pyplot as plt
import numpy as np

# input
date = '1990-2-11'
start_time = date+'T18:05:00'
end_time = date+'T18:09:00'

# output
output_dir = '../plots/Ishigaya_events/'+date+'/'
os.makedirs(output_dir, exist_ok=True)

# calc
wave_mgf_dataset = make_wave_mgf_dataset(date, mca_datatype='pwr')
sub_dataset = wave_mgf_dataset.sel(Epoch=slice(start_time, end_time))

Epwr = sub_dataset['akb_mca_Emax_pwr'].values
Bpwr = sub_dataset['akb_mca_Bmax_pwr'].values
angle_b0_Ey = sub_dataset['angle_b0_Ey'].values
angle_b0_sBy = sub_dataset['angle_b0_sBy'].values
angle_b0_Bloop = sub_dataset['angle_b0_Bloop'].values

angle_b0_Ey = np.where(angle_b0_Ey < 0, angle_b0_Ey+180, angle_b0_Ey)
angle_b0_sBy = np.where(angle_b0_sBy < 0, angle_b0_sBy+180, angle_b0_sBy)
angle_b0_Bloop = np.where(angle_b0_Bloop < 0,
                          angle_b0_Bloop+180, angle_b0_Bloop)

# plot
freq_label = ['3.16 Hz', '5.62 Hz', '10 Hz', '17.8 Hz', '31.6 Hz', '56.2 Hz', '100 Hz',
              '178 Hz', '316 Hz', '562 Hz', '1 kHz', '1.78 kHz']
angle_list = [11.25, 33.75, 56.25, 78.75, 101.25, 123.75, 146.25, 168.75]
# E field
fig = plt.figure(figsize=(14, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.scatter(angle_b0_Ey, Epwr[:, i],
               label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('Ey [(mV/m)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
plt.tight_layout()
plt.savefig(output_dir+'Epwr_vs_angle_scatter_halfspin.jpeg', dpi=300)

# M field
fig = plt.figure(figsize=(14, 10))
for i in range(10):
    ax = fig.add_subplot(4, 3, i+1)
    ax.scatter(angle_b0_sBy, Bpwr[:, i], label=freq_label[i])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('B search coil [(nT)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    # legend at upper right
    ax.legend(loc='lower right')
for j in range(2):
    ax = fig.add_subplot(4, 3, j+11)
    ax.scatter(angle_b0_Bloop, Bpwr[:, j+10], label=freq_label[j+10])
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('B loop [(nT)^2/Hz]')
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
plt.tight_layout()
plt.savefig(output_dir+'Bpwr_vs_angle_scatter_halfspin.jpeg', dpi=300)
