import numpy as np
import matplotlib.pyplot as plt
from calc_dispersion_in_cold_plasma import calc_dispersion_relation, calc_amp_ratio
import os


def plot_projected_polarization_plane(theta, phi, wna, freq, mode='l'):
    """
    theta: angle between spin plane normal vector and z axis
    phi: angle between projection vector of spin plane normal vector on x-y plane and x axis
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
    ax.scatter(2*antennna_vec[0], 2*antennna_vec[1], 2*antennna_vec[2], color='k', s=1, label='antenna vector')

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
    Evec = np.array([np.cos(phase), -Ey_Ex*np.sin(phase), Ez_Ex*np.cos(phase)]).T
    Bvec = np.array([np.cos(phase), -By_Bx*np.sin(phase), Bz_Bx*np.cos(phase)]).T
    # calc projection of E field on spin plane
    Evec_proj_vec = Evec - np.dot(Evec, spin_plane_normal_vec.reshape(3, 1))*spin_plane_normal_vec.reshape(1, 3)
    # calc projection of B field on spin plane
    Bvec_proj_vec = Bvec - np.dot(Bvec, spin_plane_normal_vec.reshape(3, 1))*spin_plane_normal_vec.reshape(1, 3)
    
    ax = fig.add_subplot(222)
    ax.scatter(np.dot(Evec_proj_vec, spin_plane_unit_vec1),
               np.dot(Evec_proj_vec, spin_plane_unit_vec2),
               color='r', s=1)
    ax.scatter(np.dot(Bvec_proj_vec, spin_plane_unit_vec1),
               np.dot(Bvec_proj_vec, spin_plane_unit_vec2),
               color='b', s=1)
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_xlabel('green')
    ax.set_ylabel('yellow')
    ax.set_aspect('equal')

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
    # print angle_E_b0 at max E field
    print(wna, phi)
    print('angle_E_b0 at max E field = '+str(np.rad2deg(angle_E_b0[np.argmax(Evec_proj_vec_norm)])))
    # print angle_B_b0 at max B field
    print('angle_B_b0 at max B field = '+str(np.rad2deg(angle_B_b0[np.argmax(Bvec_proj_vec_norm)])))
    ax = fig.add_subplot(223)
    ax.scatter(np.rad2deg(angle_E_b0), Evec_proj_vec_norm/np.nanmax(Evec_proj_vec_norm),
               color='r', label='E field', s=2.0)
    ax.scatter(np.rad2deg(angle_B_b0), Bvec_proj_vec_norm/np.nanmax(Bvec_proj_vec_norm),
               color='b', label='B field', s=2.0)
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 1.1)
    ax.vlines([-90, 90], 0, 1.1, color='k', linestyle='dashed')
    ax.vlines([112.5, 135.0], 0, 1.1, color='r', linestyle='dashed')
    ax.vlines([45.0, 67.5], 0, 1.1, color='b', linestyle='dashed')

    ax.set_xlabel('angle')
    ax.set_ylabel('power')
    ax.set_xticks([0, 90, 180])
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


for wna in np.linspace(0, 90, 10, dtype=int):
    for phi in np.linspace(0, 180, 19, dtype=int):
        theta = 123.75
        wna = wna
        freq = 178
        plot_projected_polarization_plane(theta, phi, wna, freq, mode='r')
