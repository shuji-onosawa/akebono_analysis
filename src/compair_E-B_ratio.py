from pytplot import cdf_to_tplot, tlimit, tplot, get_data, store_data, options, tplot_options
from pyspedas import tinterpol
from load import mca_h1cdf_dB_to_absolute, orb, get_inst_flag_array, calc_B0
import calc_dispersion_in_cold_plasma as calc_dr
import plasma_params as pp
import datetime


def next_day(year: str, month: str, day: str):
    date = datetime.date(int(year), int(month), int(day))
    next_date = date + datetime.timedelta(days=1)
    return str(next_date.year), str(next_date.month), str(next_date.day)


# read cdf
year = '1990'
month = '02'
date = '17'
cdf_name = 'Akebono_MCA_data/H1CDF_ave1s/ak_h1_mca_'+year+month+date+'_v02.cdf'
cdf_to_tplot(cdf_name)
mca_h1cdf_dB_to_absolute(spec_type='amp')
Eamp_tvar = get_data('Emax_amp')
times = Eamp_tvar.times
center_freq = Eamp_tvar.v
# calc observed E/cB
Bamp_tvar = get_data('Bmax_amp')
E_to_cB = Eamp_tvar.y/pp.C/Bamp_tvar.y*1e9
store_data(name='E_to_cB',
           data={'x': times, 'y': E_to_cB, 'v': center_freq})

# calc theoretical E/cB
theta = 30
n_L, n_R, S, D, P = calc_dr.calc_dispersion_relation(center_freq, theta)
_, _, _, _, E_to_cB_R = calc_dr.calc_amp_ratio(n_R, S, D, P, theta)
_, _, _, _, E_to_cB_L = calc_dr.calc_amp_ratio(n_L, S, D, P, theta)

# calc ratio of observed/theoretical
store_data(name='obs_theor_ratio_R',
           data={'x': times, 'y': E_to_cB/E_to_cB_R, 'v': center_freq})
store_data(name='obs_theor_ratio_L',
           data={'x': times, 'y': E_to_cB/E_to_cB_L, 'v': center_freq})
options(['obs_theor_ratio_R', 'obs_theor_ratio_L'],
        opt_dict={'spec': 1, 'ylog': 1, 'zlog': 1, 'zrange': [1e-1, 1e1]})
options(name='obs_theor_ratio_R',
        opt_dict={'ytitle': r'$E/B_{obs}/E/B_{theor}$', 'ysubtitle': 'R-mode'})
options('obs_theor_ratio_L',
        opt_dict={'ytitle': r'$E/B_{obs}/E/B_{theor}$', 'ysubtitle': 'L-mode'})
# get instruments flag
postgap_array = get_inst_flag_array()
store_data(name='Inst_flag',
           data={'x': times, 'y': postgap_array})
options(name='Inst_flag',
        opt_dict={'legend_names': ["off", "noisy", "BDR", "SMS", "Bit rate", "PWS"],
                  'panael_size': 0.5})

# interpolate satellite position data
next_year, next_month, next_date = next_day(year, month, date)
orb([year+'-'+month+'-'+date,
     next_year+'-'+next_month+'-'+next_date])
calc_B0()
tinterpol(names=['akb_ILAT', 'akb_MLT', 'akb_ALT', 'total_Bmdl'],
          interp_to='Emax_amp')

# plot
tlimit(['1990-2-17 03:46:00', '1990-2-17 03:48:00'])
tplot(['Emax_amp', 'Bmax_amp'], var_label=['akb_ALT-itrp', 'akb_ILAT-itrp', 'akb_MLT-itrp'],
        xsize=10, ysize=10)
'''
title = 'WNA'+str(theta)+'deg,'+'H:He:O='+str(pp.ion_ratio) + \
        ',Ne='+'{:.3g}'.format(pp.NE/1e6)+'/cc,B0='+'{:.2g}'.format(pp.B0/1e-9)+'nT'
tplot_options('title', title)

save_name = './plots/Ishigaya_event/'+year+month+date+'_WNA'+str(theta)
tplot(['Emax_amp', 'Bmax_amp', 'obs_theor_ratio_R', 'obs_theor_ratio_L', 'Inst_flag'],
      var_label=['akb_ALT-itrp', 'akb_ILAT-itrp', 'akb_MLT-itrp'],
      xsize=16, ysize=20, save_png=save_name)
'''
