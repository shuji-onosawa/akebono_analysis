import xarray as xr
import cdflib
from preprocess_mgf_epoch import convert_epoch
import pytplot


def store_elf(cdf_file: str):
    dataset = cdflib.cdf_to_xarray(cdf_file)
    epoch = convert_epoch(dataset['Epoch_wav_narrow'].values)
    E, Bx, By, Bz = calibrate_elf(dataset)
    pytplot.store_data('E_waveform', data={'x': epoch, 'y': E})
    pytplot.store_data('Bx_waveform', data={'x': epoch, 'y': Bx})
    pytplot.store_data('By_waveform', data={'x': epoch, 'y': By})
    pytplot.store_data('Bz_waveform', data={'x': epoch, 'y': Bz})

    pytplot.options('E_waveform', opt_dict={'ytitle': 'E (mV/m)',
                                            'ylim': [-1.1, 1.1]})
    pytplot.options('Bx_waveform', opt_dict={'ytitle': 'Bx (nT)',
                                             'ylim': [-5000, 5000]})
    pytplot.options('By_waveform', opt_dict={'ytitle': 'By (nT)',
                                             'ylim': [-5000, 5000]})
    pytplot.options('Bz_waveform', opt_dict={'ytitle': 'Bz (nT)',
                                             'ylim': [-5000, 5000]})
    return


def calibrate_elf(dataset: xr.Dataset):
    h = 30.0
    l = 0.05

    gep = -2.15
    ged = 20.0
    gbd = 20.0  # search coil->20dB, loop antenna->25dB

    z0 = 377.0

    u = 1.26*10**(-6.0)

    dE_wav_narrow = dataset['dE_wav_narrow'].values
    dBx_wav_narrow = dataset['dBx_wav_narrow'].values
    dBy_wav_narrow = dataset['dBy_wav_narrow'].values
    dBz_wav_narrow = dataset['dBz_wav_narrow'].values

    E = dE_wav_narrow/(h*gep*ged)  # mV/m
    Bx = dBx_wav_narrow*u/(z0*l*gbd*10**(-9))  # nT
    By = dBy_wav_narrow*u/(z0*l*gbd*10**(-9))  # nT
    Bz = dBz_wav_narrow*u/(z0*l*gbd*10**(-9))  # nT

    return E, Bx, By, Bz
