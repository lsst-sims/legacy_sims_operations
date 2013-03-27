#!/usr/bin/env python

from LSSTObject import *
from utilities import *
from AstronomicalSky import *

class SchedulingData (LSSTObject):

    def __init__ (self,
                  configFile,
		  surveyStartTime,
		  surveyEndTime,
		  astroSky,
		  lsstDB,
		  sessionID):

	self.sky = astroSky
	self.lsstDB = lsstDB
	self.sessionID = sessionID

        config, pairs = readConfFile(configFile)

	self.cycleDuration = int(config['cycleDuration'])
	self.dt = int(config['dt'])

	self.cycleSamples = self.cycleDuration/self.dt

	self.initSurvey(surveyStartTime, surveyEndTime)

	return


    def initSurvey (self, startTime, endTime):

        # Align time to NightTime
        t = startTime
        # sunRise < sunSet
        # This is what is happening:
        #  <---------------DAY------------------->
        # --------|----------------------|-------------->
        #      sunRise                 sunSet          t
	x = self.sky.getIntTwilightSunriseSunset (t)
        (sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = x
	print sunRiseTwil
	print sunRise
	print sunSet
	print sunSetTwil

	if (t < sunRise):
            #  <---------------DAY------------------->
            # --*-----|----------------------|-------------->
            #   t  sunRise                 sunSet         t

            ## LD: need to check if we're before previous day's sunset.
            #  <---------------DAY------------------->
            # --*-----|----------------------|------------->
            #   t  sunSet                  sunRise        t
            x = self.sky.getIntTwilightSunriseSunset(t - DAY)
            (yesterday_sunRise, yesterday_sunSet, yesterday_sunRiseMJD, yesterday_sunSetMJD, yesterday_sunRiseTwil, yesterday_sunSetTwil) = x
            print yesterday_sunRiseTwil
            print yesterday_sunRise
            print yesterday_sunSet
            print yesterday_sunSetTwil

            if t < yesterday_sunSet:
                t = yesterday_sunSet

	    tonight_sunSetMJD   = yesterday_sunSetMJD
            tonight_sunSet      = yesterday_sunSet
            tonight_sunSetTwil  = yesterday_sunSetTwil
	    tonight_sunRiseTwil = sunRiseTwil
	    tonight_sunRise     = sunRise

        elif (sunRise <= t < sunSet):    # Middle of the day
            #  <---------------DAY------------------->
            # -----|-------*--------------|-------------->
            #   sunRise    t            sunSet          t
            x = self.sky.getIntTwilightSunriseSunset (t + DAY)
            (tomorrow_sunRise, tomorrow_sunSet, tomorrow_sunRiseMJD, tomorrow_sunSetMJD, tomorrow_sunRiseTwil, tomorrow_sunSetTwil) = x
            print tomorrow_sunRiseTwil
            print tomorrow_sunRise
            print tomorrow_sunSet
            print tomorrow_sunSetTwil

            t = sunSet

	    tonight_sunSetMJD   = sunSetMJD
            tonight_sunSet      = sunSet
            tonight_sunSetTwil  = sunSetTwil
            tonight_sunRiseTwil = tomorrow_sunRiseTwil
            tonight_sunRise     = tomorrow_sunRise

        elif (t >= sunSet):                 # Next night
            #  <---------------DAY------------------->
            # --------|----------------------|-----*-------->
            #      sunRise                 sunSet  t       t

	    x = self.sky.getIntTwilightSunriseSunset (t + DAY)
            (tomorrow_sunRise, tomorrow_sunSet, tomorrow_sunRiseMJD, tomorrow_sunSetMJD, tomorrow_sunRiseTwil, tomorrow_sunSetTwil) = x

            tonight_sunSetMJD   = sunSetMJD
            tonight_sunSet      = sunSet
            tonight_sunSetTwil  = sunSetTwil
            tonight_sunRiseTwil = tomorrow_sunRiseTwil
            tonight_sunRise     = tomorrow_sunRise


        midnight = (int(tonight_sunSetTwil + tonight_sunRiseTwil)/2)

	print t
	print tonight_sunSet
	print tonight_sunSetTwil
	print tonight_sunRiseTwil
	print tonight_sunRise

	self.sunProfile = {}
	self.sunProfile[0] = (tonight_sunSetMJD, tonight_sunSet, tonight_sunSetTwil, midnight, tonight_sunRiseTwil, tonight_sunRise)

#        self.initMoonPhase(midnight)

        self.startTime = int(t)
        self.endTime = endTime
        self.currentTime = int(t)
        self.extendedCycleTimes = [self.currentTime]

	night = 0
        self.sunProfile[night] = (tonight_sunSetMJD, tonight_sunSet, tonight_sunSetTwil, midnight, tonight_sunRiseTwil, tonight_sunRise)

	last_sunSetMJD  = tonight_sunSetMJD
	last_sunSet     = tonight_sunSet
	last_sunSetTwil = tonight_sunSetTwil
        self.sunProfile[night] = (tonight_sunSetMJD, tonight_sunSet, tonight_sunSetTwil, midnight, tonight_sunRiseTwil, tonight_sunRise)
	while (t < self.endTime):
	    night += 1
	    t += DAY
	    x = self.sky.getIntTwilightSunriseSunset (t)
	    (sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = x
	    midnight = int((last_sunSetTwil+sunRiseTwil)/2)
	    self.sunProfile[night] = (last_sunSetMJD, last_sunSet, last_sunSetTwil, midnight, sunRiseTwil, sunRise)
	    last_sunSetMJD  = sunSetMJD
	    last_sunSet     = sunSet
	    last_sunSetTwil = sunSetTwil
	print self.sunProfile

	self.listOfActiveFields = []

	self.nightCount = 0

	self.dateProfile = {}
	self.moonProfile = {}
	self.twilightProfile = {}
	self.alt = {}
	self.az = {}
	self.airmass = {}
	self.brightness = {}
	self.visible = {}
	self.filters = {}

        self.dateProfile[self.currentTime] = self.sky.computeDateProfile(self.currentTime)
        self.moonProfile[self.currentTime] = self.sky.computeMoonProfile(self.currentTime)
	self.initNewCycle()

	return

    def initNewCycle (self):

	indexCurrentTime = self.extendedCycleTimes.index(self.currentTime)
	indexLastTime = len(self.extendedCycleTimes)

	samplesToAdd = 2*self.cycleSamples - (indexLastTime-indexCurrentTime)

	if (samplesToAdd > 0):
	    extensionStart = int(self.extendedCycleTimes[-1] + self.dt)
	    extensionEnd = int(min(extensionStart + samplesToAdd*self.dt, self.endTime))
	extensionTimes = range(extensionStart, extensionEnd+1, self.dt)
	for t in extensionTimes:
	    self.dateProfile[t] = self.sky.computeDateProfile(t)
	    self.moonProfile[t] = self.sky.computeMoonProfile(t)
	    
#	    for field in self.listOfActiveFields:
#	        self.airmass[field][t] = self.sky.airmass(t, field)
#        	self.brightness[field][t] = self.astroSky.brightness(t, field)

	self.extendedCycleTimes += extensionTimes

	if (indexCurrentTime>0):
	    del self.extendedCycleTimes[0:indexCurrentTime]
	print self.extendedCycleTimes

	self.maxIndexTime = len(self.extendedCycleTimes)-1
	self.windowSamples = min(self.cycleSamples, len(self.extendedCycleTimes))
	self.indexTime = self.extendedCycleTimes.index(self.currentTime)

        return

    def getCycleTimes (self, newCurrentTime):

	if (newCurrentTime > self.endTime):
	    return []

	while (self.currentTime < newCurrentTime):
	    self.indexTime += 1
	    if (self.indexTime > self.maxIndexTime):
		return []
	    self.currentTime = self.extendedCycleTimes[self.indexTime]

        if (self.indexTime > self.cycleSamples):
            self.initNewCycle()

	cycleTimes = self.extendedCycleTimes[self.indexTime:self.indexTime+self.windowSamples+1]

	return cycleTimes

    def updateTargets (self, dictOfNewFields, propID, dateProfile):

	listOfNewFields = sorted(dictOfNewFields.iterkeys())
	for field in listOfNewFields:
	    if field not in self.listOfActiveFields:
		self.listOfActiveFields.append(field)
		self.alt[field] = {}
		self.az[field] = {}
		self.airmass[field] = {}
		self.brightness[field] = {}
		self.visible[field] = {}
		self.filters[field] = {}
		(ra, dec) = dictOfNewFields[field]

		night = 0
		(sunSetMJD, sunSet, sunSetTwil, midnight, sunRiseTwil, sunRise) = self.sunProfile[night]
                for t in self.extendedCycleTimes[self.indexTime:]:
		    while not (sunSet <= t < sunRise):
			night += 1
			(sunSetMJD, sunSet, sunSetTwil, midnight, sunRiseTwil, sunRise) = self.sunProfile[night]
		    twilightProfile = (sunRiseTwil, sunSetTwil)

		    (am, alt, az) = self.sky.airmasst(t, ra, dec)
		    self.alt[field][t] = alt
		    self.az[field][t] = az
		    self.airmass[field][t] = am
		    br = self.sky.getSkyBrightness(0, ra, dec, alt,
						self.dateProfile[t],
						self.moonProfile[t],
						twilightProfile)
                    self.brightness[field][t] = br
                    print ("field=%5i t=%8i airmass=%5.3f brightness=%5.3f" % (field, t, am, br[2]))

		self.lsstDB.addProposalField(self.sessionID, propID, field)

	self.listOfActiveFields.sort()

	return

if (__name__ == '__main__'):

    longitude =  -70.815
    latitude =  -30.16527778
    height =  2215.
    simEpoch =  49353.
    pressure =  1010.
    temperature =  12.
    relativeHumidity =  0.
 
    obsProfile = (longitude *DEG2RAD, latitude *DEG2RAD, height, simEpoch,pressure,temperature,relativeHumidity)

    sky = AstronomicalSky(None, obsProfile, 0, 0, None, "../conf/system/AstronomicalSky.conf", False, './AstronomicalSky.log', 0)

    data = SchedulingData('../test/SchedulingData.conf', 0, 432000, sky)

#    data.initSurvey(0,36000)

#    for time in range(0,36000,2500):
#	print time
#	print data.getCycleTimes(time)
#	print data.extendedCycleTimes


    sys.exit(0)

