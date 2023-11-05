import cdflib
from preprocess_mgf_epoch import convert_epoch, interpolate_mgf_epoch
import xarray as xr


def checkEfiedlAntenna(date, startTime, endTime):
    '''
    日付、開始時刻、終了時刻を指定して、電場アンテナがxかyかを判別する
    date: str (yyyy-mm-dd)
    startTime: str (HH:MM:SS)
    endTime: str (HH:MM:SS)
    '''
    cdfFileName = '../akebono_data/vlf/mca/h0/ak_h0_mca_'+date[0:4]+date[5:7]+date[8:]+'_v01.cdf'
    cdf = cdflib.CDF(cdfFileName)
    eaxis = cdf.varget('E_axis')
    epoch = cdf.varget('Epoch')

    # epochのほうが長いので、eaxisに合わせる
    epoch_sub = epoch[:len(eaxis)]
    # epochが負の値の時、0で埋める
    epoch_sub[epoch_sub < 0] = 0.0
    # epoch の前処理
    epoch_sub_itrp = interpolate_mgf_epoch(epoch_sub)
    epoch_datetime = convert_epoch(epoch_sub_itrp)

    xry = xr.DataArray(data=eaxis, coords={'time': epoch_datetime}, dims=['time'])
    sub_xry = xry.sel(time=slice(date+' '+startTime, date+' '+endTime))
    return sub_xry