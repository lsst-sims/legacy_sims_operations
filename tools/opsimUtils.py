import numpy as np


def calc_FWHMeff(visitFilter, rawSeeing, airmass):
    """Convert the raw seeing from the seeing database into FWHMeff for a particular observation."""
    filterWave = {'u': 367.0, 'g': 482.5, 'r': 622.2, 'i': 754.5, 'z': 869.1, 'y': 971.0}
    telSeeing = 0.25
    opticalDesign = 0.08
    cameraSeeing = 0.30
    fwhm_sys = np.sqrt(telSeeing**2 + opticalDesign**2 + cameraSeeing**2) * np.power(airmass, 0.6)
    fwhm_atm = rawSeeing * np.power(500.0 / filterWave[visitFilter], 0.3) * np.power(airmass, 0.6)
    fwhmEff = 1.16 * np.sqrt(fwhm_sys**2 + 1.04*fwhm_atm**2)
    return fwhmEff
