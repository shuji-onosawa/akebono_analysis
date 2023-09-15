import numpy as np
from calc_dispersion_in_cold_plasma import calc_dispersion_relation, calc_amp_ratio
import csv

def get_peak_angle(theta, phi, wna, freq, mode):
    theta_rad = np.deg2rad(theta)
    phi_rad = np.deg2rad(phi)

    spin_plane_normal_vec = np.array([np.sin(theta_rad)*np.cos(phi_rad),
                                        np.sin(theta_rad)*np.sin(phi_rad),
                                        np.cos(theta_rad)])
    spin_plane_unit_vec1 = np.array([np.cos(theta_rad)*np.cos(phi_rad),
                                    np.cos(theta_rad)*np.sin(phi_rad),
                                    -np.sin(theta_rad)])
    spin_plane_unit_vec2 = np.cross(spin_plane_normal_vec, spin_plane_unit_vec1)

    phase = np.linspace(0, 2*np.pi, 100)

    antennna_vec = np.array([np.cos(phase)*spin_plane_unit_vec1[0] + np.sin(phase)*spin_plane_unit_vec2[0],
                            np.cos(phase)*spin_plane_unit_vec1[1] + np.sin(phase)*spin_plane_unit_vec2[1],
                            np.cos(phase)*spin_plane_unit_vec1[2] + np.sin(phase)*spin_plane_unit_vec2[2]])

    # wave polarization plane
    wna = wna
    freq = freq  # Hz
    angle_freq = 2*np.pi*freq

    k_vec = np.array([np.sin(wna*np.pi/180), 0, np.cos(wna*np.pi/180)])
    n_L, n_R, S, D, P = calc_dispersion_relation(angle_freq, wna)
    if mode == 'l':
        # left hand circular polarization
        Ey_Ex, Ez_Ex, By_Bx, Bz_Bx, E_cB = calc_amp_ratio(n_L, S, D, P, wna)
    elif mode == 'r':
        # right hand circular polarization
        Ey_Ex, Ez_Ex, By_Bx, Bz_Bx, E_cB = calc_amp_ratio(n_R, S, D, P, wna)

    # projection of wave polarization plane on spin plane
    Evec = np.array([np.cos(phase), -Ey_Ex*np.sin(phase), Ez_Ex*np.cos(phase)]).T
    Bvec = np.array([np.cos(phase), -By_Bx*np.sin(phase), Bz_Bx*np.cos(phase)]).T
    # calc projection of E field on spin plane
    Evec_proj_vec = Evec - np.dot(Evec, spin_plane_normal_vec.reshape(3, 1))*spin_plane_normal_vec.reshape(1, 3)
    # calc projection of B field on spin plane
    Bvec_proj_vec = Bvec - np.dot(Bvec, spin_plane_normal_vec.reshape(3, 1))*spin_plane_normal_vec.reshape(1, 3)


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
with open('../execute/pyEmax_Bmax_angle.csv', 'w') as f:
    for wna in np.linspace(0, 180, 10, dtype=int):
        tuple_list = []
        for phi in np.linspace(0, 180, 19, dtype=int):
            theta = 123.75
            wna = wna
            freq = 178
            mode = 'r'
            angle_tuple = get_peak_angle(theta, phi, wna, freq, mode)
            tuple_list.append(angle_tuple)
        writer = csv.writer(f)
        writer.writerow(tuple_list)
