#!/usr/bin/env python

from LSSTObject import *
from utilities import *

class SchedulingData (LSSTObject):

    def __init__ (self,
                  configFile):

        config, pairs = readConfFile(configFile)

	self.cycleDuration = int(config['cycleDuration'])
	self.dt = int(config['dt'])

	self.cycleSamples = self.cycleDuration/self.dt

	self.startTime = 0
	self.endTime = 0
	self.currentTime = 0

	return


    def initSurvey (self, startTime, endTime):

        self.startTime = startTime
	self.endTime = endTime
	self.currentTime = startTime
	self.extendedCycleTimes = [self.currentTime]

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

if (__name__ == '__main__'):

    data = SchedulingData('../test/SchedulingData.conf')

    data.initSurvey(0,36000)

    for time in range(0,36000,2500):
	print time
	print data.getCycleTimes(time)
	print data.extendedCycleTimes


    sys.exit(0)

