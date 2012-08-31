#!/usr/bin/env python

from TransientProp import *

class NearEarthProp (TransientProp):
    """
    This class is here to describe a Near Earth Objects (NEA) case scenario. 
    """
    def __init__ (self, 
                  lsstDB,
		  sky, 
                  weather,
                  sessionID,
                  filters,
                  targetList=None, 
                  dbTableDict=None,
                  log=False,
                  logfile='./NearEarthProp.log',
                  verbose=0,
                  nearEarthConf=DefaultNEAConfigFile):
        """
        Standard initializer.
        
	lsstDB:	    LSST DB access object        
	sky:        an AsronomycalSky instance.
        weather:    a Weather instance.
        sessionID:  An integer identifying this particular run.
        filters:    A Filters instance
        targetList: the name (with path) of the TEXT file containing
                    the field list. It is assumed that the target list
                    is a three column list of RA, Dec and field ID.
                    RA and Dec are assumed to be in decimal degrees; 
                    filed ID is assumed to be an integer uniquely
                    identifying any give field.
        dbTableDict:
        log         False if not set, else: log = logging.getLogger("...")
        logfile     Name (and path) of the desired log file.
                    Defaults "./NearEarthProp.log".
        verbose:    Log verbosity: -1=none, 0=minimal, 1=wordy, >1=verbose
        nearEarthConf: Near Earth Asteroid Configuration file

        """
        super (NearEarthProp, self).__init__ (lsstDB=lsstDB,
					      propConf=nearEarthConf,
                                              propName='NEA',
					      propFullName='NearEarth',
                                              sky=sky, 
                                              weather=weather,
                                              sessionID=sessionID,
                                              filters=filters,
                                              targetList=targetList,
                                              dbTableDict=dbTableDict,
                                              log=log,
                                              logfile=logfile,
                                              verbose=verbose,
                                              transientConf=nearEarthConf)
        
        config_dict, pairs = readConfFile(nearEarthConf)

	self.lsstDB = lsstDB        
	self.nextNight = 0
        self.maxAirmass     = eval(str(config_dict['MaxAirmass']))
        self.ha_maxairmass = sky.getHAforAirmass(self.maxAirmass)

        self.visitIntervals = eval(str(config_dict['VisitInterval']))
        try:
            for k in range(len(self.visitIntervals)):
                self.visitIntervals[k] = eval(str(self.visitIntervals[k]))
        except:
            self.visitIntervals = [eval(str(self.visitIntervals))]

        self.cycleRepeats   = eval(str(config_dict['CycleRepeats']))
        self.cycleInterval  = eval(str(config_dict['CycleInterval']))
        self.seqDuration    = eval(str(config_dict['SequenceDuration']))
        self.windowStart    = eval(str(config_dict['WindowStart']))
        self.windowMax      = eval(str(config_dict['WindowMax']))
        self.windowEnd      = eval(str(config_dict['WindowEnd']))
        self.rankTimeMax    = eval(str(config_dict['RankTimeMax']))
        self.rankFilter     = eval(str(config_dict['RankFilter']))
        self.rankIdleSeq    = eval(str(config_dict['RankIdleSeq']))
        self.rankLossRiskMax= eval(str(config_dict['RankLossRiskMax']))
        self.seqFilters     = config_dict['SeqFilter']

        try:
            self.maxMissedEvents = config_dict['MaxMissedEvents']
        except:
            self.maxMissedEvents = 0

        try:
            self.restartLostSequences = eval(str(config_dict['RestartLostSequences']))
        except:
            self.restartLostSequences = False
        try:
            self.restartCompleteSequences = eval(str(config_dict['RestartCompleteSequences']))
        except:
            self.restartCompleteSequences = False

        try:
            self.blockCompleteSeqConsecutiveLunations = eval(str(config_dict['BlockCompleteSeqConsecutiveLunations']))
        except:
            self.blockCompleteSeqConsecutiveLunations = False

        try:
            self.rankDaysLeftMax= eval(str(config_dict['RankDaysLeftMax']))
        except:
            self.rankDaysLeftMax= 0.0
        try:
            self.DaysLeftToStartBoost = eval(str(config_dict['DaysLeftToStartBoost']))
        except:
            self.DaysLeftToStartBoost = 0


        self.maxNumberActiveSequences = eval(str(config_dict['MaxNumberActiveSequences']))

        # original NEA read config fields
        self.maxMoonPhase   = eval(str(config_dict['MaxMoonPhase']))
        self.crossLunation  = eval(str(config_dict['CrossLunation']))
                                   
        self.EB = eval(str(config_dict['EB']))
        self.exposureTime = eval(str(config_dict['ExposureTime']))
        self.deltaLST = eval(str(config_dict['deltaLST']))
        self.maxReach = eval(str(config_dict['maxReach']))
       
        if ( config_dict.has_key ('userRegion')) :
            self.userRegion =  config_dict["userRegion"]
        else :
            self.userRegion =  None
             
        if ( config_dict.has_key ('minTransparency')) :
            self.minTransparency =  config_dict["minTransparency"]
        else :
            self.minTransparency =  .9
             
        if (not isinstance(self.userRegion,list)):
            # turn it into a list with one entry
            save = self.userRegion
            self.userRegion = []
            self.userRegion.append(save)

        try:
            self.maxProximityBonus = config_dict['MaxProximityBonus']
        except:
            self.maxProximityBonus = 1.0

        self.minSolarElong = config_dict['MinSolarElongation']
        self.maxSolarElong = config_dict['MaxSolarElongation']

        # store config in DB
        for line in pairs:
            storeParam (self.lsstDB, self.sessionID, self.propID, 'nea', line['index'],
                        line['key'], line['val'])

        self.dbField = dbTableDict['field']
        # If user-defined regions have been defined, build new FieldDB
        if not (self.userRegion[0] == None) :
            self.dbField = self.buildUserRegionDB(self.userRegion,self.dbField)

        self.lunationActive = False

        # Setup FieldFilter visit history for later ObsHistory DB  ingest
        self.fieldVisits = {}
        self.lastFieldVisit = {}
        self.lastFieldFilterVisit = {}
        self.lastTarget = (0.0,0.0)

        self.TransientType = 'NearEarth'        

	self.sky = sky
	self.firstNight = True

        return


    def startNight(self,dateProfile,moonProfile,startNewLunation,randomizeSequencesSelection,nRun, mountedFiltersList):

        super (NearEarthProp, self).startNight (dateProfile,moonProfile,startNewLunation,randomizeSequencesSelection, nRun, mountedFiltersList)

        (date,mjd,lst_RAD) = dateProfile

        # Get the moon phase
        (moonRA_RAD,moonDec_RAD,moonPhase_PERCENT) = moonProfile
        self.currentMoonPhase = moonPhase_PERCENT/100.0

        if ( self.log ):
            self.log.info('NearEarthProp: startNight() propID=%d date=%.0f moon phase=%.2f' % (self.propID,date, self.currentMoonPhase))

	if self.firstNight:
	    self.firstNight = False
	    phases = []
	    for i in range(31):
		phases.append(self.sky.getMoonPhase(mjd+i))
	    #print phases
	    if phases[0] > phases[1]:
		waning = True
	    else:
		waning = False
	    self.lastPhase = phases[0]
	    maxphase = max(phases)
	    imaxphase = phases.index(maxphase)
	    self.phases = []
	    for i in range(imaxphase,31):
		self.phases.append(phases[i])
	    for i in range(31,imaxphase+29):
		self.phases.append(self.sky.getMoonPhase(mjd+i))
	    print "moon phases = " + str(self.phases)
	    self.dayEndLunation=0
	    for i in range(14,29):
		if self.dayEndLunation == 0:
		    if self.phases[i] > self.maxMoonPhase*100:
			self.dayEndLunation = i
	    if self.dayEndLunation == 0:
		self.dayEndLunation = 28
	    print "day end lunation = " + str(self.dayEndLunation)
	else:
	    if moonPhase_PERCENT < self.lastPhase:
		waning = True
	    else:
		waning = False
	    self.lastPhase = moonPhase_PERCENT

	diffphase = []
	for i in range(29):
	    diffphase.append(abs(moonPhase_PERCENT-self.phases[i]))
	#print diffphase

	if waning:
	    closestPhase = min(diffphase[0:14])
	else:
	    closestPhase = min(diffphase[14:29])
	dayphase = diffphase.index(closestPhase)
	print "day in moon phase = " + str(dayphase)

	if (self.currentMoonPhase <= self.maxMoonPhase) and (self.crossLunation == False):
	    removedsequences=0
#	    for fieldID in self.tonightTargets.keys():
            for fieldID in sorted(self.tonightTargets.iterkeys()):
		if self.sequences[fieldID].IsIdle():
		    if self.sequences[fieldID].GetDuration()/DAY > (self.dayEndLunation-dayphase):
			removedsequences+=1
			del self.tonightTargets[fieldID]
	    if (self.log and removedsequences>0):
		self.log.info('NearEarthProp: startNight() REMOVED %d idle sequences due to insufficient time to complete' % (removedsequences))

        return

    # yanked from TransientProp.py
    def suggestObs (self,
                    dateProfile,
                    moonProfile,
                    n=100,
                    skyfields=None,
                    proximity=None,
                    targetProfiles=None,
                    exclusiveObservation=None,
                    minDistance2Moon=0.0):
        """
        Return the list of (at most) the n (currently) higher ranking
        observations.

        Input
        dateProfile     current date profile of:
                            (date,mjd,lst_RAD) where:
                                    date    simulated time (s)
                                    mjd
                                    lst_RAD local sidereal time (radians)
        moonProfile     current moon profile of:
                           (moonRA_RAD,moonDec_RAD,moonPhase_PERCENT)
                            moonPhase       current moon phase in range [0-100]
        n               number of observations to return.
        skyfields       array of fieldIDs  (with index-synced to proximity)
        proximity       array of proximity distance between current
                        telescope position and each entry in skyfields (with
                        index-synced to skyfields)
        targetProfiles: array of [AirMass,
                                Sky brightness,
                                Filterlist,
                                transparency,
                                cloudSeeing,
                                distance2moon,
                                altitude,
                                rawSeeing,
                                moonAlt]
                        values (dictionary-keyed to fieldID)

        Return
        An array of the (at most) n highest ranking observations,
        ordered from the highest ranking obs to the lowest.
        """
        if ( self.log and self.verbose > 1 ):
           self.log.info('%sProp: suggestObs() propID=%d' %(self.propName, self.propID))
        # do we need to rerank fields?
#        if self.reuseRanking > 1:
#            self.reuseRanking -= 1
#            return []

        # Copy the input vars
        inFieldID = skyfields
        inproximity = proximity
        intargetProfiles = targetProfiles
        (date,mjd,lst_RAD) = dateProfile
        (moonRA_RAD,moonDec_RAD,moonPhase_PERCENT) = moonProfile

        # Create a priority queue to choose the best n obs
        self.clearSuggestList()

        # Check the start/end of observing cycle (lunation)
        if self.CheckObservingCycle(date):

            # Discard all the targets which are not visible right now.
            fields_received=len(self.tonightTargets)
            fields_invisible=0
            fields_moon=0
            fields_nottoday=0
            fields_waiting=0
            fields_missed=0
            fields_lost=0
            fields_completed=0
            fields_proposed=0
            fieldfilter_proposed=0

            if (exclusiveObservation != None):
                if exclusiveObservation.fieldID in self.tonightTargets.keys():
                    listOfFieldsToEvaluate = [exclusiveObservation.fieldID]
                else:
                    listOfFieldsToEvaluate = []
                numberOfObsToPropose = 0
            else:
#                listOfFieldsToEvaluate = self.tonightTargets.keys()
		listOfFieldsToEvaluate = sorted(self.tonightTargets.iterkeys())
                numberOfObsToPropose = n

            for fieldID in listOfFieldsToEvaluate:
                ra = self.tonightTargets[fieldID][0]  # in degrees
                dec = self.tonightTargets[fieldID][1] # in degrees
                i = inFieldID.index (fieldID)

                if (fieldID==self.last_observed_fieldID) and (self.last_observed_wasForThisProposal) and (not self.AcceptConsecutiveObs):
                    continue

                airmass = intargetProfiles[i][0]
                if (airmass > self.maxAirmass):
                    if self.log and self.verbose>2:
                        self.log.info('%sProp: suggestObs() propID=%d field=%i too low:%f' % (self.TransientType, self.propID,fieldID,airmass))
                    fields_invisible+=1
                    continue

                # if moon is down, don't check distance
                moonAlt_RAD = intargetProfiles[i][8]
                if moonAlt_RAD > 0:
                    distance2moon = intargetProfiles[i][5]
                    # remove target for rest of night if less than minimum
                    # distance to moon
                    if (distance2moon < minDistance2Moon):
                        fields_moon+=1
                        del self.tonightTargets[fieldID]
                        continue
                
                # Candidate fields between min and max solar elongation
                target = (ra*DEG2RAD, dec*DEG2RAD)
                solarElong_RAD = self.sky.getPlanetDistance ('Sun', target, date)
                solarElong_DEG = math.degrees(solarElong_RAD)
                if solarElong_DEG < self.minSolarElong or solarElong_DEG > self.maxSolarElong:
                    # remove or just skip?
		    #del self.tonightTargets[fieldID]
                    #print "skipped field = %d due to solar elong degrees = %f" % (fieldID, solarElong_DEG)
                    continue
		
                #.............................................................
                # Gets the list of possible filters based on the sky brightness
                skyBrightness = intargetProfiles[i][1]
                allowedFilterList = self.allowedFiltersForBrightness(skyBrightness)
                filterSeeingList = intargetProfiles[i][2]
                #.............................................................

                # Obtains the time for the next event in the sequence for this field
                if self.sequences[fieldID].IsActive():
                    try:
                        nextdate = self.sequences[fieldID].nextDate()
                    except:
                        print 'fieldID = '+str(fieldID)
                        raise(IndexError, 'fieldID')

                    # Obtains the interval between the next event and the previous
                    # to quantify the precision required for next event.
                    nextperiod = self.sequences[fieldID].nextPeriod()

                    # Computes the base ranking based on the proximity of the next
                    # event.
                    deltaT = date - nextdate
                    rankTime = self.RankWindow(deltaT, nextperiod)
                    rankLossRisk = max(1.0-0.5*self.sequences[fieldID].GetRemainingAllowedMisses(), 0.0)
                else:
                    rankTime = self.rankIdleSeq
                    rankLossRisk = 0.0

                if rankTime == -0.1:
                    # if more than one day is needed for next event, then remove
                    # the target from the list, it will be received next night if it
                    # is visible.
                    fields_nottoday+=1
                    del self.tonightTargets[fieldID]

                elif rankTime > 0.0:
                    fields_proposed+=1

                    rankForFilters = self.RankFilters(fieldID, filterSeeingList, allowedFilterList)
                    # Boost factor according to the remaining observable days on sky
                    if self.DaysLeftToStartBoost > 0.0 and self.rankDaysLeftMax != 0.0:
                        observableDaysLeft = max((self.ha_twilight[fieldID]+self.ha_maxairmass) * 15.0, 0.0)
                        rankDaysLeft = max(1.0-observableDaysLeft/self.DaysLeftToStartBoost, 0.0)
                    else:
                        rankDaysLeft = 0.0

#                    for filter in rankForFilters.keys():
                    for filter in sorted(rankForFilters.iterkeys()):

                        rank = rankTime*self.rankTimeMax + rankForFilters[filter]*self.rankFilter + rankLossRisk*self.rankLossRiskMax + rankDaysLeft*self.rankDaysLeftMax

                        # Create the corresponding Observation
                        recordFieldFilter = self.obsPool[fieldID][filter]
                        #recordFieldFilter.sessionID = sessionID
                        #recordFieldFilter.propID = propID
                        #recordFieldFilter.fieldID = fieldID
                        #recordFieldFilter.filter = filter
                        recordFieldFilter.seqn = self.sequences[fieldID].seqNum
                        recordFieldFilter.date = date
                        recordFieldFilter.mjd = mjd
                        recordFieldFilter.exposureTime = self.exposureTime
                        #recordFieldFilter.slewTime = slewTime
                        #recordFieldFilter.rotatorSkyPos = 0.0
                        #recordFieldFilter.rotatorTelPos = 0.0
                        recordFieldFilter.propRank = rank
                        #recordFieldFilter.finRank = finRank
                        recordFieldFilter.maxSeeing = self.maxSeeing
                        recordFieldFilter.rawSeeing = intargetProfiles[i][7]
                        recordFieldFilter.seeing = filterSeeingList[filter]
                        recordFieldFilter.transparency = intargetProfiles[i][3]
                        recordFieldFilter.cloudSeeing = intargetProfiles[i][4]
                        recordFieldFilter.airmass = airmass
                        recordFieldFilter.skyBrightness = skyBrightness
                        #recordFieldFilter.ra = ra
                        #recordFieldFilter.dec = dec
                        recordFieldFilter.lst = lst_RAD
                        recordFieldFilter.altitude = intargetProfiles[i][6]
                        recordFieldFilter.azimuth  = intargetProfiles[i][9]
                        recordFieldFilter.distance2moon = intargetProfiles[i][5]
                        recordFieldFilter.moonRA = moonRA_RAD
                        recordFieldFilter.moonDec = moonDec_RAD
                        recordFieldFilter.moonAlt = intargetProfiles[i][8]
                        recordFieldFilter.moonPhase = moonPhase_PERCENT
                        self.addToSuggestList (recordFieldFilter, inproximity[i])
                        fieldfilter_proposed+=1
                        
                        # ZZZ mm debug - print suggest list
                        #print "suggestList field=%d filter=%s rank=%f solarElong_DEG = %f" % (fieldID, filter, rank, solarElong_DEG) 

                elif rankTime < 0.0:

                    fields_missed+=1

                    self.sequences[fieldID].missEvent(date)

                    if self.log and self.verbose>0 and not self.sequences[fieldID].IsLost():
                        t_secs = date%60
                        t_mins = (date%3600)/60
                        t_hour = (date%86400)/3600
                        t_days = (date)/86400

                        self.log.info('%sProp: suggestObs() event MISSED for propID=%d field=%i t=%dd%02dh%02dm%02ds progress=%i%%' % (self.TransientType, self.propID, fieldID, t_days, t_hour, t_mins, t_secs, 100*self.sequences[fieldID].GetProgress()))

                    # now the sequence object determines if the sequence is lost, according to the
                    # number of missed events and the maximum allowed.
                    if self.sequences[fieldID].IsLost():
                        if self.log and self.verbose>0:
                            self.log.info('%sProp: suggestObs() sequence LOST for propID=%d field=%i t=%.0f event missed' % (self.TransientType, self.propID
,fieldID, date))

                        # Update the SeqHistory database
                        self.seqHistory.addSequence (seq=self.sequences[fieldID],
                                                     fieldID=fieldID,
                                                     sessionID=self.sessionID,
                                                     obsdate=date,
                                                     status=MAX_MISSED_EVENTS)
                        fields_lost+=1
                        del self.tonightTargets[fieldID]
                    # it is also possible that the missed event was the last needed for completing the sequence
                    # in such a case the sequence object determines the completion of the sequence.
                    elif self.sequences[fieldID].IsComplete():
                        self.CompleteSequence(fieldID, date)
                        fields_completed+=1

                else:
                    fields_waiting+=1

            if self.log and self.verbose>0:
                self.log.info('%sProp: suggestObs() propID=%d fields count: received=%i invisible=%i moon=%i nottoday=%i waiting=%i proposed=%i missed=%i lost=%i completed=%i fieldfilter=%i' % (self.TransientType, self.propID, fields_received, fields_invisible, fields_moon, fields_nottoday, fields_waiting, fields_proposed, fields_missed, fields_lost, fields_completed, fieldfilter_proposed))


            # Choose the n highest ranking observations
#            self.reuseRanking = self.reuseRankingCount
            return self.getSuggestList(numberOfObsToPropose)

        else:
            # The cycle has ended and next one hasn't started yet (full moon for NEA)
            return []

    def CheckObservingCycle(self, date):

        if ( self.currentMoonPhase > self.maxMoonPhase):
            if  self.log and (self.verbose > 1):
                self.log.info ('NearEarthProp: suggestObs() propID=%d moon too bright = %.2f' % (self.propID,self.currentMoonPhase))
            if self.lunationActive:
                # The current lunation has finished
                self.FinishLunation(date)
            # No NEA observation is proposed at full moon phase
            return False
        else:
            if not self.lunationActive:
                self.StartLunation(date)
	return True

    def IsObservingCycle(self):

	return self.lunationActive

    def RankFilters(self, fieldID, filterSeeingList, allowedFilterList):

        rankForFilters = {}

        # Adds rank if the sky desired-filter coincides with the
        # requested filter for the next event.
        eventfilters = self.sequences[fieldID].nextFilters()
        for filter in allowedFilterList:
            if (filterSeeingList[filter] > self.maxSeeing):
                if self.log and self.verbose>1:
                    self.log.info ('NearEarthProp: suggestObs() propID=%d field %i bad seeing:%f' %(self.propID,fieldID,filterSeeingList[filter]))
                continue
            if filter in eventfilters:
                rankFilter = self.filters.relativeRankForFilter[filter]
                rankForFilters[filter]=rankFilter

        return rankForFilters
 
    def closeObservation (self, observation, twilightProfile):
        """
        Registers the fact that the indicated observation took place.
        This is, the corresponding event in the sequence of the indicated
        fieldID has been executed, and the sequence can continue.
        
        Input
        obs     an Observation instance
        winslewTime  slew time required for the winning observation
        
        Return
        None
        
        Raise
        Exception if Observation History update fails
        """

        if ( self.log and self.verbose > 1 ):
           self.log.info('NearEarthProp: closeObservation() propID=%d' %(self.propdID))

        obs = super (NearEarthProp, self).closeObservation(observation,
                                             twilightProfile)

        return obs

    def StartLunation(self, t=-1.0):
        """
        Starts a new lunation cycle.

        Reinitializes all the
        completed sequences from the previous lunation.
        According to the crossLunation parameter, allows
        the continuation of the incomplete sequences (True)
        or just reinitializes them to start over (False).
        """
        if ( self.log ):
            self.log.info ('NearEarthProp: StartLunation() propID=%d t=%.0f' % (self.propID,t))
        
        self.RestartSequences()
    
        self.lunationActive = True

        return

    def FinishLunation(self, t=-1.0):
        """
        Finishes the current lunation cycle. 
        """
        if ( self.log ):
            self.log.info ('NearEarthProp: FinishLunation() propID=%d t=%.0f' % (self.propID,t))

        if not self.crossLunation:
            self.FinishSequences(t)
        
	if self.blockCompleteSeqConsecutiveLunations:
	    previouslyblocked = self.blockedTargets[:]
	    self.blockedTargets = []
	    for fieldID in self.sequences.keys():
		if self.sequences[fieldID].IsComplete() and not fieldID in previouslyblocked:
		    self.blockedTargets.append(fieldID)

        self.lunationActive = False

        return
   
    def updateTargetList (self, dateProfile, obsProfile, sky, fov):
       """
       Update the list of potentially visible fields given a LST and
       a latitude. The range in coordinates of the selected fields is
       RA:  [LST-60; LST+60] (degrees)
       Dec: [lat-60; lat+60] (degrees)

       This version uses Sun.py and computes RA limits at the
       nautical twilight.

       Input:
       dateProfile  ...
       obsProfile   ...
       sky         AstronomicalSky instance
       fov         Field of view of the telescope
       dbField     DB information

       Return
       fields      A dictionary of the form {fieldID: (ra, dec)}
       """
       ## Benchmark memory use - start
       #m0 = memory()
       #r0 = resident()
       #s0 = stacksize()
       ##self.log.info("NEA: updateTargetList entry: mem: %d resMem: %d stack: %d" % (m0, r0, s0))

       dbFov = 'fieldFov'
       dbRA = 'fieldRA'
       dbDec = 'fieldDec'
       dbID = 'fieldID'
       dbEB = 'fieldEB'

       (date,mjd,lst_RAD) = dateProfile
       (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = obsProfile

       # MJD -> calendar date
       (yy, mm, dd) = mjd2gre (mjd)[:3]

       s = Sun.Sun ()
       (sunRise, sunSet) = s.__sunriset__ (yy, mm, dd, lon_RAD*RAD2DEG, lat_RAD*RAD2DEG,self.twilightBoundary,0)            

       # Compute RA min (at twilight)
       date_MJD = int (mjd) + (sunSet / 24.)
       raMin = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG) - self.deltaLST

       # Compute RA max (at twilight)
       date_MJD = int (mjd) + (sunRise / 24.)
       raMax = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG) + self.deltaLST

       # Make sure that both raMin and raMax are in the [0; 360] range
       raMin = normalize (angle=raMin, min=0., max=360, degrees=True)
       raMax = normalize (angle=raMax, min=0., max=360, degrees=True)

       # self.targets is a convenience dictionary. Its keys are
       # fieldIDs, its values are the corresponding RA and Dec.
       fields = {}
       fovEpsilon1 = fov - .01
       fovEpsilon2 = fov + .01
       EB = self.EB

       sql = 'SELECT %s, %s, %s from %s ' % (dbRA,
                                             dbDec,
                                             dbID,
                                             self.dbField)

       sql += 'WHERE %s BETWEEN %f AND %f AND ' % (dbFov,
                                                   fovEpsilon1,
                                                   fovEpsilon2)

       sql += '%s BETWEEN %f and %f AND ' % (dbEB,
                                            -1 * EB,
                                            EB)

       if (raMax > raMin):
           sql += '%s BETWEEN %f AND %f AND ' % (dbRA,
                                                 raMin,
                                                 raMax)
       elif (raMax < raMin):
           sql += '(%s BETWEEN %f AND 360.0 OR ' % (dbRA,
                                                    raMin)
           sql += '%s BETWEEN 0.0 AND %f) AND ' % (dbRA,
                                                   raMax)
       else:
           sql += '%s BETWEEN 0.0 AND 360.0 AND ' % (dbRA)

       DecLimit = math.acos(1./float(self.maxAirmass))  * RAD2DEG
       sql += '%s BETWEEN %f AND %f and %f < %s < %f' % (dbDec,
                                        lat_RAD*RAD2DEG-DecLimit,
                                        lat_RAD*RAD2DEG+DecLimit,
                                        -abs(self.maxReach),dbDec,abs(self.maxReach))

       # Send the query to the DB
       (n, res) = self.lsstDB.executeSQL (sql)

       # Build the output dictionary
       for (ra, dec, fieldID) in res:
           fields[fieldID] = (ra, dec)

       self.targets = fields

       self.computeTargetsHAatTwilight(lst_RAD)

       print ('*** Found %d NEA fields for propID=%d***' % (len (res),self.propID))

       self.targetsNewSeq = self.targets.copy()

       ## Benchmark memory use - start
       #m1 = memory()
       #r1 = resident()
       #s1 = stacksize()
       ##self.log.info("NEA: updateTargetList:(entry:exit) mem: %d:%d resMem: %d:%d stack: %d:%d" % (m0,m1, r0,r1, s0,s1))
       #print("NEA: updateTargetList:(entry:exit) mem: %d:%d resMem: %d:%d stack: %d:%d" % (m0,m1, r0,r1, s0,s1))

       return (fields)


