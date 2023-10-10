import numpy as np
import matplotlib.pyplot as plt
import calc_dispersion_in_cold_plasma as calc_dr
import plasma_params as pp
from matplotlib.markers import MarkerStyle

# 伝播角、周波数の範囲を指定
theta = 0
omega_s = pp.omega_h
freq = np.abs(omega_s['value'])*np.logspace(-2, 2, 100)

subplot_title = ['Ey / Ex', 'Ez / Ex', 'By / Bx', 'Bz / Bx', 'E / cB']

n_L, n_R, S, D, P = calc_dr.calc_dispersion_relation(freq, theta)
EyToExL, EzToExL, ByToBxL, ByToBzL, EToCB = calc_dr.calc_amp_ratio(n_L, S, D, P, theta)
EyToExR, EzToExR, ByToBxR, ByToBzR, EToCB = calc_dr.calc_amp_ratio(n_R, S, D, P, theta)

char_freq = np.array([pp.omega_o['value'], pp.omega_he['value'],
                      pp.omega_h['value'], pp.wlh['value']])

# line plot
fig, axs = plt.subplots(2, 2, figsize=(16, 8))
axs = axs.flatten()  # flatten 2D array
fig.suptitle('Cold plasma dispersion relation\nWave normal angle: {} deg'.format(theta))
for i in range(axs.size):
    axs[i].set_xscale('log')
    axs[i].set_yscale('symlog', linthresh=0.01)
    axs[i].set_xlim(freq[0], freq[-1])
    axs[i].set_xlabel('Frequency [Hz]')
    axs[i].set_ylabel(subplot_title[i])
    axs[i].vlines(char_freq, 1e-3, 1e3, linestyle='dashed', color='k', alpha=0.5)

axs[0].scatter(freq, EyToExL, label='L mode')
axs[0].scatter(freq, EyToExR, label='R mode')
axs[0].legend()

axs[1].scatter(freq, EzToExL, label='L mode')
axs[1].scatter(freq, EzToExR, label='R mode')
axs[1].legend()

axs[2].scatter(freq, ByToBxL, label='L mode')
axs[2].scatter(freq, ByToBxR, label='R mode')
axs[2].legend()

axs[3].scatter(freq, ByToBzL, label='L mode')
axs[3].scatter(freq, ByToBzR, label='R mode')
axs[3].legend()

plt.tight_layout()
plt.show()

# scatter plot
fig, axs = plt.subplots(2, 1, figsize=(8, 8))
axs = axs.flatten()  # flatten 2D array
cmap = 'coolwarm'
for ax in axs:
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(freq[0], freq[-1])
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('Squared refractive index')
    ax.set_title('Wave normal angle: {} deg'.format(theta))
    ax.vlines(char_freq, 1e-3, 1e3, linestyle='dashed', color='k', alpha=0.5)


scatterL = axs[0].scatter(freq, n_L, c=EyToExL, cmap=cmap, label='L mode', vmin=-3, vmax=3, marker=MarkerStyle(','))
colorbarL = plt.colorbar(scatterL, ax=axs[0])
colorbarL.set_label(subplot_title[0])
axs[0].legend()

scatterR = axs[1].scatter(freq, n_R, c=EyToExR, cmap=cmap, label='R mode', vmin=-3, vmax=3, marker=MarkerStyle('x'))
colorbarR = plt.colorbar(scatterR, ax=axs[1])
colorbarR.set_label(subplot_title[0])
axs[1].legend()

plt.tight_layout()
plt.show()
