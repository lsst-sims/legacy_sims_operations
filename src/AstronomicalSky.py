#!/usr/bin/env python

"""
AstronomicalSky

Inherits from: LSSTObject : object

Class Description
AstronomicalSky keeps track of the state of the sky at any given point 
during the simulation. It stores/computes the hephemeris tables for the 
main astronomical bodies (the Moon, Sun etc.) as well as the visibility
of any given field.

All the methods defined here assume that the telescope is located at
self.longitude_RAD, self.latitude_RAD and self.height.


Method Types
Constructor/Initializers
- __init__

Sun, Moon etc.
- getPlanetPosition
- getPlanetDistance
- getSunriseSunset
- getMoonPhase

Geometry
- getDistance

Visibility
- isVisible

Calculations
- getSkyBrightness
- getNightMidpoint


Select/Discard Fileds
- selectVisible
- selectEmpty
- select
"""



from utilities import *
from LSSTObject import *



class AstronomicalSky (LSSTObject):
    # Class variables
    PLANETS = {'Sun': 0,
               'Mercury': 1,
               'Venus': 2,
               'Moon': 3,
               'Mars': 4,
               'Jupiter': 5,
               'Saturn': 6,
               'Uranus': 7,
               'Neptune': 8,
               'Pluto': 9}
    
    
    def __init__ (self,
		  lsstDB, 
                  obsProfile,
                  date, 
                  sessionID,
                  dbTableDict,
                  configFile=DefaultASConfigFile,
                  log=False, 
                  logfile='./AstronomicalSky.log',
                  verbose=-1):
        """
        Standard initializer.
        
	lsstDB	    LSST DB access object        
	obsProfile  observatory profile consisting of:
                    (longitude_RAD,latitude_RAD,elev_M,epoch_MJD) where:
                    longitude_RAD:  longitude West of observatory (radians)
                    latitude_RAD:  latitude North of observatory (radians)
                    elev_M:   height of observatory (meters above sea level)
                    epoch_MJD: zero point of date system (MJD). If we want to 
                        have realistic ephemeris calculations, we will 
                        need to convert our simulated year to a real year. 
                        This is equivalent to specifying a real date (e.g. 
                        Jan. 1 2005, but espressed as MJD) that will be 
                        mapped to t=0 in our simulation. epoch defaults to
                        53371. (which corresponds to 2005-01-01T00:00:00.)
                    pressure:
                    temperature:
                    relativeHumidity:
        date:       date, in seconds from January 1st (start of the 
                    simulated year).
        dbTableDict names of all DB tables for this simulation
        configFile  configuration filename for this module
        log:        False if not set, else: log = logging.getLogger("...")
        logfile:    name (and path) of the desired log file (defaults
                    to './AstronomicalSky.log')
        verbose:    Log verbosity:-1=none, 0=minimal, 1=wordy, >1=verbose

        """
	self.lsstDB = lsstDB        
	self.obsProfile = obsProfile
	(self.longitude_RAD,self.latitude_RAD,self.height,self.epoch,\
            self.pressure,self.temp,self.relhum) = obsProfile
        self.simEpoch = self.epoch
        self.date = date
        
        # Read the configuration file
        config, pairs = readConfFile (configFile)

        # store config in DB
        for line in pairs:
            storeParam (lsstDB, sessionID, 0, 'AstronomicalSky', line['index'], line['key'], line['val'])

        try:
            self.wave = config['Wavelength']
        except:
            self.wave = 0.56

        # Advanced settings
        try:
            self.sbDateScale = float (config['SBDateScale'])
        except:
            self.sbDateScale = 3600.
        try:
            self.sbRAScale = float (config['SBRAScale'])
        except:
            self.sbRAScale = 7.
        try:
            self.sbDecScale = float (config['SBDecScale'])
        except:
            self.sbDecScale = 7.
        
        try:
            self.aDateScale = float (config['ADateScale'])
        except:
            self.aDateScale = 30.
        try:
            self.aRAScale = float (config['ARAScale'])
        except:
            self.aRAScale = 5.
        try:
            self.aDecScale = float (config['ADecScale'])
        except:
            self.aDecScale = 5.

	# Twilight settings
	try:
	    self.sunAltitudeNightLimit = float(config['SunAltitudeNightLimit'])
	except:
	    self.sunAltitudeNightLimit = -12

        try:
            self.sunAltitudeTwilightLimit = float(config['SunAltitudeTwilightLimit'])
        except:
            self.sunAltitudeTwilightLimit = -18

	try:
	    self.twilightBrightness = float(config['TwilightBrightness'])
	except:
	    self.twilightBrightness = 17.5
        self.fluxTwilight = 10.**((-self.twilightBrightness)/2.5)
        
        # store config to DB
#        for line in pairs:
#            storeParam (self.lsstDB, sessionID, 0, 'astroSky', line['index'], line['key'], line['val'])

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up AstronomicalSky logger"
            log = logging.getLogger("AstronomicalSky")
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.INFO)
        self.log = log
        self.logfile = logfile
        self.verbose = verbose
        
        # Caches
        self.skyBrightnessCache = {}
        self.airmassCache = {}

        self.n1dp92104 = (1. / 0.92104)
        self.log34p08  = math.log (34.08)

        return

    def computeDateProfile(self, date):
        """
        Convert Simulator seconds to an MJD and LST for observatory location
        and epoch.
        Input
            obsProfile  longitude, latitude, elevation, epoch of observatory
            date        elapsed simulation time in seconds

        Output
            dateProfile     an array containing
                date
                mjd
                lst_RAD
        """
        (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = self.obsProfile
        mjd = (float (date) / float (DAY)) + float(epoch_MJD)
        #lst_RAD = slalib.sla_gmst(mjd)  + lon_RAD
        lst_RAD = pal.gmst(mjd) + lon_RAD
	if lst_RAD < 0:
            lst_RAD += TWOPI
        return (date, mjd, lst_RAD)

    def mjd(self, date):

        mjd = (float (date) / float (DAY)) + float(self.simEpoch)

	return mjd

    def computeMoonProfile(self, date):
        """
        Precompute quantities relating to the moon used by subsequent routines

        Input
            dateProfile:    an array containing
                date
                mjd
                lst_RAD
        Output
            moonProfile:    an array containing
                moonRA_RAD
                moonDec_RAD
                moonPhase_PERCENT
        """
        (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = self.obsProfile
        mjd = (float (date) / float (DAY)) + epoch_MJD

        # Get the Moon RA/Dec  in radians
        #(moonRA_RAD,moonDec_RAD,moonDiam) =  slalib.sla_rdplan(mjd, 3, lon_RAD, lat_RAD)
        (moonRA_RAD,moonDec_RAD,moonDiam) =  pal.rdplan(mjd, 3, lon_RAD, lat_RAD)
        moonPhase_PERCENT = self.getMoonPhase(mjd)

        return(moonRA_RAD,moonDec_RAD,moonPhase_PERCENT)


    def isVisible (self, ra, dec, dateProfile, maxAirmass=2.):
        """
        Compute the visibility of a given point in the sky ()ra, dec 
        at a given point in time (date). We assume that a given 
        position on the sky is visible at a given time from a given
        location on Earth if and only if the corresponding airmass
        is less or equal than 2.
        
        Input
        ra:         RA in decimal degrees.
        dec:        Dec in decimal degrees.
        dateProfile:    current profile of date as list:
                        (date, mjd,lst_RAD) where:
                            date in seconds from Jan 1 of simulated year.
                            mjd - modified Julian date
                            lst_RAD - local sidereal time at site (radians)
        maxAirmass: airmass limit for a field to be considered visible
                    it defaults to 2.0
        
        Return
        True    if the given position is visible.
        False   otherwise.
        """
        # Compute the airmass
        (a,dummy,dummyz) = self.airmass (dateProfile, ra, dec)
        
        if (a > maxAirmass or a < 0.):
            return (False)
        else:
            return (True)
        return
    
    
    def getTwilightSunriseSunset (self, date):
        """
        Compute the time of the astronomical twilight for Sun raise 
        and set times at the location on Earth specified by 
        (self.latitude_RAD, self.longitude_RAD).
        
        Input
        date:   date in seconds from Jan 1 of the simulated year.
        
        Return
        A four-element array:
		(sunriseTime, 
		sunsetTime,
		sunriseMJD,
		sunsetMJD)
 	sunriseTime & sunsetTime are in seconds from Jan 1 of simulated year;
	sunriseMJD and sunsetMJD are MJD equivalents.
        """
        # Convert date in MJD
        mjd = (float (date) / float (DAY)) + self.simEpoch
        
        # MJD -> calendar date
        (yy, mm, dd) = mjd2gre (mjd)[:3]
        
        # Compute sunset and sunrise at twilight. Return values are in
        # decimal hours.
        s = Sun.Sun ()
        #(sunRise, sunSet) = s.sunRiseSet(yy, mm, dd, 
        #                        self.longitude_RAD * RAD2DEG, self.latitude_RAD * RAD2DEG)
        # Following set to nauticalTwilight
        (sunRise, sunSet) = s.__sunriset__(yy, mm, dd,
                                self.longitude_RAD * RAD2DEG,
                                self.latitude_RAD * RAD2DEG,
				self.sunAltitudeNightLimit, 0)
#                                -12.0, 0)
        (sunRiseTwil, sunSetTwil) = s.__sunriset__(yy, mm, dd, 
                                self.longitude_RAD * RAD2DEG,
                                self.latitude_RAD * RAD2DEG,
				self.sunAltitudeTwilightLimit, 0)
#                                -18.0, 0)
        
        # Compute MJD values for sunrise and sunset
        sunSetMJD = int (mjd) + (sunSet / 24.)
        sunRiseMJD = int (mjd) + (sunRise / 24.)
        sunSetTwilMJD = int (mjd) + (sunSetTwil / 24.)
        sunRiseTwilMJD = int (mjd) + (sunRiseTwil / 24.)
        
        # MJD -> simulated seconds
        sunsetDate = (sunSetMJD - self.simEpoch) * float (DAY)
        sunriseDate = (sunRiseMJD - self.simEpoch) * float (DAY)
        sunsetTwilDate = (sunSetTwilMJD - self.simEpoch) * float (DAY)
        sunriseTwilDate = (sunRiseTwilMJD - self.simEpoch) * float (DAY)
        self.log.info("getTwilightSunriseSunset:date:%d mjd:%f sunriseMJD:%f sunsetMJD:%f sunriseDate:%f sunsetDate:%f" % (date,mjd,sunRiseMJD,sunSetMJD,sunriseDate,sunsetDate))
        self.log.info("getTwilightSunriseSunset:date:%d mjd:%f sunriseTwilMJD:%f sunsetTwilMJD:%f sunriseTwilDate:%f sunsetTwilDate:%f" % (date,mjd,sunRiseTwilMJD,sunSetTwilMJD,sunriseTwilDate,sunsetTwilDate))

        return ((sunriseDate,sunsetDate,sunRiseMJD,sunSetMJD, sunriseTwilDate,sunsetTwilDate))
        
    def getIntTwilightSunriseSunset (self, date):

	(sunriseDate,sunsetDate,sunRiseMJD,sunSetMJD, sunriseTwilDate,sunsetTwilDate) = self.getTwilightSunriseSunset(date)
	return (int(sunriseDate),int(sunsetDate),sunRiseMJD,sunSetMJD,int(sunriseTwilDate),int(sunsetTwilDate))

    def computeTwilightProfile(self, date):

	(sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = self.getTwilightSunriseSunset(date)

	return (sunRiseTwil, sunSetTwil)


    def getNightMidpoint(self, date):

        """
        Compute the midpoint between sunset and sunrise at the location on 
        Earth specified by (self.latitude_RAD, self.longitude).
        
        Input
        date:   date in seconds from Jan 1 of the simulated year.
        
        Return
        A two-element array of the form (sunriseTime, sunsetTime). All
        the times are in seconds from Jan 1 of the simulated year.
        """
        # Convert date in MJD
        mjd = (float (date) / float (DAY)) + self.simEpoch

        (sunRise,sunSet)= self.getTwilightSunriseSunset (date)

        sunSetMJD = (sunSet / DAY) + self.simEpoch 
        sunRiseMJD = (sunRise / DAY) + self.simEpoch 
        
        
        if ( sunSetMJD > sunRiseMJD) :
            midpointMJD = sunRiseMJD +  (sunSetMJD - sunRiseMJD) / 2
        else:
            midpointMJD = sunRiseMJD +  ((sunSetMJD+1) - sunRiseMJD) / 2

        midpoint = (midpointMJD - self.simEpoch) * float(DAY)
        self.log.info("getNightMidPoint:date:%d mjd:%f sunrise:%f sunset:%f sunriseMJD:%f sunsetMJD:%f midpoint%f midpointMJD:%f" % (date,mjd,sunRise,sunSet,sunRiseMJD,sunSetMJD,midpoint,midpointMJD))
        return (midpoint)
    
    def getMoonPhase(self, mjd):
        """
        Compute phase of the Moon at a given date 
        
        Input
            mjd:  mean julian date
        Return
            Phase of the Moon at date in percent (i.e. in the range [0, 100]).
        """
        #v6moon =  slalib.sla_dmoon(mjd)
        v6moon = pal.dmoon(mjd)
        #Rmatrix =  slalib.sla_prenut(2000.0, mjd)
        Rmatrix = pal.prenut(2000.0, mjd)
        #xyzMoon2000 =  slalib.sla_dmxv(Rmatrix, v6moon)
        xyzMoon2000 = pal.dmxv(Rmatrix, v6moon)
        #(moonra, moondec)  =  slalib.sla_dcc2s(xyzMoon2000)
        (moonra, moondec)  =  pal.dcc2s(xyzMoon2000)
        #moonra =  slalib.sla_dranrm(2.0*math.pi + moonra)
        moonra =  pal.dranrm(2.0*math.pi + moonra)
        #sun12 =  slalib.sla_evp(mjd, 2000.0)
        sun12 = pal.evp(mjd, 2000.0)
        #sun3heliocentric = (-sun12[3]) 
        sun3heliocentric = sun12[3] 
        for i in range(3) :
            sun3heliocentric[i] *= -1
        #(sunra, sundec) =  slalib.sla_dcc2s(sun3heliocentric)
        (sunra, sundec) =  pal.dcc2s(sun3heliocentric)
        #sunra =  slalib.sla_dranrm(2.0*math.pi + sunra)
        sunra =  pal.dranrm(2.0*math.pi + sunra)
        #moonsunsep =  slalib.sla_dsep(sunra, sundec, moonra, moondec)
        moonsunsep =  pal.dsep(sunra, sundec, moonra, moondec)
        phase = ((1.0 - math.cos(moonsunsep))/2.0) * 100

        return (phase)
    
    def getPlanetPosition (self, planet, date):
        """
        Compute the position (RA, Dec) of a given Solar System body 
        (planet) at a given date.
        
        Input
        planet      the name of the Solar System body of interest. 
                    Valid values are:
                    Sun, Moon
        date        date in seconds from Jan 1 of the simulated year.
        
        Return
        (RA, Dec)   a two-element array. RA and Dec in radians
        
        Raise
        Exception if planet is not supported.
        """
        # Convert date in MJD
        mjd = (float (date) / float (DAY)) + self.simEpoch
        
        #(ra_RAD, dec_RAD, diam) = slalib.sla_rdplan (mjd, self.PLANETS[planet], self.longitude_RAD, self.latitude_RAD)
        (ra_RAD, dec_RAD, diam) = pal.rdplan (mjd, self.PLANETS[planet], self.longitude_RAD, self.latitude_RAD)
        return ((ra_RAD, dec_RAD))
   
    def  getSunAltAz(self, dateProfile):
        
        (date, mjd, lst_RAD) = dateProfile
                
        (ra_RAD, dec_RAD) = self.getPlanetPosition('Sun',date)
        lha_RAD = lst_RAD - ra_RAD
        #(az_RAD,d1,d2,alt_RAD,d4,d5,d6,d7,d8) = slalib.sla_altaz (lha_RAD,dec_RAD,self.latitude_RAD)
        (az_RAD,d1,d2,alt_RAD,d4,d5,d6,d7,d8) = pal.altaz (lha_RAD,dec_RAD,self.latitude_RAD)
        return (alt_RAD,az_RAD)
        
    def getPlanetDistance (self, planet, target, date):
        """
        Compute the distance between a given Solar System body 
        (planet) and a position on the sky (target) at a given date.
        
        Input
        planet      the name of the Solar System body of interest. 
                    Valid values are:
                    Sun, Moon
        target      (RA, Dec) a two-element array. RA and Dec in radians
        date        date in seconds from Jan 1 of the simulated year.
        
        Return
        distance    distance between planet and target in radians
        """
        # Convert date in MJD
        mjd = (float (date) / float (DAY)) + self.simEpoch
        
        # planet RA/Dec in radian
        #(planetRA_RAD, planetDec_RAD, diam) = slalib.sla_rdplan (mjd, 
        #                                     self.PLANETS[planet],
        #                                     self.longitude_RAD,
        #                                     self.latitude_RAD)
        (planetRA_RAD, planetDec_RAD, diam) = pal.rdplan (mjd,
                                             self.PLANETS[planet],
                                             self.longitude_RAD,
                                             self.latitude_RAD)
        #slaDist_RAD = slalib.sla_dsep(target[0],target[1],
        #                          planetRA_RAD,planetDec_RAD)
        slaDist_RAD = pal.dsep(target[0], target[1], planetRA_RAD,planetDec_RAD)
        #print "getPlanetDistance: slaDist_RAD:%f" % (slaDist_RAD)
        return (slaDist_RAD)
    
    
    def getDistance (self, target1, target2):
        """
        Compute the distance between a two given sets of coordinates.
        
        Input
        target1     (RA, Dec) a two-element array. RA and Dec in radians
        target2     (RA, Dec) a two-element array. RA and Dec in radians
        
        Return
        The distance between target1 and target2 in radians
        """
        # Make sure that the two points are not the same
        if (target1[0] == target2[0] and
            target1[1] == target2[1]):
            return (0.)
        
        #slaDist_RAD = slalib.sla_dsep(target1[0],target1[1],
        #                              target2[0],target2[1])
        slaDist_RAD = pal.dsep(target1[0],target1[1],
                                      target2[0],target2[1])

        return (slaDist_RAD)
    
    
    def selectVisible (self, targets, date):
        """
        Given a list of (RA, Dec) couples and a date, select the 
        targets that fall above the local horizon.
        
        Input
        targets     an array of (RA, Dec) two-element arrays. RA and
                    Dec both in decimal degrees.
        date        date in seconds from Jan 1 of the simulated year.
        
        Return
        An array of (RA, Dec) two-element arrays. RA and Dec both in 
        decimal degrees.
        """
        visible = []
        
        for (ra, dec) in targets:
            if (self.isVisible (ra, dec, date)):
                visible.append ((ra, dec))
        return (visible)
    
    
    def selectEmpty (self, targets, planets, date):
        """
        NOT IMPLEMENTED YET
        Given a list of (RA, Dec) couples the names of Solar System 
        bodies to avoid (and the corresponding minimum distance) and a 
        date, select the targets that do not fall in any of the so
        defined avoidance zones.
        
        Input
        targets     an array of (RA, Dec) two-element arrays. RA and
                    Dec both in decimal degrees.
        planets     a dictionary of the form 
                    planet: distance
                    See self.getPlanetPosition() for the definition of 
                    planet. distance in decimal degrees.
        date        date in seconds from Jan 1 of the simulated year.
        
        Return
        An array of (RA, Dec) two-element arrays. RA and Dec both in 
        decimal degrees.
        """
        return (targets)
    
    
    def select (self, targets, planets, date):
        """
        NOT IMPLEMENTED YET
        Convenience method for self.selectVisible() AND 
        self.selectEmpty()
        
        Input
        targets     an array of (RA, Dec) two-element arrays. RA and
                    Dec both in decimal degrees.
        planets     a dictionary of the form 
                    planet: distance
                    See self.getPlanetPosition() for the definition of 
                    planet. distance in decimal degrees.
        date        date in seconds from Jan 1 of the simulated year.
        
        Return
        An array of (RA, Dec) two-element arrays. RA and Dec both in 
        decimal degrees.
        """
        return (targets)
    
    def getSkyBrightness (self, 
                          fieldID,
                          ra,
                          dec,
                          targetAlt_RAD,
                          dateProfile, 
                          moonProfile,
			  twilightProfile,
                          extinction=0.172,
                          skyBrightness=21.587):
        """
        Estimate the correction to be applied to the sky brightness 
        due to moonlight.
        
        The calculation is based on Krisciunas and Schaaefer 1991 PASP
        103, 1033. This model has a nominal accuracy of 8%-23%.
        
        It is important that both extinction and skyBrightness are in
        the same passband.
        
        Input:
        fieldID:        id of target
        ra:             target's ra in dec degrees
        dec:            target's dec in dec degrees
        targetAlt_RAD:  target elevation in radians
        dateProfile:    current profile of date as list:
                        (date, mjd,lst_RAD) where:
                            date in seconds from Jan 1 of simulated year.
                            mjd - modified Julian date
                            lst_RAD - local sidereal time at site (radians)
        extinction:     the mean value of the extinction coefficient
                        (mag/airmass).
        skyBrightness:  average dark sky brightness at the zenith
                        (mag/arcsec^2)
        moonProfile:    current profile of the moon as list:
                        (moonRA_RAD,moonDec_RAD,
                         moonPhase_PERCENT)
        
        Return
        (totBrightness, distance2moon, moonAlt_RAD, brightProfile)
        where 
            totBrightness - brightness of the sky (mag/arcsec^2) 
                at the given position taking into consideration the 
                moon presence
            distance2moon - distance (degrees) between the moon and target
            moonAlt_RAD  - moon altitude (radians)
        """
        (date, mjd, lst_RAD) = dateProfile
        (moonRA_RAD,moonDec_RAD,moonPhase_PERCENT) = moonProfile

        # Compute moon altitude in radians
        moonha_RAD = lst_RAD - moonRA_RAD
        #(moonAz_RAD,d1,d2,moonAlt_RAD,d4,d5,d6,d7,d8) = \
        #        slalib.sla_altaz(moonha_RAD, moonDec_RAD, self.latitude_RAD)
        (moonAz_RAD,d1,d2,moonAlt_RAD,d4,d5,d6,d7,d8) = \
                pal.altaz(moonha_RAD, moonDec_RAD, self.latitude_RAD)
        moonAlt_DEG = moonAlt_RAD * RAD2DEG

        # compute moon's zenith distance
        if moonAlt_RAD < 0. :
                moonZD_RAD = 1.5707963
        else:
                moonZD_RAD = 1.5707963 - moonAlt_RAD
        moonZD_DEG = moonZD_RAD * RAD2DEG

        # Extinction coefficient
        k = extinction
        
        # Compute the phase angle given the illuminated fraction
        # formula from http://astro.ft.uam.es/TJM/tjm/webpaginas/practicas/ephemeris/moon.js
        alpha = math.acos ( 2. * moonPhase_PERCENT/100. - 1.) * RAD2DEG
        alpha = normalize (alpha, min=0., max=180., degrees=True)
        
        #distance2moon_RAD = slalib.sla_dsep (moonRA_RAD, moonDec_RAD,
        #                                     ra*DEG2RAD,dec*DEG2RAD)
        distance2moon_RAD = pal.dsep (moonRA_RAD, moonDec_RAD,
                                             ra*DEG2RAD,dec*DEG2RAD)

        distance2moon_DEG = distance2moon_RAD * RAD2DEG
        
        # Altitude -> Zenith distance (degrees)
        targetZD_DEG = 90. - (targetAlt_RAD * RAD2DEG)

        # Compute Raileigh scattering
        rs = (10. ** 5.36) * (1.06 + (math.cos (distance2moon_RAD)) ** 2.)
        
        # Compute Mie scattering
        if (distance2moon_DEG > 10.):
            ms = 10. ** (6.15 - (distance2moon_DEG / 40.))
        else:
            ms = 6.2E7 / (distance2moon_DEG ** 2.)
        
        # Compute illumninace of the Moon
        i = 10. ** (-0.4 * (3.84 + 0.026 * abs (alpha) + 4.E-9 * (alpha) ** 4.))
        
        # Compute optical pathlength (in units of airmass) as a 
        # function of the Zenith Distance (ZD)
        x = lambda z: (1. - 0.96 * (math.sin (z * DEG2RAD)) ** 2.) ** -0.5
        
        # Put all together (nanoLamberts)!

        moonBr = (rs + ms) * i * 10. ** (-0.4 * k * x (moonZD_DEG))
        moonBr *= (1. - 10. ** (-0.4 * k * x (targetZD_DEG)))

        #  Taper brightness to 0, at moon altitude = self.sunAltitudeNightLimit
        if moonAlt_DEG < self.sunAltitudeNightLimit:
            moonBr = 0.
        elif moonAlt_DEG < 0.  and  moonAlt_DEG >= self.sunAltitudeNightLimit :
            moonBr *= (1 - moonAlt_DEG / self.sunAltitudeNightLimit)
        
        # Now, compute the dark sky brightness (in nanoLamberts) at
        # the Zenith from the same value in mag/arcsec^s
        skyBrightness = 34.08 * math.exp (20.7233 - 0.92104 * skyBrightness)
        
        # ... and at our position in the sky (targetZD_DEG)
        skyBr = skyBrightness * x (targetZD_DEG) * 10. ** (-0.4 * k * 
                                    (x (targetZD_DEG) - 1.))
        
        # Add the brightness of the moon to that of the dark sky (nanoLamberts)
        totBr = moonBr + skyBr
        
        # Transform it into mag/arcsec^2
#        totBr = (1. / 0.92104) * math.log (34.08 * math.exp (20.7233) / totBr)
        totBr = self.n1dp92104 * (self.log34p08 + 20.7233 - math.log(totBr))
        
	(sunriseTwilDate,sunsetTwilDate) = twilightProfile

        # We are in twilight so correct brightness
	if (date < sunsetTwilDate) or (date > sunriseTwilDate):
            totBr = -2.5*math.log10( 10.**((-totBr)/2.5) + self.fluxTwilight)

        brightProfile = alpha, k, rs, ms, i, moonBr, skyBr

        return (totBr,distance2moon_RAD,moonAlt_RAD, brightProfile)
   

    def airmass (self, dateProfile, ra, dec):
        """
        Compute the airmass of (ra, dec) at date with respect of the
        location of the observatory (defined by self.latitude_RAD etc.).
        
        The routine works for Zenith distances less or equal than
        87.1469 degrees (1.521 radians).
        
        In order to speed up computation, we implement a caching 
        strategy. The result of each computation is stored in a cache
        (self.skyBrightnessCache). This cache is implemented as a hash 
        table with an alphanumeric key. Every time this method is 
        called the appropriate key is generated. With this key we check
        the cache and, if possible, return the cached answer.
        
        The choice of key generation algorithm is quite important as it
        allows for approximations in the way the sky brightness is 
        computed. In particular, it allows users to compute the sky 
        brightness on a low resolution spatial and temporal grid.
        
        The key is, infact, built as
        targetRA_targetDec_date_extinction_skyBrightness
        
        The choice of the precision for each of these five quantities
        determines the resolution of the computation.
        
        Right now, the resolution is as follows
        RA          5 degrees
        Dec         5 degrees
        date        30 seconds
        
        
        Input
            dateProfile:    profile of date as list, (date, mjd,lst_RAD) where:
                                date in seconds from Jan 1 of simulated year.
                                mjd - modified Julian date
                                lst_RAD - local sidereal time at site (radians)
            ra                  RA (decimal degrees).
            dec                 Dec (decimal degrees).
        
        Output
            airmass (float)
            ailtitude (float) in radians
        """
        (date, mjd, lst_RAD) = dateProfile
        # Calculate the low resolution input values
#        ra_RND = round (ra / self.aRAScale) * self.aRAScale
#        dec_RND = round (dec / self.aDecScale) * self.aDecScale
#        t = int (round (date / self.aDateScale)) * self.aDateScale
        
        # Do we have the answer in the cache?
#        key = '%.02f_%.02f_%d' % (ra_RND, dec_RND, t)
#        try:
#            (airmass,alt_RAD,az_RAD) = self.airmassCache[key]
            # print 'AstronomicalSky::airmass() cache hit: %s ra:%f dec:%f date:%f am:%f' % ( key,ra,dec,date,airmass)
#            return (airmass,alt_RAD,az_RAD)
#        except:
            # print ('AstronomicalSky::airmass() cache miss')
#            pass
        
        # Compute local Hour angle  (radian)
        lha_RAD = lst_RAD - ra * DEG2RAD
        
        # Compute altitude 
        #(az_RAD,d1,d2,alt_RAD,d4,d5,pa_RAD,d7,d8) = slalib.sla_altaz (lha_RAD,
        #                           dec * DEG2RAD,
        #                           self.latitude_RAD)
        (az_RAD,d1,d2,alt_RAD,d4,d5,pa_RAD,d7,d8) = pal.altaz (lha_RAD,
                                   dec * DEG2RAD,
                                   self.latitude_RAD)

        # Altitude -> Zenith distance (radian)
        zd_RAD = 1.5707963 - alt_RAD
        # Airmass
        #am = slalib.sla_airmas (zd_RAD)
        am = pal.airmas(zd_RAD)

        #print "t: %d raDEG:%f decDEG:%f mjd:%f lstRAD:%f lhaDEG:%f lha_RAD:%f altRAD:%f zdRAD:%f am:%f" % (date,ra,dec,mjd,lst_RAD,lha,lha_RAD,alt_RAD,zd_RAD,am)
        
        # Update the cache
#        self.airmassCache[key] = (am,alt_RAD,az_RAD)
        return (am,alt_RAD,az_RAD,pa_RAD)

    def airmasst (self, date, ra, dec):

        dateProfile = self.computeDateProfile(date)

        return self.airmass(dateProfile, ra, dec)


    def computeMoonProfile(self, date):
        """
        Precompute quantities relating to the moon used by subsequent routines

        Input
            dateProfile:    an array containing
                date
                mjd
                lst_RAD
        Output
            moonProfile:    an array containing
                moonRA_RAD
                moonDec_RAD
                moonPhase_PERCENT
        """
        (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = self.obsProfile
        mjd = (float (date) / float (DAY)) + epoch_MJD

        # Get the Moon RA/Dec  in radians
        #(moonRA_RAD,moonDec_RAD,moonDiam) =  slalib.sla_rdplan(mjd,
        #                                            3,
        #                                            lon_RAD,
        #                                            lat_RAD)
        (moonRA_RAD,moonDec_RAD,moonDiam) = pal.rdplan(mjd,
                                                    3,
                                                    lon_RAD,
                                                    lat_RAD)

        moonPhase_PERCENT = self.getMoonPhase(mjd)

        return(moonRA_RAD,moonDec_RAD,moonPhase_PERCENT)


    def computeMoonProfileAltAz(self, date):
        """
        Precompute quantities relating to the moon used by subsequent routines

        Input
            dateProfile:    an array containing
                date
                mjd
                lst_RAD
        Output
            moonProfile:    an array containing
                moonRA_RAD
                moonDec_RAD
                moonPhase_PERCENT
        """
        (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = self.obsProfile
        mjd = (float (date) / float (DAY)) + epoch_MJD
        #lst_RAD = slalib.sla_gmst(mjd)  + lon_RAD
        lst_RAD = pal.gmst(mjd) + lon_RAD

        (moonRA_RAD, moonDec_RAD, moonPhase_PERCENT) = self.computeMoonProfile(date)

        # Compute moon altitude in radians
        moonha_RAD = lst_RAD - moonRA_RAD
        #(moonAz_RAD,d1,d2,moonAlt_RAD,d4,d5,d6,d7,d8) = \
        #        slalib.sla_altaz(moonha_RAD, moonDec_RAD, self.latitude_RAD)
        (moonAz_RAD,d1,d2,moonAlt_RAD,d4,d5,d6,d7,d8) = \
                 pal.altaz(moonha_RAD, moonDec_RAD, self.latitude_RAD)


	return (moonRA_RAD, moonDec_RAD, moonPhase_PERCENT, moonAlt_RAD, moonAz_RAD)
    
    def getHAforAirmass(self, airmass):
	"""
	Given an airmass, this function calculates the
	corresponding HA in the west, in HOUR units.
	"""

        zd_airmass = math.acos(1.0/airmass)
        #(ha_RAD, dec_RAD)=slalib.sla_dh2e(-math.pi/2, math.pi/2-zd_airmass, self.latitude_RAD)
        (ha_RAD, decRAD) = pal.dh2e(-math.pi/2, math.pi/2-zd_airmass, self.latitude_RAD)

        return 12.0*ha_RAD/math.pi
    
    def localSiderealTime (self, mjd, longitude_RAD):
        """
        Given a date in MJD and a longitude on the Earth, compute the 
        local sidereal time at that meridian.
        
        Input
        mjd         Modified Julias Day in days and fractions of a day.
        longitude_RAD   longitude North in radians
        
        Output
        local Sidereal Time (float) in radians
        """
        ## LSST convention is W is negative, East is positive
        #lst_RAD = slalib.sla_gmst(mjd)  + longitude_RAD
        lst_RAD = pal.gmst(mjd) + longitude_RAD       
 
        return (lst_RAD)
    
    
    def altitude (self, latitude_RAD, dec_RAD, hourAngle_RAD):
        """
        Compute the Altitude given latitude, declination and hour 
        angle.
        
        Input
        latitude_RAD    latitude West in radians
        dec_RAD         declination in radians
        hourAngle_RAD   Hour Angle in radians
        
        Return
        Altitude in radians (float)
        """
        # Compute azimuth and altitude
        #(az_RAD,d1,d2,alt_RAD,d4,d5,d6,d7,d8) = slalib.sla_altaz (hourAngle_RAD, 
        #                           dec_RAD, 
        #                           latitude_RAD)
        (az_RAD,d1,d2,alt_RAD,d4,d5,d6,d7,d8) = pal.altaz (hourAngle_RAD, 
                                   dec_RAD, 
                                   latitude_RAD)

        # Fetch altitude from result (radians)
        return (alt_RAD )
    
    
    def azimuth (self, latitude_RAD, dec_RAD, hourAngle_RAD):
        """
        Compute the Azimuth given latitude, declination and hour 
        angle.
        
        Input
        latitude_RAD    latitude West in radians
        dec_RAD         declination in radians
        hourAngle_RAD   Hour Angle in radians
        
        Return
        Azimuth in radians (float)
        """
        # Compute azimuth and altitude
        #(az_RAD,d1,d2,alt_RAD,d4,d5,d6,d7,d8) = slalib.sla_altaz (hourAngle_RAD, 
        #                           dec_RAD, 
        #                           latitude_RAD)
        (az_RAD,d1,d2,alt_RAD,d4,d5,d6,d7,d8) = pal.altaz (hourAngle_RAD, 
                                   dec_RAD, 
                                   latitude_RAD)

        # Fetch azimuth from result (radians) 
        return (az_RAD )
    
    
    def flushCache (self):
        """
        Flush the in-memory caches
        """
        self.skyBrightnessCache = {}
        self.airmassCache = {}
        
        # Find out which variables to flush
        # for var in self.__dict__.keys ():
        #     if (len (var) >= 5 and var[-5:] == 'Cache'):
        #         eval ('self.%s = {}' % (var))
        return

# 
# UNIT TESTS
# 
if (__name__ == '__main__'):
    import unittest
    
    class KnownValues (unittest.TestCase):
        """
        Make sure that we get what we expect.
        """
        ctioHeight = 2215.
        ctioLat = -30.16527778
        ctioLon = 70.815
        ctioEpoch = 53371.              # 2005-01-01T00:00:00.0
        
        knownIsVisibleValues = (((58.8264, -2.3188, 53371.), True), 
                               ((276.4457, 32.0771, 53451.), False), 
                               ((40.7232, 57.6051, 53531.), False), 
                               ((53.1727, 26.8857, 53611.), False), 
                               ((114.9067, 61.2719, 53691.), False), 
                               ((17.6506, 67.2208, 53771.), False), 
                               ((287.6387, 39.6601, 53851.), False), 
                               ((269.3325, -77.3260, 53931.), True), 
                               ((102.8912, 24.9691, 54011.), False), 
                               ((191.2703, 33.9905, 54091.), False), 
                               ((150.9973, 36.0769, 54171.), False), 
                               ((2.9198, -64.8521, 54251.), False), 
                               ((307.8593, 43.8667, 54331.), False), 
                               ((30.6832, -84.1524, 54411.), True), 
                               ((174.6318, -17.9298, 54491.), False))
        knownPositionValues = ((('Sun', 53371.), (281.5976, -23.0108)), 
                               (('Sun', 53451.), (1.3424, 0.5843)), 
                               (('Sun', 53531.), (78.2791, 23.0045)), 
                               (('Sun', 53611.), (157.5510, 9.4017)), 
                               (('Sun', 53691.), (232.3738, -18.9518)), 
                               (('Sun', 53771.), (318.4933, -16.0295)), 
                               (('Sun', 53851.), (33.3250, 13.4004)), 
                               (('Sun', 53931.), (114.1818, 21.5813)), 
                               (('Sun', 54011.), (188.8629, -3.8216)), 
                               (('Sun', 54091.), (269.9799, -23.4394)), 
                               (('Sun', 54171.), (351.7554, -3.5559)), 
                               (('Sun', 54251.), (67.5011, 21.8311)), 
                               (('Sun', 54331.), (147.9202, 12.9680)), 
                               (('Sun', 54411.), (221.7254, -16.0960)), 
                               (('Sun', 54491.), (307.7511, -18.9209)))
        knownSelectVisibleValues = ((((58.8264, -2.3188), 
                                      (276.4457, 32.0771), 
                                      (40.7232, 57.6051),
                                      (53.1727, 26.8857),
                                      (114.9067, 61.2719),
                                      (17.6506, 67.2208),
                                      (287.6387, 39.6601),
                                      (269.3325, -77.3260),
                                      (102.8912, 24.9691),
                                      (191.2703, 33.9905),
                                      (150.9973, 36.0769),
                                      (2.9198, -64.8521),
                                      (307.8593, 43.8667),
                                      (30.6832, -84.1524),
                                      (174.6318, -17.9298)), 53931.),
                                     [(269.3325, -77.3260),
                                      (174.6318, -17.9298)])
        knownDistanceValues = ((([58.8256, -2.3205], [276.4457, 32.0771]), 133.7969),
                               (([276.4457, 32.0771], [40.7232, 57.6051]), 78.8871),
                               (([40.7232, 57.6051], [53.1727, 26.8857]), 31.9572),
                               (([53.1727, 26.8857], [114.9067, 61.2719]), 53.1611),
                               (([114.9067, 61.2719], [17.6506, 67.2208]), 38.2784),
                               (([17.6506, 67.2208], [287.6387, 39.6601]), 53.9571),
                               (([287.6387, 39.6601], [269.3325, -77.3260]), 117.5371),
                               (([269.3325, -77.3260], [102.8912, 24.9691]), 127.2431),
                               (([102.8912, 24.9691], [191.2703, 33.9905]), 75.0928),
                               (([191.2703, 33.9905], [150.9973, 36.0769]), 32.8071),
                               (([150.9973, 36.0769], [2.9198, -64.8521]), 145.5451),
                               (([2.9198, -64.8521], [307.8593, 43.8667]), 116.8614),
                               (([307.8593, 43.8667], [30.6832, -84.1524]), 132.8594),
                               (([174.6318, -17.9298], [174.6318, -17.9298]), 0.0000))
        knownPlanetDistanceValues = ((('Sun', [53.1727, 26.8857], 53371.), 136.1826),
                                     (('Sun', [17.6506, 67.2208], 53451.), 67.6052),
                                     (('Sun', [287.6387, 39.6601], 53531.), 111.6036),
                                     (('Sun', [269.3325, -77.3260], 53611.), 103.8685),
                                     (('Sun', [102.8912, 24.9691], 53691.), 133.0209),
                                     (('Sun', [191.2703, 33.9905], 53771.), 129.5261),
                                     (('Sun', [150.9973, 36.0769], 53851.), 103.2181),
                                     (('Sun', [2.9198, -64.8521], 53931.), 118.4412),
                                     (('Sun', [307.8593, 43.8667], 54011.), 113.2595),
                                     (('Sun', [174.6318, -17.9298], 54091.), 87.6448))
        knownSkyBrightness = ((((151.24782, -28.263821), -5436.7006944, 0.172, 21.587), 19.813),
                              (((130.34890, -28.277804), 48247.2951389 - ctioEpoch, 0.172, 21.587), 18.907),
                              (((140.50113, -38.762811), 48260.3381944 - ctioEpoch, 0.172, 21.587), 20.141),
                              (((156.37750, -8.9140565), 48260.3437500 - ctioEpoch, 0.172, 21.587), 19.605),
                              (((147.28862, -10.825619), 48260.3493056 - ctioEpoch, 0.172, 21.587), 19.684))
        # knownSelectVisibleValues = ((, ), )
        # knownSelectEmptyValues = ((, ), )
        # knownSelectValues = ((, ), )
        
        def testGetPlanetPosition (self):
            """Testing getPlanetPosition..."""
            sky = AstronomicalSky (self.ctioLat, 
                                   self.ctioLon, 
                                   self.ctioHeight, 
                                   0., self.ctioEpoch)
            
            for (input, expectedResult) in self.knownPositionValues:
                date = (input[1] - self.ctioEpoch) * DAY
                
                result = sky.getPlanetPosition (input[0], date)
                
                deltaRA = abs (expectedResult[0] - result[0])
                deltaDec = abs (expectedResult[1] - result[1])
                
                # Let's be optimistic and assume 10% accuracy
                deltaRAMax = abs (expectedResult[0] * 0.1)
                deltaDecMax = abs (expectedResult[1] * 0.1)
                
                self.assert_ (deltaRA < deltaRAMax)
                self.assert_ (deltaDec < deltaDecMax)
            return
        
        def testIsVisible (self):
            """Testing isVisible..."""
            sky = AstronomicalSky (self.ctioLat, 
                                   self.ctioLon, 
                                   self.ctioHeight, 
                                   0., self.ctioEpoch)
            
            for (input, expectedResult) in self.knownIsVisibleValues:
                ra = input[0]
                dec = input[1]
                date = (input[2] - self.ctioEpoch) * DAY
                
                result = sky.isVisible (ra, dec, date)
                
                self.assertEqual (result, expectedResult)
            return
        
        def testSelectVisible (self):
            """Testing selectVisible..."""
            sky = AstronomicalSky (self.ctioLat, 
                                   self.ctioLon, 
                                   self.ctioHeight, 
                                   0., self.ctioEpoch)
            
            input = self.knownSelectVisibleValues[0]
            expectedResult = self.knownSelectVisibleValues[1]
            
            targets = input[0]
            date = (input[1] - self.ctioEpoch) * DAY
            
            result = sky.selectVisible (targets, date)
            
            self.assertEqual (result, expectedResult)
            return
        
        def testGetDistance (self):
            """Testing getDistance..."""
            sky = AstronomicalSky (self.ctioLat, 
                                   self.ctioLon, 
                                   self.ctioHeight, 
                                   0., self.ctioEpoch)
            
            for (input, expectedResult) in self.knownDistanceValues:
                target1 = input[0]
                target2 = input[1]
                
                result = sky.getDistance (target1, target2)
                
                self.assertEqual ('%.04f' % (result), 
                                  '%.04f' % (expectedResult))
            return
        
        def testGetPlanetDistance (self):
            """Testing getPlanetDistance..."""
            sky = AstronomicalSky (self.ctioLat, 
                                   self.ctioLon, 
                                   self.ctioHeight, 
                                   0., self.ctioEpoch)
            
            for (input, expectedResult) in self.knownPlanetDistanceValues:
                planet = input[0]
                target = input[1]
                date = (input[2] - self.ctioEpoch) * DAY
                
                result = sky.getPlanetDistance (planet, target, date)
                
                delta = abs (expectedResult - result)
                
                # Let's be optimistic and assume 1% accuracy
                deltaMax = expectedResult * 0.01
                self.assert_ (delta < deltaMax)
            return
        
        def testGetSkyBrightness (self):
            """
            Testing getSkyBrightness...
            
            Remember that the model has a nominal accuracy of 8%-23%.
            """
            sky = AstronomicalSky (self.ctioLat, 
                                   self.ctioLon, 
                                   self.ctioHeight, 
                                   0., self.ctioEpoch)
            
            for (input, expectedResult) in self.knownSkyBrightness:
                t = input[0]
                d = input[1] * DAY
                k = input[2]
                s = input[3]
                
                result = sky.getSkyBrightness (target=t, 
                                               date=d,
                                               extinction=k,
                                               skyBrightness=s)
                
                delta = abs (expectedResult - result)
                
                # Let's be optimistic and assume 8% accuracy
                deltaMax = expectedResult * 0.08
                try:
                    self.assert_ (delta < deltaMax)
                except:
                    if ( self.log ):
                        self.log.info ('testGetSkyBrightness: accuracy worse than 8%')
                
                # Let's assume worst-case senarion; 23% accuracy
                deltaMax = expectedResult * 0.23
                self.assert_ (delta < deltaMax)
            return
        
    
    class BadInput (unittest.TestCase):
        """
        Make sure that all the methods check for invalid or malformed
        input.
        """
        pass
    
    
    class BadOutput (unittest.TestCase):
        """
        Make sure that none of the methods return syntactically wrong
        results.
        """
        pass
    
    
    class SanityCheck (unittest.TestCase):
        """
        Make sure that methods check the semantic validity of both 
        input and output.
        """
        pass
    
    # Run the tests
    unittest.main ()
