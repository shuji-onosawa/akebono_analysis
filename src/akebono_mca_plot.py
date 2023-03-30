import pyspedas
import pytplot
from pytplot import options, tplot, tlimit, tplot_options, get_data, store_data
import numpy as np
from load import mca, orb

freq_channel_index = 2
channels = ["3.16 Hz", "5.62 Hz", "10 Hz", "17.6 Hz",
            "31.6 Hz", "56.2 Hz", "100 Hz", "176 Hz",
            "316 Hz", "562 Hz", "1 kHz", '1.76 kHz']

surfix = 'Pwr'

ILAT_min = 55
start_day_string = '2003-12-15'
start_day_time_double = pyspedas.time_double(start_day_string)

seconds_per_day = 86400
day_list = []
for i in range(0, 5):
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
    
    tplot_names = ['Emax', 'Eave', 'Bmax', 'Bave']

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
    pyspedas.tinterpol('akb_Bmdl_X', interp_to='Emax_Pwr', newname = 'Bmdl_X')
    pyspedas.tinterpol('akb_Bmdl_Y', interp_to='Emax_Pwr', newname = 'Bmdl_Y')
    pyspedas.tinterpol('akb_Bmdl_Z', interp_to='Emax_Pwr', newname = 'Bmdl_Z')
    
    #Limit ILAT range
    Emax = get_data('Emax_Pwr')
    time = Emax.times
    ILAT = get_data('ILAT')
    ILAT = ILAT.y
    MLAT = get_data('MLAT')
    MLAT = MLAT.y
    MLT = get_data('MLT')
    MLT = MLT.y

    north_index_tuple = np.where((MLAT>0) & (ILAT>ILAT_min) ) 
    south_index_tuple = np.where((MLAT<0) & (ILAT>ILAT_min) )

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
    

    #ion gyro freq 
    Bx = pytplot.get_data('Bmdl_X')
    By = pytplot.get_data('Bmdl_Y')
    Bz = pytplot.get_data('Bmdl_Z')
    B = np.sqrt(Bx.y**2 + By.y**2 + Bz.y**2) * 1e-9

    mass_o = 2.656e-26
    mass_h = 1.67e-27
    q = 1.60217663e-19

    O_gyro = q*B/mass_o/(2*np.pi)
    H_gyro = q*B/mass_h/(2*np.pi)
    gyro_matrix = np.array([O_gyro, H_gyro]).T
    store_data('gyro_freq', data = {'x': Bx.times, 'y':gyro_matrix})
    options('gyro_freq', 'legend_names', ['fcO', 'fcH'])
    options('gyro_freq', 'legend_location', 'spedas')
    options('gyro_freq', 'ylog', 1)
    options('gyro_freq', 'yrange', [1, 2e4])
    options('gyro_freq', 'ytitle', 'Frequency [Hz]')


    #calc power law alpha 
    def reg1dim(x, y):
        n = x.size
        a = ((np.dot(x, y)- np.sum(y) * np.sum(x)/n)/
            (np.sum(x ** 2) - np.sum(x)**2 / n))
        b = (np.sum(y) - a * np.sum(x))/n
        return a, b

    Emax_tvar = pytplot.get_data('Emax_Pwr')
    freq = Emax_tvar.v
    Emax = Emax_tvar.y
    times = Emax_tvar.times

    alpha_list_low_freq = []
    alpha_list_high_freq = []
    Emax_res_list = []

    fit_frange_low = np.log10(freq[2:7]) #10-100 Hz
    fit_frange_high = np.log10(freq[6:11]) #100-1000 Hz

    for j in range(times.size):
        fit_Emax_low = np.log10(Emax[j][2:7])
        a, b = reg1dim(fit_frange_low, fit_Emax_low)
        alpha_list_low_freq.append(a)       
        p0 = 10**b
        Emax_lsm = p0*freq**a
        Emax_res = (np.log10(Emax[j]) - np.log10(Emax_lsm)).tolist()
        Emax_res_list.append(Emax_res)

        fit_Emax_high = np.log10(Emax[j][6:11])
        a, b = reg1dim(fit_frange_high, fit_Emax_high)
        alpha_list_high_freq.append(a)

    store_data('Emax_alpha', data={'x':times, 'y':np.array([alpha_list_low_freq, alpha_list_high_freq]).T})
    options('Emax_alpha', 'legend_names', [r'$\alpha -low$',r'$\alpha -high$'])
    options('Emax_alpha', 'yrange', [-5, 0])
    
    store_data('Emax_pwr_res', data={'x':times, 'y':Emax_res_list, 'v':freq})
    options('Emax_pwr_res', 'spec', 1)
    options('Emax_pwr_res', 'ylog', 1)
    options('Emax_pwr_res', 'ztitle', 'log10((mV/m)^2/Hz)')
    options('Emax_pwr_res', 'zrange', [-2, 2])
    options('Emax_pwr_res', 'Colormap', 'coolwarm')


    #make tplot vars of Electric field Amplitude at 3.16 - 1000 Hz
    Eamp = get_data('Emax_Amp')
    Eamp_0_1000Hz = Eamp.y.T[0:11]
    
    store_data(name = 'Emax_lines_Amp', 
               data={'x': time,'y': Eamp_0_1000Hz.T})

    #make tplot vars of Electric field Amplitude at 3.16 - 1000 Hz
    Epwr = get_data('Emax_Pwr')
    Epwr_0_1000Hz = Epwr.y.T[0:11]
    
    store_data(name = 'Emax_lines_Pwr', 
               data={'x': time,'y': Epwr_0_1000Hz.T})
 

    #dir_list = ['./akb_North_mca_plot/', './akb_South_mca_plot/']
    dir_list = ['./plots/akb_North_mca_w_gyro_plot/', './plots/akb_South_mca_w_gyro_plot/']
    hemisphere_list = ['north', 'south']


    #plot
    for i in range(2):
        dir = dir_list[i]
        hemisphere = hemisphere_list[i]
        start_time_list = start_time_list_list[i]
        if start_time_list == None:
            print('No orbits in the ' + hemisphere + ' hemisphere satisfy the condition.')
            continue
        end_time_list = end_time_list_list[i]
        Passname_list = Passname_list_list[i]

        print(hemisphere)
        print(start_time_list)
        print(end_time_list)
        for j in range(len(start_time_list)):
            start_time = start_time_list[j]
            end_time = end_time_list[j]

            year = start_time[:4]
            Month = start_time[5:7]
            day = start_time[8:10]
            hour = start_time[11:13]
            minute = start_time[14:16]
            second = start_time[17:19]

            Passname = Passname_list[j]
            Passname = str(int(Passname))
            Passname = Passname[-4:]
            
            #dict event case
            Emax_pwr = get_data('Emax_Pwr')
            index_tuple = np.where((pyspedas.time_double(start_time_list[j]) < Emax_pwr.times) 
                                 & (Emax_pwr.times < pyspedas.time_double(end_time_list[j]))
                                 & (MLT>=10) & (MLT<=14))
            Emax_10Hz = Emax_pwr.y.T[2][index_tuple[0]]
            
            save_name = ''
            
            if Emax_10Hz.size == 0:
                continue
            if np.isnan(np.nanmax(Emax_10Hz)):
                continue
            if np.nanmax(Emax_10Hz) >=0.5:
                save_name = dir + 'super_strong_event/' + 'akb-mca-'+ hemisphere +'_'+ year + Month + day + '_' + hour + minute + second
            elif np.nanmax(Emax_10Hz) >=0.3:
                save_name = dir + 'strong_event/' + 'akb-mca-'+ hemisphere +'_'+ year + Month + day + '_' + hour + minute + second
            elif np.nanmax(Emax_10Hz) >=0.01:
                save_name = dir + 'normal_event/' + 'akb-mca-'+ hemisphere +'_'+ year + Month + day + '_' + hour + minute + second 

            tlimit([start_time, end_time])
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'spec', 1)
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'ylog', 1)
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'zlog', 1)
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'yrange', [1, 2e4])
            options(['Emax_' + surfix, 'Bmax_' + surfix], 'ysubtitle', 'freq [Hz]')
            options('Emax_lines_' + surfix, 'ylog', 1)
            options('Emax_lines_' + surfix, 'legend_location', 'spedas')
            options('Emax_lines_' + surfix, 'legend_names', ["3.16 Hz", "5.62 Hz", "10 Hz", "17.6 Hz",
                                                             "31.6 Hz", "56.2 Hz", "100 Hz", "176 Hz",
                                                             "316 Hz", "562 Hz", "1000 Hz"])
            #options(['Emax_' + surfix, 'Bmax_' + surfix], 'Colormap', 'viridis')
            if surfix == 'Amp':
                options('Emax_' + surfix, 'zrange', [1e-5, 10])
                options('Bmax_' + surfix, 'zrange', [1e-5, 10])
                options('Emax_lines_' + surfix, 'yrange', [1e-3, 10])
                options('Emax_' + surfix, 'ztitle', '$[mV/m/Hz^(1/2)]$')
                options('Bmax_' + surfix, 'ztitle', '$[pT/Hz^(1/2)]$')
                options('Emax_lines_' + surfix, 'ysubtitle', '$[mV/m/Hz^(1/2)]$')
            elif surfix == 'Pwr':
                options('Emax_' + surfix, 'zrange', [1e-10, 100])
                options('Bmax_' + surfix, 'zrange', [1e-8, 1e6])
                options('Emax_lines_' + surfix, 'yrange', [1e-6, 100])
                options('Emax_' + surfix, 'ztitle', '$[(mV/m)^2/Hz]$')
                options('Bmax_' + surfix, 'ztitle', '$[pT^2/Hz]$')
                options('Emax_lines_' + surfix, 'ysubtitle', '$[(mV/m)^2/Hz]$')

            
            
            options('ALT', 'ytitle', 'ALT [km]')
            options('MLT', 'ytitle', 'MLT [h]')
            options('ILAT', 'ytitle', 'ILAT [deg]')
            options(['ALT', 'MLT', 'ILAT'], 'panel_size', 0.3)
            
            omni_data_names = ['SYM_H', 'IMF', 'flow_speed', 'proton_density', 'Pressure', 'E']
            options(omni_data_names, 'panel_size', 0.5)
            options('IMF', 'legend_names', ['IMF x', "IMF y", "IMF z"])
            options('IMF', 'legend_location', 'spedas')
            options('SYM_H', 'ytitle', 'SYM-H')
            options('SYM_H', 'ysubtitle', '[nT]')
            options('flow_speed', 'ytitle', 'flow \n speed')
            options('flow_speed', 'ysubtitle', '[km/s]')
            options('proton_density', 'ytitle', 'proton \n density')
            options('Pressure', 'ytitle', 'flow \n pressure')
            options('E', 'ytitle', 'E_sw')
            options('E', 'ysubtitle', 'mV/m')
            
            tplot_options('title', Passname + hemisphere + '_' + year+Month+day+ ' MCA ' + surfix)

        
            tplot(['IMF', 'flow_speed', 'proton_density', 'Pressure', 'gyro_freq', 'Bmax_' + surfix, 'Emax_' + surfix, 'Emax_pwr_res', 'Emax_alpha', 'Emax_lines_' + surfix, 'SYM_H'], 
                  var_label = ['ALT', 'MLT', 'ILAT'], 
                  save_png = save_name,
                  xsize=26, ysize=22,
                  display=False)
            
                
    tplot_names = pytplot.tplot_names(True)
    pytplot.store_data(tplot_names, delete=True)
    print(pytplot.tplot_names())
