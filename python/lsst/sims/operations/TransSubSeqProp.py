#!/usr/bin/env python

from utilities import *
from LSSTObject import *
from Filters import *
from Observation import *
from ObsHistory import *
from Sequence     import *
from SuperSequence import *
from Proposal import *
from SeqHistory import *
import copy

class TransSubSeqProp (Proposal):
    """
    This class is here to describe a Transient Objects case scenario. 
    """
    def __init__ (self,
		  lsstDB, 
                  propConf,
                  propName,
		  propFullName,
                  sky, 
                  weather,
                  sessionID,
                  filters,
                  targetList=None, 
                  dbTableDict=None,
                  log=False,
                  logfile='./TransSubSeqProp.log',
                  verbose=0,
                  transientConf=DefaultNEAConfigFile):
        """
        Standard initializer.
        
        lsstDB	    LSST DB access object
	propConf    file name containing the instance's configuration data
        propName    proposal name
        sky:        an AsronomycalSky instance.
        weather:    a Weather instance.
        sessionID:  An integer identifying this particular run.
        filters:    a Filters instance
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
        transientConf: Near Earth Asteroid Configuration file

        """
        super (TransSubSeqProp, self).__init__ (lsstDB=lsstDB,
					      propConf=propConf,
                                              propName=propName,
					      propFullName=propFullName,
                                              sky=sky, 
                                              weather=weather, 
                                              sessionID=sessionID,
                                              filters=filters,
                                              targetList=targetList,
                                              dbTableDict=dbTableDict,
                                              log=log,
                                              logfile=logfile,
                                              verbose=verbose)
        
	self.lsstDB = lsstDB        
	self.verbose     = verbose
        self.dbTableDict = dbTableDict
        
        # DataBase specifics
        self.dbTable = self.dbTableDict['field']
        self.dbRA = 'fieldRA'
        self.dbDec = 'fieldDec'
        self.dbID = 'fieldID'
        
        self.winners = []
        self.loosers = []
        
        self.obsHistory = None
#        self.seqHistory = None
        self.sessionID = sessionID

        # self.targets is a convenience dictionary. Its keys are 
        # fieldIDs, its values are the corresponding RA and Dec.
        self.targets = {}
        self.tonightTargets = {}
        self.sequences= {}
	self.tonightSubseqsForTarget = {}

        # Create the ObsHistory instance and cleanup any leftover
        self.obsHistory = ObsHistory ( lsstDB=self.lsstDB,
				      dbTableDict=self.dbTableDict,
                                      log=self.log,
                                      logfile=self.logfile,
                                      verbose=self.verbose)
        
        self.obsHistory.cleanupProposal (self.propID, self.sessionID)
        
        # Create the SeqHistory instance and cleanup any leftover
#        self.seqHistory = SeqHistory (lsstDB=self.lsstDB,
#				      dbTableDict=self.dbTableDict,
#                                      log=self.log,
#                                      logfile=self.logfile,
#                                      verbose=self.verbose)
        
#        self.seqHistory.cleanupProposal (self.propID, self.sessionID)

	self.exclusiveBlockNeeded = False
	self.exclusiveObs = None
        self.exclusiveField = None
        self.exclusiveSubseq = None
	self.SeqCount = 0

        return

    
    def start (self):
        """
        Activate the TransientProp instance.

        """

	# Removes the subsequences that require 0 events
	N = len(self.subSeqName)
	for n in range(N):
	    ix = N-n-1
	    if self.subSeqEvents[ix] == 0:
		self.subSeqName.pop(ix)
		self.subSeqNested.pop(ix)
		self.subSeqFilters.pop(ix)
		self.subSeqExposures.pop(ix)
		self.subSeqEvents.pop(ix)
		self.subSeqMaxMissed.pop(ix)
		self.subSeqInterval.pop(ix)
                self.subSeqWindowStart.pop(ix)
                self.subSeqWindowMax.pop(ix)
                self.subSeqWindowEnd.pop(ix)

        # PAUSE
#        yield hold, self
        return

    def startNight(self,dateProfile,moonProfile,startNewLunation,randomizeSequencesSelection,nRun, mountedFiltersList):

        super (TransSubSeqProp, self).startNight (dateProfile,moonProfile,startNewLunation, mountedFiltersList)

	(date,mjd,lst_RAD) = dateProfile
	runProgress = date/YEAR/nRun

        self.tonightTargets = self.targets.copy()

	# deletes all sequences that did not start while the fields were
	# in the region for starting new sequences.
        notstarted = 0
        for fieldID in self.sequences.keys():
	    if not fieldID in self.targetsNewSeq.keys():
		if self.sequences[fieldID].IsIdle():
		    self.log.info('%sProp: startNight() deleted sequence field=%d at progress=%.3f%% state=%d nevents=%d' % (self.propFullName, fieldID, 100*self.sequences[fieldID].GetProgress(), self.sequences[fieldID].state, self.sequences[fieldID].nAllEvents))
		    notstarted+=1
		    del self.sequences[fieldID]

	# counts the active sequences in the target region
        currentActiveSequences = 0
	coaddedProgress = 0.0
	coaddedNumber = 0
        for fieldID in self.sequences.keys():
            if fieldID in self.tonightTargets.keys():
                coaddedProgress += self.sequences[fieldID].GetProgress()
		coaddedNumber += 1
                if (not self.sequences[fieldID].IsLost()) and (not self.sequences[fieldID].IsComplete()):
                    currentActiveSequences+=1

        # creates the sequence object for all the new fields in the restricted area
        newseq=0
	restartedlost=0
	restartedcomplete=0
	keptsequences=0
#        listOfNewFields=self.targetsNewSeq.keys()
	listOfNewFields=sorted(self.targetsNewSeq.iterkeys())
	while (len(listOfNewFields)>0 and currentActiveSequences<self.maxNumberActiveSequences and (coaddedProgress/max(coaddedNumber,1)>runProgress or currentActiveSequences<self.minNumberActiveSequences)):
		if randomizeSequencesSelection:
		    fieldID=random.choice(listOfNewFields)
		else:
		    fieldID=listOfNewFields[0]
		listOfNewFields.remove(fieldID)

                # create a new sequence object
                if not fieldID in self.sequences.keys():
		    self.SeqCount += 1
                    self.sequences[fieldID]=SuperSequence(self.propID,
                                                         fieldID,
							 self.SeqCount,
							 self.WLtype,
						         self.masterSubSequence,
							 self.subSeqName,
							 self.subSeqNested,
                                                         self.subSeqFilters,
							 self.subSeqExposures,
                                                         self.subSeqEvents,
                                                         self.subSeqMaxMissed,
                                                         self.subSeqInterval,
                                                         self.subSeqWindowStart,
                                                         self.subSeqWindowMax,
                                                         self.subSeqWindowEnd,
							 self.overflowLevel,
							 self.progressToStartBoost,
							 self.maxBoostToComplete)
		    coaddedNumber += 1
                    newseq+=1
                    currentActiveSequences+=1
                # was sequence lost?
                elif self.sequences[fieldID].IsLost():
	    	    if self.restartLostSequences:
			self.SeqCount += 1
		        self.sequences[fieldID].Restart(self.SeqCount)
		        restartedlost+=1
                        currentActiveSequences+=1
		    else:
                        # ZZZZ - mm debug 2nd delete of tonightTargets
#                        print "Prop[%d].startNight() while targetsNewSeq: seq lost: delete self.tonightTargets[%d] date = %d" % (self.propID, fieldID, date)
                        del self.tonightTargets[fieldID]
                # was sequence completed?
	        elif self.sequences[fieldID].IsComplete():
		    if self.restartCompleteSequences and not self.overflow:
			self.SeqCount += 1
                        self.sequences[fieldID].Restart(self.SeqCount)
		        restartedcomplete+=1
                        currentActiveSequences+=1
                    else:
                        # ZZZZ - mm debug 2nd delete of tonightTargets
#                        print "Prop[%d].startNight() while targetsNewSeq: seq complete: delete self.tonightTargets[%d] date = %d" % (self.propID, fieldID, date)
                        del self.tonightTargets[fieldID]
		#else:
		#    prog = self.sequences[fieldID].GetProgress()
		#    if prog >= 1.0:
		#	print "seqnNum=%i fieldID=%i progress=%f" % (self.sequences[fieldID].seqNum,fieldID,prog,str(self.sequences[fieldID].allHistory),self.sequences[fieldID].state)

	# From the broad target area, just keep the fields
	# associated to a target that is not lost and not complete
	self.tonightSubseqsForTarget = {}
	for fieldID in self.tonightTargets.keys():
	    if fieldID in self.sequences.keys():
		if (self.sequences[fieldID].IsLost() or (self.sequences[fieldID].IsComplete() and not self.overflow)):
                    # ZZZZ - mm debug 2nd delete of tonightTargets
#                    print "Prop[%d].startNight() for tonightTargets() in self.sequences: seq is lost or complete: delete self.tonightTargets[%d] date = %d" % (self.propID, fieldID, date)
#                    print "how would we ever get here?"
                    del self.tonightTargets[fieldID]
		else:
		    keptsequences+=1
                    self.tonightSubseqsForTarget[fieldID] = list(self.sequences[fieldID].subSeqName)
            # only pursue targets that are already started sequences
	    else:
                # ZZZZ - mm debug 2nd delete of tonightTargets
#                print "TSS.startNight() for tonightTargets() and not in self.sequences: delete self.tonightTargets[%d] date = %d" % (fieldID, date)
		del self.tonightTargets[fieldID]

	if coaddedNumber > 0:
	    self.globalProgress = coaddedProgress / coaddedNumber
	else:
	    self.globalProgress = 0.0

        if ( self.log ):
            self.log.info('%sProp: startNight() propID=%d Sequences: new=%i deletedidle=%i restartedlost=%i restartedcomplete=%i total=%i targetprogress=%.3f%% runprogress=%.3f%%' % (self.propFullName, self.propID,newseq, notstarted, restartedlost, restartedcomplete, keptsequences, 100*self.globalProgress, 100*runProgress))

        return

    def GetProgressPerFilter(self):

        coaddedNumber = 0
        coaddedSubseqProgress = {}
	progressFilter = {}
	numsubseFilter = {}
#        for subseq in self.subSeqName:
#            coaddedSubseqProgress[subseq] = 0
        for fieldID in self.sequences.keys():
            if not self.sequences[fieldID].IsLost():
                coaddedNumber += 1
                for subseq in self.sequences[fieldID].subSeqName:
		    progress = self.sequences[fieldID].GetProgress(subseq)
		    if subseq in coaddedSubseqProgress.keys():
			coaddedSubseqProgress[subseq] += progress
		    else:
			coaddedSubseqProgress[subseq] = progress

		    for filter in self.sequences[fieldID].GetFilterListForSubseq(subseq):
			if filter in progressFilter.keys():
			    progressFilter[filter] += progress
			    numsubseFilter[filter] += 1
			else:
			    progressFilter[filter] = progress
			    numsubseFilter[filter] = 1

	if coaddedNumber > 0:
	    for subseq in coaddedSubseqProgress.keys():
		coaddedSubseqProgress[subseq] /= coaddedNumber
        if ( self.log ):
            for subseq in coaddedSubseqProgress.keys():
                self.log.info('%sProp: GetProgressPerFilter() propID=%d Sub-Sequence progress: %20s = %.3f%%' % (self.propFullName, self.propID, subseq, 100*coaddedSubseqProgress[subseq]))

#	progressFilter = {}
#	numsubseFilter = {}
#	for ix in range(len(self.subSeqName)):
#	    subseq =  self.subSeqName[ix]
#	    for filter in self.subSeqFilters[ix].split(','):
#		if filter != '':
#		    if filter in progressFilter.keys():
#			progressFilter[filter] += coaddedSubseqProgress[subseq]
#			numsubseFilter[filter] += 1
#		    else:
#                        progressFilter[filter]  = coaddedSubseqProgress[subseq]
#                        numsubseFilter[filter]  = 1

	for filter in progressFilter.keys():
	    progressFilter[filter] /= numsubseFilter[filter]
	if ( self.log ):
            for filter in progressFilter.keys():
                self.log.info('%sProp: GetProgressPerFilter() propID=%d Filter progress: %10s = %.3f%%' % (self.propFullName, self.propID, filter, 100*progressFilter[filter]))

	return progressFilter

    def MissEvent(self, date, mjd, fieldID, subseq, obsHistID):
    
        self.sequences[fieldID].MissEvent(date, subseq, obsHistID)
        if self.log and self.verbose>0 and not self.sequences[fieldID].IsLost():
            t_secs = date%60
            t_mins = (date%3600)/60
            t_hour = (date%86400)/3600
            t_days = (date)/86400
            self.log.info('%sProp: suggestObs() subevent MISSED for propID=%d field=%i subseq=%s t=%dd%02dh%02dm%02ds progress=%i%%' % (self.propFullName, self.propID, fieldID, subseq, t_days, t_hour, t_mins, t_secs, 100*self.sequences[fieldID].GetProgress()))

        filter = self.sequences[fieldID].GetNextFilter(subseq)
        obs    = self.obsPool[fieldID][filter]
        obs.propID          = self.propID
        obs.seqn            = self.sequences[fieldID].seqNum
        obs.subsequence     = subseq
        obs.pairNum         = self.sequences[fieldID].GetPairNum(subseq)
        obs.date            = date
        obs.mjd             = mjd

        super (TransSubSeqProp, self).missObservation(obs)

        return

    def suggestObs (self, 
                    dateProfile, 
#                    moonProfile,
                    n=100,
#                    skyfields=None,
#		    proximity=None, 
#                    targetProfiles=None,
		    exclusiveObservation=None,
		    minDistance2Moon=0.0,
                    rawSeeing=0.0,
                    seeing=0.0,
                    transparency=0.0,
                    sdnight=0, sdtime=0):
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

        Return
        An array of the (at most) n highest ranking observations,
        ordered from the highest ranking obs to the lowest.
        """
        if ( self.log and self.verbose > 1 ):
           self.log.info('%sProp: suggestObs() propID=%d' %(self.propFullName, self.propID))
            
        # Copy the input vars
#        inFieldID = skyfields
#	inproximity = proximity
#        intargetProfiles = targetProfiles
        (date,mjd,lst_RAD) = dateProfile
        (moonRA_RAD,moonDec_RAD,moonPhase_PERCENT) = self.schedulingData.moonProfile[sdnight]

	# Check the start/end of observing cycle.
	# For NEA the lunation is checked
	if self.CheckObservingCycle(date):

            # Create a priority queue to choose the best n obs
            self.clearSuggestList()

            # If in an exclusive block, no new observation candidates. If this
            # proposal originated request, it should re-suggest observation.
	    if (exclusiveObservation != None):
                # adjust counter for one obs
#                self.reuseRanking -= 1
		if exclusiveObservation.propID == self.propID:

		    # The exclusive block is for this proposal
		    # so we just suggest our exclusive observation
		    fieldID = exclusiveObservation.fieldID
		    subseq = self.exclusiveSubseq
		    rank = 1.0

#                    i = inFieldID.index (fieldID)
	            #airmass = self.schedulingData.airmass[fieldID][sdtime]

		    filter = self.sequences[fieldID].GetNextFilter(subseq)
		    #print filter
		    exclusiveBlockRequired = self.sequences[fieldID].GetExclusiveBlockNeed(subseq)
		    #print "exclusiveBlockRequired = %s" % (exclusiveBlockRequired)

		    recordFieldFilter = self.obsPool[fieldID][filter]
		    recordFieldFilter.propID		= self.propID
		    recordFieldFilter.subsequence	= subseq
                    recordFieldFilter.seqn = self.sequences[fieldID].seqNum
                    recordFieldFilter.pairNum = self.sequences[fieldID].GetPairNum(subseq)
		    recordFieldFilter.date		= date
                    recordFieldFilter.mjd		= mjd
                    recordFieldFilter.night             = sdnight
                    recordFieldFilter.exposureTime	= self.exposureTime
                    recordFieldFilter.propRank		= rank
                    recordFieldFilter.maxSeeing		= self.exclusiveObs.maxSeeing
                    recordFieldFilter.rawSeeing		= self.exclusiveObs.rawSeeing
                    recordFieldFilter.seeing		= self.exclusiveObs.seeing
                    recordFieldFilter.transparency	= self.exclusiveObs.transparency
                    recordFieldFilter.cloudSeeing	= self.exclusiveObs.cloudSeeing
                    recordFieldFilter.airmass		= self.exclusiveObs.airmass
                    recordFieldFilter.skyBrightness	= self.exclusiveObs.skyBrightness
                    recordFieldFilter.lst		= lst_RAD
                    recordFieldFilter.altitude		= self.exclusiveObs.altitude
                    recordFieldFilter.azimuth           = self.exclusiveObs.azimuth
                    recordFieldFilter.distance2moon	= self.exclusiveObs.distance2moon
                    recordFieldFilter.moonRA		= self.exclusiveObs.moonRA
                    recordFieldFilter.moonDec		= self.exclusiveObs.moonDec
                    recordFieldFilter.moonAlt		= self.exclusiveObs.moonAlt
                    recordFieldFilter.moonPhase		= self.exclusiveObs.moonPhase
                    recordFieldFilter.exclusiveBlockRequired = exclusiveBlockRequired

                    self.addToSuggestList (recordFieldFilter)#, inproximity[i])
	            return self.getSuggestList(1)

		else:
		    # The exclusive block is not for this proposal
		    # so we don't propose observations
		    # but we must update the ranking and availability
		    # of the exclusive observation for correct serendipity
		    if exclusiveObservation.fieldID in self.tonightTargets.keys():
			listOfFieldsToEvaluate = [exclusiveObservation.fieldID]
		    else:
			listOfFieldsToEvaluate = []
#                    return []
                    numberOfObsToPropose = 0

	    else:
		# Normal observation block, all proposals competing
                # If not time to rerank fields, return no suggestions.
#                if self.reuseRanking > 1:
#                    self.reuseRanking -= 1
#                    return []

#		listOfFieldsToEvaluate = self.tonightTargets.keys()
		listOfFieldsToEvaluate = sorted(self.tonightTargets.iterkeys())
		numberOfObsToPropose = n

                # ZZZ - This block needs attention. Do we get here? Does it make sense? - mm
		if self.exclusiveBlockNeeded == True:
		    # We needed an exclusive block to complete the current event
		    # so we miss this event and evaluate if the sequence is missed or complete
		    fieldID = self.exclusiveField
                    subseq = self.exclusiveSubseq

		    self.exclusiveBlockNeeded = False

		    obsHist = self.lsstDB.addMissedObservation(self.sequences[fieldID].GetNextFilter(subseq), date, mjd, 0, lst_RAD, self.sessionID, fieldID)
                    self.MissEvent(date, mjd, fieldID, subseq, obsHist.missedHistID)

            fields_received=len(listOfFieldsToEvaluate)
            fields_invisible=0
	    fields_moon=0
            events_waiting=0
            events_proposed=0
            events_missed=0
            seq_lost=0
            seq_completed=0
            events_nottonight=0
	    events_nofilter=0
	    events_noseeing=0

            for fieldID in listOfFieldsToEvaluate:

		fieldRecordList = []

                ra = self.tonightTargets[fieldID][0]
                dec = self.tonightTargets[fieldID][1]
#                i = inFieldID.index (fieldID)

		if (fieldID==self.last_observed_fieldID) and (self.last_observed_wasForThisProposal) and (not self.AcceptConsecutiveObs):
		    continue

                airmass = self.schedulingData.airmass[sdtime][fieldID]
                if (airmass > self.maxAirmass):
                    if self.log and self.verbose>2:
                        self.log.info('%sProp: suggestObs() propID=%d field=%i too low:%f' % (self.propFullName, self.propID,fieldID,airmass))
                    fields_invisible+=1
                    continue

                distance2moon = self.schedulingData.dist2moon[sdtime][fieldID]
                if (distance2moon < minDistance2Moon):
                    fields_moon+=1
                    # remove the target for the rest of the night if it is too close to the moon
                    # ZZZZ - mm debug 2nd delete of tonightTargets
#                    print "Prop[%d].suggestObs():too close to moon - delete self.tonightTargets[%d] date = %d" % (self.propID, fieldID, date)
                    del self.tonightTargets[fieldID]
                    continue

#		if not self.sequences[fieldID].HasEventsTonight(date):
#		    seq_nottonight+=1
#		    del self.tonightTargets[fieldID]
#		    continue
                #.............................................................
                # Gets the list of possible filters based on the sky brightness
		skyBrightness = self.schedulingData.brightness[sdtime][fieldID]
		allowedFilterList = self.allowedFiltersForBrightness(skyBrightness)
                filterSeeingList = self.filters.computeFilterSeeing(seeing, airmass)
                #rankForFilters = self.RankFilters(fieldID, filterSeeingList)
                #.............................................................
                for subseq in self.tonightSubseqsForTarget[fieldID]:

		    # Prevents that a lost sequence due to a missed event
		    # keeps beeing evaluated for the other subsequences
		    # wasting time and triggering an error when deleting
		    # the already deleted field from the target list.
		    if self.sequences[fieldID].IsLost():
			continue

		    allfiltersavailable = True
		    for f in self.sequences[fieldID].GetFilterListForSubseq(subseq):
			if not f in allowedFilterList:
			    allfiltersavailable = False
			    events_nofilter+=1
			elif filterSeeingList[f] > self.FilterMaxSeeing[f]:
			    allfiltersavailable = False
			    events_noseeing+=1

		    if allfiltersavailable == False:
			continue

		    # Boost factor according to the remaining observable days on sky
                    if self.DaysLeftToStartBoost > 0.0 and self.rankDaysLeftMax != 0.0:
			observableDaysLeft = max((self.ha_twilight[fieldID]+self.ha_maxairmass) * 15.0, 0.0)
                        rankDaysLeft = max(1.0-observableDaysLeft/self.DaysLeftToStartBoost, 0.0)
                    else:
			rankDaysLeft = 0.0

		    if self.WLtype or self.sequences[fieldID].IsActive(subseq):
			(rankTime, timeWindow) = self.sequences[fieldID].RankTimeWindow(subseq,date)
                        rankLossRisk = max(1.0-0.5*self.sequences[fieldID].GetRemainingAllowedMisses(subseq), 0.0)
                    elif self.sequences[fieldID].IsIdle(subseq):
                        rankTime = self.rankIdleSeq/self.rankTimeMax
			timeWindow = True
                        rankLossRisk = 0.0
		    else:
			rankTime = 0.0
			timeWindow = False
                        rankLossRisk = 0.0

                    if rankTime == -0.1:
                        events_nottonight+=1
                        self.tonightSubseqsForTarget[fieldID].remove(subseq)
                    elif rankTime > 0.0:
			events_proposed+=1
			#print 'ha_twilight='+str(self.ha_twilight[fieldID])+' ha_maxairmass='+str(self.ha_maxairmass)+' observableDaysLeft='+str(observableDaysLeft)+' rankDaysLeft='+str(rankDaysLeft)

			if timeWindow:
			    factor = self.rankTimeMax
			else:
			    if self.globalProgress < 1.0:
				factor = self.rankIdleSeq/(1.0-self.globalProgress)
			    elif self.overflowLevel > 0.0:
                                factor = self.rankIdleSeq/(self.overflowLevel/self.globalProgress)

                        rank = rankTime*factor + rankLossRisk*self.rankLossRiskMax + rankDaysLeft*self.rankDaysLeftMax

			filter = self.sequences[fieldID].GetNextFilter(subseq)
			#print 'subseq='+str(subseq)+' filter='+str(filter)
			exclusiveBlockRequired = self.sequences[fieldID].GetExclusiveBlockNeed(subseq)
                        
                        # Create the corresponding Observation
                        recordFieldFilter = self.obsPool[fieldID][filter]
                        #recordFieldFilter.sessionID = sessionID
                        recordFieldFilter.propID = self.propID
			recordFieldFilter.subsequence = subseq
                        #recordFieldFilter.fieldID = fieldID
                        #recordFieldFilter.filter = filter
                        recordFieldFilter.seqn = self.sequences[fieldID].seqNum
                        recordFieldFilter.pairNum = self.sequences[fieldID].GetPairNum(subseq)
                        recordFieldFilter.date = date
                        recordFieldFilter.mjd = mjd
			recordFieldFilter.night = sdnight
                        recordFieldFilter.exposureTime = self.exposureTime
                        #recordFieldFilter.slewTime = slewTime
                        #recordFieldFilter.rotatorSkyPos = 0.0
                        #recordFieldFilter.rotatorTelPos = 0.0
                        recordFieldFilter.propRank = rank
                        #recordFieldFilter.finRank = finRank
                        recordFieldFilter.maxSeeing = self.FilterMaxSeeing[filter]
                        recordFieldFilter.rawSeeing = rawSeeing
                        recordFieldFilter.seeing = filterSeeingList[filter]
                        recordFieldFilter.transparency = transparency
#                        recordFieldFilter.cloudSeeing = intargetProfiles[i][4]
                        recordFieldFilter.airmass = airmass
                        recordFieldFilter.skyBrightness = skyBrightness
                        #recordFieldFilter.ra = ra
                        #recordFieldFilter.dec = dec
                        recordFieldFilter.lst = lst_RAD
                        recordFieldFilter.altitude = self.schedulingData.alt[sdtime][fieldID]
                        recordFieldFilter.azimuth  = self.schedulingData.az[sdtime][fieldID]
			recordFieldFilter.parallactic = self.schedulingData.pa[sdtime][fieldID]
                        recordFieldFilter.distance2moon = distance2moon
                        recordFieldFilter.moonRA = moonRA_RAD
                        recordFieldFilter.moonDec = moonDec_RAD
#                        recordFieldFilter.moonAlt = intargetProfiles[i][8]
                        recordFieldFilter.moonPhase = moonPhase_PERCENT
			recordFieldFilter.exclusiveBlockRequired = exclusiveBlockRequired

			fieldRecordList.append(recordFieldFilter)

                    elif rankTime < 0.0:

                        events_missed+=1

	                obsHist = self.lsstDB.addMissedObservation(self.sequences[fieldID].GetNextFilter(subseq), date, mjd, 0, lst_RAD, self.sessionID, fieldID)
                        self.MissEvent(date, mjd, fieldID, subseq, obsHist.missedHistID)

	                if self.sequences[fieldID].IsLost():
        	            if self.log and self.verbose>0:
                	        self.log.info('%sProp: suggestObs() sequence LOST for propID=%d field=%i t=%.0f event missed' % (self.propFullName, self.propID,fieldID, date))
                                                                                                                                    
	                    # Update the SeqHistory database
			    seq = self.sequences[fieldID]
			    seqHist = self.lsstDB.addSeqHistory(seq.date,
							date,
							seq.seqNum,
							seq.GetProgress(),
							seq.GetNumTargetEvents(),
							seq.GetNumActualEvents(),
							MAX_MISSED_EVENTS,
							0,
							fieldID,
							self.sessionID,
							self.propID)
			    for obsID in seq.GetListObsID():
				self.lsstDB.addSeqHistoryObsHistory(seqHist.sequenceID, obsID, self.sessionID)

                            for misID in seq.GetListMisID():
                                self.lsstDB.addSeqHistoryMissedHistory(seqHist.sequenceID, misID, self.sessionID)


	                    seq_lost+=1
                            # ZZZZ - mm debug 2nd delete of tonightTargets
                            print "Prop[%d].suggestObs() seq lost: delete self.tonightTargets[%d] date = %d" % (self.propID, fieldID, date)
        	            del self.tonightTargets[fieldID]
			    # Also remove the posible previously considered subsequences
			    # as the whole sequence is now lost they must not be proposed.
			    fieldRecordList = []
	                # it is also possible that the missed event was the last needed for
        	        # completing the sequence
                	# in such a case the sequence object determines the completion of the sequence.
	                elif self.sequences[fieldID].IsComplete():
        	            self.CompleteSequence(fieldID, date)
                	    seq_completed+=1
			    fieldRecordList = []
                                                                                                                                    
                    else:
                        # rankTime==0.0
                        events_waiting+=1

		if self.tonightSubseqsForTarget[fieldID] == []:
                    # ZZZZ - mm debug 2nd delete of tonightTargets
#                    print "Prop[%d].suggestObs() no subseqs for target: delete self.tonightTargets[%d] date = %d" % (self.propID, fieldID, date)
		    del self.tonightTargets[fieldID]

		for record in fieldRecordList:
		    self.addToSuggestList (record)#, inproximity[i])

            if self.log and self.verbose>0:
                self.log.info('%sProp: suggestObs() propID=%d : Fields received=%i invisible=%i moon=%i Events nottonight=%i waiting=%i nofilter=%i noseeing=%i proposed=%i missed=%i Sequences lost=%i completed=%i' % (self.propFullName, self.propID, fields_received, fields_invisible, fields_moon, events_nottonight, events_waiting, events_nofilter, events_noseeing, events_proposed, events_missed, seq_lost, seq_completed))

            # Choose the n highest ranking observations
#            self.reuseRanking = self.reuseRankingCount
            return self.getSuggestList(numberOfObsToPropose)

	else:
	    # The cycle has ended and next one hasn't started yet (full moon for NEA)
	    return []

    def getFieldCoordinates (self, fieldID):
        """
        Given a fieldID, fetch the corresponding values for RA and Dec
        
        Input
        fieldID:    a field identifier (long int)
        
        Return
        (ra, dec) in decimal degrees
        
        Raise
        Exception if fieldID is unknown.
        """
        return (self.targets[fieldID])
    
    
    def setMaxSeeing (self, seeing):
        """
        Setter method for self.seeing
        
        Input
        seeing:     float
        
        Return
        None
        """
#        self.maxSeeing = float (seeing)
        return
    
    
    def setSlewTime (self, slewTime):
        """
        Setter method for self.maxSlewTime
        
        Input
        slewTime:   float
        
        Return
        None
        """
        self.maxSlewTime = float (slewTime)
        return
    
    
    def closeObservation (self, observation, obsHistID, twilightProfile):
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

	if not self.IsObservingCycle():
	    self.last_observed_wasForThisProposal = False
	    return None

#        if ( self.log and self.verbose > 1 ):
#           self.log.info('%sProp: closeObservation()' % (self.propFullName))

        obs = super (TransSubSeqProp, self).closeObservation(observation, obsHistID, twilightProfile)

        if obs != None:
            self.sequences[obs.fieldID].ObserveEvent(obs.date, obs.subsequence, obsHistID)
            progress = self.sequences[obs.fieldID].GetProgress()

            if self.log and self.verbose>0:
		t_secs = obs.date%60
		t_mins = (obs.date%3600)/60
		t_hour = (obs.date%86400)/3600
		t_days = (obs.date)/86400

		if self.sequences[obs.fieldID].IsEventInProgress(obs.subsequence):
		    progrmod = '+'
		else:
		    progrmod = ''
                self.log.info('%s: closeObservation() propID=%d field=%d filter=%s propRank=%.4f finRank=%.4f t=%dd%02dh%02dm%02ds progress=%d%s%%' % (self.propConf, self.propID, obs.fieldID, obs.filter, obs.propRank, obs.finRank, t_days, t_hour, t_mins, t_secs, int(100*progress), progrmod))

	    if obs.exclusiveBlockRequired == True:
		self.exclusiveBlockNeeded = True
		self.exclusiveObs = copy.copy(obs)
		self.exclusiveField = obs.fieldID
		self.exclusiveSubseq = obs.subsequence
	    else:
		self.exclusiveBlockNeeded = False

            # if sequence is complete, then deletes target from tonight's list.
            if progress == 1.0:
		self.CompleteSequence(obs.fieldID, obs.date)
		self.exclusiveBlockNeeded = False
       
        return obs

    def CompleteSequence(self, fieldID, date):

        # Update sequence history DB
        seq = self.sequences[fieldID]
        seqHist = self.lsstDB.addSeqHistory(seq.date,
				date,
                                seq.seqNum,
                                seq.GetProgress(),
                                seq.GetNumTargetEvents(),
                                seq.GetNumActualEvents(),
                                SUCCESS,
                                0,
                                fieldID,
                                self.sessionID,
                                self.propID)
	for obsID in seq.GetListObsID():
	    self.lsstDB.addSeqHistoryObsHistory(seqHist.sequenceID, obsID, self.sessionID)

        for misID in seq.GetListMisID():
            self.lsstDB.addSeqHistoryMissedHistory(seqHist.sequenceID, misID, self.sessionID)

        if not self.overflow:
            # ZZZZ - mm debug 2nd delete of tonightTargets
#            print "Prop[%d].CompleteSequence() delete self.tonightTargets[%d] date = %d" % (self.propID, fieldID, date)
	    if fieldID in self.tonightTargets.keys():
		del self.tonightTargets[fieldID]

	if (self.log and self.verbose >0):
            self.log.info('%sProp: CompleteSequence() sequence COMPLETE for propID=%d field=%d' % (self.propFullName, self.propID, fieldID))

	return

    def FinishSequences(self, obsdate):
        """
        Finishes the current sequences.
        """
        if ( self.log ):
            self.log.info ('%sProp: FinishSequences()' % (self.propFullName))

        for fieldID in self.sequences.keys():
            if (not self.sequences[fieldID].IsComplete()) and (not self.sequences[fieldID].IsLost()):
                if ( self.log ):
                    self.log.info('%sProp: suggestObs() propID=%d sequence LOST for field=%i end of cycle' % (self.propFullName, self.propID, fieldID))
                self.sequences[fieldID].Abort()

                # Update sequence history DB
                seq = self.sequences[fieldID]
                seqHist = self.lsstDB.addSeqHistory(seq.date,
					obsdate,
                                        seq.seqNum,
                                        seq.GetProgress(),
                                        seq.GetNumTargetEvents(),
                                        seq.GetNumActualEvents(),
                                        CYCLE_END,
                                        0,
                                        fieldID,
                                        self.sessionID,
                                        self.propID)
        	for obsID in seq.GetListObsID():
	            self.lsstDB.addSeqHistoryObsHistory(seqHist.sequenceID, obsID, self.sessionID)

	        for misID in seq.GetListMisID():
        	    self.lsstDB.addSeqHistoryMissedHistory(seqHist.sequenceID, misID, self.sessionID)

        return

    def closeProposal(self, time):
        """
        Finishes the current sequences.
        """
        if ( self.log ):
            self.log.info ('%sProp: closeProposal()' % (self.propFullName))

        for fieldID in self.sequences.keys():
            if (not self.sequences[fieldID].IsComplete()) and (not self.sequences[fieldID].IsLost()):
                if ( self.log ):
                    self.log.info('%sProp: closeProposal() propID=%d sequence LOST for field=%i end of simulation' % (self.propFullName, self.propID, fieldID))
                #self.sequences[fieldID].Abort()

                # Update sequence history DB
                seq = self.sequences[fieldID]
                seqHist = self.lsstDB.addSeqHistory(seq.date,
                                        time,
                                        seq.seqNum,
                                        seq.GetProgress(),
                                        seq.GetNumTargetEvents(),
                                        seq.GetNumActualEvents(),
                                        SIMULATION_END,
                                        0,
                                        fieldID,
                                        self.sessionID,
                                        self.propID)
	        for obsID in seq.GetListObsID():
        	    self.lsstDB.addSeqHistoryObsHistory(seqHist.sequenceID, obsID, self.sessionID)

	        for misID in seq.GetListMisID():
        	    self.lsstDB.addSeqHistoryMissedHistory(seqHist.sequenceID, misID, self.sessionID)

        # delete OlapField user-defined region table
        if not (self.userRegion[0] == None): 
            overlappingField = "OlapField_%d_%d" %(self.sessionID,self.propID)
            result = self.lsstDB.dropTable(overlappingField)
        return

    def RestartSequences(self):

        if (self.log): 
            self.log.info('%sProp: RestartFinishedSequences() propID=%d' %(self.propFullName, self.propID))

        for fieldID in self.sequences.keys():
            if self.sequences[fieldID].IsLost() or self.sequences[fieldID].IsComplete():
		self.SeqCount += 1
                self.sequences[fieldID].Restart(self.SeqCount)
                if self.log and self.verbose>0:
                    self.log.info('%sProp: RestartSequences() sequence for propID=%d field=%i restarted' % (self.propFullName, self.propID,fieldID))

        return 

    def updateTargetList (self, dateProfile, obsProfile, sky, fov ):

        return


