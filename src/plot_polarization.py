import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import calc_dispersion_in_cold_plasma as calc_dr
import plasma_params as pp

theta = 90
omega_s = pp.wlh
freq = np.abs(omega_s['value'])*np.logspace(-3, 1, 100)

amp_ratio_L = np.empty((5, freq.size))
amp_ratio_R = np.empty((5, freq.size))
subplot_title = ['Ey / Ex', 'Ez / Ex', 'By / Bx', 'Bz / Bx', 'E / cB']

n_L, n_R, S, D, P = calc_dr.calc_dispersion_relation(freq, theta)
amp_ratio_L[0], amp_ratio_L[1], amp_ratio_L[2], amp_ratio_L[3], amp_ratio_L[4] = \
    calc_dr.calc_amp_ratio(n_L, S, D, P, theta)
amp_ratio_R[0], amp_ratio_R[1], amp_ratio_R[2], amp_ratio_R[3], amp_ratio_R[4] = \
    calc_dr.calc_amp_ratio(n_R, S, D, P, theta)

char_freq = np.array([pp.omega_o['value'], pp.omega_he['value'],
                      pp.omega_h['value'], pp.wlh['value']])

'''
fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 10))
fig.suptitle('WNA'+str(theta)+'deg,'+'H:He:O='+str(pp.ion_ratio) +
             ',Ne='+'{:.2g}'.format(pp.NE/1e6)+'/cc,B0='+'{:.2g}'.format(pp.B0/1e-9)+'nT')
for i in range(2):
    for j in range(2):
        mp = axs[i][j].scatter(x=freq/np.abs(omega_s['value']), y=n_L, c=amp_ratio_L[2*i+j], marker='.',
                               cmap='jet', vmin=-2, vmax=2, label='L')
        mp = axs[i][j].scatter(x=freq/np.abs(omega_s['value']), y=n_R, c=amp_ratio_R[2*i+j], marker=',',
                               cmap='jet', vmin=-2, vmax=2, label='R')
        fig.colorbar(mappable=mp, ax=axs[i][j])
        axs[i][j].vlines(char_freq/np.abs(omega_s['value']), ymin=0, ymax=1e7, colors='k', linestyles='dashed')
        # axs[i][j].vlines(crossover_freq, ymin=0, ymax=1e7, colors='r', linestyles='dashed')
        axs[i][j].set_ylabel(r'$n^2$')
        axs[i][j].set_xscale('log')
        axs[i][j].set_yscale('log')
        axs[i][j].set_ylim(top=1e7)
        axs[i][j].set_title(subplot_title[2*i+j])
        axs[i][j].legend()
        if i == 1:
            axs[i][j].set_xlabel(r'$\omega/$'+omega_s['label'])
plt.savefig('plots/polarization/Amp_ratio_WNA'+str(theta)+'_H_He_O_'
            + str(pp.ion_ratio)+'_N_e'+str(pp.NE/1e6)+'cc_B0_'
            + str(pp.B0/1e-9) + '_nT'+'.png')
plt.show()
'''
fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(10, 8))
fig.suptitle('WNA'+str(theta)+'deg,'+'H:He:O='+str(pp.ion_ratio) +
             ',Ne='+'{:.2g}'.format(pp.NE/1e6)+'/cc,B0='+'{:.2g}'.format(pp.B0/1e-9)+'nT')
mp = axs.scatter(x=freq/np.abs(omega_s['value']), y=n_L, c=amp_ratio_L[4], marker='.',
                 cmap='jet', label='L', norm=colors.LogNorm(vmin=1e-4, vmax=1))
mp = axs.scatter(x=freq/np.abs(omega_s['value']), y=n_R, c=amp_ratio_R[4], marker=',',
                 cmap='jet', label='R', norm=colors.LogNorm(vmin=1e-4, vmax=1))
fig.colorbar(mappable=mp, ax=axs)
axs.vlines(char_freq/np.abs(omega_s['value']), ymin=0, ymax=1e7, colors='k', linestyles='dashed')
# axs[i][j].vlines(crossover_freq, ymin=0, ymax=1e7, colors='r', linestyles='dashed')
axs.set_ylabel(r'$n^2$')
axs.set_xscale('log')
axs.set_yscale('log')
axs.set_ylim(top=1e7)
axs.set_title(subplot_title[4])
axs.legend()
axs.set_xlabel(r'$\omega/$'+omega_s['label'])
plt.show()
