# epoch値を入力すると、epoch値の配列から入力したepoch値と最も近いepoch値のインデックスを返す関数

import numpy as np


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx
