# Takes an array of type np.float64 containing 0 as input and returns a linear interpolation of the position of 0. The length of the array shall be the same as the length of the input array.
# The function is used to interpolate the MGF values of the epochs in the time series.
# This function can also be applied to
# Two or more zeros in a row.
# The first value in the array is 0.
# Multiple zeros in a row starting from the first value in the array
# When the last value in the array is 0
# The last zero in the array is also a zero.

import numpy as np


def interpolate_mgf_epoch(mgf_array):
    # Find the indices of the zeros in the array
    zero_index = np.where(mgf_array == 0)[0]
    # If there are no zeros in the array, return the array
    if len(zero_index) == 0:
        return mgf_array
    # Find the indices of the non-zeros in the array
    non_zero_index = np.where(mgf_array != 0)[0]
    # Find the index whose difference from its neighbor is 1
    non_zero_in_a_row_index = np.where(np.diff(non_zero_index) == 1)[0]
    # get time delta
    time_delta = mgf_array[non_zero_index[non_zero_in_a_row_index[0]+1]] - mgf_array[non_zero_index[non_zero_in_a_row_index[0]]]
    # If there is only one zero in the array, interpolate the value
    if len(zero_index) == 1:
        mgf_array[zero_index[0]] = mgf_array[zero_index[0]-1] + time_delta
        return mgf_array
    # If there are two or more zeros in the array, interpolate the values
    else:
        # If the first value in the array is 0, interpolate the first value
        if zero_index[0] == 0:
            mgf_array[0] = mgf_array[non_zero_index[0]] - time_delta*non_zero_index[0]
        # IF the last value in the array is 0, interpolate the last value
        if zero_index[-1] == len(mgf_array) - 1:
            mgf_array[-1] = mgf_array[non_zero_index[-1]] + time_delta*(len(mgf_array) - non_zero_index[-1] - 1)
        # get the indices of the zeros in the array
        zero_index = np.where(mgf_array == 0)[0]
        # interpolate the values
        for i in range(len(zero_index) - 1):
            # If the zeros are in a row, interpolate the values
            if zero_index[i+1] - zero_index[i] == 1:
                mgf_array[zero_index[i]] = mgf_array[zero_index[i]-1] + time_delta
            # If the zeros are not in a row, interpolate the values
            if zero_index[i+1] - zero_index[i] != 1:
                mgf_array[zero_index[i]] = mgf_array[zero_index[i]-1] + time_delta
                mgf_array[zero_index[i+1]] = mgf_array[zero_index[i+1]-1] + time_delta

            if i == len(zero_index) - 2:
                mgf_array[zero_index[i+1]] = mgf_array[zero_index[i+1]-1] + time_delta
        return mgf_array
