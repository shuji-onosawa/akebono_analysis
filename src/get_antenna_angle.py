import numpy as np
import math


def unit_vector(vector):
    """与えられたベクトルの単位ベクトルを計算する関数"""
    magnitude = np.linalg.norm(vector)  # ベクトルの大きさを計算
    if magnitude == 0:
        return vector  # ベクトルの大きさが0の場合はそのまま返す
    return vector / magnitude  # ベクトルを大きさで除算して単位ベクトルを計算


def angle_between_vectors(u, v):
    """与えられた二つの単位ベクトルのなす角を計算する関数"""
    dot_product = np.dot(u, v)  # 内積を計算
    angle = math.acos(np.clip(dot_product, -1.0, 1.0))  # 余弦から逆余弦を取得して角度を計算
    return np.degrees(angle)  # ラジアンから度数に変換して返す


Ey_antenna_vector = np.array([-np.sin(np.deg2rad(35)),
                              np.cos(np.deg2rad(35)),
                              0])
sBy_antenna_vector = np.array([0.0, -1.0, 0.0])
