import akebono
from calc_pwr_matrix_angle_vs_freq import make_wave_mgf_dataset
from plot_high_res_mca import store_angle_b0
import pytplot
from datetime import datetime, timedelta


def plot_mca_ql(startTime, endTime):
    '''
    startTime, endTime: 'YYYY-MM-DD HH:MM:SS'の形式
    '''
    date = startTime.split(' ')[0]
    nextDate = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    # load data
    # load wave data
    akebono.vlf_mca(trange=[date, nextDate], datatype='pwr',
                    del_invalid_data=['off', 'sms', 'noisy', 'bdr', 'bit rate m', 'pws'])
    # load orbit data
    akebono.orb(trange=[date, nextDate])

    # plot
    pytplot.tlimit([startTime, endTime])
    pytplot.tplot(['akb_mca_Emax_pwr', 'akb_mca_Bmax_pwr'],
                  var_label=['akb_orb_inv', 'akb_orb_mlt', 'akb_orb_alt'],
                  xsize=10, ysize=8)


def plot_mca_high_res_ql(startTime, endTime):
    '''
    startTime, endTime: 'YYYY-MM-DD HH:MM:SS'の形式
    '''
    date = startTime.split(' ')[0]
    nextDate = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    # load data
    # load wave data
    ds = make_wave_mgf_dataset(date=date, mca_datatype='pwr',
                               del_invalid_data=['off', 'sms', 'noisy', 'bdr', 'bit rate m', 'pws'])
    store_angle_b0(ds)
    # load orbit data
    akebono.orb(trange=[date, nextDate])

    # plot
    pytplot.tlimit([startTime, endTime])
    pytplot.tplot(['akb_mca_Emax_pwr', 'angle_b0_Ey', 'akb_mca_Bmax_pwr', 'angle_b0_B'],
                  var_label=['akb_orb_inv', 'akb_orb_mlt', 'akb_orb_alt'],
                  xsize=10, ysize=16)


plot_mca_ql('1990-02-17 14:00:00', '1990-02-17 14:15:00')
plot_mca_high_res_ql('1990-02-17 14:00:00', '1990-02-17 14:15:00')
