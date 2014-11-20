#!/usr/bin/env python
import math
"""
This could be the skeleton of the ETC class. This object can be instantiated in the beginning when the simulator starts and can
be kept in the simulator structure and functions from it can be called as and when required.

modified 06Dec2007 to match the flatter y fit that was done in that version of lunemag.c
		   also realized that I had not added the .27 mag correction from UKIDDS Y -> LSST Y2
		   but the old value was only off by .05 due to a compensating change from avg -> max
		   since the 18.11 AB mag YUKIDDS is actually taken at solar max.
"""

class ETC:
    
    DEFAULT_MOON_ZENITH_ANGLE = 50
    DEFAULT_AIRMASS = 1
    DEFAULT_MOON_OBS_ANGLE = 90
    DEFAULT_LUNAR_PHASE_ANGLE = 90
    #    Types of solar phases allowed
    SOLAR_DARK_AVG = 1;
    SOLAR_DARK_MIN = 2;
    SOLAR_DARK_MAX = 3;
    
    # caching scales
    sbAltScale = 7.0       #degrees
    sbAzScale = 7.0        #degrees
    sbMJDScale = .05       #days
    sbMoonSepScale = 7.0
    skyBrightnessCache = {}

    def __init__ (self):
        """
        In this function you can read in files etc. (Constructor of the class)
        """
        return
  
        """
          bandindex    a number from 0,5 representing u,g,r,i,z,y
          MJD          A number representing the number of days 
          k            Extinction coefficient for this band, 0-1
          alt          alt/az coordinates of the observation, in degrees
          malt/maz     position of the moon in alt/az coordinates
          mphase       phase angle of the moon, from 0-180
          salt/saz     position of the sun in alt/az coordinates (not used)
          rho          moon-obs separation in degrees.  This is for testing only
     """

    def getSkyBrightnessAB(self,
                           bandindex,
                           MJD,
                           k,
                           alt,
                           az,
                           malt,
                           maz,
                           mphase,
                           saz,
                           salt,
                           moonSep=0,
                           useCache=False):
        
        
        if (useCache):
            # Calculate the low resolution input values.  These are used when caching to
            # reduce the size of the cache (at the cost of resolution)
            ext = k
            alt_RND = round (alt / self.sbAltScale) * self.sbAltScale
            az_RND = round (az / self.sbAzScale) * self.sbAzScale
            t = int (round (MJD / self.sbMJDScale)) * self.sbMJDScale
            moonSep_RND = int (round (moonSep / self.sbMoonSepScale)) * self.sbMoonSepScale
            # Do we have the answer in the cache?
            key = '%.02f_%.02f_%.04f_%.02f%.02f' % (alt_RND, az_RND, t, ext, moonSep_RND)
            try:
                # if already in the cache, just return the value
                (result) = self.skyBrightnessCache[key]
                return result
            
            except:
                pass
            

        
        # Note: a0, 3, 7, 11, n arbitrary value of rho can be specified for testing purposes.
        # moonSep = 0 in normal use, in which case it is calculated from the positions 
        if moonSep == 0:
            moonSep = self.getAngle(alt,az,malt,maz)

        
        # This formula from Krisciunas is good to 2 airmass or more
        # Note that a different formulat is used for the lunar airmass
        # which can be much closer to the horizon
        airmass = 1/math.sqrt(1 - 0.96*pow(math.cos(alt*math.pi/180.0),2))
        # Get the lunar contribution at standard airmass, lunar airmass, and moonSep,
        # and convert to the desired lunar parameters
        mmoon = self.getLunarMag(mphase, bandindex)
        Imoon = math.pow(10, -.4 * mmoon)
        if (Imoon > 0 and malt > 0):
            #  get the amount of lunar flux expected at standard airmass, rhos, and moon_airmass
            #  convert to correct moon separation
            #  <pgee> commented out scat angle) for now
            factor = self.convertObsAngle(self.DEFAULT_MOON_OBS_ANGLE, moonSep, bandindex)
            Imoon *= factor

            #  convert for extinction of the lunar light
            factor = self.convertLunarZenithAngle(self.DEFAULT_MOON_ZENITH_ANGLE, 90-malt, k)
            Imoon *= factor

            #  convert for the effect of airmass on scattered moonlight
            factor = self.convertScatteringAirmass(self.DEFAULT_AIRMASS, airmass, k)
            Imoon *= factor
        else:
            Imoon = 0

        # get the sky emission (dark) component, and correct for airmass
        mdark = self.getDarkMag(self.SOLAR_DARK_AVG, bandindex)
        Idark = math.pow(10.0, -.4 * mdark);
        factor = self.convertDark(1, airmass, k)
        Idark *= factor

        # calculate the result in AB mags
        result = (-2.5 * math.log10(Idark+Imoon))
        
        # stuff it in the cache
        if (useCache):
            self.skyBrightnessCache[key] = result;
        
        return result

    
    def getSignalToNoise(self):
        """
        We can calculate signalToNoise here (dummy value being returned)
        I have not put in the arguments here.
        """        
        signalToNoise = 10

        return (signalToNoise)

#   Utility routines used to do conversions for changes in lunar phase angle,
#   moon-observation angle, lunar elevation, and airmass of the observation

    # Relation between the amount of scattered moonlight and moon-observation angle R
    # This equation comes from a fit of the Krisciunas&Schafer formula for
    # combined Mie and Rayleigh scattering.  It is actually in flux units,
    # but opnly the variation with angle is important

    # fit of Dec 6, 2007
    def getObsAngleFactor(self, R, bandindex):
	 scatp0 = [2.5573e-01, 3.9323e-01, 2.4854e-01, 2.3688e-01, 3.1613e-01, 7.5894e-17]
	 scatp1 = [3.1554e-13, 1.7097e+00, 2.9850e+00, 4.1227e+00, 5.5089e+00, 2.7105e-18]

# version of Dec 4, 2007
#        scatp0 = [2.5573e-01, 4.1994e-01, 2.7373e-01, 2.5426e-01, 3.2310e-01, 5.6921e-17]
#        scatp1 = [3.1554e-13, 1.5633e+00, 2.8459e+00, 4.0254e+00, 5.4686e+00, 2.7105e-18]

         return scatp0[bandindex]*(1.06 + math.pow(math.cos((R*math.pi)/180.),2.0)) + scatp1[bandindex]*(math.pow(10,-R/40.0))

    
    #      Effect of changing lunar separation from R1 degrees to R2 degrees
    def convertObsAngle(self, R1, R2, bandindex):
    
        f1 = self.getObsAngleFactor(R1, bandindex)
        f2 = self.getObsAngleFactor(R2, bandindex)
        return f2/f1
    
    
    # Effect of changing the airmass from X=1 to X=airmass on the dark component
    # Using Krisciunas 1992 model (assumes emission proportional to airmass)
    # and losses due to extinction follows the usual extinction relation
    def getDarkAirmassFactor(self, airmass, k):
    
        # float k = getExtinction(bandindex)
        return math.pow(10.0, -.4 * k * (airmass - 1)) * airmass
    
    
    #   effect on dark sky from X=airmass1 to X=airmass2
    def convertDark(self, airmass1, airmass2, k):
    
        f1 = self.getDarkAirmassFactor(airmass1, k)
        f2 = self.getDarkAirmassFactor(airmass2, k)
        return f2/f1
    

    #  the airmass correction for scattered light is just 1 - extinction
    #  This is just the fraction of scattered moonlight which reaches the observer,
    #  Other geometrical effect involving the position of the moon relative
    #  to the scattering air are not included here.
    
    def getScatteringAirmassFactor(self, airmass, k): 
        return 1 - math.pow(10.0, -.4 * k * airmass)
    

    #     effect of changing from X=airmass1 to X=airmass2 on the scattered light
    def convertScatteringAirmass(self, airmass1, airmass2, k):
    
        f1 = self.getScatteringAirmassFactor(airmass1, k)
        f2 = self.getScatteringAirmassFactor(airmass2, k)
        return f2/f1
    

    #  Effect of Lunary Zenith angle on intensity of scattered moonlight
    #  This is the change from Xmoon=1 to Xmoon=sec(angle)
    #  The formula for airmass is from Kriciunas&Schafer, and is supposed
    #  to be valid even near the horizon
    def getLunarZenithAngleFactor(self, angle, k):
    
        cosa = math.cos(angle * math.pi / 180.0)
        return math.pow(10.0, -.4 * k/(cosa + .025*math.pow(2.7, -11.*cosa)))
    

    #  effect of changing the lunar zenith angle from angle1 to angle2
    def convertLunarZenithAngle(self, angle1, angle2, k):
    
        f1 = self.getLunarZenithAngleFactor(angle1, k)
        f2 = self.getLunarZenithAngleFactor(angle2, k)
        return f2/f1
    
    # get the magnitude of the sky emission part of the sky brightness
    # sphase can actually only be 1,2,or 3 (avg, min, max)
    # These values are from a study including SDSS, DLS, and Standard
    # Southern Stars, UKIDDS converted to below the sky
    def getDarkMag(self, sphase, bandindex):
        if sphase == self.SOLAR_DARK_MIN:
            aDark = [ 22.95, 22.32, 21.43, 20.40, 19.22, 18.11]	        # this is min
        elif sphase == self.SOLAR_DARK_AVG:
            aDark = [22.80, 22.20, 21.30, 20.30, 19.10, 17.96]		# this is avg
        elif sphase == self.SOLAR_DARK_MAX:
            aDark = [22.65, 22.10, 21.13, 20.12, 18.92, 17.81]		# this is max
        
	result = aDark[bandindex]
        darkToLSSTMag = [0.1757, -0.3135,-0.0081,-0.0445,0.5726,0.2735] # 0.2735, 0.1705, 0.2211, 0.5587
        result += darkToLSSTMag[bandindex]
        return result
    
    # get the lunar magnitude for a lunar phase angle of mphase,
    # based on the parameterized values for the lunar fit done
    # on Southern Standard Stars data from CTIO .9m 
    def getLunarMag(self, mphase, bandindex):
        I = self.getLunarIntensity(mphase, bandindex)
        mag = -2.5*math.log(I)/math.log(10);
        lunarToLSSTMag = [-.0621, -.0039, .0004, .0006, -.0096, -.0189]; # -.0189, -.0091, -.0135, -.0257]
        mag += lunarToLSSTMag[bandindex];
        return mag;
    
    def getLunarIntensity(self, mphase, bandindex):
        mmoon = self.getLunarFit(mphase, bandindex)
        Imoon = math.pow(10, -.4 * mmoon)
        mdark = self.getLunarFit(180, bandindex)
        Idark = math.pow(10, -.4 * mdark)
        if Imoon <= Idark:
            result = 1.0e-100        #essentially 0, but doesn't blow up Python
        else:
            result = Imoon - Idark
        return result
    
    # -------------------------------------------------------------
    
        #  these coefficients were calculated by airmag.C for Krisciunas model
        #  They are actually just dark sky at zenith values for the CTIO .9m data
        #  However, they are not used except as part of the fitting process
        #  They are very close to the alpha=180 degree values from the Luarn fit
    def getAirmassFit(self, bandindex):
        am0 = [2.2837e+01, 2.1959e+01, 2.1053e+01,  2.0057e+01, 1.8928e+01, 1.8121e+01]
        return am0[bandindex]
    
    #    These are coefficients for the second order fit of AB magnitude vs lunar phase
    #    Only the difference between the value at a given phase - value at 180 degrees
    #    is actually used.
    def getLunarFit(self, A, bandindex): 
	lunarp0 = [1.8819e+01, 1.8301e+01, 1.8938e+01, 1.9032e+01, 1.8547e+01, 1.8108e+01];
	lunarp1 = [3.5802e-02, 3.6370e-02, 2.6097e-02, 1.3086e-02, 4.4932e-03, 1.2908e-04];
	lunarp2 = [-7.6183e-05, -9.0022e-05, -8.0058e-05, -4.1280e-05, -1.3532e-05, 2.9816e-16];
	# version of Dec 4, 2007
	#lunarp0 = [1.8819e+01, 1.8301e+01, 1.8936e+01, 1.9030e+01, 1.8542e+01, 1.7992e+01]
        #lunarp1 = [3.5802e-02, 3.6371e-02, 2.6109e-02, 1.3099e-02, 4.5210e-03, 3.2448e-03]
        #lunarp2 = [-7.6183e-05, -9.0032e-05, -8.0054e-05, -4.1298e-05, -1.3541e-05, -1.4011e-05]
        return lunarp0[bandindex] + A*lunarp1[bandindex] + A*A*lunarp2[bandindex]
    
    # this extinction value is used only if there isn't one given
    # These are average values taken from CTIO from 2000-2005
    def getAverageExtinction(self, i):
        kavg = [.4837, .1756, .09398, .05958, .05217, .03]
        return kavg[i]

    # get the Angle in degrees between two alt/az coordinates
    def getAngle(self, alt1, az1, alt2, az2):
        DEG2RAD = math.pi/180
        alt1 *= DEG2RAD;
        az1 *= DEG2RAD;
        alt2 *= DEG2RAD;
        az2 *= DEG2RAD;
        dx = math.cos(az1)*math.cos(alt1) - math.cos(az2)*math.cos(alt2);
        dy = math.sin(az1)*math.cos(alt1) - math.sin(az2)*math.cos(alt2);
        dz = math.sin(alt1) - math.sin(alt2);
        d = math.sqrt(dx*dx + dy*dy + dz*dz)/2.0;
        return 2 * (math.atan2(d, math.sqrt(1-(d*d)))/DEG2RAD);
