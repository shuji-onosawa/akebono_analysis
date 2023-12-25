# wnaEstimation.pyの中で、作成したdictionary.csvを読み込んで、グラフを作成する
# プロットには、pytplotライブラリを使用する
import pandas as pd
import pytplot
from store_high_time_res_spectrum_data import store_mca_high_time_res_data
import os
from store_mgf_data import preprocess_mgf_angle


def plotPeakAngle(date, startTime, endTime, fold, color='k'):
    """
    Args:
        date (str): 日付, yyyy-mm-dd
        startTime (str): 開始時刻, hh:mm:ss
        endTime (str): 終了時刻, hh:mm:ss
        fold (bool): 角度を0~180度に折り返すか否か
    """
    # constant
    freqLabel = ['3.16', '5.62', '10', '17.8',
                '31.6', '56.2', '100', '178',
                '316', '562', '1000', '1780',
                '3160', '5620', '10000', '17800']

    # Read the CSV file
    df = pd.read_csv('../execute/wnaEstimation/peakAngleObs.csv')

    # Convert 'timeAtPeak*pwrCh*' to datetime
    for i in range(16):
        df['timeAtPeakEpwrCh'+str(i)] = pd.to_datetime(df['timeAtPeakEpwrCh'+str(i)])
        df['timeAtPeakBpwrCh'+str(i)] = pd.to_datetime(df['timeAtPeakBpwrCh'+str(i)])

    # store data
    for i in range(16):
        yrange = [-180, 180]
        ymajor_ticks = [-180, -90, 0, 90, 180]
        yminor_tick_interval = 10
        if fold:
            yrange = [0, 180]
            ymajor_ticks = [0, 90, 180]
            yminor_tick_interval = 10
            df['angleAtPeakEpwrCh'+str(i)] = preprocess_mgf_angle(df['angleAtPeakEpwrCh'+str(i)])
            df['angleAtPeakBpwrCh'+str(i)] = preprocess_mgf_angle(df['angleAtPeakBpwrCh'+str(i)])

        pytplot.store_data('AngleAtPeakEpwrCh'+str(i),
                        data={'x': df['timeAtPeakEpwrCh'+str(i)],
                                'y': df['angleAtPeakEpwrCh'+str(i)]})
        pytplot.options('AngleAtPeakEpwrCh'+str(i),
                        opt_dict={'yrange': yrange, 'ymajor_ticks': ymajor_ticks, 'yminor_tick_interval': yminor_tick_interval,
                        'color': color, 'marker': '.', 'line_style': ' ',
                        'ytitle': f'Angle (deg) @ {freqLabel[i]} Hz'})
        pytplot.store_data('AngleAtPeakBpwrCh'+str(i),
                        data={'x': df['timeAtPeakBpwrCh'+str(i)],
                                'y': df['angleAtPeakBpwrCh'+str(i)]})
        pytplot.options('AngleAtPeakBpwrCh'+str(i),
                        opt_dict={'yrange': yrange, 'ymajor_ticks': ymajor_ticks, 'yminor_tick_interval': yminor_tick_interval,
                        'color': color, 'marker': '.', 'line_style': ' ',
                        'ytitle': f'Angle (deg) @ {freqLabel[i]} Hz'})

        pytplot.tplot_options('title', 'Angle at Peak Power (Threshold: '+str(df['thresholdPercent'].values[0])+'%)')

    store_mca_high_time_res_data(date=date, datatype='pwr', del_invalid_data=['off', 'bit rate m', 'sms', 'bdr', 'noisy'])

    # Plot the graph
    pytplot.tlimit([date+' '+startTime, date+' '+endTime])

    saveDir = '../plots/peakAngles/'+ date + '_' \
        + startTime[0:2] + startTime[3:5] + startTime[6:8] + '-' \
        + endTime[0:2] + endTime[3:5] + endTime[6:8] + '/'
    os.makedirs(saveDir, exist_ok=True)
    for i in range(16):
        saveName = 'angleAtPeakPwr'+freqLabel[i]+'Hz_'+'threshold'+str(df['thresholdPercent'].values[0])
        if fold:
            saveName += 'folded'
        pytplot.tplot(['akb_mca_Emax_pwr', 'AngleAtPeakEpwrCh'+str(i), 'akb_mca_Bmax_pwr', 'AngleAtPeakBpwrCh'+str(i)],
                    xsize=12, ysize=10,
                    save_jpeg=saveDir+saveName,
                    display=False)
