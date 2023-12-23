# wnaEstimation.pyの中で、作成したdictionary.csvを読み込んで、グラフを作成する
# プロットには、pytplotライブラリを使用する
import pandas as pd
import pytplot
from store_high_time_res_spectrum_data import store_mca_high_time_res_data
import os


def plotPeakAngle(date, startTime, endTime):
    """
    Args:
        date (str): 日付, yyyy-mm-dd
        startTime (str): 開始時刻, hh:mm:ss
        endTime (str): 終了時刻, hh:mm:ss
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
        pytplot.store_data('AngleAtPeakEpwrCh'+str(i),
                        data={'x': df['timeAtPeakEpwrCh'+str(i)],
                                'y': df['angleAtPeakEpwrCh'+str(i)]})
        pytplot.options('AngleAtPeakEpwrCh'+str(i),
                        opt_dict={'yrange': [-180, 180], 'color': 'k', 'marker': '.', 'line_style': ' ',
                        'ytitle': 'Angle (deg) @ '+freqLabel[i]+' Hz'})
        pytplot.store_data('AngleAtPeakBpwrCh'+str(i),
                        data={'x': df['timeAtPeakBpwrCh'+str(i)],
                                'y': df['angleAtPeakBpwrCh'+str(i)]})
        pytplot.options('AngleAtPeakBpwrCh'+str(i),
                        opt_dict={'yrange': [-180, 180], 'color': 'k', 'marker': '.', 'line_style': ' ',
                        'ytitle': 'Angle (deg) @ '+freqLabel[i]+' Hz'})

    store_mca_high_time_res_data(date=date, datatype='pwr', del_invalid_data=['off', 'bit rate m', 'sms', 'bdr', 'noisy'])

    # Plot the graph
    pytplot.tlimit([date+' '+startTime, date+' '+endTime])

    saveDir = '../plots/peakAngles/'+ date + '_' \
        + startTime[0:2] + startTime[3:5] + startTime[6:8] + '-' \
        + endTime[0:2] + endTime[3:5] + endTime[6:8] + '/'
    os.makedirs(saveDir, exist_ok=True)
    for i in range(16):
        pytplot.tplot(['akb_mca_Emax_pwr', 'AngleAtPeakEpwrCh'+str(i), 'akb_mca_Bmax_pwr', 'AngleAtPeakBpwrCh'+str(i)],
                    xsize=10, ysize=10, save_jpeg=saveDir+'angleAtPeakPwr'+freqLabel[i]+'Hz', display=False)