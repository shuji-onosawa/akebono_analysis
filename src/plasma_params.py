import numpy as np

# constant
Q = 1.6e-19  # [C]
EPS = 8.9e-12  # [F m*-1]
MYU = 1.3e-6  # [N A**-2]
ME = 9.1e-31  # [kg]
MH = 1.7e-27  # [kg]
MHE = 6.7e-27  # [kg]
MO = 2.7e-26  # [kg]
C = 2.97e8  # [m s**-1]
B0 = 5300e-9  # [T]

# plasma parameter
NE = 128e6  # [m**-3]
ion_ratio = np.array([0.24, 0.08, 0.68])
nh = ion_ratio[0]*NE
nhe = ion_ratio[1]*NE
no = ion_ratio[2]*NE

RHO = sum(ion_ratio*np.array([MH, MHE, MO]))

pi_e = {'value': (NE*Q**2/(EPS*ME))**0.5, 'label': r'$\Pi_{e}$'}
pi_h = {'value': (nh*Q**2/(EPS*MH))**0.5, 'lable': r'$\Pi_{h}$'}
pi_he = {'value': (nhe*Q**2/(EPS*MHE))**0.5, 'label': r'$\Pi_{he}$'}
pi_o = {'value': (no*Q**2/(EPS*MO))**0.5, 'label': r'$\Pi_{o}$'}

omega_e = {'value': -Q*B0/ME, 'label': r'$\Omega_{ce}$'}
omega_h = {'value': Q*B0/MH, 'label': r'$\Omega_{ch}$'}
omega_o = {'value': Q*B0/MO, 'label': r'$\Omega_{co}$'}
omega_he = {'value': Q*B0/MHE, 'label': r'$\Omega_{che}$'}
wlh = {'value': np.sqrt((omega_h['value']**2 + pi_h['value']**2) / (1 + (pi_e['value']/omega_e['value'])**2)),
       'label': r'$\Omega_{lh}$'}
wuh = {'value': np.sqrt(omega_e['value']**2 + pi_e['value']**2),
       'label': r'$\Omega_{uh}$'}
Va = B0/(MYU*RHO)**0.5
