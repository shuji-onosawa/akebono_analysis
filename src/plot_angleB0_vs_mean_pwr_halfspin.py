from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset, calc_pwr_matrix_angle_vs_freq_halfspin
import os
import matplotlib.pyplot as plt
import numpy as np

# input
date = '1990-2-11'
start_time = date+'T18:05:00'
end_time = date+'T18:09:00'

# output
output_dir = '../plots/Isigaya/'+date+'/'
os.makedirs(output_dir, exist_ok=True)

# calc
wave_mgf_dataset = make_wave_mgf_dataset(date, mca_datatype='pwr')
sub_dataset = wave_mgf_dataset.sel(Epoch=slice(start_time, end_time))

mean_Ematrix, std_Ematrix = calc_pwr_matrix_angle_vs_freq_halfspin(sub_dataset, 'akb_mca_Emax_pwr', 'angle_b0_Ey')
mean_sBmatrix, std_sBmatrix = calc_pwr_matrix_angle_vs_freq_halfspin(sub_dataset, 'akb_mca_Bmax_pwr', 'angle_b0_sBy')
mean_lBmatrix, std_lBmatrix = calc_pwr_matrix_angle_vs_freq_halfspin(sub_dataset, 'akb_mca_Bmax_pwr', 'angle_b0_Bloop')

# plot
freq_label = ['3.16 Hz', '5.62 Hz', '10 Hz', '17.8 Hz', '31.6 Hz', '56.2 Hz', '100 Hz',
              '178 Hz', '316 Hz', '562 Hz', '1 kHz', '1.78 kHz']
angle_list = [11.25, 33.75, 56.25, 78.75, 101.25, 123.75, 146.25, 168.75]
fig = plt.figure(figsize=(14, 10))
for i in range(12):
    ax = fig.add_subplot(4, 3, i+1)
    ax.plot(angle_list, mean_Ematrix[:, i]/np.nanmax(mean_Ematrix[:, i]),
            label=freq_label[i], marker='o')
    # errorbar
    ax.errorbar(angle_list, mean_Ematrix[:, i]/np.nanmax(mean_Ematrix[:, i]),
                yerr=std_Ematrix[:, i]/np.nanmax(mean_Ematrix[:, i]), fmt='none', ecolor='k')
    ax.set_xlabel('angle [deg]')
    ax.set_ylabel('Epwr_mean/Epwr_max')
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 1.1)
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.legend(loc='lower right')
plt.tight_layout()
# plt.savefig('../plots/Ishigaya_events/1990-2-11/Epwr_vs_angle.jpeg')
plt.show()
