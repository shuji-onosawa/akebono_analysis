import numpy as np
import calc_dispersion_in_cold_plasma as calc_dr

# 入力としてのwとtheta
w = np.arange(100, 1000, 100)  # [rad/s]
theta = 30  # [deg]

# calc_dispersion_relation関数を実行
n_L, n_R, S, D, P = calc_dr.calc_dispersion_relation(w, theta)

# 結果を表示
print("w:", w)
print("Left-hand mode refractive index:", n_L)
print("Right-hand mode refractive index:", n_R)
print("S:", S)
print("D:", D)
print("P:", P)
print("RL:", S**2-D**2)
