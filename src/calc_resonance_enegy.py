from calc_dispersion_in_cold_plasma import calc_dispersion_relation
import numpy as np
import plasma_params as pp


def calc_resonance_enegy(frequency: float or np.ndarray,
                         waveNormalAngle: float,
                         pitchAngle: float,
                         particle: str):
    """
    Parameters
    ----------
    frequency : float or np.ndarray
        wave frequency [rad/s]
    waveNormalAngle : float
        wave normal angle [deg]
    pitchAngle : float
        pitch angle [deg]
    particle : str
        'e', 'h', 'he', 'o'
    """
    nL, nR, S, D, P = calc_dispersion_relation(frequency, waveNormalAngle)
    # 粒子種によって質量を設定
    if particle == 'e':
        mass = pp.ME
        cyclotronFrequency = pp.omega_e['value']
    elif particle == 'h':
        mass = pp.MH
        cyclotronFrequency = pp.omega_h['value']
    elif particle == 'he':
        mass = pp.MHE
        cyclotronFrequency = pp.omega_he['value']
    elif particle == 'o':
        mass = pp.MO
        cyclotronFrequency = pp.omega_o['value']
    else:
        raise ValueError('particle must be "e", "h", "he" or "o".')
    #
