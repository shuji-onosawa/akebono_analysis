import numpy as np

# constant
Q = 1.602176634e-19  # [C]
EPS = 8.8541878128e-12  # [F m*-1]
MYU = 1.25663706212e-6  # [N A**-2]
ME = 9.1093837015e-31  # [kg]
MH = 1.67262192369e-27  # [kg]
MHE = 6.646477e-27  # [kg]
MO = 2.6566962e-26  # [kg]
C = 2.99792458e8  # [m s**-1]
B0 = 8531e-9  # [T]

# plasma parameter
NE = 71e6  # [m**-3]
ion_ratio = np.array([0.30, 0.06, 0.64])  # H:He:O
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
