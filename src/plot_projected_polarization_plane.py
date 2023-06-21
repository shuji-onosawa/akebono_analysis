import numpy as np
import matplotlib.pyplot as plt

theta_polari = np.deg2rad(0)
phi_polari = np.deg2rad(0)

polari_vec1 = np.array([np.sin(theta_polari)*np.cos(phi_polari),
                        np.sin(theta_polari)*np.sin(phi_polari),
                        np.cos(theta_polari)])
polari_vec2 = np.array([np.cos(theta_polari)*np.cos(phi_polari),
                        np.cos(theta_polari)*np.sin(phi_polari),
                        -np.sin(theta_polari)])

theta = np.deg2rad(0)
phi = np.deg2rad(0)

spin_plane_normal_vec = np.array([np.sin(theta)*np.cos(phi),
                                  np.sin(theta)*np.sin(phi),
                                  np.cos(theta)])
spin_plane_unit_vec1 = np.array([np.cos(theta)*np.cos(phi),
                                 np.cos(theta)*np.sin(phi),
                                 -np.sin(theta)])
spin_plane_unit_vec2 = np.cross(spin_plane_normal_vec, spin_plane_unit_vec1)

phase = np.linspace(0, 2*np.pi, 100)

# 3D plot and 2D plot in the same figure
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(211, projection='3d')
ax.quiver(0, 0, 0,
            spin_plane_normal_vec[0], spin_plane_normal_vec[1], spin_plane_normal_vec[2],
            color='blue', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0,
            spin_plane_unit_vec1[0], spin_plane_unit_vec1[1], spin_plane_unit_vec1[2],
            color='black', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0,
            spin_plane_unit_vec2[0], spin_plane_unit_vec2[1], spin_plane_unit_vec2[2],
            color='black', arrow_length_ratio=0.1)
ax.scatter(np.cos(phase), np.sin(phase), np.zeros_like(phase), color='black', s=1)
vec = np.array([np.cos(phase), np.sin(phase), np.zeros_like(phase)]).T

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_zlim(-1.5, 1.5)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

ax = fig.add_subplot(212)
ax.scatter(np.dot(vec, spin_plane_unit_vec1), np.dot(vec, spin_plane_unit_vec2))

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_aspect('equal')
plt.show()
