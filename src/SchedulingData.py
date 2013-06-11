#!/usr/bin/env python

import gc
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

	self.lookAheadNights = int(eval(str(config['lookAheadNights'])))
	self.dt = int(eval(str(config['lookAheadInterval'])))

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


	self.lookAhead_nights = []
	self.lookAhead_times  = {}

        self.sunSetMJD   = {}
        self.sunSet      = {}
        self.sunSetTwil  = {}
        self.midnight    = {}
        self.sunRiseTwil = {}
        self.sunRise     = {}

	self.dictOfAllFields = {}
	self.dictOfActiveFields = {}
        self.listOfProposals = []

        self.dateProfile = {}
        self.moonProfile = {}
        self.twilightProfile = {}
	self.computedFields  = {}
	self.computedVisible = {}
        self.alt = {}
        self.az = {}
	self.pa = {}
        self.airmass = {}
        self.brightness = {}
	self.dist2moon = {}
	self.ticks = []
	self.visible = {}
	self.visibleTime = {}
        self.proposals = {}

        self.startTime = int(t)
        self.endTime   = int(endTime)
        self.currentTime = self.startTime

	night = 0
	self.currentNight           = night
        self.sunSetMJD[night]       = tonight_sunSetMJD
        self.sunSet[night]          = tonight_sunSet
        self.sunSetTwil[night]      = tonight_sunSetTwil
        self.midnight[night]        = midnight
        self.sunRiseTwil[night]     = tonight_sunRiseTwil
        self.sunRise[night]         = tonight_sunRise
        self.moonProfile[night]     = self.sky.computeMoonProfile(midnight)
	self.twilightProfile[night] = (self.sunRiseTwil[night], self.sunSetTwil[night])
	print ("night=%i twilightProfile=%s" % (night, str(self.twilightProfile[night]))) 
        self.lookAhead_nights       = [night]
	self.lookAhead_times[night] = range(self.startTime, self.sunRise[night], self.dt)
	for date in self.lookAhead_times[night]:
	    self.dateProfile[date] = self.sky.computeDateProfile(date)
            self.alt[date]        = {}
            self.az[date]         = {}
            self.pa[date]         = {}
            self.airmass[date]    = {}
            self.brightness[date] = {}
            self.dist2moon[date]  = {}
            self.visible[date]    = {}
        self.computedFields[night] = []
        self.computedVisible[night] = {}

        self.list_propID            = []
        self.dict_dictOfNewFields   = {}
        self.dict_maxAirmass        = {}
        self.dict_dictFilterMinBrig = {}
        self.dict_dictFilterMaxBrig = {}

	self.newMoonThreshold = 100.0

	self.updateLookAheadWindow()

    def updateLookAheadWindow(self):

	lastnight = self.lookAhead_nights[-1]
        nightsToAdd = 1*self.lookAheadNights+1 - (lastnight - self.currentNight) -1

	self.lookAheadLastNight = lastnight + nightsToAdd

        night = lastnight
        t = self.midnight[night]
        x = self.sky.getIntTwilightSunriseSunset(t)
        #print x
        (sunRise,sunSet,sunRiseMJD,sunSetMJD,sunRiseTwil,sunSetTwil) = x
	last_sunSetMJD  = sunSetMJD
	last_sunSet     = sunSet
	last_sunSetTwil = sunSetTwil
	while ( (last_sunSet < self.endTime) and (night < self.lookAheadLastNight) ):
	    night += 1
            t += DAY
	    x = self.sky.getIntTwilightSunriseSunset(t)
	    (sunRise,sunSet,sunRiseMJD,sunSetMJD,sunRiseTwil,sunSetTwil) = x
	    midnight = int((last_sunSetTwil+sunRiseTwil)/2)

	    self.sunSetMJD[night]       = last_sunSetMJD
	    self.sunSet[night]          = last_sunSet
	    self.sunSetTwil[night]      = last_sunSetTwil
	    self.midnight[night]        = midnight
	    self.sunRiseTwil[night]     = sunRiseTwil
	    self.sunRise[night]         = sunRise
	    self.moonProfile[night]     = self.sky.computeMoonProfile(midnight)
	    self.twilightProfile[night] = (self.sunRiseTwil[night], self.sunSetTwil[night])
	    print ("night=%i twilightProfile=%s" % (night, str(self.twilightProfile[night])))

	    self.lookAhead_nights   += [night]
	    self.lookAhead_times[night] = range(self.sunSet[night], self.sunRise[night], self.dt)
	    for date in self.lookAhead_times[night]:
		self.dateProfile[date] = self.sky.computeDateProfile(date)
	        self.alt[date]        = {}
                self.az[date]         = {}
                self.pa[date]         = {}
                self.airmass[date]    = {}
                self.brightness[date] = {}
                self.dist2moon[date]  = {}
                self.visible[date]    = {}
	    self.computedFields[night] = []
	    self.computedVisible[night] = {}

	    last_sunSetMJD  = sunSetMJD
	    last_sunSet     = sunSet
	    last_sunSetTwil = sunSetTwil

	len_alt      = 0
	siz_alt      = sys.getsizeof(self.alt)
	for t in self.alt.keys():
	    len_alt  += len(self.alt[t])
	    siz_alt  += sys.getsizeof(self.alt[t])
        len_visible  = 0
	siz_visible  = sys.getsizeof(self.visible)
        for t in self.visible.keys():
	    siz_visible += sys.getsizeof(self.visible[t])
	    for field in self.visible[t].keys():
		siz_visible += sys.getsizeof(self.visible[t][field])
		for filter in self.visible[t][field].keys():
		    len_visible += len(self.visible[t][field][filter])
		    siz_visible += sys.getsizeof(self.visible[t][field][filter])
        print("CLEANING DATA alt=%i size=%i  visible=%i size=%i" % (len_alt, siz_alt, len_visible, siz_visible))

	for n in range(self.lookAhead_nights[0], self.currentNight):
            for t in self.lookAhead_times[n]:
		if t in self.alt.keys():
		    del self.alt[t]
		    del self.az[t]
                    del self.pa[t]
                    del self.airmass[t]
                    del self.brightness[t]
                    del self.dist2moon[t]

                if t in self.visible.keys():
                    del self.visible[t]

                del self.dateProfile[t]

	    del self.sunSetMJD[n]
            del self.sunSet[n]
            del self.sunSetTwil[n]
            del self.midnight[n]
            del self.sunRiseTwil[n]
            del self.sunRise[n]
            del self.moonProfile[n]
            del self.twilightProfile[n]

	    del self.lookAhead_times[n]
	    self.lookAhead_nights.remove(n)

	    removed = len(self.computedFields[n])
	    del self.computedFields[n]
	    del self.computedVisible[n]
	    if (removed > 0):
                print ("SchedulingData:: night %i removed %4i fields" % (n, removed))

        len_alt      = 0
        siz_alt      = sys.getsizeof(self.alt)
        for t in self.alt.keys():
            len_alt  += len(self.alt[t])
            siz_alt  += sys.getsizeof(self.alt[t])
        len_visible  = 0
        siz_visible  = sys.getsizeof(self.visible)
        for t in self.visible.keys():
            siz_visible += sys.getsizeof(self.visible[t])
            for field in self.visible[t].keys():
                siz_visible += sys.getsizeof(self.visible[t][field])
                for filter in self.visible[t][field].keys():
                    len_visible += len(self.visible[t][field][filter])
                    siz_visible += sys.getsizeof(self.visible[t][field][filter])
        print("CLEANED  DATA alt=%i size=%i  visible=%i size=%i" % (len_alt, siz_alt, len_visible, siz_visible))

	self.dictOfActiveFields = {}

#        self.computeTargetData(self.currentNight, {}, 0, 0.0, {}, {})

	return


    def findNightAndTime(self, time):
	n = self.lookAhead_nights[0]
	foundNight = False
	while (n<= self.lookAhead_nights[-1] and not foundNight):
	    if (time < self.sunSet[n]):
		t = self.sunSet[n]
		foundNight = True
	    elif (self.sunSet[n] <= time <= self.sunRise[n]):
		t = time
		foundNight = True
	    else:
	        n += 1
	if foundNight:
	    ix = 0
	    foundTime = False
	    while (ix < len(self.lookAhead_times[n]) and not foundTime):
		if (t > self.lookAhead_times[n][ix]):
		    ix += 1
		elif (ix == 0):
		    next_time = self.lookAhead_times[n][ix]
		    foundTime = True
		elif ( (t-self.lookAhead_times[n][ix-1]) < (self.lookAhead_times[n][ix]-t) ):
		    next_time = self.lookAhead_times[n][ix-1]
		    foundTime = True
		else:
                    next_time = self.lookAhead_times[n][ix]
		    foundTime = True
	    if not foundTime:
		next_time = self.lookAhead_times[n][-1]
	    return (n, next_time)
	else:
	    return None


    def updateTargets(self, dictOfNewFields, propID, dateProfile, maxAirmass, dictFilterMinBrig, dictFilterMaxBrig):

	self.list_propID.append(propID)
	self.dict_dictOfNewFields[propID]   = dictOfNewFields
	self.dict_maxAirmass[propID]        = maxAirmass
	self.dict_dictFilterMinBrig[propID] = dictFilterMinBrig
	self.dict_dictFilterMaxBrig[propID] = dictFilterMaxBrig

	return

    def startNight(self, dateProfile):

	(date,mjd,lst_RAD) = dateProfile

	(nextNight, nextTime) = self.findNightAndTime(date)
	print ("nextNight=%i nextTime=%i" % (nextNight, nextTime))
        self.currentNight = nextNight
        self.currentTime  = nextTime
	if ( (self.lookAhead_nights[-1] - self.currentNight) < self.lookAheadNights):
	    self.updateLookAheadWindow()

	for propID in self.list_propID:
	    dictOfNewFields   = self.dict_dictOfNewFields[propID]
            maxAirmass        = self.dict_maxAirmass[propID]
            dictFilterMinBrig = self.dict_dictFilterMinBrig[propID]
            dictFilterMaxBrig = self.dict_dictFilterMaxBrig[propID]

	    self.computeTargetData(nextNight, dictOfNewFields, propID, maxAirmass, dictFilterMinBrig, dictFilterMaxBrig)

        self.list_propID            = []
        self.dict_dictOfNewFields   = {}
        self.dict_maxAirmass        = {}
        self.dict_dictFilterMinBrig = {}
        self.dict_dictFilterMaxBrig = {}
	
	return

    def computeTargetData(self, initNight, dictOfNewFields, propID, maxAirmass, dictFilterMinBrig, dictFilterMaxBrig):

        listOfFilters = sorted(dictFilterMinBrig.iterkeys())
	if propID not in self.listOfProposals:
	    self.listOfProposals.append(propID)
#	    self.computedVisibleNighrs[propID] = {}
	listOfNewFields    = sorted(dictOfNewFields.iterkeys())
	listOfAllFields    = sorted(self.dictOfAllFields.iterkeys())
	listOfActiveFields = sorted(self.dictOfActiveFields.iterkeys())
	newfields = 0
	newprops  = 0
	for field in listOfNewFields:
	    if field not in listOfAllFields:
		self.dictOfAllFields[field] = dictOfNewFields[field]

#                self.computedNights[field] = []
#                self.computedVisibleNights[propID][field] = []

                self.proposals[field] = [propID]
                self.lsstDB.addProposalField(self.sessionID, propID, field)
		newfields += 1
            else:
                if propID not in self.proposals[field]:

                    self.proposals[field].append(propID)
                    self.lsstDB.addProposalField(self.sessionID, propID, field)
		    newprops += 1
	    if field not in listOfActiveFields:
		self.dictOfActiveFields[field] = dictOfNewFields[field]

        listOfAllFields    = sorted(self.dictOfAllFields.iterkeys())
	listOfActiveFields = sorted(self.dictOfActiveFields.iterkeys())
	for field in listOfAllFields:
	    if field not in self.visibleTime.keys():
	        self.visibleTime[field] = {}
	    for filter in listOfFilters:
	        if filter not in self.visibleTime[field].keys():
		    self.visibleTime[field][filter] = {}
		if propID not in self.visibleTime[field][filter].keys():
	            self.visibleTime[field][filter][propID] = 0

	print ("SchedulingData:: %4i new fields from propID=%4i" % (newfields, propID))
	print ("SchedulingData:: %4i existing fields registered for propID=%4i" % (newprops, propID))

        print ("night %i" % (initNight))
	print self.lookAhead_nights
        for n in range(initNight, self.lookAhead_nights[-1]+1):
            computed = 0
            for field in listOfActiveFields:
		if field not in self.computedFields[n]:
		    (ra, dec) = self.dictOfAllFields[field]
		    for t in self.lookAhead_times[n]:
#		if t not in self.alt.keys():
#		    self.alt[t]        = {}
#                    self.az[t]         = {}
#                    self.pa[t]         = {}
#                    self.airmass[t]    = {}
#                    self.brightness[t] = {}
#                    self.dist2moon[t]  = {}
#		    self.visible[t]    = {}

#		    if field not in self.alt[t].keys():
			(am, alt, az, pa) = self.sky.airmasst(t, ra, dec)
			(br, dist2moon, moonAlt, brprofile) = \
                        	self.sky.getSkyBrightness(0, ra, dec, alt,
                                            self.dateProfile[t],
                                            self.moonProfile[n],
                                            self.twilightProfile[n])

			self.alt[t][field]        = alt
			self.az[t][field]         = az
			self.pa[t][field]         = divmod(pa, TWOPI)[1]
			self.airmass[t][field]    = am
			self.brightness[t][field] = br
			self.dist2moon[t][field]  = dist2moon
			self.visible[t][field]    = {}

		    self.computedFields[n].append(field)
                    computed += 1

                if propID in self.proposals[field]:
		    if propID not in self.computedVisible[n].keys():
			self.computedVisible[n][propID] = []
                    if field not in self.computedVisible[n][propID]:
                        for t in self.lookAhead_times[n]:
                            for filter in listOfFilters:
	                        if filter not in self.visible[t][field].keys():
        	                    self.visible[t][field][filter] = {}
				if (self.airmass[t][field] < maxAirmass):
				    if (filter == "u") and (self.moonProfile[n][2] > self.newMoonThreshold):
                                        visible = False
                                        delta = 0
				    elif (dictFilterMinBrig[filter] < self.brightness[t][field] < dictFilterMaxBrig[filter]):
				        visible = True
				        delta   = self.dt
				    else:
				        visible = False
				        delta   = 0
			        else:
				    visible = False
				    delta   = 0

			        self.visible[t][field][filter][propID] = visible
			        self.visibleTime[field][filter][propID] += delta

			self.computedVisible[n][propID].append(field)

        len_alt      = 0
        siz_alt      = sys.getsizeof(self.alt)
        for t in self.alt.keys():
            len_alt  += len(self.alt[t])
            siz_alt  += sys.getsizeof(self.alt[t])
        len_visible  = 0
        siz_visible  = sys.getsizeof(self.visible)
        for t in self.visible.keys():
            siz_visible += sys.getsizeof(self.visible[t])
            for field in self.visible[t].keys():
                siz_visible += sys.getsizeof(self.visible[t][field])
                for filter in self.visible[t][field].keys():
                    len_visible += len(self.visible[t][field][filter])
                    siz_visible += sys.getsizeof(self.visible[t][field][filter])
        print("UPDATED  DATA alt=%i size=%i  visible=%i size=%i" % (len_alt, siz_alt, len_visible, siz_visible))

	# Clean past calculations in look ahead window
#	for n in range(self.lookAhead_nights[0], initNight):
#	    removed = 0
#	    for t in self.lookAhead_times[n]:
#		ixt = self.ticks.index(t)
#		print("t=%i ixt=%i" % (t, ixt))
#		for field in listOfActiveFields:
#                    if n in self.computedNights[field]:

#                            del self.alt[field][t]
#                            del self.az[field][t]
#			    del self.pa[field][t]
#                            del self.airmass[field][t]
#                            del self.brightness[field][t]
#			    del self.dist2moon[field][t]

#			    for prop in self.listOfProposals:
#				if field in self.computedVisibleNights[prop].keys():
#				    if n in self.computedVisibleNights[prop][field]:
#					for filter in self.visible[prop][field].keys():
#					    print("prop=%i field=%i filter=%s" % (prop, field, filter))
#					    if self.visible[prop][field][filter][ixt]:
#					        self.visibleTime[prop][field][filter] -= self.dt
#					    self.visible[prop][field][filter].pop(ixt)
#					self.computedVisibleNights[prop][field].remove(n)
#                            self.computedNights[field].remove(n)
#                            removed += 1
#		self.ticks.pop(ixt)

#	    if (removed > 0):
#		print ("SchedulingData:: night %i removed %4i fields" % (n, removed))

#        size_alt = 0
#	len_alt  = 0
#        size_az = 0
#        size_pa = 0
#        size_airmass = 0
#        size_brightness = 0
#	size_dist2moon = 0
#        size_visible = 0
#	len_visible  = 0

#        size_alt += sys.getsizeof(self.alt)
#        size_az += sys.getsizeof(self.az)
#        size_pa += sys.getsizeof(self.pa)
#        size_airmass += sys.getsizeof(self.airmass)
#       size_brightness += sys.getsizeof(self.brightness)
#	size_dist2moon += sys.getsizeof(self.dist2moon)
#        size_visible += sys.getsizeof(self.visible)
#	for field in self.alt.keys():
#                size_alt += sys.getsizeof(self.alt[field])
#		len_alt += len(self.alt[field])
#                size_az += sys.getsizeof(self.az[field])
#                size_pa += sys.getsizeof(self.pa[field])
#                size_airmass += sys.getsizeof(self.airmass[field])
#                size_brightness += sys.getsizeof(self.brightness[field])
#		size_dist2moon += sys.getsizeof(self.dist2moon[field])
#	for prop in self.visible.keys():
#                size_visible += sys.getsizeof(self.visible[prop])
#		for field in self.visible[prop].keys():
#			size_visible += sys.getsizeof(self.visible[prop][field])
#			for filter in self.visible[prop][field].keys():
#				size_visible += sys.getsizeof(self.visible[prop][field][filter])
#				len_visible += len(self.visible[prop][field][filter])

#        print("size of data alt        = %i length=%i" % (size_alt, len_alt))
#        print("size of data az         = %i" % size_az)
#        print("size of data pa         = %i" % size_pa)
#        print("size of data airmass    = %i" % size_airmass)
#        print("size of data brightness = %i" % size_brightness)
#        print("size of data dist2moon  = %i" % size_dist2moon)
#	print("size of data visible    = %i length=%i" % (size_visible, len_visible))


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

    sys.exit(0)

