# epoch値を入力すると、epoch値の配列から入力したepoch値と最も近いepoch値のインデックスを返す関数

import numpy as np


def get_idx_of_nearest_value(array, value):
    array = np.array(array)
    idx = np.nanargmin(np.abs(array - value))
    # if array[i] - value = array[i+1] -value, return the index of the first value
    return idx
