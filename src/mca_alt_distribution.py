import load
import numpy as np
from pytplot import get_data


def count_number_occurrences(array, number, axis, start_time, end_time):
    return np.sum(array[start_time:end_time+1, :] == number, axis=axis)


matrix_count = np.zeros((16, 256))

start_date = '1989-03-06'
end_date = '1989-03-07'

load.mca(trange=[start_date, end_date], del_invalid_data=True, spec_type='dB')
load.orb(trange=[start_date, end_date])

Etvar = get_data('Emax')
for ch in range(16):
    for dB_val in range(256):
        matrix_count[ch][dB_val] = \
            count_number_occurrences(Etvar.y, dB_val, ch)
