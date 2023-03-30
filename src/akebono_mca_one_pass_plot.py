import pyspedas
import pytplot
from pytplot import options, tplot, tlimit, tplot_options, get_data, store_data
import numpy as np
from load import mca, orb

gyro_plot = True
ILAT_min = 55
start_day_string = '1990-02-25'
start_day_time_double = pyspedas.time_double(start_day_string)
seconds_per_day = 86400
day_list = []
for i in range(0, 2):
    time_double = start_day_time_double + i * seconds_per_day
    day_list.append(pyspedas.time_string(time_double, fmt='%Y-%m-%d %H:%M:%S'))

for k in range(len(day_list)-1):
    
    trange = [day_list[k], day_list[k+1]]
    print(trange)
    try:
        mca(trange= trange)
    except Exception as e:
        print(e)
        continue
    try:
        orb(trange= trange)
    except Exception as e:
        print(e)
        #with open('./akebono_orbit_error_day_list.txt', mode="a") as f:
        #       f.write(trange[0] + '\n')
        
        #print('orbit file does not exists')
        continue
    try:
        pyspedas.omni.data(trange = trange, level = 'hro', datatype='1min', no_update=True)
    except:
        pyspedas.omni.data(trange = trange, level = 'hro', datatype='1min', no_update=True)

    IMFx_tvar = pytplot.get_data('BX_GSE')
    IMFy_tvar = pytplot.get_data('BY_GSM')
    IMFz_tvar = pytplot.get_data('BZ_GSM')

    time = IMFx_tvar.times
    IMFx = IMFx_tvar.y
    IMFy = IMFy_tvar.y
    IMFz = IMFz_tvar.y

    IMF_matrix = [IMFx,
                  IMFy,
                  IMFz]
    IMF_matrix = np.array(IMF_matrix).T
    pytplot.store_data('IMF', data = {'x':time, 'y':IMF_matrix})
    
    tplot_names = pytplot.tplot_names(True)

    #dB to amplitude
    for i in range(4):
        tplot_variable = pytplot.get_data(tplot_names[i])
        tplot_variable_float = (tplot_variable.y).astype(float)
        np.place(tplot_variable_float, tplot_variable_float == 254, np.nan)
        tplot_variable_0dB = 1e-6 #mV or pT
        bandwidth = tplot_variable.v * 0.3
        tplot_variable_amplitude = (10**(tplot_variable_float/20)) * (tplot_variable_0dB)  / np.sqrt(bandwidth)
        tplot_variable_power = (10**(tplot_variable_float/10)) * ((tplot_variable_0dB)**2)  / bandwidth
        pytplot.store_data(tplot_names[i] +'_Amp', data={'x': tplot_variable.times, 'y': tplot_variable_amplitude, 'v': tplot_variable.v})
        pytplot.store_data(tplot_names[i] +'_Pwr', data={'x': tplot_variable.times, 'y': tplot_variable_power, 'v': tplot_variable.v})

    #ion gyro freq 
    Bx = pytplot.get_data('akb_Bmdl_X')
    By = pytplot.get_data('akb_Bmdl_Y')
    Bz = pytplot.get_data('akb_Bmdl_Z')
    B = np.sqrt(Bx.y**2 + By.y**2 + Bz.y**2) * 1e-9

    mass_o = 2.656e-26
    mass_h = 1.67e-27
    q = 1.60217663e-19

    O_gyro = q*B/mass_o/(2*np.pi)
    H_gyro = q*B/mass_h/(2*np.pi)
    gyro_matrix = np.array([O_gyro, H_gyro]).T
    store_data('gyro_freq', data = {'x': Bx.times, 'y':gyro_matrix})
    
    #Time interpolate
    try:
        pyspedas.tinterpol('akb_ILAT', interp_to='Emax_Pwr', newname = 'ILAT')
    except:
        with open('./akebono_orbit_error_day_list.txt', mode="a") as f:
                f.write(trange[0] + '\n')
        print('orbit file is not perfect')
        continue
    pyspedas.tinterpol('akb_MLAT', interp_to='Emax_Pwr', newname = 'MLAT')
    pyspedas.tinterpol('akb_Pass', interp_to='Emax_Pwr', newname = 'Pass', method = 'nearest')
    pyspedas.tinterpol('akb_ALT', interp_to='Emax_Pwr', newname = 'ALT')
    pyspedas.tinterpol('akb_MLT', interp_to='Emax_Pwr', newname = 'MLT', method = 'nearest')
    #Limit ILAT range
    Emax = get_data('Emax_Pwr')
    time = Emax.times
    ILAT = get_data('ILAT')
    ILAT = ILAT.y
    MLAT = get_data('MLAT')
    MLAT = MLAT.y
    MLT = get_data('MLT')
    MLT = MLT.y

    north_index_tuple = np.where((MLAT>0) & (ILAT>ILAT_min)) 
    south_index_tuple = np.where((MLAT<0) & (ILAT>ILAT_min))

    north_index = north_index_tuple[0]
    south_index = south_index_tuple[0]


    #make start_time list, end_time list
    if len(north_index) == 0:
        north_start_time_list = None
        north_end_time_list = None
    else:    
        north_start_time_index = [north_index[0]]
        north_end_time_index = []
        for i in range(north_index.size-1):
            if north_index[i+1] - north_index[i] > 1:
                north_end_time_index.append(north_index[i])
                north_start_time_index.append(north_index[i+1])
                
        north_end_time_index.append(north_index[-1])

        north_start_time_index = np.array(north_start_time_index)
        north_end_time_index = np.array(north_end_time_index)

        north_start_time_list = pyspedas.time_string(time[north_start_time_index], fmt='%Y-%m-%d %H:%M:%S')
        north_end_time_list = pyspedas.time_string(time[north_end_time_index], fmt='%Y-%m-%d %H:%M:%S')

    if len(south_index) == 0:
        south_start_time_list = None
        south_end_time_list = None
    else:
        south_start_time_index = [south_index[0]]
        south_end_time_index = []
        for i in range(south_index.size-1):
            if south_index[i+1] - south_index[i] > 1:
                south_end_time_index.append(south_index[i])
                south_start_time_index.append(south_index[i+1])
                
        south_end_time_index.append(south_index[-1])

        south_start_time_index = np.array(south_start_time_index)
        south_end_time_index = np.array(south_end_time_index)

        south_start_time_list = pyspedas.time_string(time[south_start_time_index], fmt='%Y-%m-%d %H:%M:%S')
        south_end_time_list = pyspedas.time_string(time[south_end_time_index], fmt='%Y-%m-%d %H:%M:%S')


    start_time_list_list = [north_start_time_list, south_start_time_list]
    end_time_list_list = [north_end_time_list, south_end_time_list]
    print(start_time_list_list)
    print(end_time_list_list)
    
    #make Passname list corresponding with start(end) time list
    Passname = get_data('Pass')
    Passname = Passname.y
    if len(north_index) == 0:
        north_Passname_list = None
    else:
        north_Passname_list = Passname[north_start_time_index]
    if len(south_index) == 0:
        south_Passname_list = None
    else:       
        south_Passname_list = Passname[south_start_time_index]

    Passname_list_list = [north_Passname_list, south_Passname_list]
    
    surfix = 'Pwr'

    #plot

    start_time_list = start_time_list_list[0]
    if start_time_list == None:
        print('No orbits satisfy the condition.')
        continue
    end_time_list = end_time_list_list[1]

    for j in range(len(start_time_list)):
            start_time = start_time_list[j]
            end_time = end_time_list[j]

            year = start_time[:4]
            Month = start_time[5:7]
            day = start_time[8:10]
            hour = start_time[11:13]
            minute = start_time[14:16]
            second = start_time[17:19]
            
            print([start_time, end_time])

            tlimit([start_time, end_time])
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'spec', 1)
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'ylog', 1)
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'zlog', 1)
            
            if surfix == 'Amp':
                options('Emax_' + surfix, 'zrange', [1e-5, 10])
                options('Bmax_' + surfix, 'zrange', [1e-5, 10])
                #options('Emax_lines_' + surfix, 'yrange', [1e-3, 10])
                options('Emax_' + surfix, 'ztitle', '$[mV/m/Hz^(1/2)]$')
                options('Bmax_' + surfix, 'ztitle', '$[pT/Hz^(1/2)]$')
                options('Emax_lines_' + surfix, 'ysubtitle', '$[mV/m/Hz^(1/2)]$')
            elif surfix == 'Pwr':
                options('Emax_' + surfix, 'zrange', [1e-10, 100])
                options('Bmax_' + surfix, 'zrange', [1e-8, 1e6])
                #options('Emax_lines_' + surfix, 'yrange', [1e-6, 100])
                options('Emax_' + surfix, 'ztitle', '$[(mV/m)^2/Hz]$')
                options('Bmax_' + surfix, 'ztitle', '$[pT^2/Hz]$')
                options('Emax_lines_' + surfix, 'ysubtitle', '$[(mV/m)^2/Hz]$')
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'yrange', [1, 2e4])
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'ysubtitle', 'freq [Hz]')
            options('ALT', 'ytitle', 'ALT [km]')
            options('MLT', 'ytitle', 'MLT [h]')
            options('ILAT', 'ytitle', 'ILAT [deg]')
            
            omni_data_names = ['SYM_H', 'IMF', 'flow_speed', 'proton_density', 'Pressure', 'E']
            options(omni_data_names, 'panel_size', 0.5)
            options('IMF', 'legend_names', ['IMF x', "IMF y", "IMF z"])
            options('SYM_H', 'ytitle', 'SYM-H')
            options('SYM_H', 'ysubtitle', '[nT]')
            options('flow_speed', 'ytitle', 'flow \n speed')
            options('flow_speed', 'ysubtitle', '[km/s]')
            options('proton_density', 'ytitle', 'proton \n density')
            options('Pressure', 'ytitle', 'flow \n pressure')
            options('E', 'ytitle', 'E_sw')
            options('E', 'ysubtitle', 'mV/m')
            
            options('gyro_freq', 'ylog', 1)
            options('gyro_freq', 'legend_names', ['fco','fcH'])
            options('gyro_freq', 'panel_size', 0.5)

            tplot_options('title',  year+Month+day+ ' MCA ' + surfix)
            tplot_options('var_label', ["3.16 Hz", "5.62 Hz", "10 Hz", "17.6Hz",
                                        "31.6 Hz", "56.2 Hz", "100 Hz", "176 Hz",
                                        "316 Hz", "562 Hz", '1000 Hz'])

            
            if gyro_plot:
                tplot(['Bmax_' + surfix, 'Emax_' + surfix, 'gyro_freq'], 
                var_label = ['ALT', 'akb_MLT', 'ILAT'], 
                save_png = './' + 'akb_'+ year + Month + day + '_' + hour + minute + second,
                xsize=14, ysize=16,
                display= False)
            else:
                tplot(['IMF', 'flow_speed', 'proton_density','Pressure', 'E','Bmax_' + surfix, 'Emax_' + surfix, 'Emax_lines_' + surfix, 'SYM_H'], 
                var_label = ['ALT', 'MLT', 'ILAT'], 
                xsize=14, ysize=16)
