# Spin modulation analysis with Akebono-MCA

## Instruments
- Multi-channel analyzer (MCA): time resolution 0.5s
- Magnetic field (MGF): time resolution 0.5s

## Method
The follwing method to calculate the angle between the background magnetic field and the sensors is not correct because arccos returns the angle between 0 to $\pi$ radian and the angle between 0 to $2\pi$ radian is needed.
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
The correct method is to use arctan2 function.
The following method is correct.
```math
\begin{align}
\theta_{E} &= \arctan2(\hat{\boldsymbol{B_0}} \times \hat{\boldsymbol{u_{Esensor}}}, \hat{\boldsymbol{B_0}} \cdot \hat{\boldsymbol{u_{Esensor}}}) \\
\theta_{B} &= \arctan2(\hat{\boldsymbol{B_0}} \times \hat{\boldsymbol{u_{Msensor}}}, \hat{\boldsymbol{B_0}} \cdot \hat{\boldsymbol{u_{Msensor}}})
\end{align}
```
```math
\begin{align}
\hat{\boldsymbol{B_0}} \times \hat{\boldsymbol{u_{Esensor}}} &= (cos(\theta_{E}), sin(\theta_{E}), 0) \\
\hat{\boldsymbol{B_0}} \times \hat{\boldsymbol{u_{Msensor}}} &= (0, 0, 1)
\end{align}
```
The definition of arctan2 is
```math
\begin{align}
\arctan2(y, x) &= \arctan(y/x) \\
&= \begin{cases}
\arctan(y/x) & x > 0 \\
\arctan(y/x) + \pi & x < 0, y \geq 0 \\
\arctan(y/x) - \pi & x < 0, y < 0 \\
\frac{\pi}{2} & x = 0, y > 0 \\
-\frac{\pi}{2} & x = 0, y < 0 \\
\text{undefined} & x = 0, y = 0
\end{cases}
\end{align}
```
