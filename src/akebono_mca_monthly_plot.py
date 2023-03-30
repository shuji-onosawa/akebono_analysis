import pyspedas
from pytplot import get_data, store_data, tplot_names, options, tplot_options
from pytplot.MPLPlotter.tplot import tplot
from pyspedas import time_clip, time_double, time_string, tinterpol
import numpy as np
from load import mca, orb
import os

def akebono_mca_monthly_plot(start_date = '1989-03-01', end_date = '1989-04-01', unit_time_hour = 2, freq_channel_index = 2, spec_type = 'pwr'):
    channels = ["3.16 Hz", "5.62 Hz", "10 Hz", "17.6 Hz",
                "31.6 Hz", "56.2 Hz", "100 Hz", "176 Hz",
                "316 Hz", "562 Hz", "1 kHz", '1.76 kHz']

    seconds_per_day = 86400
    unit_time_width = 3600 * unit_time_hour
    unit_per_day = seconds_per_day/(unit_time_width)
    lat_array = np.arange(55, 90, 0.5)

    hemispheres = ['north','south']
    north_E_matrix = []
    north_B_matrix = []
    north_alpha_low_freq_matrix = []
    north_alpha_high_freq_matrix = []
    north_alt_matrix = []

    south_E_matrix = []
    south_B_matrix = []
    south_alpha_low_freq_matrix = []
    south_alpha_high_freq_matrix = []
    south_alt_matrix = []

    start_time_string = start_date + ' 00:00:00'
    end_time_string = end_date + ' 00:00:00'
    start_time = time_double(start_time_string)
    end_time = time_double(end_time_string)

    days = np.arange(start_time, end_time, seconds_per_day, float)
    days_string = time_string(days, fmt= '%Y-%m-%d %H:%M:%S')


    for i in range(len(days_string)-1):
        trange = [days_string[i], days_string[i+1]]
        print(trange)
        mca(trange)
        try:
            orb(trange)
        except:
            print('/// Orbit data on '+days_string[i]+' is not available. ///')
            for i in range(int(24/unit_time_hour)):
                no_data = np.empty(lat_array.size)
                no_data[:] = np.nan
                no_data = no_data.tolist()
                north_E_matrix.append(no_data)
                north_B_matrix.append(no_data)
                north_alpha_low_freq_matrix.append(no_data)
                north_alpha_high_freq_matrix.append(no_data)
                north_alt_matrix.append(no_data)
                south_E_matrix.append(no_data)
                south_B_matrix.append(no_data)
                south_alpha_low_freq_matrix.append(no_data)
                south_alpha_high_freq_matrix.append(no_data)
                south_alt_matrix.append(no_data)
            continue

        tplot_name = ['Emax', 'Eave', 'Bmax', 'Bave']
        for k in range(4):
                tplot_variable = get_data(tplot_name[k])
                tplot_variable_float = (tplot_variable.y).astype(float)
                np.place(tplot_variable_float, tplot_variable_float == 254, np.nan)
                tplot_variable_0dB = 1e-6 #mV or pT
                bandwidth = tplot_variable.v * 0.3
                tplot_variable_amplitude = (10**(tplot_variable_float/20)) * (tplot_variable_0dB)  / np.sqrt(bandwidth)
                tplot_variable_power = (10**(tplot_variable_float/10)) * ((tplot_variable_0dB)**2)  / bandwidth
                store_data(tplot_name[k] +'_amp', data={'x': tplot_variable.times, 'y': tplot_variable_amplitude, 'v': tplot_variable.v})
                store_data(tplot_name[k] +'_pwr', data={'x': tplot_variable.times, 'y': tplot_variable_power, 'v': tplot_variable.v})
                
        try:
            tinterpol('akb_ILAT', interp_to='Emax_pwr', newname = 'ILAT')
        except:
            print('orbit file is not perfect')
            continue
        tinterpol('akb_MLAT', interp_to = 'Emax', newname = 'MLAT')
        tinterpol('akb_MLT', interp_to = 'Emax', newname = 'MLT', method = 'nearest')
        tinterpol('akb_ALT', interp_to = 'Emax', newname = 'ALT')

        start_time_hour = time_double(days_string[i])
        hours = np.arange(start_time_hour, start_time_hour + (unit_per_day + 1)*unit_time_width, unit_time_width)
        
        Emax_tvar = get_data('Emax_'+spec_type)
        Bmax_tvar = get_data('Bmax_'+spec_type)
        
        #calc power law alpha 
        def reg1dim(x, y):
            n = x.size
            a = ((np.dot(x, y)- np.sum(y) * np.sum(x)/n)/
                (np.sum(x ** 2) - np.sum(x)**2 / n))
            b = (np.sum(y) - a * np.sum(x))/n
            return a, b

        freq = Emax_tvar.v
        Emax = Emax_tvar.y
        times = Emax_tvar.times

        alpha_low_freq_list = []
        alpha_high_freq_list = []

        fit_frange_low = np.log10(freq[2:7]) #10-100 Hz
        fit_frange_high = np.log10(freq[6:11]) #100-1000 Hz

        for j in range(times.size):
            fit_Emax_low = np.log10(Emax[j][2:7])
            a, b = reg1dim(fit_frange_low, fit_Emax_low)
            alpha_low_freq_list.append(a)       

            fit_Emax_high = np.log10(Emax[j][6:11])
            a, b = reg1dim(fit_frange_high, fit_Emax_high)
            alpha_high_freq_list.append(a)
        alpha_low_freq_array = np.array(alpha_low_freq_list)
        alpha_high_freq_array = np.array(alpha_high_freq_list)


        ILAT = get_data('ILAT')
        MLAT = get_data('MLAT')
        MLT = get_data('MLT')
        
        alt_array = get_data('ALT')
        alt_array = alt_array.y

        for hemisphere in hemispheres:
            for j in range(hours.size-1):
                E_list_per_hour = []    
                B_list_per_hour = []
                alpha_low_freq_per_hour = []
                alpha_high_freq_per_hour = []
                alt_per_hour = []

                for lat in lat_array:            
                    if hemisphere == 'north':
                        index_tuple = np.where((hours[j] <= Emax_tvar.times) & (Emax_tvar.times < hours[j+1]) 
                                            & (ILAT.y > lat) & (ILAT.y < lat+1) 
                                            & (10 <= MLT.y) & (MLT.y <= 14)
                                            & (MLAT.y>0))
                                            
                    if hemisphere == 'south':
                        index_tuple = np.where((hours[j] <= Emax_tvar.times) & (Emax_tvar.times < hours[j+1]) 
                                            & (ILAT.y > lat) & (ILAT.y < lat+1) 
                                            & (10 <= MLT.y) & (MLT.y <= 14)
                                            & (MLAT.y<0))
                    index = index_tuple[0] 
                    if len(index) == 0:
                        E_list_per_hour.append(np.nan)
                        B_list_per_hour.append(np.nan)
                        alpha_low_freq_per_hour.append(np.nan)
                        alpha_high_freq_per_hour.append(np.nan)
                        alt_per_hour.append(np.nan)

                    else:
                        E_var_1deg = Emax_tvar.y.T[freq_channel_index][index]
                        E_list_per_hour.append(np.nanmax(E_var_1deg))
                        
                        B_var_1deg = Bmax_tvar.y.T[freq_channel_index][index]
                        B_list_per_hour.append(np.nanmax(B_var_1deg))

                        alt_1deg = alt_array[index]
                        alt_per_hour.append(np.average(alt_1deg[np.where(E_var_1deg == np.nanmax(E_var_1deg))[0]]))

                        if np.nanmax(E_var_1deg) >= 0.01:
                            alpha_low_freq_1deg = alpha_low_freq_array[index]
                            alpha_high_freq_1deg = alpha_high_freq_array[index]
                            alpha_low_freq_per_hour.append(np.average(alpha_low_freq_1deg[np.where(E_var_1deg == np.nanmax(E_var_1deg))[0]]))
                            alpha_high_freq_per_hour.append(np.average(alpha_high_freq_1deg[np.where(E_var_1deg == np.nanmax(E_var_1deg))[0]]))
                        else:
                            alpha_low_freq_per_hour.append(np.nan)
                            alpha_high_freq_per_hour.append(np.nan)
                        
                if hemisphere == 'north':
                    north_E_matrix.append(E_list_per_hour)
                    north_B_matrix.append(B_list_per_hour)
                    north_alpha_low_freq_matrix.append(alpha_low_freq_per_hour)
                    north_alpha_high_freq_matrix.append(alpha_high_freq_per_hour)
                    north_alt_matrix.append(alt_per_hour)

                if hemisphere == 'south':
                    south_E_matrix.append(E_list_per_hour)
                    south_B_matrix.append(B_list_per_hour)
                    south_alpha_low_freq_matrix.append(alpha_low_freq_per_hour)
                    south_alpha_high_freq_matrix.append(alpha_high_freq_per_hour)
                    south_alt_matrix.append(alt_per_hour)

    times = np.arange(start_time, end_time-seconds_per_day, unit_time_width, dtype=float)    #2時間刻み

    store_data('E'+spec_type+'_N_monthly', data={'x':times, 'y':north_E_matrix, 'v':lat_array})
    store_data('E'+spec_type+'_S_monthly', data={'x':times, 'y':south_E_matrix, 'v':lat_array})
    store_data('B'+spec_type+'_N_monthly', data={'x':times, 'y':north_B_matrix, 'v':lat_array})
    store_data('B'+spec_type+'_S_monthly', data={'x':times, 'y':south_B_matrix, 'v':lat_array})
    options(['E'+spec_type+'_N_monthly','E'+spec_type+'_S_monthly', 'B'+spec_type+'_N_monthly', 'B'+spec_type+'_S_monthly'], 'spec', 1)
    options(['E'+spec_type+'_N_monthly','E'+spec_type+'_S_monthly', 'B'+spec_type+'_N_monthly', 'B'+spec_type+'_S_monthly'], 'zlog', 1)
    options(['E'+spec_type+'_N_monthly','E'+spec_type+'_S_monthly', 'B'+spec_type+'_N_monthly', 'B'+spec_type+'_S_monthly'], 'ytitle', 'ILAT \n[deg]')
    options(['E'+spec_type+'_N_monthly', 'E'+spec_type+'_S_monthly'], 'ztitle', 'Electric field ')
    options(['B'+spec_type+'_N_monthly', 'B'+spec_type+'_S_monthly'], 'ztitle', 'Magnetic field ')
    options(['E'+spec_type+'_N_monthly', 'E'+spec_type+'_S_monthly'], 'zsubtitle', 'PSD  [(mV/m)^2/Hz]')
    options(['E'+spec_type+'_N_monthly', 'E'+spec_type+'_S_monthly'], 'zrange', [1e-6, 1])
    options(['B'+spec_type+'_N_monthly', 'B'+spec_type+'_S_monthly'], 'zsubtitle', 'PSD  [pT^2/Hz]')
    options(['B'+spec_type+'_N_monthly', 'B'+spec_type+'_S_monthly'], 'zrange', [1e-1, 1e5])

    store_data('alpha_low_N', data={'x':times, 'y':north_alpha_low_freq_matrix, 'v':lat_array})
    store_data('alpha_low_S', data={'x':times, 'y':south_alpha_low_freq_matrix, 'v':lat_array})
    store_data('alpha_diff_N', data={'x':times, 'y':np.array(north_alpha_high_freq_matrix)-np.array(north_alpha_low_freq_matrix), 'v':lat_array})
    store_data('alpha_diff_S', data={'x':times, 'y':np.array(south_alpha_high_freq_matrix)-np.array(south_alpha_low_freq_matrix), 'v':lat_array})
    options(['alpha_low_N', 'alpha_low_S', 'alpha_diff_N', 'alpha_diff_S'], 'spec', 1)
    options(['alpha_low_N', 'alpha_low_S', 'alpha_diff_N', 'alpha_diff_S'], 'ytitle', 'ILAT \n[deg]')
    options(['alpha_low_N', 'alpha_low_S'], 'zrange', [-4, -1])
    options(['alpha_low_N', 'alpha_low_S'], 'ztitle', 'Alpha')
    options(['alpha_diff_N', 'alpha_diff_S'], 'zrange', [-3, 3])
    options(['alpha_diff_N','alpha_diff_S'], 'ztitle', 'Alpha_diff')

    store_data('ALT_N', data={'x':times, 'y':north_alt_matrix, 'v':lat_array})
    store_data('ALT_S', data={'x':times, 'y':south_alt_matrix, 'v':lat_array})
    options(['ALT_N', 'ALT_S'], 'spec', 1)
    options(['ALT_N', 'ALT_S'], 'zrange', [0, 10500])
    options(['ALT_N', 'ALT_S'], 'ztitle', 'ALT [km]')
    options('ALT_N', 'ytitle', 'ILAT \n[deg]')
    options('ALT_S', 'ytitle', 'ILAT \n[deg]')

    pyspedas.omni.data([start_time, end_time], datatype='1min', level='hro', no_update=True)
    omni_var_name = ['BZ_GSM', 'flow_speed', 'proton_density', 'Pressure', 'SYM_H']
    options(omni_var_name, 'panel_size', 0.5)

    try:
        os.mkdir('./akb_mca_monthly_plot/south_10Hz/'+start_date[:4]+'/')
    except:
        pass
    try:
        os.mkdir('./akb_mca_monthly_plot/north_10Hz/'+start_date[:4]+'/')
    except:
        pass
    tplot_options('axis_font_size', 14)
    tplot_options('title','Akebono/MCA South Cusp ' + spec_type + ' @' + channels[freq_channel_index])
    options(['SYM_H', 'B'+spec_type+'_S_monthly','E'+spec_type+'_S_monthly', 'alpha_low_S', 'alpha_diff_S', 'ALT_S'], 'char_size', 16)
    options(['SYM_H', 'B'+spec_type+'_N_monthly','E'+spec_type+'_N_monthly', 'alpha_low_N', 'alpha_diff_N', 'ALT_N'], 'char_size', 16)
    tplot(['SYM_H', 'B'+spec_type+'_S_monthly','E'+spec_type+'_S_monthly', 'alpha_low_S', 'alpha_diff_S', 'ALT_S'], xsize = 12, ysize=14,  save_png='./plots/akb_mca_monthly_plot/Epwr_10Hz/'+'mca_monthly_2h_south_'+ spec_type +channels[freq_channel_index]+start_date+'_test1')
    tplot_options('title','Akebono/MCA North Cusp ' + spec_type + ' @' + channels[freq_channel_index])
    tplot(['SYM_H', 'B'+spec_type+'_N_monthly','E'+spec_type+'_N_monthly', 'alpha_low_N', 'alpha_diff_N', 'ALT_N'], xsize = 12, ysize=14,  save_png='./plots/akb_mca_monthly_plot/Epwr_10Hz/'+'mca_monthly_2h_north_'+ spec_type +channels[freq_channel_index]+start_date+'_test1')


from datetime import datetime
import pandas as pd


date_list = pd.date_range(start='1991-09-01', end='1991-10-01', freq='MS')
date_list = np.datetime_as_string(date_list, unit='D')
date_list = date_list.astype(object)

for i in range(date_list.size-1):
    akebono_mca_monthly_plot(start_date = date_list[i], end_date = date_list[i+1], unit_time_hour = 2, freq_channel_index = 2, spec_type = 'pwr')
