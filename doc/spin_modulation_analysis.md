# Spin modulation analysis with Akebono-MCA

## Instruments
- Multi-channel analyzer (MCA): time resolution 0.5 s
- Magnetic field (MGF): time resolution 1/32 s

## Method
Take a 0.5-second average of MGF data.
In the satellite XYZ coordinate system:
- Unit vector of the ambient magnetic field
$$ \hat{\boldsymbol{B_0(t)}} = \frac{\boldsymbol{B_{MGF}(t)}}{\boldsymbol{|B_{MGF}(t)|}} $$
- Unit vector in the direction of fields measured by the sensors.
```math
\begin{align}
\hat{\boldsymbol{u_{Esensor}}} &= (-sin(35*2\pi/360), cos(35*2\pi/360), 0) \\
\hat{\boldsymbol{u_{Bsensor}}} &= (0, -1, 0)
\end{align}
```
- Normal vector of the plane defined by $\hat{\boldsymbol{B_0(t)}}$ and $\hat{\boldsymbol{B_0(t+0.5)}}$.
```math
\begin{align}
\hat{\boldsymbol{n}} &= \frac{\hat{\boldsymbol{B_0(t)}} \times \hat{\boldsymbol{B_0(t+0.5)}}}{|\hat{\boldsymbol{B_0(t)}} \times \hat{\boldsymbol{B_0(t+0.5)}}|} \\
\end{align}
```
- Cross product of $\hat{\boldsymbol{B_0(t)}}$ and $\hat{\boldsymbol{u_{Esensor}}}$, $\hat{\boldsymbol{u_{Bsensor}}}$.
```math
\begin{align}
\hat{\boldsymbol{u_{Ecross}}} =& \hat{\boldsymbol{B_0}} \times \hat{\boldsymbol{u_{Esensor}}} \\
\hat{\boldsymbol{u_{Bcross}}} =& \hat{\boldsymbol{B_0}} \times \hat{\boldsymbol{u_{Bsensor}}}
\end{align}
```
- Angle between the sensors and the background magnetic field
```math
\begin{align}
\theta_{S} &=
\begin{cases}
\arccos(\hat{\boldsymbol{B_0}} \cdot \hat{\boldsymbol{u_{Ssensor}}}) & \text{if } \hat{\boldsymbol{u_{Scross}}} \cdot \hat{\boldsymbol{n}} > 0 \\
\pi - \arccos(\hat{\boldsymbol{B_0}} \cdot \hat{\boldsymbol{u_{Ssensor}}}) & \text{if } \hat{\boldsymbol{u_{Scross}}} \cdot \hat{\boldsymbol{n}} < 0
\end{cases}
S = E, B\\
\end{align}
```

