import numpy as np
import matplotlib.pyplot as plt

theta = np.deg2rad(0)
phi = np.deg2rad(0)

vec = np.array([0.1, 0.4, 0.3])

spin_plane_normal_vec = np.array([np.sin(theta)*np.cos(phi),
                                  np.sin(theta)*np.sin(phi),
                                  np.cos(theta)])
spin_plane_unit_vec1 = np.array([np.cos(theta)*np.cos(phi),
                                 np.cos(theta)*np.sin(phi),
                                 -np.sin(theta)])
spin_plane_unit_vec2 = np.cross(spin_plane_normal_vec, spin_plane_unit_vec1)

fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(111, projection='3d')

ax.quiver(0, 0, 0,
          spin_plane_normal_vec[0], spin_plane_normal_vec[1], spin_plane_normal_vec[2],
          color='blue', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0,
          spin_plane_unit_vec1[0], spin_plane_unit_vec1[1], spin_plane_unit_vec1[2],
          color='black', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0,
          spin_plane_unit_vec2[0], spin_plane_unit_vec2[1], spin_plane_unit_vec2[2],
          color='black', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0,
          vec[0], vec[1], vec[2],
          color='green', arrow_length_ratio=0.1)
ax.quiver(0, 0, 0,
          np.dot(vec, spin_plane_unit_vec1)*spin_plane_unit_vec1[0]+np.dot(vec, spin_plane_unit_vec2)*spin_plane_unit_vec2[0],
          np.dot(vec, spin_plane_unit_vec1)*spin_plane_unit_vec1[1]+np.dot(vec, spin_plane_unit_vec2)*spin_plane_unit_vec2[1],
          np.dot(vec, spin_plane_unit_vec1)*spin_plane_unit_vec1[2]+np.dot(vec, spin_plane_unit_vec2)*spin_plane_unit_vec2[2],
          color='red', arrow_length_ratio=0.1, linestyle='dashed')

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_zlim(-1.5, 1.5)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

plt.show()
