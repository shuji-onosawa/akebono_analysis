2018.03.26
文責　石ヶ谷侑季

Akebono/SMS, SDBデータの解析プログラム
DARTS（データ公開ページ）http://www.darts.isas.jaxa.jp/index.html.ja
Akebono/SMSのreadmeを参考に

- 基本的な読み書き
    - smsread.c
        - 読み込みプログラム修正版, 説明はファイル先頭に記載
        - コンパイルしたら”○○ yymmddhh.sms”で動作
    - smsplot.c
        - thermalデータのgnuplot用、読み込み・書き出し
        - 書き出したファイルsmsploto.txtはsmsplot.pltでDARTSのQLに近い形式でプロットされる

- ○up, perpカウント数計算
    - smsread2.c
        - thermal H+,O+の読み込み・書き出し
    - heating.c
        - thermal*.txtでup, perpのカウント数のトータルを計算し、smscup.txt, smscperp.txtに時刻 各エネルギーの合計(4) 全エネルギーの合計という形式で書き出し

2018.03.26 
文責　石ヶ谷侑季

SMSデータから導出したイオンの各種パラメータ
参考文献（導出手法）Watanabe S., B. A. Whalen, and A. W. Yau, Thermal Ion Observations of Depletion and Refilling in the Plasmaspheric Trough, J. Geophys. Res., Vol. 97, No. A2, 1081-1096, 1992.

- 山田学さん（千葉工業大学）より提供いただいたもの
    - y1990.dat  
	山田さんが導出した1990年1-4月の各種イオンのパラメータ
    - readpara.f  
	y1990.datの読み込みプログラム

- その他
    - readpara2.f  
    指定した日付のH+,O+のデータを読みこみ別のファイルに任意のデータを書き込む  
    書き出すデータは以下を参照

| Variable | Description |
| -------- | ----------- |
| c       | Comment     |
| iyymmdd | Year Month Day |
| ihhmmss | Hour Minute Second |
| dmlt    | Magnetic Local Time |
| dinv    | Invariant Latitude (deg) |
| dalt    | Altitude (km) <br> dalt > 0: Northern Hemisphere <br> dalt < 0: Southern Hemisphere |
| dmlat   | Magnetic Latitude (deg) |
| VI(3)   | Ion Velocity (km/sec) <br> Upward: Northern > 0, Southern < 0 |
| TEMP(3) | Ion Temperature (log(K)) |
| ytime   | |
|* bx      | Magnetic field in the X direction (nT) |
|* by      | Magnetic field in the Y direction (nT) |
|* bz      | Magnetic field in the Z direction (nT) |
|* stemp   | Plasma temperature (K) |
|* sden    | Ploton Density (cm^-3) |
|* ivs     | Bulk Speed (km/sec) |
|* kp      | Kp index * 10 <br> ex. 57 = 6-, 60 = 6, 63 = 6+ |
|* suns    | Sunspot Number |
|* Dst     | Dst index (Gammas) |
| dlat    | 90 - invlat |
| deg     | mlt/24*360 |
| DEN(3)  | Ion Density (log(ions/m^3)) |
| cvsa    | Satellite Potential (V) |
| cvpe    | Perpendicular Velocity (km/s) |
| ves()   | Satellite Velocity in the Satellite Coordinate (km/s) |

※ 全体が[]で囲まれている変数は他の値から導き出せる.  
(学部時代 gnuplot を使うために値を書き込んだもの.プログラムのデータ読み込みの都合でまだ残しているがそのうち他の変数を記述するかも知れない…)  
※ コメントの直後にアスタリスクが付いている変数はNSSDC からダウンロードしたデータ

