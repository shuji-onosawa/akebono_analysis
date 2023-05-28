import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# calculate the angle between two vectors
def calculate_angle(vec1, vec2):

    OP = vec1
    OA = vec2
    
    angle = np.arccos(np.dot(OP, OA)/(np.linalg.norm(OP)*np.linalg.norm(OA)))
    if np.cross(OP, OA)[2] < 0:
        angle = -angle

    return np.degrees(angle)


theta = np.linspace(0, 2*np.pi, 16)
e_antenna_vec = np.array([-np.sin(np.deg2rad(35)), np.cos(np.deg2rad(35)), 0])
m_antenna_vec = np.array([0, -1, 0])

bg_b0 = np.empty([theta.size, 3])
b0_theta = np.pi/3
for i in range(theta.size):
    bg_b0[i, :] = np.array([np.cos(b0_theta), 0, np.sin(b0_theta)])*np.cos(theta[i]) + \
        np.array([0, 1, 0])*np.sin(theta[i])

# take the average of the cross product of bg_b0[i] and bg_b0[i+1]
# to get the normal vector of the plane
normal_vec = np.empty([theta.size, 3])
for i in range(theta.size):
    normal_vec[i, :] = np.cross(bg_b0[i], bg_b0[(i+1)%theta.size])

print(normal_vec)
for i in range(16):
    print(np.dot(normal_vec[i], bg_b0[i]))
# plot the plane
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for idx in range(16):
    #plot the vectors(bg_b0, normal_vec) as arrows with the label at the end of the arrow
    ax.quiver(0, 0, 0, bg_b0[idx, 0], bg_b0[idx, 1], bg_b0[idx, 2], color='b', label='bg_b0')
    ax.quiver(0, 0, 0, normal_vec[idx, 0], normal_vec[idx, 1], normal_vec[idx, 2], color='r', label='normal_vec')

ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

plt.show()
