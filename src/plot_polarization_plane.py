#3次元内の楕円板をプロットするプログラム

import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(0, 2*np.pi, 100)


# 楕円板のプロット
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(np.cos(theta), 2*np.sin(theta), np.cos(theta), c='b', marker='o')
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-2.5, 2.5)
ax.set_zlim(-2.5, 2.5)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()


