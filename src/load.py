from pyspedas.utilities.dailynames import dailynames
from pyspedas import time_double
from pytplot import cdf_to_tplot, store_data, get_data, options

import os
import urllib.request
import numpy as np
import time
from calendar import timegm
from datetime import datetime, timedelta


# mca
def mca(trange=['2014-01-01', '2014-01-02'],
        downloadonly=False,
        spec_type='pwr',
        del_invalid_data=['off']):

    '''
    spec_type: dB :
        decibel, 0[dB]=10^-6[mV/m] for E-field and 0[dB] = 10^-6[pT] for B-field
    amp: mV/m/Hz^1/2 or nT/Hz^1/2
    pwr: (mV/m)^2/Hz or nT^2/Hz
    del_invalid_data:
        list of string.
        mca cdf contain data from which the interference by BDR or SMS is *not* yet removed.
        You can remove data contaminated by interference by passing a list containing the following words. 
        off: mca is off
        noisy: data is noisy
        sms: SMS on
        bdr: BDR on
        bit rate m: Bit rate is medium
        pws: PWS sounder on

    explanation of VLF/MCA data is here(https://www.stp.isas.jaxa.jp/akebono/readme/readme.vlf.txt).
    '''
    remote_name_prefix = 'https://akebono-vlf.db.kanazawa-u.ac.jp/permalink.php?keyword='
    pathformat = 'https://akebono-vlf.db.kanazawa-u.ac.jp/permalink.php?keyword=ak_h1_mca_%Y%m%d_v02.cdf'

    remote_names = dailynames(file_format=pathformat, trange=trange)

    out_files = []

    pathname = './Akebono_MCA_data/'

    try:
        os.mkdir(pathname)
    except Exception as e:
        print(e)
        pass

    for remote_name in remote_names:

        save_name = pathname + remote_name
        save_name = save_name.replace(remote_name_prefix, '')

        if (os.path.isfile(save_name) == False):

            data = urllib.request.urlopen(remote_name).read()

            with open(save_name, mode="wb") as f:
                f.write(data)

        out_files.append(save_name)

    if downloadonly:
        return

    out_files = sorted(out_files)

    try:
        cdf_to_tplot(out_files)
    except Exception as e:
        print('///////////////////////////ERROR/////////////////////////')
        print("You cannot get cdf file of mca or you can not open orbit file \n")
        print(e)
        os.remove(save_name)
        return
    '''
    if time_clip:
        for new_var in tvars:
            tclip(new_var, trange[0], trange[1], suffix='')
    '''

    if not del_invalid_data:
        pass
    else:
        Emax, Bmax, Eave, Bave = get_data('Emax'), get_data('Bmax'), get_data('Eave'), get_data('Bave')
        Emax_array, Bmax_array, Eave_array, Bave_array = Emax.y.astype(float), Bmax.y.astype(float), Eave.y.astype(float), Bave.y.astype(float)
        postgap_array = get_inst_flag_array()
        postgap_array = postgap_array.T

        invalid_data_index = np.array([])
        for inst_name in del_invalid_data:
            inst_name = inst_name.lower()
            if inst_name in ['off', 'noisy', 'bdr', 'sms', 'bit rate m', 'pws']:
                pass
            else:
                raise Exception('del_invalid_data list must consist of either off, noisy, bdr, sms, bit rate m or pws')

            if inst_name == 'off':
                off_index_tuple = np.where(postgap_array[0] == 1)
                invalid_data_index = np.append(invalid_data_index, off_index_tuple[0])
            if inst_name == 'noisy':
                noisy_index_tuple = np.where(postgap_array[1] == 1)
                invalid_data_index = np.append(invalid_data_index, noisy_index_tuple[0])
            if inst_name == 'bdr':
                bdr_index_tuple = np.where(postgap_array[2] == 1)
                invalid_data_index = np.append(invalid_data_index, bdr_index_tuple[0])
            if inst_name == 'sms':
                sms_index_tuple = np.where(postgap_array[3] == 1)
                invalid_data_index = np.append(invalid_data_index, sms_index_tuple[0])
            if inst_name == 'bit rate m':
                bitrate_index_tuple = np.where(postgap_array[4] == 1)
                invalid_data_index = np.append(invalid_data_index, bitrate_index_tuple[0])
            if inst_name == 'pws':
                pws_index_tuple = np.where(postgap_array[5] == 1)
                invalid_data_index = np.append(invalid_data_index, pws_index_tuple[0])
            
        invalid_data_index = invalid_data_index.astype(int)
        
        Emax_array[invalid_data_index] = np.nan
        Bmax_array[invalid_data_index] = np.nan
        Eave_array[invalid_data_index] = np.nan
        Bave_array[invalid_data_index] = np.nan

        store_data('Emax', data={'x':Emax.times, 'y':Emax_array, 'v':Emax.v})
        store_data('Bmax', data={'x':Bmax.times, 'y':Bmax_array, 'v':Bmax.v})
        store_data('Eave', data={'x':Eave.times, 'y':Eave_array, 'v':Eave.v})
        store_data('Bave', data={'x':Bave.times, 'y':Bave_array, 'v':Bave.v})

    if spec_type == 'dB':
        return
    else:
        mca_h1cdf_dB_to_absolute(spec_type)
    return


# orbit
def orb(trange=['2013-01-01', '2013-01-02'],
        downloadonly=False):

    pathformat = 'https://darts.isas.jaxa.jp/stp/data/exosd/orbit/daily/%Y%m/ED%y%m%d.txt'
    remote_names = dailynames(file_format=pathformat, trange=trange)

    out_files = []

    pathname = './Akebono_orb_data/'

    try:
        os.mkdir(pathname)
    except Exception as e:
        print(e)
        pass

    for remote_name in remote_names:
    # remote_name = 'https://darts.isas.jaxa.jp/stp/data/exosd/orbit/daily/%Y%m/ED%y%m%d.txt'

        save_name = pathname + remote_name[-12:]

        if (os.path.isfile(save_name) == False):
            
            try:
                get_data = urllib.request.urlopen(remote_name).read()
            except Exception as e:
                print('///////////////////////////ERROR/////////////////////////')
                print("You can not get orbit file or you can not open orbit file \n")
                print(e)
                continue
            
            with open(save_name, mode="wb") as f:
                f.write(get_data)
        
        out_files.append(save_name)
    # save_name = './Akebono_orb_data/ED%y%m%d.txt'

    if downloadonly:
        return 
    
    out_files = sorted(out_files)
    # out_files = list of './Akebono_orb_data/ED%y%m%d.txt'
    
    Pass = []
    UT_time_double = []
    ILAT = []
    MLAT = []
    MLT = []
    ALT = []
    Bmdl_X = []
    Bmdl_Y = []
    Bmdl_Z = []
    sc_vel_x = []
    sc_vel_y = []
    sc_vel_z = []

    for out_file in out_files:
        datalines = []
        with open(out_file) as f:
            datalines = f.readlines()
            for i in range(len(datalines)):
                datalines[i] = datalines[i].split()

        del datalines[0]
        
        data_array = np.array(datalines, dtype=str).T
        
        #decide %Y from %y in file name, 'ED%y%m%d.txt'

        UT = data_array[1].tolist()
        
        year_suffix = UT[0][:2]
        
        if int(year_suffix) < 16:
            year = '20' + year_suffix
        else:
            year = '19' + year_suffix
            
        for time_index in range(len(UT)):
            Time = UT[time_index]
            month, day, hour, minute, second = Time[2:4], Time[4:6], Time[6:8], Time[8:10], Time[10:12]
            time_string = year + '/' + month + '/' + day + '/' + hour + ':' + minute + ':' + second

            utc_time_tuple = time.strptime(time_string, "%Y/%m/%d/%H:%M:%S")
            dt = datetime(1970, 1, 1) + timedelta(seconds=timegm(utc_time_tuple))
            time_string = dt.strftime("%Y/%m/%d/%H:%M:%S")
            #yyyymmdd.orb has UT data in the format of 'yymmddhhmmss'.
            #To use pyspedas.time_double, change format from 'yymmddhhmmss' to 'yyyy/mm/dd/hh:mm:ss'
            time_time_double = time_double(time_string)
            UT_time_double.append(time_time_double)
        Pass = Pass + data_array[0].tolist()
        ILAT = ILAT + data_array[20].tolist()
        MLAT = MLAT + data_array[22].tolist()
        MLT = MLT + data_array[23].tolist()
        ALT = ALT + data_array[29].tolist()
        Bmdl_X = Bmdl_X + data_array[24].tolist()
        Bmdl_Y = Bmdl_Y + data_array[25].tolist()
        Bmdl_Z = Bmdl_Z + data_array[26].tolist()
        sc_vel_x = sc_vel_x + data_array[-3].tolist()
        sc_vel_y = sc_vel_y + data_array[-2].tolist()
        sc_vel_z = sc_vel_z + data_array[-1].tolist()

    Pass = [float(n) for n in Pass]
    ILAT = [float(n) for n in ILAT]
    MLAT = [float(n) for n in MLAT]
    MLT = [float(n) for n in MLT]
    ALT = [float(n) for n in ALT]

    Bmdl_X = [float(n) for n in Bmdl_X]
    Bmdl_Y = [float(n) for n in Bmdl_Y]
    Bmdl_Z = [float(n) for n in Bmdl_Z]
    sc_vel_x = [float(n) for n in sc_vel_x]
    sc_vel_y = [float(n) for n in sc_vel_y]
    sc_vel_z = [float(n) for n in sc_vel_z]

    '''
    datalist_header
    'PASS',
    'UT',
    'ksc_azm(deg)', 'ksc_elv(deg)', 'ksc_dis(km)', 'ksc_ang(deg)',
    'syo_azm(deg)', 'syo_elv(deg)', 'syo_dis(km)', 'syo_ang(deg)',
    'pra_azm(deg)', 'pra_elv(deg)', 'pra_dis(km)', 'pra_ang(deg)',
    'esr_azm(deg)', 'esr_elv(deg)', 'esr_dis(km)', 'esr_ang(deg)',
    'GCLAT(deg)', 'GCLON(deg)',
    'INV(deg)',
    'FMLAT(deg)',
    'MLAT(deg)',
    'MLT(h)',
    'Bmdl_X', 'Bmdl_Y', 'Bmdl_Z', :X, Y, AND Z COMPONENTS OF THE IGRF 2005 MAGNETIC FIELD (nT)
    'GCLON_S/C(deg)', 'GCLAT_S/C(deg)',
    'ALT(km)',
    'LSUN',
    's_Direc_x','s_Direc_y', 's_Direc_z',
    's/c_pos_x', 's/c_pos_y', 's/c_pos_z',
    's/c_vel(km/s)_x', 's/c_vel(km/s)_y','s/c_vel(km/s)_z' ]
header information (https://github.com/spedas-j/member_contrib/blob/master/akb_lib/Akebono_orbit_Header.txt)
    '''
    if int((time_double(trange[1])-time_double(trange[0]))/30) > len(UT_time_double):
        start_to_end_time_double = np.arange(time_double(trange[0]), time_double(trange[1]), 30)
        Pass_array = ILAT_array = MLAT_array = MLT_array = ALT_array = Bmdl_X_array = Bmdl_Y_array = Bmdl_Z_array = sc_vel_x_array = sc_vel_y_array = sc_vel_z_array =\
        np.empty(start_to_end_time_double.size)*np.nan

        for i in range(len(UT_time_double)):
            time_index = np.where(start_to_end_time_double == UT_time_double[i])
            Pass_array[time_index] = Pass[i]
            ILAT_array[time_index] = ILAT[i]
            MLAT_array[time_index] = MLAT[i]
            MLT_array[time_index] = MLT[i]
            ALT_array[time_index] = ALT[i]
            Bmdl_X_array[time_index] = Bmdl_X[i]
            Bmdl_Y_array[time_index] = Bmdl_Y[i]
            Bmdl_Z_array[time_index] = Bmdl_Z[i]
            sc_vel_x_array[time_index] = sc_vel_x[i]
            sc_vel_y_array[time_index] = sc_vel_y[i]
            sc_vel_z_array[time_index] = sc_vel_z[i]

        UT_time_double = start_to_end_time_double
        Pass = Pass_array
        ILAT = ILAT_array
        MLAT = MLAT_array
        MLT = MLT_array
        ALT = ALT_array
        Bmdl_X = Bmdl_X_array
        Bmdl_Y = Bmdl_Y_array
        Bmdl_Z = Bmdl_Z_array
        sc_vel_x = sc_vel_x_array
        sc_vel_y = sc_vel_y_array
        sc_vel_z = sc_vel_z_array

    prefix = 'akb_'
    store_data(prefix+'Pass', data={'x': UT_time_double, 'y': Pass})
    store_data(prefix+'ILAT', data={'x': UT_time_double, 'y': ILAT})
    store_data(prefix+'MLAT', data={'x': UT_time_double, 'y': MLAT})
    store_data(prefix+'MLT', data={'x': UT_time_double, 'y': MLT})
    store_data(prefix+'ALT', data={'x': UT_time_double, 'y': ALT})
    store_data(prefix+'Bmdl_X', data={'x': UT_time_double, 'y': Bmdl_X})
    store_data(prefix+'Bmdl_Y', data={'x': UT_time_double, 'y': Bmdl_Y})
    store_data(prefix+'Bmdl_Z', data={'x': UT_time_double, 'y': Bmdl_Z})
    store_data(prefix+'sc_vel_x', data={'x': UT_time_double, 'y':sc_vel_x})
    store_data(prefix+'sc_vel_y', data={'x': UT_time_double, 'y':sc_vel_y})
    store_data(prefix+'sc_vel_z', data={'x': UT_time_double, 'y':sc_vel_z})
    store_data(prefix+'sc_vel', data={'x':UT_time_double, 'y':np.sqrt(np.array(sc_vel_x)**2+np.array(sc_vel_y)**2+np.array(sc_vel_z)**2)})

    return


def dB_to_absolute(dB_value, reference_value):
    return reference_value * 10**(dB_value/10)


def mca_h1cdf_dB_to_absolute(spec_type: str):
    if spec_type == 'pwr':
        tvar_names = ['Emax', 'Eave', 'Bmax', 'Bave']
        for i in range(4):
            tvar = get_data(tvar_names[i])
            tvar_pwr = dB_to_absolute((tvar.y).astype(float), 1e-12)
            # (mV/m)^2/Hz or pT^2/Hz
            store_data(tvar_names[i] + '_pwr',
                       data={'x': tvar.times, 'y': tvar_pwr, 'v': tvar.v})
            if tvar_names[i] == 'Emax' or tvar_names[i] == 'Eave':
                opt_dict = {'spec': 1, 'ylog': 1, 'zlog': 1,
                            'yrange': [1, 2e4], 'ysubtitle': 'freq [Hz]',
                            'zrange': [1e-10, 1e2], 'ztitle': '$[(mV/m)^2/Hz]$'}
                options(tvar_names[i] + '_pwr', opt_dict=opt_dict)
            if tvar_names[i] == 'Bmax' or tvar_names[i] == 'Bave':
                opt_dict = {'spec': 1, 'ylog': 1, 'zlog': 1,
                            'yrange': [1, 2e4], 'ysubtitle': 'freq [Hz]',
                            'zrange': [1e-8, 1e6], 'ztitle': '$[pT^2/Hz]$'}
                options(tvar_names[i] + '_pwr', opt_dict=opt_dict)

    if spec_type == 'amp':
        tvar_names = ['Emax', 'Eave', 'Bmax', 'Bave']
        for i in range(4):
            tvar = get_data(tvar_names[i])
            tvar_pwr = dB_to_absolute((tvar.y).astype(float), 1e-12)
            tvar_amp = np.sqrt(tvar_pwr)
            # mV/m/Hz^0.5 or pT/Hz^0.5
            store_data(tvar_names[i] + '_amp',
                       data={'x': tvar.times, 'y': tvar_amp, 'v': tvar.v})
            if tvar_names[i] == 'Emax' or tvar_names[i] == 'Eave':
                opt_dict = {'spec': 1, 'ylog': 1, 'zlog': 1,
                            'yrange': [1, 2e4], 'ysubtitle': 'freq [Hz]',
                            'zrange': [1e-4, 10], 'ztitle': '$[mV/m/Hz^{0.5}]$'}
                options(tvar_names[i] + '_amp', opt_dict=opt_dict)
            if tvar_names[i] == 'Bmax' or tvar_names[i] == 'Bave':
                opt_dict = {'spec': 1, 'ylog': 1, 'zlog': 1,
                            'yrange': [1, 2e4], 'ysubtitle': 'freq [Hz]',
                            'zrange': [1e-4, 1e3], 'ztitle': '$[pT/Hz^{0.5}]$'}
                options(tvar_names[i] + '_amp', opt_dict=opt_dict)

def get_inst_flag_array():
    postgap = get_data('PostGap')
    postgap_array = np.empty([postgap.y.size, 6])
    for i in range(postgap.y.size):
        postgap_str = format(postgap.y[i], '08b')
        # "off"               "noisy",             "BDR",               "SMS",               "Bit rate",          "PWS",
        postgap_array[i][0], postgap_array[i][1], postgap_array[i][2], postgap_array[i][3], postgap_array[i][4], postgap_array[i][5] = \
        int(postgap_str[7]), int(postgap_str[6]), int(postgap_str[3]), int(postgap_str[2]), int(postgap_str[1]), int(postgap_str[0])
    return postgap_array

def calc_B0():
    Bx = get_data('akb_Bmdl_X')
    By = get_data('akb_Bmdl_Y')
    Bz = get_data('akb_Bmdl_Z')

    store_data(name='total_Bmdl',
               data={'x': Bx.times, 'y': np.sqrt(Bx.y**2+By.y**2+Bz.y**2)})
    options(name='B0',
            opt_dict={'ytitle': 'B0', 'ysubtitle': '[nT]'})
    return