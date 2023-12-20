# スペクトルデータを用いたホドグラム解析による波数ベクトル推定手法
## 波数ベクトル推定手法
z軸を背景磁場$\vec B_0$の向きとする。
xz面に波数ベクトルがあるようにx軸をとる。
y軸は左手系をなすようにとる。

コールドプラズマ中のプラズマ波動の分散関係および偏波を考える。
波動電場、波動磁場は
$\begin{aligned}
\left(E_x, E_y, E_z\right) & =\left(E_x,-\frac{i D}{S-n^2} E_x,-\frac{n^2 \cos \theta \sin \theta}{P-n^2 \sin ^2 \theta} E_x\right) \\
& =Ex \vec{P_E} = \vec{E_w}\\
\vec{P}_E & = \left(1, -\frac{i D}{S-n^2}, -\frac{n^2 \cos \theta \sin \theta}{P-n^2 \sin ^2 \theta}\right)\\
E_x &= \tilde{E_0} exp(i(\vec{k} \cdot \vec{r} - \omega t))\\
\left(B_x, B_y, B_z\right) & =\left(-\frac{k \cos \theta}{\omega} E_y, \frac{k}{\omega}\left(E_x \cos \theta-E_y \sin \theta\right), \frac{k \sin \theta}{\omega} E_y\right) \\
& =\left(\frac{k \cos \theta}{\omega} \cdot \frac{i D}{S-n^2} E_x, \frac{k}{\omega}\left(E_x \cos \theta+\frac{i D}{S-n^2} E_x \sin \theta\right), \frac{k \sin \theta}{\omega} \cdot\left(-\frac{i P}{S-n^2}\right) E_x\right)\\
& = E_x\vec{P_B} = \vec{B_w}\\
\vec{P_B}& = \left(\frac{k \cos \theta}{\omega} \cdot \frac{i D}{S-n^2}, \frac{k}{\omega}\left(\cos \theta+\frac{i D}{S-n^2} \sin \theta\right), \frac{k \sin \theta}{\omega} \cdot\left(-\frac{i P}{S-n^2}\right)\right)\\
\end{aligned}$
$S, D, P$はそれぞれ、コールドプラズマの分散関係式の係数である。
$n$ はコールドプラズマの屈折率である。
$\theta$はプラズマ波動の伝搬角、$\omega$はプラズマ波動の角周波数。
$\tilde{E_0}$は実数

波動の周波数に対して、データサンプリング周波数が十分に小さい時を考える。
電場アンテナがさす方向を$\vec{a_E}$、磁場アンテナがさす方向を$\vec{a_B}$とする。
$\vec {a_E}$と$\vec B_0$がなす角が$\theta_E$のとき、MCAのスペクトルデータの値$E_{MCA}$は
$$
\begin{aligned}
E_{MCA} = max(|\vec{E_w} \cdot \vec{a_E}|)_{while \ \delta t}\\
\delta t \ is \ the \ time \ interval \ of \ MCA \ data.
\end{aligned}
$$
同様に、$\vec {a_B}$と$\vec B_0$がなす角が$\theta_B$のとき、MCAのスペクトルデータの値$B_{MCA}$は
$$
\begin{aligned}
B_{MCA} = max(|\vec{B_w} \cdot \vec{a_B}|)_{while \ \delta t}\\
\delta t \ is \ the \ time \ interval \ of \ MCA \ data.
\end{aligned}
$$

$\vec{n}$は衛星のスピン面の単位法線ベクトルであり、
$\vec{n} = (\sin \psi \cos \phi, \sin \psi \sin \phi, \cos \psi)$
である。
$\psi$はz軸からスピン軸までの角度であり、$\phi$はx軸からスピン軸のxy平面への投影までの角度である。

スピン面に投影された電場ベクトルおよび磁場ベクトルとz軸（背景磁場の向き）とのなす角 $\theta_E, \theta_B$ は
$$
\begin{aligned}
\cos \theta_E & = \frac{\vec{E_{\text {spin }(t)}}}{|\vec{E_{\text {spin }(t)}}|} \cdot \vec{e_z}\\
\cos \theta_B & = \frac{\vec{B_{\text {spin }(t)}}}{|\vec{B_{\text {spin }(t)}}|} \cdot \vec{e_z}\\
\end{aligned}
$$

スピン面に投影された電場ベクトルおよび磁場ベクトルの大きさが最大となる時刻 $t=t_{max}$での$\theta_{E}, \theta_{B}$を$\theta_{E_{max}}, \theta_{B_{max}}$とすると
$$
\begin{aligned}
\cos \theta_{E_{max}} & = \frac{\vec{E_{\text {spin }(t_{max})}}}{|\vec{E_{\text {spin }(t_{max})}}|} \cdot \vec{e_z}\\
\cos \theta_{B_{max}} & = \frac{\vec{B_{\text {spin }(t_{max})}}}{|\vec{B_{\text {spin }(t_{max})}}|} \cdot \vec{e_z}\\
\end{aligned}
$$

観測データから算出した$\theta_{E_{max}}, \theta_{B_{max}}$と、模擬観測データから算出した$\theta_{E_{max}}, \theta_{B_{max}}$を比較することで、波数ベクトルの推定を行う。

## 背景磁場とアンテナのなす角の算出方法
背景磁場$\vec{B_0}$とアンテナベクトル$\vec{a}$のなす角を$θ$とする。スピン面の法線ベクトルを$\vec{n}$とする。それぞれのベクトルは以下のように表わされる。
$$
\begin{aligned}
\vec{B_0} & = B_0 (0, 0, 1)\\
& = B_0 \vec{e_z} \\
\vec{a} & = (x_a, y_a, z_a)\\
\vec{n} & = (sin\theta_n cos\phi_n, sin\theta_n sin\phi_n, cos\theta_n)\\
\end{aligned}
$$
$\theta$は以下のように定義する。
$$
\begin{aligned}
\theta =
\begin{cases}
    arccos(\vec{a} \cdot \vec{B_0}) & if \ \ \vec{n} \cdot (\vec{e_z} \times \vec{a}) < 0 \\
    \ - arccos(\vec{a} \cdot \vec{B_0}) & if \ \ \vec{n} \cdot (\vec{e_z} \times \vec{a}) > 0 \\
\end{cases}
\end{aligned}
$$

### メモ
$$
\begin{aligned}
\vec{n} \cdot (\vec{e_z} \times \vec{a}) & = \vec{n} \cdot \vec{e_z} \times \vec{a}\\
& = \vec{n} \cdot ((0, 0, 1) \times (x_a, y_a, z_a))\\
& = (sin\theta_n cos\phi_n, sin\theta_n sin\phi_n, cos\theta_n) \cdot (-y_a, x_a, 0)\\
& = sin\theta_n (-cos\phi_n y_a + sin\phi_n x_a)\\
\end{aligned}
$$
$ 0 < \theta < \pi $ なので $\vec{n} \cdot (\vec{e_z} \times \vec{a})$ の正負は$(-cos\phi_n y_a + sin\phi_n x_a)$の正負で決まる。\
$(-cos\phi_n y_a + sin\phi_n x_a) > 0$ となる場合を考える。
$$
\begin{aligned}
-cos\phi_n y_a + sin\phi_n x_a & > 0\\
sin\phi_n x_a & > cos\phi_n y_a\\
\begin{aligned}
&[i] \ 0 < \phi_n < \frac{\pi}{2} or \frac{3\pi}{2} < \phi_n < 2\pi  \Rightarrow y_a < x_a \tan\phi_n\\
&[ii] \ \frac{\pi}{2} < \phi_n < \frac{3\pi}{2}  \Rightarrow y_a > x_a \tan\phi_n\\
\end{aligned}
\end{aligned}
$$
[i], [ii] のいずれの場合を考えても、$(-cos\phi_n y_a + sin\phi_n x_a) > 0$ となるのは、$\vec{e_z}, \vec{n}$ を含む平面より $\phi_n$ が小さい領域に $\vec{a}$ があるときである。
