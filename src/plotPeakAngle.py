# wnaEstimation.pyの中で、作成したdictionary.csvを読み込んで、グラフを作成する
# プロットには、pytplotライブラリを使用する
import pandas as pd
import pytplot
from store_high_time_res_spectrum_data import store_mca_high_time_res_data
import os
from store_mgf_data import preprocess_mgf_angle, get_mgf_with_angle_xry
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np


def plotPeakAngle(date, startTime, endTime, fold, color='k'):
    """
    Args:
        date (str): 日付, yyyy-mm-dd
        startTime (str): 開始時刻, hh:mm:ss
        endTime (str): 終了時刻, hh:mm:ss
        fold (bool): 角度を0~180度に折り返すか否か
        color (str): マーカーの色
    """
    # constant
    freqLabel = ['3.16', '5.62', '10', '17.8',
                '31.6', '56.2', '100', '178',
                '316', '562', '1000', '1780',
                '3160', '5620', '10000', '17800']

    # Read the CSV file
    csvSaveDir = '../execute/wnaEstimation/'+ date + '_' \
        + startTime[0:2] + startTime[3:5] + startTime[6:8] + '-' \
        + endTime[0:2] + endTime[3:5] + endTime[6:8] + '/'
    df = pd.read_csv(csvSaveDir+'peakAngleObs.csv')

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
            df['angleAtPeakEpwrCh'+str(i)] = preprocess_mgf_angle(df['angleAtPeakEpwrCh'+str(i)])
            df['angleAtPeakBpwrCh'+str(i)] = preprocess_mgf_angle(df['angleAtPeakBpwrCh'+str(i)])

        pytplot.store_data('AngleAtPeakEpwrCh'+str(i),
                        data={'x': df['timeAtPeakEpwrCh'+str(i)],
                                'y': df['angleAtPeakEpwrCh'+str(i)]})
        pytplot.options('AngleAtPeakEpwrCh'+str(i),
                        opt_dict={'yrange': yrange, 'y_major_ticks': ymajor_ticks, 'y_minor_tick_interval': yminor_tick_interval,
                        'color': color, 'marker': '.', 'line_style': ' ',
                        'ytitle': f'Angle (deg) @ {freqLabel[i]} Hz'})
        pytplot.store_data('AngleAtPeakBpwrCh'+str(i),
                        data={'x': df['timeAtPeakBpwrCh'+str(i)],
                                'y': df['angleAtPeakBpwrCh'+str(i)]})
        pytplot.options('AngleAtPeakBpwrCh'+str(i),
                        opt_dict={'yrange': yrange, 'y_major_ticks': ymajor_ticks, 'y_minor_tick_interval': yminor_tick_interval,
                        'color': color, 'marker': '.', 'line_style': ' ',
                        'ytitle': f'Angle (deg) @ {freqLabel[i]} Hz'})

        pytplot.tplot_options('title', 'Angle at Peak Power (Threshold: '+str(df['thresholdPercent'].values[0])+'%)')

    store_mca_high_time_res_data(date=date, datatype='pwr', del_invalid_data=['off', 'bit rate m', 'sms', 'bdr', 'noisy'])
    pytplot.options('akb_mca_Emax_pwr', 'y_major_ticks', [1e0, 1e1, 1e2, 1e3, 1e4])
    pytplot.options('akb_mca_Bmax_pwr', 'y_major_ticks', [1e0, 1e1, 1e2, 1e3, 1e4])

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


def plotAngleHist(date, startTime, endTime):
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
    csvSaveDir = '../execute/wnaEstimation/'+ date + '_' \
        + startTime[0:2] + startTime[3:5] + startTime[6:8] + '-' \
        + endTime[0:2] + endTime[3:5] + endTime[6:8] + '/'
    df = pd.read_csv(csvSaveDir+'peakAngleObs.csv')

    # Load mgf data
    mgf_ds = get_mgf_with_angle_xry(date=date)
    mgf_ds_sel = mgf_ds.sel(Epoch=slice(date+' '+startTime, date+' '+endTime))

    # plot histogram for each frequency
    for ch in range(len(freqLabel)):
        EpeakAngle = df['angleAtPeakEpwrCh'+str(ch)]
        BpeakAngle = df['angleAtPeakBpwrCh'+str(ch)]
        EpeakAngleFolded = preprocess_mgf_angle(EpeakAngle)
        BpeakAngleFolded = preprocess_mgf_angle(BpeakAngle)

        angleB0E = mgf_ds_sel['angle_b0_Ey']
        if ch < 10:
            angleB0B = mgf_ds_sel['angle_b0_sBy']
        else:
            angleB0B = mgf_ds_sel['angle_b0_Bloop']
        angleB0EFolded = preprocess_mgf_angle(angleB0E)
        angleB0BFolded = preprocess_mgf_angle(angleB0B)

        # count
        countE, binE = np.histogram(angleB0EFolded, bins=18, range=(0, 180))
        countEpeak, binEpeak = np.histogram(EpeakAngleFolded, bins=18, range=(0, 180))
        countB, binB = np.histogram(angleB0BFolded, bins=18, range=(0, 180))
        countBpeak, binBpeak = np.histogram(BpeakAngleFolded, bins=18, range=(0, 180))

        # normalize
        # 0で割るとRuntimeWarningが出るので、0の要素を1に置き換える
        countE = np.where(countE > 0, countE, 1)
        countB = np.where(countB > 0, countB, 1)
        # 割合を計算
        countEPeakPercent = countEpeak / countE * 100
        countBPeakPercent = countBpeak / countB * 100

        # plot histogram
        # all data and peak data
        fig, ax = plt.subplots(1, 2, figsize=(8, 5))
        ax[0].hist(angleB0EFolded, bins=18, range=(0, 180), color='k', label='all data')
        ax[0].hist(EpeakAngleFolded, bins=18, range=(0, 180), color='b', label='peak angle')
        ax[0].set_title('E angle distribution @ '+freqLabel[ch]+' Hz')
        ax[0].set_xlabel('Angle (deg)')
        ax[0].set_ylabel('Counts')
        ax[0].legend()
        ax[1].hist(angleB0BFolded, bins=18, range=(0, 180), color='k', label='all data')
        ax[1].hist(BpeakAngleFolded, bins=18, range=(0, 180), color='r', label='peak angle')
        ax[1].set_title('B angle distribution @ '+freqLabel[ch]+' Hz')
        ax[1].set_xlabel('Angle (deg)')
        ax[1].set_ylabel('Counts')
        ax[1].legend()
        plt.tight_layout()
        saveDir = '../plots/peakAngles/'+ date + '_' \
        + startTime[0:2] + startTime[3:5] + startTime[6:8] + '-' \
        + endTime[0:2] + endTime[3:5] + endTime[6:8] + '/'
        os.makedirs(saveDir, exist_ok=True)
        saveName = 'count_hist_'+freqLabel[ch]+'Hz'
        plt.savefig(saveDir+saveName+'.png')
        plt.close()

        # peak data percentage
        fig, ax = plt.subplots(1, 2, figsize=(8, 5))
        ax[0].hist(binE[:-1], bins=binE, weights=countEPeakPercent)
        ax[0].set_title('E angle percentage distribution @ '+freqLabel[ch]+' Hz')
        ax[0].set_xlabel('Angle (deg)')
        ax[0].set_ylabel('Percentage (%)')

        ax[1].hist(binB[:-1], bins=binB, weights=countBPeakPercent)
        ax[1].set_title('B angle percentage distribution @ '+freqLabel[ch]+' Hz')
        ax[1].set_xlabel('Angle (deg)')
        ax[1].set_ylabel('Percentage (%)')
        plt.tight_layout()
        saveName = 'percent_hist_'+freqLabel[ch]+'Hz'
        plt.savefig(saveDir+saveName+'.png')
        plt.close()


def combineImages(imagePath1, imagePath2, outputPath, alpha=0.3):
    """
    2つの画像を読み込み、一方の画像の透明度を設定した後、他方の画像に重ねて保存する。

    :param imagePath1: 最初の画像のパス
    :param imagePath2: 二番目の画像のパス
    :param outputPath: 出力画像の保存パス
    :param alpha: 最初の画像の透明度 (0.0 - 1.0の範囲)
    """
    # 画像を読み込む
    image1 = Image.open(imagePath1).convert("RGBA")
    image2 = Image.open(imagePath2).convert("RGBA")

    # 画像のサイズを確認
    if image1.size != image2.size:
        raise ValueError("Images must be the same size")

    # 透明度を設定
    alphaValue = int(alpha * 255)
    image1.putalpha(alphaValue)

    # 画像を重ねる
    combinedImage = Image.alpha_composite(image2, image1)

    # 画像を保存
    combinedImage.save(outputPath, "PNG")
