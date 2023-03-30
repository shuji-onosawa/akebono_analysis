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


def calc_amp_ratio(n, S, D, P, theta):
    '''
    !!!caution!!!
    n means squared refractive index
    '''
    theta = np.deg2rad(theta)

    Ey_to_Ex = -D/(S-n)
    Ez_to_Ex = np.where(P-n*np.sin(theta)**2 != 0, -n*np.cos(theta)*np.sin(theta)/(P-n*(np.sin(theta))**2), 0)
    By_to_Bx = np.where(D*(P-n*(np.sin(theta))**2) != 0, -P*(S-n)/(D*(P-n*(np.sin(theta))**2)), 0)
    Bz_to_Bx = -np.tan(theta)*np.ones(n.size)
    squared_E_to_cB = (1-(Ey_to_Ex)**2+Ez_to_Ex**2)/(-(Ey_to_Ex)**2+(np.cos(theta)-Ez_to_Ex*np.sin(theta))**2)/n
    for i in range(n.size):
        if squared_E_to_cB[i] < 0:
            squared_E_to_cB[i] = 0
    E_to_cB = np.sqrt(squared_E_to_cB)

    return Ey_to_Ex, Ez_to_Ex, By_to_Bx, Bz_to_Bx, E_to_cB
