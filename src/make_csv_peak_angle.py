import numpy as np
from calc_dispersion_in_cold_plasma import calc_dispersion_relation, calc_amp_ratio
import csv


def get_peak_angle(theta, phi, wna, freq, mode):
    """
    theta: angle between spin plane normal vector and z axis
    phi: angle between projection vector of spin plane normal vector
    on x-y plane and x axis
    wna: wave normal angle
    freq: wave frequency [Hz]
    mode: 'l' or 'r'
    """
    theta_rad = np.deg2rad(theta)
    phi_rad = np.deg2rad(phi)

    spin_plane_normal_vec = np.array([np.sin(theta_rad)*np.cos(phi_rad),
                                      np.sin(theta_rad)*np.sin(phi_rad),
                                      np.cos(theta_rad)])
    spin_plane_unit_vec1 = np.array([np.cos(theta_rad)*np.cos(phi_rad),
                                    np.cos(theta_rad)*np.sin(phi_rad),
                                    -np.sin(theta_rad)])
    spin_plane_unit_vec2 = np.cross(spin_plane_normal_vec, spin_plane_unit_vec1)

    phase = np.linspace(0, 2*np.pi, 1000)

    antenna_vec = np.array([np.cos(phase)*spin_plane_unit_vec1[0] + np.sin(phase)*spin_plane_unit_vec2[0],
                            np.cos(phase)*spin_plane_unit_vec1[1] + np.sin(phase)*spin_plane_unit_vec2[1],
                            np.cos(phase)*spin_plane_unit_vec1[2] + np.sin(phase)*spin_plane_unit_vec2[2]])

    # wave polarization plane
    wna = wna
    freq = freq  # Hz
    angle_freq = 2*np.pi*freq

    n_L, n_R, S, D, P = calc_dispersion_relation(angle_freq, wna)
    if mode == 'l':
        # left hand circular polarization
        Ey_Ex, Ez_Ex, By_Bx, Bz_Bx, E_cB = calc_amp_ratio(n_L, S, D, P, wna)
    elif mode == 'r':
        # right hand circular polarization
        Ey_Ex, Ez_Ex, By_Bx, Bz_Bx, E_cB = calc_amp_ratio(n_R, S, D, P, wna)

    Evec = np.array([np.cos(phase), -Ey_Ex*np.sin(phase), Ez_Ex*np.cos(phase)]).T
    Bvec = np.array([np.cos(phase), -By_Bx*np.sin(phase), Bz_Bx*np.cos(phase)]).T
    # calc projection of E field on spin plane
    EvecProjVec = np.zeros((len(phase), 3))
    for i in range(len(phase)):
        EvecDotAntenna = np.dot(antenna_vec[:, i], Evec)
        EvecProjVec[i] = np.nanmax(EvecDotAntenna)*antenna_vec[:, i]
    # calc projection of B field on spin plane
    BvecProjVec = np.zeros((len(phase), 3))
    for i in range(len(phase)):
        BvecDotAntenna = np.dot(antenna_vec[:, i], Bvec)
        BvecProjVec[i] = np.nanmax(BvecDotAntenna)*antenna_vec[:, i]
    # angle between z axis and field vectors
    # calc angle between z axis and E field vectors
    normarized_Evec_proj_vec = Evec_proj_vec/np.linalg.norm(Evec_proj_vec, axis=1).reshape(-1, 1)
    angle_E_b0 = np.arccos(np.dot(normarized_Evec_proj_vec, np.array([0, 0, 1]).reshape(3, 1)))
    for i in range(len(angle_E_b0)):
        if np.dot(normarized_Evec_proj_vec[i], spin_plane_unit_vec2) < 0:
            angle_E_b0[i] = -angle_E_b0[i]
    # calc angle between z axis and B field vectors
    normarized_Bvec_proj_vec = Bvec_proj_vec/np.linalg.norm(Bvec_proj_vec, axis=1).reshape(-1, 1)
    angle_B_b0 = np.arccos(np.dot(normarized_Bvec_proj_vec, np.array([0, 0, 1]).reshape(3, 1)))
    for i in range(len(angle_B_b0)):
        if np.dot(normarized_Bvec_proj_vec[i], spin_plane_unit_vec2) < 0:
            angle_B_b0[i] = -angle_B_b0[i]

    # plot angle dependence of power
    # calc field vector norm
    Evec_proj_vec_norm = np.linalg.norm(Evec_proj_vec, axis=1)
    Bvec_proj_vec_norm = np.linalg.norm(Bvec_proj_vec, axis=1)

    Emax_angle = np.rad2deg(angle_E_b0[np.argmax(Evec_proj_vec_norm)])
    Bmax_angle = np.rad2deg(angle_B_b0[np.argmax(Bvec_proj_vec_norm)])

    if Emax_angle < 0:
        Emax_angle += 180
    if Bmax_angle < 0:
        Bmax_angle += 180
    # 第2位を四捨五入した値を返す
    return (round(Emax_angle[0], 1), round(Bmax_angle[0], 1))


# wna, phi を変えて、theta=123.75, freq=178, mode='r'で計算して、csvに保存する
# csvには、(Emax_angle, Bmax_angle)を保存する
wna_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]
phi_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]
freqList = [3.16, 5.62, 10, 17.8, 31.6, 56.2, 100, 178, 316, 562]
for freq in freqList:
    mode = 'r'
    theta = 123.75
    saveName = '../execute/pyEmax_Bmax_angle_freq-{}_mode-{}.csv'
    with open(saveName.format(freq, mode), 'w') as f:
        writer = csv.writer(f)
        writer.writerow([""]+phi_list)
        for wna in wna_list:
            tuple_list = []
            for phi in phi_list:
                wna = wna
                freq = freq
                angle_tuple = get_peak_angle(theta, phi, wna, freq, mode)
                tuple_list.append(angle_tuple)
            writer.writerow([wna]+tuple_list)
