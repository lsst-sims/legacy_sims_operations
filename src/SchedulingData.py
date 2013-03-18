#!/usr/bin/env python

from LSSTObject import *
from utilities import *

class SchedulingData (LSSTObject):

    def __init__ (self,
                  configFile,
		  surveyStartTime,
		  surveyEndTime,
		  astroSky):

	self.astroSky = astroSky

        config, pairs = readConfFile(configFile)

	self.cycleDuration = int(config['cycleDuration'])
	self.dt = int(config['dt'])

	self.cycleSamples = self.cycleDuration/self.dt

	self.initSurvey(surveyStartTime, surveyEndTime)

	return


    def initSurvey (self, startTime, endTime):

        self.startTime = startTime
	self.endTime = endTime
	self.currentTime = startTime
	self.extendedCycleTimes = [self.currentTime]

	self.listOfActiveFields = []
	self.airmass = {}
	self.brightness = {}
	self.visible = {}
	self.filters = {}

	self.initNewCycle()

	return

    def initNewCycle (self):

	indexCurrentTime = self.extendedCycleTimes.index(self.currentTime)
	indexLastTime = len(self.extendedCycleTimes)

	samplesToAdd = 2*self.cycleSamples - (indexLastTime-indexCurrentTime)

	if (samplesToAdd > 0):
	    extensionStart = self.extendedCycleTimes[-1] + self.dt
	    extensionEnd = min(extensionStart + samplesToAdd*self.dt, self.endTime)
	extensionTimes = range(extensionStart, extensionEnd+1, self.dt)
	for t in extensionTimes:
	    for field in self.listOfActiveFields:
	        self.airmass[field][t] = self.astroSky.airmass(t, field)
#        	self.brightness[field][t] = self.astroSky.brightness(t, field)

	self.extendedCycleTimes += extensionTimes

	del self.extendedCycleTimes[0:indexCurrentTime]

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
		self.airmass[field] = {}
		self.brightness[field] = {}
		self.visible[field] = {}
		self.filters[field] = {}
                for t in self.extendedCycleTimes[self.indexTime:]:
		    print t
		    (ra, dec) = dictOfNewFields[field]
		    self.airmass[field][t] = self.astroSky.airmasst(t, ra, dec)
#		    self.brightness[field][t] = self.astroSky.brightness(t, ra, dec)
	self.listOfActiveFields.sort()

	return

if (__name__ == '__main__'):

    data = SchedulingData('../test/SchedulingData.conf')

    data.initSurvey(0,36000)

    for time in range(0,36000,2500):
	print time
	print data.getCycleTimes(time)
	print data.extendedCycleTimes


    sys.exit(0)

