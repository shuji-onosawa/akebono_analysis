import numpy as np
import plasma_params as pp
import matplotlib.pyplot as plt
import calc_dispersion_in_cold_plasma as calc_dr
import os


def plotFreqVsWavelength(waveNormalAngle, save_dir):
    # before running this script, check plasma parameters in plasma_params.py

    # set parameters
    omega_s = pp.wlh
    freq = np.abs(omega_s['value'])*np.logspace(-3, 1, 10000)

    # calc dispersion relation
    n_L, n_R, S, D, P = calc_dr.calc_dispersion_relation(freq, waveNormalAngle)

    char_freq = np.array([pp.omega_he['value'], pp.omega_h['value'], pp.omega_o['value'], -pp.omega_e['value'], pp.wlh['value']])/omega_s['value']
    # plot frequency vs wave number
    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=[8, 8])
    axs.scatter(x=freq*n_L**0.5/pp.C/2/np.pi, y=freq/2/np.pi, label=r'$L mode$', c='r', marker='.')
    axs.scatter(x=freq*n_R**0.5/pp.C/2/np.pi, y=freq/2/np.pi, label=r'$R mode$', c='b', marker='.')

    xmax = 5e-4
    xmin = 1e-7
    axs.hlines(char_freq*omega_s['value']/2/np.pi, xmin, xmax, linestyles='dashed', colors='k')  # charateristic frequencies
    axs.hlines([3.16, 5.62, 10, 17.8, 31.6, 56.2, 100, 178, 316, 562], xmin, xmax, linestyles='dashed', colors='k', alpha=0.5)  # MCA's center frequencies

    axs.set_xlim(xmin, xmax)
    axs.set_ylim(1, np.abs(omega_s['value'])/2/np.pi)
    axs.set_xscale('log')
    axs.set_yscale('log')
    axs.set_xlabel(r'$1/\lambda [m^-1]$')
    axs.set_ylabel(r'$Frequency [Hz]$')

    plt.legend()
    # make directory if not exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    plt.savefig(save_dir+'/freqVSwavelength_' + str(waveNormalAngle)+'.png')

    # save plasma parameters in text file
    with open(save_dir+'/plasma_params.txt', mode='w') as f:
        f.write('plasma parameters\n')
        f.write('B0 = '+str(pp.B0)+' [T]\n')
        f.write('NE = '+str(pp.NE)+' [m^-3]\n')
        f.write('ion_ratio: NH+:NHe+:NO+ = '+str(pp.ion_ratio)+'\n')
        f.write('Va = '+str(pp.Va)+' [m s^-1]\n')


def plotRefractionIndexVsFrequency(waveNormalAngle, save_dir):
    # before running this script, check plasma parameters in plasma_params.py

    # set parameters
    omega_s = pp.wlh
    freq = np.abs(omega_s['value'])*np.logspace(-3, 1, 10000)

    # calc dispersion relation
    n_L, n_R, S, D, P = calc_dr.calc_dispersion_relation(freq, waveNormalAngle)

    # plot refraction index vs frequency
    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=[8, 8])
    axs.scatter(x=freq, y=n_L, label=r'$L mode$', c='r', marker='.')
    axs.scatter(x=freq, y=n_R, label=r'$R mode$', c='b', marker='.')
    axs.vlines([pp.omega_he['value'], pp.omega_h['value'], pp.omega_o['value'], -pp.omega_e['value'], pp.wlh['value']], 0, 1e7, linestyles='dashed', colors='k')  # charateristic frequencies
    axs.set_xscale('log')
    axs.set_yscale('log')
    axs.set_xlabel(r'$\omega/$'+omega_s['label'])
    axs.set_ylabel(r'$Refraction index ^2$')

    plt.legend()
    # make directory if not exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    plt.savefig(save_dir+'/refractionIndexVsfrequency_' + str(waveNormalAngle)+'.png')


for wna in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
    save_dir = '../plots/'
    plotRefractionIndexVsFrequency(wna, save_dir)
