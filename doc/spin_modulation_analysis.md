# Spin modulation analysis with Akebono-MCA

## Instruments
- Multi-channel analyzer (MCA): time resolution 0.5s
- Magnetic field (MGF): time resolution 0.5s

## Method
In the satellite XYZ coordinate system:
- Unit vector of background magnetic field
$$ \hat{\boldsymbol{B_0}} = \frac{\boldsymbol{B_{MGF}}}{\boldsymbol{|B_{MGF}|}} $$
- Unit vector in the direction of fields measured by the sensors.
```math
\begin{align}
\hat{\boldsymbol{u_{Esensor}}} &= (-sin(35*2\pi/360), cos(35*2\pi/360), 0) \\
\hat{\boldsymbol{u_{Msensor}}} &= (0, -1, 0)
\end{align}
```
- Angle between the sensors and the background magnetic field
```math
\begin{align}
\theta_{E} &= \arccos(\hat{\boldsymbol{B_0}} \cdot \hat{\boldsymbol{u_{Esensor}}}) \\
\theta_{B} &= \arccos(\hat{\boldsymbol{B_0}} \cdot \hat{\boldsymbol{u_{Msensor}}})
\end{align}
```
- We want the angle in the range of - $\pi$ to $\pi$, so adjast the angle by considering the sign of the vector compornents. To do this, we can use the cross product of the vectors.
```math
\theta_s = 
\begin{cases}
\theta_{s} & \text{if } (\hat{\boldsymbol{B_0}} \times \hat{\boldsymbol{u_{Esensor}}})_Z > 0 \\
-\theta_{s} & \text{if } (\hat{\boldsymbol{B_0}} \times \hat{\boldsymbol{u_{Esensor}}})_Z < 0
\end{cases}
s = E, B
```
