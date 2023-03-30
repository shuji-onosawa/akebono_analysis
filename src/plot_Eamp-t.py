import load
import pytplot
import pytplot.MPLPlotter.tplot as tplot
from scipy.spatial.distance import cdist

start_date = '1990 2 25'
end_date = '1990 2 26'
load.mca([start_date, end_date], spec_type='amp')
load.orb([start_date, end_date])

Emax_tvar = pytplot.get_data('Emax_amp')
Bmax_tvar = pytplot.get_data('Bmax_amp')

Eamp_array = Emax_tvar.y.T
Bamp_array = Bmax_tvar.y.T
freq = Emax_tvar.v

O_gyro = 8

closest_freq_idx = cdist([[O_gyro]]*freq.size, freq.reshape(-1, 1)).argmin()

if closest_freq_idx > 0:
    if freq[closest_freq_idx]-O_gyro > 0:
        second_closest_freq_idx = closest_freq_idx-1
    else:
        second_closest_freq_idx = closest_freq_idx+1

    Eamp_near_fco = Eamp_array[closest_freq_idx]
    Eamp_near_fco_ = Eamp_array[second_closest_freq_idx]
    Eamp_fco = (Eamp_near_fco-Eamp_near_fco_) / \
        (freq[closest_freq_idx]-freq[second_closest_freq_idx]) *\
        (O_gyro - freq[closest_freq_idx])+Eamp_near_fco

    Bamp_near_fco = Bamp_array[closest_freq_idx]
    Bamp_near_fco_ = Bamp_array[second_closest_freq_idx]
    Bamp_fco = (Bamp_near_fco-Bamp_near_fco_) / \
        (freq[closest_freq_idx]-freq[second_closest_freq_idx]) *\
        (O_gyro - freq[closest_freq_idx])+Bamp_near_fco

pytplot.store_data('Eamp_fco', data={'x': Emax_tvar.times, 'y': Eamp_fco})
pytplot.store_data('Bamp_fco', data={'x': Bmax_tvar.times, 'y': Bamp_fco})

pytplot.tlimit([start_date+' 12:22:00', start_date+' 12:26:00'])
# tplot.tplot('Emax_amp')
tplot.tplot(['Eamp_fco', 'Bamp_fco'])
