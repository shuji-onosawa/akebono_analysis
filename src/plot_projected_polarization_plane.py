import numpy as np
import matplotlib.pyplot as plt
from calc_dispersion_in_cold_plasma import calc_dispersion_relation, calc_amp_ratio
import os
import csv


def plot_projected_polarization_plane(theta, phi, wna, freq, mode='l'):
    """
    theta: angle between spin plane normal vector and z axis
    phi: angle between projection vector of spin plane normal vector
    on x-y plane and x axis
    wna: wave normal angle
    freq: wave frequency
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
    spin_plane_unit_vec2 = np.array([-np.sin(phi_rad), np.cos(phi_rad), 0])

    phase = np.linspace(0, 2*np.pi, 360, endpoint=False)

    antenna_vec = np.array([np.cos(phase)*spin_plane_unit_vec1[0] + np.sin(phase)*spin_plane_unit_vec2[0],
                            np.cos(phase)*spin_plane_unit_vec1[1] + np.sin(phase)*spin_plane_unit_vec2[1],
                            np.cos(phase)*spin_plane_unit_vec1[2] + np.sin(phase)*spin_plane_unit_vec2[2]])

    print('calc for these parameters:')
    print('theta:', theta)
    print('phi:', phi)
    print('wna:', wna)
    print('freq:', freq)
    print('mode:', mode)

    # wave polarization plane
    wna = wna
    freq = freq  # Hz
    angle_freq = 2*np.pi*freq

    k_vec = np.array([np.sin(wna*np.pi/180), 0, np.cos(wna*np.pi/180)])
    n_L, n_R, S, D, P = calc_dispersion_relation(angle_freq, wna)
    print('n_L:', n_L)
    print('n_R:', n_R)
    if mode == 'l':
        # left hand circular polarization
        Ey_Ex, Ez_Ex, By_Bx, Bz_Bx, E_cB = calc_amp_ratio(n_L, S, D, P, wna)
    elif mode == 'r':
        # right hand circular polarization
        Ey_Ex, Ez_Ex, By_Bx, Bz_Bx, E_cB = calc_amp_ratio(n_R, S, D, P, wna)

    # 3D plot of spin plane and wave polarization plane
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(221, projection='3d')
    ax.quiver(0, 0, 0,
              spin_plane_normal_vec[0], spin_plane_normal_vec[1], spin_plane_normal_vec[2],
              color='k', arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0,
              spin_plane_unit_vec1[0], spin_plane_unit_vec1[1], spin_plane_unit_vec1[2],
              color='g', arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0,
              spin_plane_unit_vec2[0], spin_plane_unit_vec2[1], spin_plane_unit_vec2[2],
              color='y', arrow_length_ratio=0.1)
    ax.scatter(np.cos(phase), -Ey_Ex*np.sin(phase), Ez_Ex*np.cos(phase),
               color='r', s=1.0, marker='o', label='E field, WNA = '+str(wna)+' [deg]')
    ax.quiver(0, 0, 0, k_vec[0], k_vec[1], k_vec[2])
    ax.scatter(np.cos(phase), -By_Bx*np.sin(phase), Bz_Bx*np.cos(phase),
               color='b', s=1.0, marker='o', label='M field, WNA = '+str(wna)+' [deg]')
    ax.scatter(2*antenna_vec[0], 2*antenna_vec[1], 2*antenna_vec[2], color='k', s=1, label='antenna vector')

    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_zlim(-2.5, 2.5)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.view_init(elev=30, azim=45)
    ax.set_aspect('equal')
    ax.legend()

    # projection of wave polarization plane on spin plane
    Evec = np.array([np.cos(phase), -Ey_Ex*np.sin(phase), Ez_Ex*np.cos(phase)])
    Bvec = np.array([np.cos(phase), -By_Bx*np.sin(phase), Bz_Bx*np.cos(phase)])
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
    ax = fig.add_subplot(222)
    ax.scatter(np.dot(EvecProjVec, spin_plane_unit_vec1),
               np.dot(EvecProjVec, spin_plane_unit_vec2),
               color='r', s=1)
    ax.scatter(np.dot(BvecProjVec, spin_plane_unit_vec1),
               np.dot(BvecProjVec, spin_plane_unit_vec2),
               color='b', s=1)
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_xlabel('green')
    ax.set_ylabel('yellow')
    ax.set_aspect('equal')

    # angle between z axis and field vectors
    # calc angle between z axis and E field vectors
    normarizedEvecProjVec = EvecProjVec/np.linalg.norm(EvecProjVec, axis=1).reshape(-1, 1)
    angle_E_b0 = np.arccos(np.dot(normarizedEvecProjVec, np.array([0, 0, 1]).reshape(3, 1)))
    for i in range(len(angle_E_b0)):
        if np.dot(normarizedEvecProjVec[i], spin_plane_unit_vec2) < 0:
            angle_E_b0[i] = -angle_E_b0[i]
    # calc angle between z axis and B field vectors
    normarizedBvecProjVec = BvecProjVec/np.linalg.norm(BvecProjVec, axis=1).reshape(-1, 1)
    angle_B_b0 = np.arccos(np.dot(normarizedBvecProjVec, np.array([0, 0, 1]).reshape(3, 1)))
    for i in range(len(angle_B_b0)):
        if np.dot(normarizedBvecProjVec[i], spin_plane_unit_vec2) < 0:
            angle_B_b0[i] = -angle_B_b0[i]

    # plot angle dependence of power
    # calc field vector norm
    EvecProjVecNorm = np.linalg.norm(EvecProjVec, axis=1)
    BvecProjVecNorm = np.linalg.norm(BvecProjVec, axis=1)

    ax = fig.add_subplot(223)
    ax.scatter(np.rad2deg(angle_E_b0), EvecProjVecNorm/np.nanmax(EvecProjVecNorm),
               color='r', label='E field', s=2.0)
    ax.scatter(np.rad2deg(angle_B_b0), BvecProjVecNorm/np.nanmax(BvecProjVecNorm),
               color='b', label='B field', s=2.0)
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 1.1)

    ax.set_xlabel('angle')
    ax.set_ylabel('power')
    ax.set_xticks([0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180])
    # legend position
    ax.legend(loc='lower right')
    plt.show
    if mode == 'l':
        savefig_dir = '../plots/projected_polarization_plane/left_hand_circular/freq'+str(freq)+'/wna'+str(wna)+'theta'+str(theta)+'/'
    elif mode == 'r':
        savefig_dir = '../plots/projected_polarization_plane/right_hand_circular/freq'+str(freq)+'/wna'+str(wna)+'theta'+str(theta)+'/'

    os.makedirs(savefig_dir, exist_ok=True)
    plt.savefig(savefig_dir+'spin-phi'+str(phi)+'.jpeg', dpi=300)
    plt.close()

    # find max power angle
    Emax_angle = np.rad2deg(angle_E_b0[np.argmax(EvecProjVecNorm)])
    Bmax_angle = np.rad2deg(angle_B_b0[np.argmax(BvecProjVecNorm)])

    if Emax_angle < 0:
        Emax_angle += 180
    if Bmax_angle < 0:
        Bmax_angle += 180
    # 第2位を四捨五入した値を返す
    return (round(Emax_angle[0], 1), round(Bmax_angle[0], 1))


wna_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 89, 100, 110, 120, 130, 140, 150, 160, 170, 180]
phi_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 89, 100, 110, 120, 130, 140, 150, 160, 170, 180]
freqList = [3.16, 5.62, 10, 17.8, 31.6, 56.2, 100, 178, 316, 562]
# calc for mode='r
for freq in freqList:
    mode = 'r'
    theta = 123.75
    saveDir = '../execute/0211/'
    os.makedirs(saveDir, exist_ok=True)
    saveName = saveDir+'pyEmax_Bmax_angle_freq-{}_mode-{}.csv'
    with open(saveName.format(freq, mode), 'w') as f:
        writer = csv.writer(f)
        writer.writerow([""]+phi_list)
        for wna in wna_list:
            tuple_list = []
            for phi in phi_list:
                wna = wna
                freq = freq
                angle_tuple = plot_projected_polarization_plane(theta, phi, wna, freq, mode)
                tuple_list.append(angle_tuple)
            writer.writerow([wna]+tuple_list)

# calc for mode='l'
for freq in freqList:
    mode = 'l'
    theta = 123.75
    saveDir = '../execute/0211/'
    os.makedirs(saveDir, exist_ok=True)
    saveName = saveDir+'pyEmax_Bmax_angle_freq-{}_mode-{}.csv'
    with open(saveName.format(freq, mode), 'w') as f:
        writer = csv.writer(f)
        writer.writerow([""]+phi_list)
        for wna in wna_list:
            tuple_list = []
            for phi in phi_list:
                wna = wna
                freq = freq
                angle_tuple = plot_projected_polarization_plane(theta, phi, wna, freq, mode)
                tuple_list.append(angle_tuple)
            writer.writerow([wna]+tuple_list)
