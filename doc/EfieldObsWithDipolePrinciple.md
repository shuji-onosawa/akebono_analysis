ダイポールアンテナによる電界観測の原理

## 設定
背景磁場の向きをz軸方向とする。
電場は磁力線垂直方向（x軸）に存在するとし、そのポテンシャルは以下のように書けるとする。
$$
\phi(x, t) = \phi_0 \cos(kx - \omega t) \\
k: 波数 \\
\omega: 角周波数
$$
衛星の座標は以下のようにかけるとする。
$$
x(t) = V_{sc} t \\
V_{sc}: 衛星の速度
$$
ダイポールアンテナの長さは$L$とする。衛星はスピンしており、アンテナはxz平面上を角速度$\omega_{spin}$で回転しているとする。
このとき、アンテナの位置は以下のようにかける。
$$
x_1(t) = V_{sc} t - \frac{L}{2} \cos(\omega_{spin} t) \\
x_2(t) = V_{sc} t + \frac{L}{2} \cos(\omega_{spin} t)
$$

## 電場の観測
ある時刻における、アンテナの両端でのポテンシャルは以下のようになる。
$$
\phi_1(t) = \phi_0 \cos(kx_1 - \omega t) \\
\phi_2(t) = \phi_0 \cos(kx_2 - \omega t)
$$
衛星で観測される電位差は以下のようになる。
$$
\begin{align*}
\Delta \phi(t) &= \phi_1(t) - \phi_2(t) = \phi_0 \cos(kx_1 - \omega t) - \phi_0 \cos(kx_2 - \omega t) \\
&= \phi_0 \left( \cos(kx_1 - \omega t) - \cos(kx_2 - \omega t) \right) \\
&= \phi_0 \left( \cos(k(V_{sc} t - \frac{L}{2} \cos(\omega_{spin} t)) - \omega t) - \cos(k(V_{sc} t + \frac{L}{2} \cos(\omega_{spin} t)) - \omega t) \right) \\
&= \phi_0 \left( \cos(kV_{sc} t - \frac{L}{2} k \cos(\omega_{spin} t) - \omega t) - \cos(kV_{sc} t + \frac{L}{2} k \cos(\omega_{spin} t) - \omega t) \right) \\
&= \phi_0 \left( \cos(kV_{sc} t - \omega t) \cos(\frac{L}{2} k \cos(\omega_{spin} t)) + \sin(kV_{sc} t - \omega t) \sin(\frac{L}{2} k \cos(\omega_{spin} t)) - \cos(kV_{sc} t - \omega t) \cos(\frac{L}{2} k \cos(\omega_{spin} t)) + \sin(kV_{sc} t - \omega t) \sin(\frac{L}{2} k \cos(\omega_{spin} t)) \right) \\
&= 2 \phi_0 \sin(kV_{sc} t - \omega t) \sin(\frac{L}{2} k \cos(\omega_{spin} t))
\end{align*}
$$
電場はポテンシャルの勾配であるが、観測値としては以下のようになる。
$$
\begin{align*}
E(t) &= - \frac{\Delta \phi(t)}{L} \\
&= - \frac{2 \phi_0 \sin(kV_{sc} t - \omega t) \sin(\frac{L}{2} k \cos(\omega_{spin} t))}{L}
\end{align*}
$$
