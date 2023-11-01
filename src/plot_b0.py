import cdflib
import numpy as np
from store_high_time_res_spectrum_data import get_mgf_with_angle_xry
import matplotlib.pyplot as plt

# Get the MGF data
new_mgf = get_mgf_with_angle_xry(date='1990-02-11')

start_time = '1990-02-11T18:08:00'
end_time = '1990-02-11T18:08:30'
sub_ds = new_mgf.sel(Epoch=slice(start_time, end_time))

# plot the angle between B0 and Ey antenna and the angle between B0 and sBy antenna
fig = plt.figure(figsize=(10, 10))
ax1 = fig.add_subplot(211)
ax1.plot(sub_ds['Epoch'], sub_ds['angle_b0_Ey'], 'o')
ax1.set_ylabel('angle_b0_Ey')
ax1.set_xlabel('Epoch')
ax1.set_ylim(-180, 180)
ax1.set_title('angle between B0 and Ey antenna')
ax2 = fig.add_subplot(212)
ax2.plot(sub_ds['Epoch'], sub_ds['angle_b0_sBy'], 'o')
ax2.set_ylabel('angle_b0_sBy')
ax2.set_xlabel('Epoch')
ax2.set_ylim(-180, 180)
ax2.set_title('angle between B0 and sBy antenna')
plt.show()

# plot B0_spin
fig = plt.figure(figsize=(10, 10))
ax1 = fig.add_subplot(311)
ax1.plot(sub_ds['Epoch'], sub_ds['B0_spin'][:, 0], 'o')
ax1.set_ylabel('B0_spin_x')
ax1.set_xlabel('Epoch')
ax1.set_title('B0_spin')
ax2 = fig.add_subplot(312)
ax2.plot(sub_ds['Epoch'], sub_ds['B0_spin'][:, 1], 'o')
ax2.set_ylabel('B0_spin_y')
ax2.set_xlabel('Epoch')
ax3 = fig.add_subplot(313)
ax3.plot(sub_ds['Epoch'], sub_ds['B0_spin'][:, 2], 'o')
ax3.set_ylabel('B0_spin_z')
ax3.set_xlabel('Epoch')
plt.show()