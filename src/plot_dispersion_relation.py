import numpy as np
import plasma_params as pp
import matplotlib.pyplot as plt
import calc_dispersion_in_cold_plasma as calc_dr
import os

wave_normal_angle = 60
omega_s = pp.wlh
freq = np.abs(omega_s['value'])*np.logspace(-3, 1, 10000)

n_L, n_R, S, D, P = calc_dr.calc_dispersion_relation(freq, wave_normal_angle)
# idx = calc_dr.get_crossover_freq_idx(D, theta)

char_freq = np.array([pp.omega_he['value'], pp.omega_h['value'], pp.omega_o['value'], -pp.omega_e['value'], pp.wlh['value']])/omega_s['value']

# crossover_freq = np.empty(idx.size)
# for i in range(idx.size):
#     crossover_freq[i] = freq[idx[i]] / omega_s

fig, axs = plt.subplots(nrows=1, ncols=1, figsize=[16, 8])
axs.scatter(x=freq/omega_s['value'], y=n_L, label=r'$L mode$', c='r', marker='.')
axs.scatter(x=freq/omega_s['value'], y=n_R, label=r'$R mode$', c='b', marker='.')
axs.vlines(char_freq, 0, 1e7, linestyles='dashed', colors='k')
# axs.vlines(crossover_freq, 0, 1e7, linestyles='dashed', colors='r')
axs.set_xscale('log')
axs.set_yscale('log')
axs.set_xlabel(r'$\omega/$'+omega_s['label'])
axs.set_ylabel(r'$Refraction index ^2$')

plt.legend()
# plt.savefig('../plots/dispersion_relation/refraction_index_wna_'+str(theta)+'.png')
plt.show()

fig, axs = plt.subplots(nrows=1, ncols=1, figsize=[8, 8])
axs.scatter(x=freq*n_L**0.5/pp.C/2/np.pi, y=freq/2/np.pi, label=r'$L mode$', c='r', marker='.')
axs.scatter(x=freq*n_R**0.5/pp.C/2/np.pi, y=freq/2/np.pi, label=r'$R mode$', c='b', marker='.')
axs.hlines(char_freq*omega_s['value']/2/np.pi, 0, 1e-3, linestyles='dashed', colors='k')

axs.set_ylim(0.1, np.abs(omega_s['value'])/2/np.pi)
axs.set_xscale('log')
axs.set_yscale('log')
axs.set_xlabel(r'$1/\lambda [m^-1]$')
axs.set_ylabel(r'$frequency [Hz]$')

plt.legend()
# make directory if not exist
if not os.path.exists('../plots/dispersion_relation'):
    os.makedirs('../plots/dispersion_relation')
plt.savefig('../plots/dispersion_relation/refraction_index_wna_' +
            str(wave_normal_angle)+'.png')
plt.show()
'''
fig, axs = plt.subplots(nrows=1, ncols=1, figsize=[16, 8])
axs.scatter(x=freq/omega_s['value'], y=D, label=r'$D$', c='g', marker='.')
axs.scatter(x=freq/omega_s['value'], y=S, label=r'$S$', c='y', marker='.')
axs.scatter(x=freq/omega_s['value'], y=P, label=r'$P$', c='k', marker='.')
axs.vlines(char_freq, 0, 1e7, linestyles='dashed', colors='k')
# axs.vlines(crossover_freq, 0, 1e7, linestyles='dashed', colors='r')
axs.set_xscale('log')
axs.set_yscale('log')
axs.set_xlabel(r'$\omega/$'+omega_s['label'])
axs.set_ylabel(r'$Refraction index ^2$')

plt.legend()
plt.show()
'''
