import os, copy
import numpy as np
import matplotlib.pyplot as plt
from lsst.sims.photUtils import Bandpass, Sed, SignalToNoise, PhotometricParameters
from lsst.sims.maf.db import OpsimDatabase

def setup_photUtils():
    throughputDir = os.getenv('LSST_THROUGHPUTS_DEFAULT')
    filterlist = ('u', 'g' , 'r', 'i', 'z', 'y')
    hardware = {}
    system = {}
    corecomponents = ['detector.dat', 'lens1.dat', 'lens2.dat', 'lens3.dat', 'm1.dat', 'm2.dat', 'm3.dat']
    for f in filterlist:
        hardware[f] = Bandpass()
        system[f] = Bandpass()
        componentlist = copy.deepcopy(corecomponents)
        componentlist += ['filter_%s.dat' %f]
        hardware[f].readThroughputList(componentlist, rootDir=throughputDir)
        componentlist += ['atmos_10.dat']
        system[f].readThroughputList(componentlist, rootDir=throughputDir)
    darksky = Sed()
    darksky.readSED_flambda(os.path.join(throughputDir, 'darksky.dat'))
    return hardware, system, darksky

def calc_m5_photUtils(hardware, system, darksky,
                      visitFilter, filtsky, FWHMeff, expTime, airmass, tauCloud=0):
    m5 = np.zeros(len(expTime))
    for i in range(len(m5)):
        photParams = PhotometricParameters(exptime=expTime[i]/2.0, nexp=2)
        skysed = copy.deepcopy(darksky)
        fluxnorm = skysed.calcFluxNorm(filtsky[i], system[visitFilter[i]])
        skysed.multiplyFluxNorm(fluxnorm)
        # Calculate the m5 value (this is for x=1.0 because we used x=1.0 in the atmosphere for system)
        m5[i] = SignalToNoise.calcM5(skysed, system[visitFilter[i]], hardware[visitFilter[i]], photParams, FWHMeff=FWHMeff[i])
    return m5

def calc_m5_opsim(visitFilter, filtsky, FWHMeff, expTime, airmass, tauCloud=0):
    # Set up expected extinction (kAtm) and m5 normalization values (Cm) for each filter.
    # The Cm values must be changed when telescope and site parameters are updated.
    visitFilter = visitFilter[0]
    Cm = {'u':22.34,
          'g':23.99,
          'r':24.11,
          'i':24.05,
          'z':23.95,
          'y':23.55}
    dCm_infinity = {'u':0.56,
                    'g':0.12,
                    'r':0.06,
                    'i':0.05,
                    'z':0.03,
                    'y':0.02}
    kAtm = {'u':0.50,
            'g':0.20,
            'r':0.12,
            'i':0.10,
            'z':0.07,
            'y':0.18}
    # Calculate adjustment if readnoise is significant for exposure time
    # (see overview paper, equation 7)
    Tscale = expTime / 30.0
    dCm = dCm_infinity[visitFilter] - 1.25*np.log10(1 + (10**(0.8*dCm_infinity[visitFilter]) - 1)/Tscale)
    # Calculate fiducial m5
    m5 = (Cm[visitFilter] + dCm + 0.50*(filtsky-21.0) + 2.5*np.log10(0.7/FWHMeff) +
          1.25*np.log10(Tscale) - kAtm[visitFilter]*(airmass-1.0) + 1.1*tauCloud)
    # Calculate m5 without airmass
    m5_x1 = (Cm[visitFilter] + dCm + 0.50*(filtsky-21.0) + 2.5*np.log10(0.7/FWHMeff) +
          1.25*np.log10(Tscale))
    return m5, m5_x1


if __name__ == '__main__':

    # Replace this with the filename for your sqlite database.
    dbFile = '/Users/lynnej/opsim/db/ewok_1003_sqlite.db'
    opsdb = OpsimDatabase(dbFile)

    hardware, system, darksky = setup_photUtils()

    cols = ['filter', 'filtSkyBrightness', 'FWHMeff', 'visitExpTime', 'airmass', 'fiveSigmaDepth']
    # Loop through each bandpass and examine all m5 values at low airmass. (just using low airmass because
    #  the atmosphere we use in the system bandpass is for X=1.0, so high airmass would be unfair comparison).
    for f in ('u', 'g', 'r', 'i', 'z','y'):
        sqlconstraint = 'airmass<1.05 and filter="%s"' %(f)
        data = opsdb.fetchMetricData(cols, sqlconstraint)
        m5_phot = calc_m5_photUtils(hardware, system, darksky, data['filter'], data['filtSkyBrightness'],
                                    data['FWHMeff'], data['visitExpTime'], data['airmass'])
        m5_ops, m5_ops_x1 = calc_m5_opsim(data['filter'], data['filtSkyBrightness'], data['FWHMeff'], data['visitExpTime'], data['airmass'])
        m5_pre = data['fiveSigmaDepth']

        plt.figure()
        plt.plot(m5_phot, m5_ops, 'k.')
        plt.title('%s band' %f)
        plt.xlabel('m5 photUtils')
        plt.ylabel('m5 ops')

        plt.figure()
        plt.plot(m5_pre, m5_ops, 'k.')
        plt.title('%s band' %f)
        plt.xlabel('m5 database')
        plt.ylabel('m5 ops')
        print 'done with', f

    plt.show()




