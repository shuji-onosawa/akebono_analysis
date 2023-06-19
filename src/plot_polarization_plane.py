#3次元内のプラズマ波動の偏波面をプロットするプログラム

import numpy as np
import matplotlib.pyplot as plt
from calc_dispersion_in_cold_plasma import calc_dispersion_relation, calc_amp_ratio

angle_freq = 2*np.pi*100
theta = np.linspace(0, 2*np.pi, 100)

# 偏波面のプロット
fig = plt.figure(figsize=(14, 16))
ax = fig.add_subplot(211, projection='3d')
ax2 = fig.add_subplot(212, projection='3d')

wave_normal_angles = np.linspace(0, 90, 10)
color = [[0, 0, 0], [0, 0, 0.1], [0, 0, 0.2], [0, 0, 0.3], [0, 0, 0.4],
         [0, 0, 0.5], [0, 0, 0.6], [0, 0, 0.7], [0, 0, 0.8], [0, 0, 0.9]]

for i in range(wave_normal_angles.size):
    wna = wave_normal_angles[i]
    wave_number_vec = np.array([np.sin(wna*np.pi/180), 0, np.cos(wna*np.pi/180)])
    n_L, n_R, S, D, P = calc_dispersion_relation(angle_freq, wna)
    Ey_Ex, Ez_Ex, By_Bx, Bz_Bx, E_cB = calc_amp_ratio(n_L, S, D, P, wna)

    ax.scatter(np.cos(theta), -Ey_Ex*np.sin(theta), Ez_Ex*np.cos(theta),
               color=color[i], s=1.0, marker='o', label='WNA = '+str(wna)+' [deg]')
    ax.quiver(0, 0, 0, wave_number_vec[0], wave_number_vec[1], wave_number_vec[2])
    ax2.scatter(np.cos(theta), -By_Bx*np.sin(theta), Bz_Bx*np.cos(theta),
                color=color[i], s=1.0, marker='o', label='WNA = '+str(wna)+' [deg]')
    ax2.quiver(0, 0, 0,
               5*wave_number_vec[0], 5*wave_number_vec[1], 5*wave_number_vec[2])
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_zlim(-1.5, 1.5)
ax.set_xlabel('Ex/Ex')
ax.set_ylabel('Ey/Ex')
ax.set_zlabel('Ez/Ex')
ax.set_title('Electric field')
ax2.set_xlim(-10, 10)
ax2.set_ylim(-10, 10)
ax2.set_zlim(-10, 10)
ax2.set_xlabel('Bx/Bx')
ax2.set_ylabel('By/Bx')
ax2.set_zlabel('Bz/Bx')
ax2.set_title('Magnetic field')
# 枠外に凡例を表示
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, fontsize=8)
# 枠外に凡例を表示
ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, fontsize=8)
# plt.savefig('../plots/polarization_plane/wna_'+str(wave_normal_angle)+'_w_'+str(angle_freq/2/np.pi)+'Hz'+'.png')


plt.show()
