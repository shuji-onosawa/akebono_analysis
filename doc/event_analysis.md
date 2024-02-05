# イベント解析の流れ
## イベントセレクション
- MLT: 10-14 hr
- ILAT: 65-80 deg #石ケ谷修論のイベント選択条件
  - Zhou+2000だとequatorward edge は68 deg, poleward edge は85 degくらいまである
## データプロット
- event_analysis.py
   - ダイナミックスペクトル&アンテナとB0の角度のプロット
   - 角度vsMCA強度のプロット
     - 平均値+-標準偏差をプロット
   - 各周波数でMCA強度のラインプロット
     - 1 hr 移動平均と移動標準偏差の2倍と併せてプロット
     - 移動平均より大きいかを目視で確認
   - 電場アンテナをテキストに書き出し、xかyかを確認
   - モデルの平均磁場強度を計算 -> 分散関係計算に使用
## 偏波面計算 (kvectorEstimation.md)
- plot_projected_polarization_plane.py
  - モデルの平均磁場強度を使用
  - 電子密度は"https://www.darts.isas.jaxa.jp/stp/data/exosd/pws/NE/" から取得
    - 石ケ谷修論のイベント中で最も早い時刻のデータを使用
  - イオン組成比はy1990.datファイル中の組成比を使用
    - 電子密度を使用する時刻に一番近い時刻の組成比を使用？
