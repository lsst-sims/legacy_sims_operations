import numpy as np


def calc_m5(visitFilter, filtsky, FWHMeff, expTime, airmass, tauCloud=0):
    """Calculate the m5 value, using opsim methods."""
    # Set up expected extinction (kAtm) and m5 normalization values (Cm) for each filter.
    # The Cm values must be changed when telescope and site parameters are updated.
    #
    # These values are calculated using $SYSENG_THROUGHPUTS/python/calcM5.py.
    # This set of values are calculated using v1.0 of the SYSENG_THROUGHPUTS repo.
    Cm = {'u':22.94,
          'g':24.46,
          'r':24.48,
          'i':24.34,
          'z':24.18,
          'y':23.73}
    dCm_infinity = {'u':0.56,
                    'g':0.12,
                    'r':0.06,
                    'i':0.05,
                    'z':0.03,
                    'y':0.02}
    kAtm = {'u':0.50,
            'g':0.21,
            'r':0.13,
            'i':0.10,
            'z':0.07,
            'y':0.18}
    msky = {'u':22.95,
            'g':22.24,
            'r':21.20,
            'i':20.47,
            'z':19.60,
            'y':18.63}
    # Calculate adjustment if readnoise is significant for exposure time
    # (see overview paper, equation 7)
    Tscale = expTime / 30.0 * np.power(10.0, -0.4*(filtsky - msky[visitFilter]))
    dCm = dCm_infinity[visitFilter] - 1.25*np.log10(1 + (10**(0.8*dCm_infinity[visitFilter]) - 1)/Tscale)
    # Calculate fiducial m5
    m5 = (Cm[visitFilter] + dCm + 0.50*(filtsky-21.0) + 2.5*np.log10(0.7/FWHMeff) +
          1.25*np.log10(expTime/30.0) - kAtm[visitFilter]*(airmass-1.0) + 1.1*tauCloud)
    return m5

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
