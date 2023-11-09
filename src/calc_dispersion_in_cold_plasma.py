import numpy as np


def get_num_ion_species():
    import plasma_params as pp
    num_ion_species = sum(pp.ion_ratio != 0)
    return num_ion_species


def get_crossover_freq_idx(array, value):
    num_ion_species = get_num_ion_species()
    print(num_ion_species)
    array_ = np.copy(array)
    idx = np.empty(num_ion_species, dtype=int)
    for i in range(num_ion_species):
        idx[i] = int(np.nanargmin(np.abs(array_ - value)))
        array_[idx[i]] = np.nan

    return idx


def calc_dispersion_relation(w, theta):
    """
    w: float or array of float, rad/s
    theta: int, wave normal angle, 0 - 90 [deg]

    return: n_L, n_R, S, D, P
    """
    import plasma_params as pp

    Theta = np.deg2rad(theta)

    Xe = (pp.pi_e['value']/w)**2
    Xh = (pp.pi_h['value']/w)**2
    Xhe = (pp.pi_he['value']/w)**2
    Xo = (pp.pi_o['value']/w)**2
    Ye = pp.omega_e['value']/w
    Yh = pp.omega_h['value']/w
    Yhe = pp.omega_he['value']/w
    Yo = pp.omega_o['value']/w

    R = 1 - Xe/(1 + Ye) - Xh/(1 + Yh) - Xhe/(1 + Yhe) - Xo/(1 + Yo)
    L = 1 - Xe/(1 - Ye) - Xh/(1 - Yh) - Xhe/(1 - Yhe) - Xo/(1 - Yo)

    S = (R + L)*0.5
    D = (R - L)*0.5
    P = 1 - Xe - Xh - Xhe - Xo

    A = S*(np.sin(Theta))**2 + P*(np.cos(Theta))**2
    B = R*L*(np.sin(Theta))**2 + P*S*(1+(np.cos(Theta))**2)
    C = P*R*L
    F = np.sqrt(B**2 - 4*A*C)

    n_plus = (B + F)/(2*A)
    n_minus = (B - F)/(2*A)

    # n_plus, n_minusの負の値をnp.nanに置き換える
    n_plus = np.where(n_plus < 0, np.nan, n_plus)
    n_minus = np.where(n_minus < 0, np.nan, n_minus)

    # if w is array, n_L and n_R are array, too.
    if type(w) == np.ndarray:
        n_L = np.nan*np.arange(w.size)
        n_R = np.nan*np.arange(w.size)

        polarization_plus = - D / (S - n_plus)
        polarization_minus = - D / (S - n_minus)

        L_mode_plus_idx = np.where(polarization_plus < 0)
        L_mode_minus_idx = np.where(polarization_minus < 0)
        R_mode_plus_idx = np.where(polarization_plus > 0)
        R_mode_minus_idx = np.where(polarization_minus > 0)

        n_L[L_mode_plus_idx[0]], n_L[L_mode_minus_idx[0]] = \
            n_plus[L_mode_plus_idx[0]], n_minus[L_mode_minus_idx[0]]
        n_R[R_mode_plus_idx[0]], n_R[R_mode_minus_idx[0]] = \
            n_plus[R_mode_plus_idx[0]], n_minus[R_mode_minus_idx[0]]

        return n_L, n_R, S, D, P

    # if w is float, n_L and n_R are float, too.
    else:
        polarization_plus = - D / (S - n_plus)
        polarization_minus = - D / (S - n_minus)

        # polarization_plusとpolarization_minusがどちらもnp.nanの場合はn_Lとn_Rもnp.nanにする
        if np.isnan(polarization_plus) and np.isnan(polarization_minus):
            n_L = np.nan
            n_R = np.nan
        # polarization_plusとpolarization_minusのどちらかがnp.nanの場合はn_Lとn_Rを決める
        elif np.isnan(polarization_plus):
            if polarization_minus < 0:
                n_L = n_minus
                n_R = np.nan
            else:
                n_L = np.nan
                n_R = n_minus
        elif np.isnan(polarization_minus):
            if polarization_plus < 0:
                n_L = n_plus
                n_R = np.nan
            else:
                n_L = np.nan
                n_R = n_plus
        # polarization_plusとpolarization_minusのどちらもnp.nanでない場合はn_Lとn_Rを決める
        else:
            if polarization_plus < 0:
                n_L = n_plus
                n_R = n_minus
            else:
                n_L = n_minus
                n_R = n_plus
        return n_L, n_R, S, D, P


def calc_amp_ratio(n, S, D, P, theta):
    '''
    !!!caution!!!
    n means squared refractive index
    theta: wave normal angle, 0 - 90 (180) [deg]
    '''
    if theta == 0:
        cos = 1
        sin = 0
    elif theta == 90:
        cos = 0
        sin = 1
    else:
        cos = np.cos(np.deg2rad(theta))
        sin = np.sin(np.deg2rad(theta))

    # nがscalarの場合、ndarrayに変換する
    if type(n) is not np.ndarray:
        n = np.array([n])
    Ey_to_Ex = -D/(S-n)
    Ez_to_Ex = np.where(P-n*sin**2 != 0, -n*cos*sin/(P-n*sin**2), 0)
    By_to_Bx = np.where(D*(P-n*sin**2) != 0, -P*(S-n)/(D*(P-n*sin**2)), 0)
    Bz_to_Bx = -np.tan(np.deg2rad(theta))*np.ones(n.size)
    squared_E_to_cB = (1+Ey_to_Ex**2+Ez_to_Ex**2)/(Ey_to_Ex**2+(cos-Ez_to_Ex*sin)**2)/n
    squared_E_to_cB = np.where(squared_E_to_cB > 0, squared_E_to_cB, np.nan)
    E_to_cB = np.sqrt(squared_E_to_cB)

    return Ey_to_Ex, Ez_to_Ex, By_to_Bx, Bz_to_Bx, E_to_cB
