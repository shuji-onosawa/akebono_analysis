import pyspedas
from pytplot import get_data, store_data, tplot_names, tplot, options, tplot_options
from pyspedas import time_clip, time_double, time_string, tinterpol
import numpy as np
from load import mca, orb

start_date = '1989-05-01'
end_date = '1989-05-30'
spec_type = 'pwr' #amplitude, amp or power, pwr

orb([start_date, end_date])
mca([start_date, end_date])

tvar_names = ['Emax', 'Bmax']
for tvar_name in tvar_names:
    tplot_variable = get_data(tvar_name)
    tplot_variable_float = (tplot_variable.y).astype(float)
    np.place(tplot_variable_float, tplot_variable_float == 254, np.nan)
    tplot_variable_0dB = 1e-6 #mV or pT
    bandwidth = tplot_variable.v * 0.3
    tplot_variable_amplitude = (10**(tplot_variable_float/20)) * (tplot_variable_0dB)  / np.sqrt(bandwidth)
    tplot_variable_power = (10**(tplot_variable_float/10)) * ((tplot_variable_0dB)**2)  / bandwidth
    store_data(tvar_name +'_'+spec_type, data={'x': tplot_variable.times, 'y': tplot_variable_power, 'v': tplot_variable.v})

tinterpol('akb_ILAT', interp_to='Emax', newname = 'ILAT', )
tinterpol('akb_MLAT', interp_to='Emax', newname = 'MLAT')
tinterpol('akb_MLT', interp_to='Emax', newname = 'MLT', method = 'nearest')

