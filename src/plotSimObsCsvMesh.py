import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


def readSimObsCsv(file_path):
    """
    シミュレーション結果のCSVファイルを読み込む
    :param file_path: CSVファイルのパス
    :return: row_labels, column_labels, leftValMatrix, rightValMatrix
    """
    # CSVファイルを読み込む
    # 初期のデータ構造を理解するために、先頭部分のみを表示
    df = pd.read_csv(file_path)
    df.head()
    # 第1列と第1行の値を配列として読み込む
    row_labels = df.iloc[:, 0].tolist()  # 第1列
    column_labels = df.columns.tolist()[1:]  # 第1行（最初の列を除く）

    # "v"で分割された左側と右側の値を取得
    leftValMatrix = []
    rightValMatrix = []

    for i in range(len(row_labels)):
        left_row = []
        right_row = []
        for j in column_labels:
            # 現在のセルの値を取得
            cell_value = df.at[i, j]
            # NaN値の処理
            if pd.isna(cell_value):
                left_val = right_val = None
            else:
                # "v"で分割して数値を取得
                left_val, right_val = cell_value.split('v')
                left_val = float(left_val)
                right_val = float(right_val)

            left_row.append(left_val)
            right_row.append(right_val)

        leftValMatrix.append(left_row)
        rightValMatrix.append(right_row)

    return row_labels, column_labels, leftValMatrix, rightValMatrix

def plot_mesh(matrix, row_labels, col_labels, title, cmax, cmin):
    # matrix の最大値と最小値を取得
    matrix_max = np.nanmax(matrix)
    matrix_min = np.nanmin(matrix)

    fig, ax = plt.subplots()
    c = ax.pcolormesh(matrix, cmap='viridis', vmin=cmin, vmax=cmax)  # カラーマップと値の範囲を設定  # カラーマップを選択
    ax.set_title(title)

    # 縦軸と横軸の主要な目盛りを設定
    x_major_ticks = [0, 90, 180]
    y_major_ticks = [0, 90, 180, 270, 360]
    row_labels.append(360)
    ax.set_xticks(np.array([col_labels.index(str(label)) for label in x_major_ticks])+0.5)
    # col_labelsは文字列なので、indexを取得するためにstrに変換
    ax.set_yticks(np.array([row_labels.index(label) for label in y_major_ticks])+0.5)

    ax.set_xticklabels(x_major_ticks)
    ax.set_yticklabels(y_major_ticks)

    # 縦軸と横軸の副目盛りを設定
    ax.set_xticks(np.arange(len(col_labels))+0.5, minor=True)
    ax.set_yticks(np.arange(len(row_labels))+0.5, minor=True)

    # カラーバーを追加
    plt.colorbar(c, ax=ax)
    # カラーバーのz軸範囲を設定
    c.set_clim(cmin, cmax)

    # 図の保存
    saveDir = '../plots/simObsCsvMesh/'
    os.makedirs(saveDir, exist_ok=True)
    plt.savefig(saveDir + title + '.png')
    plt.close()

# 実行部分
ferqList = [3.16, 5.62, 10.0, 17.8, 31.6, 56.2, 100, 178, 316, 562, 1000,
            1780, 3160]
modeList = ['l', 'r']

mode = 'r'
freq = 3.16
csvDir = '../execute/SimulatedObservation/event1/'
csvFileName = 'pyEmax_Bmax_angle_freq-' + str(freq) + '_mode-' + mode + '.csv'
row_labels, column_labels, leftValMatrix, rightValMatrix = readSimObsCsv(csvDir + csvFileName)

cmin, cmax = 150, 160
title = 'freq-' + str(freq) + '_mode-' + mode+'_B'
plot_mesh(rightValMatrix, row_labels, column_labels, title, cmax, cmin)
cmin, cmax = 20, 60
title = 'freq-' + str(freq) + '_mode-' + mode+'_E'
plot_mesh(leftValMatrix, row_labels, column_labels, title, cmax, cmin)


