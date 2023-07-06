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
    angle_aryの中でangle_rangeの範囲にあるdata_aryの値または配列を返す
    Parameters
    ----------
    angle_ary : list or np.ndarray
        角度の時刻変化を表す1次元配列
    data_ary : list or np.ndarray
        angle_aryに対応するデータの配列
    angle_range : list
        角度の範囲
    Returns
    -------
    list
        angle_aryの中でangle_rangeの範囲にある値
    """
    # data_aryが1次元の場合、angle_aryとdata_aryの長さが一致していることを確認
    if len(data_ary.shape) == 1:
        assert len(angle_ary) == len(data_ary)
    # data_aryが2次元の場合、angle_aryとdata_aryの長さが一致していることを確認
    elif len(data_ary.shape) == 2:
        assert len(angle_ary) == data_ary.shape[0]
    angle_ary = np.array(angle_ary)
    data_ary = np.array(data_ary)
    idx = np.where((angle_ary >= angle_range[0]) & (angle_ary <= angle_range[1]))
    if len(idx[0]) == 0:
        return np.nan*np.empty(data_ary.shape)
    return data_ary[idx[0]]


# 与えられた配列の要素が負の値から正の値に変わるインデックスを取得
def find_positive_negative_pairs(input_array):
    # 入力をNumPy配列に変換
    np_array = np.array(input_array)

    # 正の数にTrue, 負の数にFalseを割り当てた配列を生成
    pos_mask = np_array > 0
    neg_mask = np_array < 0

    # pos_maskを1つシフトしてから、論理ANDをとることで、正の値の次が負の値となるインデックスを見つける
    indices = np.where(pos_mask[:-1] & neg_mask[1:])[0]

    return indices.tolist()
