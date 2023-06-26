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

    # calc angle between z axis and antenna vector
    angle = np.arccos(np.dot(antennna_vec.T, np.array([0, 0, 1]))/np.linalg.norm(antennna_vec, axis=0))
    # if phase > 180, angle = -angle
    angle = np.where(phase > np.pi, -angle, angle)

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
    ax.scatter(np.cos(phase), -Ey_Ex*np.sin(phase), Ez_Ex*np.cos(phase),
                color='r', s=1.0, marker='o', label='E field, WNA = '+str(wna)+' [deg]')
    ax.quiver(0, 0, 0, k_vec[0], k_vec[1], k_vec[2])
    ax.scatter(np.cos(phase), -By_Bx*np.sin(phase), Bz_Bx*np.cos(phase),
                color='b', s=1.0, marker='o', label='M field, WNA = '+str(wna)+' [deg]')
    ax.scatter(2*antennna_vec[0], 2*antennna_vec[1], 2*antennna_vec[2], color='k', s=1, label='antenna vector')
    Evec = np.array([np.cos(phase), -Ey_Ex*np.sin(phase), Ez_Ex*np.cos(phase)]).T
    Bvec = np.array([np.cos(phase), -By_Bx*np.sin(phase), Bz_Bx*np.cos(phase)]).T

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
    ax = fig.add_subplot(222)
    Ecomp1 = np.dot(Evec, spin_plane_unit_vec1)
    Ecomp2 = np.dot(Evec, spin_plane_unit_vec2)
    ax.scatter(Ecomp1, Ecomp2, color='r', s=1)
    Bcomp1 = np.dot(Bvec, spin_plane_unit_vec1)
    Bcomp2 = np.dot(Bvec, spin_plane_unit_vec2)
    ax.scatter(Bcomp1, Bcomp2, color='b', s=1)

    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_aspect('equal')

    # angle between z axis and antenna vector
    ax = fig.add_subplot(223)
    ax.scatter(angle/np.pi*180, phase/np.pi*180, color='black', linewidth=0.5)
    ax.set_ylabel('phase')
    ax.set_xlabel('angle')

    # angle dependence of power
    ax = fig.add_subplot(224)
    Epwr = Ecomp1**2+Ecomp2**2
    normarized_Epwr = Epwr/np.max(Epwr)
    Bpwr = Bcomp1**2+Bcomp2**2
    normarized_Bpwr = Bpwr/np.max(Bpwr)
    ax.scatter(angle/np.pi*180, normarized_Epwr, color='r', linewidth=0.5, label='E field')
    ax.scatter(angle/np.pi*180, normarized_Bpwr, color='b', linewidth=0.5, label='B field')
    ax.set_xlabel('angle')
    ax.set_ylabel('power')
    ax.set_xticks([-180, -90, 0, 90, 180])
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.legend()

    if mode == 'l':
        savefig_dir = '../plots/projected_polarization_plane/left_hand_circular/freq'+str(freq)+'wna'+str(wna)+'theta'+str(theta)+'/'
    elif mode == 'r':
        savefig_dir = '../plots/projected_polarization_plane/right_hand_circular/freq'+str(freq)+'wna'+str(wna)+'theta'+str(theta)+'/'

    os.makedirs(savefig_dir, exist_ok=True)
    plt.savefig(savefig_dir+'spin-phi'+str(phi)+'.jpeg', dpi=300)
    plt.close()


for wna in np.linspace(0, 180, 19, dtype=int):
    for phi in np.linspace(0, 180, 19, dtype=int):
        theta = 123.75
        wna = wna
        freq = 100
        plot_projected_polarization_plane(theta, phi, wna, freq, mode='r')
