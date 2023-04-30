import math


def calc_angle_btwn_vectors(a, b):
    """
    与えられた二つのベクトルのなす角を計算する関数
    Parameters
    ----------
    a : numpy.ndarray
        ベクトル
    b : numpy.ndarray
        ベクトル
    Returns
    -------
    float
        二つの単位ベクトルのなす角
    """
    dot_product = a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
    magnitude_a = math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
    magnitude_b = math.sqrt(b[0]**2 + b[1]**2 + b[2]**2)
    angle_radians = math.acos(dot_product / (magnitude_a * magnitude_b))
    angle_degrees = math.degrees(angle_radians)

    if dot_product < 0:
        angle_degrees = -angle_degrees

    return angle_degrees
