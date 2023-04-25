import numpy as np
import datetime


def get_idx_of_nearest_value(array, value):
    """
    arrayの中でvalueに最も近い値のindexを返す
    Parameters
    ----------
    array : list or np.ndarray
        比較する配列
    value : float
        比較する値
    Returns
    -------
    int
        arrayの中でvalueに最も近い値のindex
    """
    array = np.array(array)
    idx = np.nanargmin(np.abs(array - value))
    # if array[i] - value = array[i+1] -value, return the index of the first value
    return idx


def get_next_date(date: str = '1970-1-1'):
    """
    日付を次の日にする
    Parameters
    ----------
    date : str, optional
        日付, by default '1970-1-1'
    Returns
    -------
    str
        次の日の日付
    """
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    date += datetime.timedelta(days=1)
    return date.strftime('%Y-%m-%d')


def get_data_in_angle_range(angle_ary, data_ary, angle_range: list):
    """
    angle_aryの中でangle_rangeの範囲にあるdata_aryの値を返す
    Parameters
    ----------
    angle_ary : np.ndarray
        角度の配列
    data_ary : np.ndarray
        角度に対応する値の配列
    angle_range : list
        角度の範囲
    Returns
    -------
    np.ndarray
        angle_aryの中でangle_rangeの範囲にあるdata_aryの値
    """
    return data_ary[np.logical_and(angle_ary >= angle_range[0], angle_ary < angle_range[1])]
