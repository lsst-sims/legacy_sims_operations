#!/usr/bin/env python

from utilities import *
from LSSTObject import *
from Filters import *
from Observation import *
from ObsHistory import *
from Distribution import *
from Sequence     import *
from Proposal import *
from SeqHistory import *


class TransientProp (Proposal):
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
                  logfile='./TransientProp.log',
                  verbose=0,
                  transientConf=DefaultNEAConfigFile):
        """
        Standard initializer.
        
	lsstDB      LSST DB access object        
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
        super (TransientProp, self).__init__ (lsstDB=lsstDB,
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
	self.blockedTargets = []

        # Create the ObsHistory instance and cleanup any leftover
        self.obsHistory = ObsHistory (lsstDB=self.lsstDB,
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

	self.SeqCount = 0

        return

    
    def start (self):
        """
        Activate the TransientProp instance.

        """

        # PAUSE
#        yield hold, self
        return

    def startNight(self,dateProfile,moonProfile,startNewLunation,randomizeSequencesSelection,nRun, mountedFiltersList):

        super (TransientProp, self).startNight (dateProfile,moonProfile,startNewLunation, mountedFiltersList)

        self.tonightTargets = self.targets.copy()

        date = 0
        duration   =self.seqDuration
        distrib = IvezicDistribution(date,
                                     duration,
                                     intervals  =self.visitIntervals,
                                     repeats    =self.cycleRepeats,
                                     repeatdelay=self.cycleInterval )
        filters = self.seqFilters
	if not isinstance(filters, list):
	    filters = [filters]

        # deletes all sequences that did not start while the fields were
        # in the region for starting new sequences.
        notstarted = 0
        for fieldID in self.sequences.keys():
            if not fieldID in self.targetsNewSeq.keys():
                if self.sequences[fieldID].IsIdle():
                    notstarted+=1
                    del self.sequences[fieldID]

        # counts the active sequences in the target region
	currentActiveSequences = 0
	for fieldID in self.sequences.keys():
	    if fieldID in self.tonightTargets.keys():
		if (not self.sequences[fieldID].IsLost()) and (not self.sequences[fieldID].IsComplete()):
		    currentActiveSequences+=1

        # creates the sequence object for all the new fields in the restricted area
        newseq=0
	restartedlost=0
	restartedcomplete=0
	keptsequences=0
#        listOfNewFields=self.targetsNewSeq.keys()
	listOfNewFields=sorted(self.targetsNewSeq.iterkeys())
	while (len(listOfNewFields)>0 and currentActiveSequences<self.maxNumberActiveSequences):
		if randomizeSequencesSelection:
		    fieldID=random.choice(listOfNewFields)
		else:
		    fieldID=listOfNewFields[0]
		listOfNewFields.remove(fieldID)
                if not fieldID in self.sequences.keys():
		    self.SeqCount += 1
                    self.sequences[fieldID]=IvezicSequence(self.propID,
	    						   fieldID,
							   self.SeqCount,
						           filters,
						           distrib,
						           date,
						           duration,
						           self.maxMissedEvents)
                    newseq+=1
		    currentActiveSequences+=1
                elif self.sequences[fieldID].IsLost():
        	    if self.restartLostSequences:
			self.SeqCount += 1
		        self.sequences[fieldID].Restart(self.SeqCount)
		        restartedlost+=1
			currentActiveSequences+=1
		    else:
                        del self.tonightTargets[fieldID]

	        elif self.sequences[fieldID].IsComplete():
		    if self.restartCompleteSequences and not self.blockCompleteSeqConsecutiveLunations:
			self.SeqCount += 1
                        self.sequences[fieldID].Restart(self.SeqCount)
		        restartedcomplete+=1
			currentActiveSequences+=1
                    else:
                        del self.tonightTargets[fieldID]

	# From the broad target area, just keep the fields
	# associated to a target that is not lost and not complete
	for fieldID in self.tonightTargets.keys():
	    if fieldID in self.sequences.keys():
                if self.sequences[fieldID].IsLost() or self.sequences[fieldID].IsComplete():
		    del self.tonightTargets[fieldID]
		else:
                    keptsequences+=1
	    else:
		del self.tonightTargets[fieldID]

        if ( self.log ):
            self.log.info('%sProp: startNight() propID=%d added %i new sequences, deleted %i notstarted, restarted %i lost, restarted %i complete, kept %i' % (self.propFullName, self.propID,newseq, notstarted, restartedlost, restartedcomplete, keptsequences))

        return

    def GetProgressPerFilter(self):
                                                                                                                                                                                                                             
        coaddedNumber = 0
        coaddedProgress = 0
        for fieldID in self.sequences.keys():
            if not self.sequences[fieldID].IsLost():
                coaddedNumber += 1
                coaddedProgress += self.sequences[fieldID].GetProgress()
	if coaddedNumber > 0:
	    coaddedProgress /= coaddedNumber
        if ( self.log ):
            self.log.info('%sProp: GetProgressPerFilter() propID=%d Sequence progress: %.3f%%' % (self.propFullName, self.propID, 100*coaddedProgress))
                                                                                                                                                                                                                    
        progressFilter = {}
        for filter in self.seqFilters:
            progressFilter[filter]  = coaddedProgress
        if ( self.log ):
            for filter in progressFilter.keys():
                self.log.info('%sProp: GetProgressPerFilter() propID=%d Filter progress: %10s = %.3f%%' % (self.propFullName, self.propID, filter, 100*progressFilter[filter]))
                                                                                                                                                                                                                             
        return progressFilter

    def RankWindow(self, deltat, scale=300.0):
        """
        Evaluates the priority of an event according to the proximity to the
        event time.

        Input
        deltat: the proximity in seconds to the event (current T - event T)
        scale:  the time scale for the window. Default 5 minutes.
        """

        w_start  = self.windowStart*scale
        w_inflex = self.windowMax  *scale
        w_end    = self.windowEnd  *scale

        if deltat <= w_start-DAY:
            rank = -0.1
        elif   deltat <= w_start:
	    rank = 0.0
        elif deltat <= w_inflex:
            rank = (deltat-w_start)/(w_inflex-w_start)
        elif deltat <= w_end:
            rank = 1.0
        else:
            rank = -1.0
            
        return rank

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
           self.log.info('%sProp: suggestObs() propID=%d' %(self.TransientType, self.propID))
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
	# before checking observing cycle to assure the clearance
	# of winners and losers list avoiding wrong serendipity observations.
        self.clearSuggestList()

	# Check the start/end of observing cycle.
	# For NEA the lunation is checked
	if self.CheckObservingCycle(date):

            # First of all, discard all the targets which are not visible
            # right now.
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
                ra = self.tonightTargets[fieldID][0]
                dec = self.tonightTargets[fieldID][1]
                i = inFieldID.index (fieldID)

                #=============================================================
                # RAA --- To Be Done  04 May 2005
                # Factor into ranking the proximity of this target to all fields
                # check all target fields for this local proposal
                #
                #    # ? If proximity == 0 then want to set factor to infinite?
                #
                #    # do something with the telescope's proximity to this Field
                #    .....  inproximity[i]   ....
                #=============================================================

                if (fieldID==self.last_observed_fieldID) and (self.last_observed_wasForThisProposal) and (not self.AcceptConsecutiveObs):
                    continue

                airmass = intargetProfiles[i][0]
                if (airmass > self.maxAirmass):
                    if self.log and self.verbose>2:
                        self.log.info('%sProp: suggestObs() propID=%d field=%i too low:%f' % (self.TransientType, self.propID,fieldID,airmass))
                    fields_invisible+=1
                    continue

                distance2moon = intargetProfiles[i][5]
                if (distance2moon < minDistance2Moon):
                    fields_moon+=1
                    # remove the target for the rest of the night if it is too close to the moon
                    del self.tonightTargets[fieldID]
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

                elif rankTime < 0.0:

                    fields_missed+=1

                    obsHist = self.lsstDB.addMissedObservation(self.sequences[fieldID].GetNextFilter(), date, mjd, 0, lst_RAD, self.sessionID, fieldID)
                    self.sequences[fieldID].missEvent(date, obsHist.obsHistID)

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
        self.maxSeeing = float (seeing)
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
    
    
    def closeObservation (self, observation, twilightProfile, obsHistID):
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

        if ( self.log and self.verbose > 1 ):
            self.log.info('TransientProp: closeObservation()')

        obs = super (TransientProp, self).closeObservation(observation, twilightProfile, obsHistID)

        if obs != None:
            self.sequences[obs.fieldID].closeEvent(obs.date, obs.filter)
            progress = self.sequences[obs.fieldID].GetProgress()

            if self.log and self.verbose>0:
                t_secs = obs.date%60
                t_mins = (obs.date%3600)/60
                t_hour = (obs.date%86400)/3600
                t_days = (obs.date)/86400

                self.log.info('%sProp: closeObservation() propID=%d field=%d filter=%s propRank=%.4f finRank=%.4f t=%dd%02dh%02dm%02ds progress=%d%%' % (self.propFullName, self.propID, obs.fieldID, obs.filter, obs.propRank, obs.finRank, t_days, t_hour, t_mins, t_secs, int(100*progress)))

            # if sequence is complete, then deletes target from tonight's list.
            if progress == 1.0:
		self.CompleteSequence(obs.fieldID, obs.date)
       
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

        del self.tonightTargets[fieldID]

        if (self.log and self.verbose >0):
            self.log.info('%sProp: closeObservation() sequence COMPLETE for propID=%d field=%d' % (self.propFullName, self.propID, fieldID))

	return

    def FinishSequences(self, obsdate):
        """
        Finishes the current sequences.
        """
        if ( self.log ):
            self.log.info ('TransientProp: FinishSequences()')

        for fieldID in self.sequences.keys():
            if self.sequences[fieldID].IsProgressing():
                if ( self.log ):
                    self.log.info('%sProp: FinishSequences() propID=%d sequence LOST for field=%i end of cycle' % (self.propFullName, self.propID, fieldID))
                self.sequences[fieldID].SetLost()

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
            if self.sequences[fieldID].IsProgressing():
                if ( self.log ):
                    self.log.info('%sProp: closeProposal() propID=%d sequence LOST for field=%i end of simulation' % (self.propFullName, self.propID, fieldID))
                self.sequences[fieldID].SetLost()

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
            self.log.info('TransientProp: RestartFinishedSequences() propID=%d' %(self.propID))

        for fieldID in self.sequences.keys():
            if self.sequences[fieldID].IsLost() or (self.sequences[fieldID].IsComplete() and not fieldID in self.blockedTargets):
		self.SeqCount += 1
                self.sequences[fieldID].Restart(self.SeqCount)
                if self.log and self.verbose>0:
                    self.log.info('TransientProp: RestartSequences() sequence for propID=%d field=%i restarted' % (self.propID,fieldID))

        return 

    def updateTargetList (self, dateProfile, obsProfile, sky, fov ):

        return


