from geopack import geopack
import numpy as np


def calc_sza_from_geo(epoch: float or np.ndarray,
                      xgeo: float or np.ndarray,
                      ygeo: float or np.ndarray,
                      zgeo: float or np.ndarray):
    psi = geopack.recalc(epoch)
    x1gsm, y1gsm, z1gsm, xx, yy, zz = geopack.trace(xgeo, ygeo, zgeo, dir=1, rlim=100, r0=1,
                                                    inname='igrf')
    # calc solar zenith angle
    sza = np.arccos(x1gsm/np.sqrt(x1gsm**2+y1gsm**2+z1gsm**2))
    return sza
