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
