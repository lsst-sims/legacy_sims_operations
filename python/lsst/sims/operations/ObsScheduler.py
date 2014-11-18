#!/usr/bin/env python

"""
ObsScheduler

Inherits from: LSSTObject : object

Class Description
The ObsScheduler class is the access point to the telescope 
itself (via the instaance variable telQueue). In the simulation
paradigm, the telescope (of better yet the telescope queue) is a
Resource object. Processes (observations in our case) compete for 
access to the Resource. The Process with the highest priority wins.

In order to have control over recomputing priorities, down time and
Resource availability in general, the artefact of a ObsScheduler
instance is created.


Method Types
Constructor/Initializers
- __init__

Scheduling strategy
- applyCuts (internal use)
- applyBonuses (internal use)
- suggestObservation

Handle Proposal instances
- addProposal
- removeProposal
- setProposalPriority

Record the observation
- closeObservation
"""

from utilities import *
from LSSTObject import *
from Proposal import *
from Observation import *
from TimeHistory import *
import copy
import heapq

class ObsScheduler (LSSTObject):
    def __init__ (self, 
                  lsstDB,
		  schedulingData,
		  obsProfile,
                  dbTableDict,
                  telescope,
                  weather, 
                  sky,
                  filters,
                  sessionID,
                  runSeeingFudge,
                  schedulerConf,
                  log=False,
                  logfile='./ObsScheduler.log',
                  verbose=0):
        """
        Standard initializer.
        
	lsstDB      LSST DB access object        
	obsProfile  ....
        dbTableDict DB table names
        telescope:  an instance of Instrument class.
        weather     instance of the Weather class.
        sky         instance of the AstronomicalSky class
        filters     ...
        sessionID:  An integer identifying this particular run.
        runSeeingFudge:
        schedulerConf:
        log         False if not set, else: log = logging.getLogger("...")
        logfile     Name (and path) of the desired log file.
                    Defaults "././ObsScheduler.log".
        verbose:    Log verbosity: 0=minimal, 1=wordy, >1=very verbose

        """
	self.lsstDB = lsstDB        
	self.schedulingData = schedulingData
	self.obsProfile = obsProfile
        self.telescope = telescope
        self.weather = weather
        self.sky = sky
        self.filters = filters
        self.sessionID = sessionID
        self.runSeeingFudge = runSeeingFudge
        self.dbTableDict = dbTableDict
        
        # Force suggestObs to reacquire the top ranked target observations
        self.recalcSky = 0
	self.reuseRanking = 0

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up ObsScheduler logger"
            log = logging.getLogger("ObsScheduler")
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.INFO)
                                                                                
        self.log=log
        self.logfile=logfile
        self.verbose = verbose

        # Proposals and their relative importance (rank)
#        self.interProposalRank = {}
	self.proposals_list = []
        
        # This is to keep track of the number of completed proposals
        # so that we do not query them anymore
        self.completedProposals = 0
        
        # Which proposals proposed the winner observation?
        self.winningProposals = []
        
        # List of potential targets (observations are a fieldID a filterID
        # and a rank)
        self.targets = {}
#        self.targetProfiles = {}
        
        self.targetRank = {}
	self.targetXblk = {}
#        self.masterTargets = {}
        self.winner = None
        
        # Dictionary of fieldID: (ra, dec) values
        #self.fieldCoords = {}
        
        # Dictionary of fieldID: filter values
        self.fieldFilter = {}

        config_dict, pairs = readConfFile(schedulerConf)
        self.maxSlewTimeBonus  = eval(str(config_dict['MaxSlewTimeBonus']))
        self.numSuggObsPerProp = int(config_dict['NumSuggestedObsPerProposal'])
        # recalcSkyCount is not being used .. removed from Config files therefore removing it here
	# 3/4/2014 Srinivasan Chandrasekharan
	# self.recalcSkyCount = int(config_dict['recalcSkyCount'])
        self.recalcSkyCount = 0
	self.reuseRankingCount = int(config_dict['reuseRankingCount'])
        self.log.info("reuseRankingCount=%d" % self.reuseRankingCount)
        self.tooGoodSeeingLimit = float(config_dict['tooGoodSeeingLimit'])
	self.randomizeSequencesSelection = eval(str(config_dict['randomizeSequencesSelection']))

        # save Scheduler configuration parameters to the DB
        for line in pairs:
            storeParam (self.lsstDB, sessionID, 0, 'scheduler', line['index'], line['key'], line['val'])

        self.maxExposureTime = 0.0
        self.verbose = verbose

	self.exclusiveObs = None

	self.NewMoonPeriod = False
	self.NewMoonPhaseThreshold = float(config_dict["NewMoonPhaseThreshold"])
	self.NminFiltersToSwap = int(config_dict["NminFiltersToSwap"])
        self.NmaxFiltersToSwap = int(config_dict["NmaxFiltersToSwap"])
	self.schedulingData.newMoonThreshold = self.NewMoonPhaseThreshold

	try:
	    self.minDistance2Moon = float(config_dict["MinDistance2Moon"])*DEG2RAD
	except:
	    self.minDistance2Moon = 0.0

        return
    
    def startNight (self, dateProfile, moonProfile, 
                          startNewLunation, startNewYear, fov, nRun, nightCnt):
        """
        Perform any necessary setup for the start of the night,
        such as updating the list of visible fields. If timely,
        initiate new lunation processing and/or new year, also.
        
        Input
            dateProfile    Precomputed values relating to current simdate/time:
                                date
                                mjd
                                lst_RAD
            moonProfile    precomputed values relating to moon phase:
                                moonRA_RAD
                                moonDec_RAD
                                moonPhase_PERCENT
            startNewLunation    True = moon start waning == new lunation
            startNewYear        True = start of first lunation after 2cd year
                                    (or  more) simulated time 
            fov     		Field of View (degrees) of the telescope
            nightCnt		count of nights simulated
        
        Return
            None
        """
        if ( self.log) :
            self.log.info("obsScheduler:startNight")

	(date,mjd,lst_RAD) = dateProfile
        self.nightCnt = nightCnt

        # Force suggestObs to reacquire the top ranked target observations
        self.recalcSky = 0
	self.reuseRanking = 0
        self.targets = {}
#        self.masterTargets = {}

	self.exclusiveObs = None

        mountedFiltersList = self.telescope.GetMountedFiltersList()

#        for proposal in self.interProposalRank.keys ():
	for proposal in self.proposals_list:
            if proposal.nextNight < self.nightCnt:
                proposal.nextNight = self.nightCnt + proposal.hiatusNights
            #print "ObsScheduler.startNight: prop %s prop.nextNight = %d self.nightCnt = %d prop.hiatus = %d" % (proposal.propFullName, proposal.nextNight, self.nightCnt, proposal.hiatusNights)
	    if proposal.IsActiveTonight(date, self.nightCnt) == False:
		continue
      
            # Build new target list
            fields = proposal.updateTargetList(dateProfile, self.obsProfile,
                                               self.sky, fov)
            self.targets.update(fields)
            print "Targetcount:%d" % len(self.targets)
    
            # Notify all proposals of startNight processing
            proposal.startNight (dateProfile, moonProfile, startNewLunation, self.randomizeSequencesSelection, nRun, mountedFiltersList)
            if startNewYear == True:
                # Notify all proposal of startYear Processing
                proposal.startNewYear()

	self.schedulingData.startNight(dateProfile)

        return

    # flush sky brightness cache and reset recalcSky to zero to
    # recalculate the sky for precise behavior regarding twilight 

    def flushSkyCache (self):
        self.recalcSky = 0
        self.sky.skyBrightnessCache.clear()

    def startDay(self, moonProfile):

	self.moonProfile = moonProfile
	(moonRA_RAD, moonDec_RAD, moonPhase_PERCENT) = self.moonProfile

	if (self.log):
	    self.log.info('obsScheduler: startDay(): moonPhase=%f' % (moonPhase_PERCENT))

	if self.NewMoonPeriod:
	    if moonPhase_PERCENT > self.NewMoonPhaseThreshold:
		self.SwapExtraFilterOut()
		self.NewMoonPeriod = False
	else:
	    if moonPhase_PERCENT < self.NewMoonPhaseThreshold:
		self.SwapExtraFilterIn()
		self.NewMoonPeriod = True

        mountedFiltersList = self.telescope.GetMountedFiltersList()
        unmountedFiltersList=self.telescope.GetUnmountedFiltersList()
        print "Mounted filters = "+str(mountedFiltersList)
        print "Unmounted filters = "+str(unmountedFiltersList)

	return    

    def SwapExtraFilterIn(self):

	if (self.log):
            self.log.info('obsScheduler: SwapExtraFilterIn()')

	# obtains the weighted need for all the filters, mounted and unmounted.
	mountedFiltersList = self.telescope.GetMountedFiltersList()
	removableFiltersList=self.telescope.GetRemovableFiltersList()
	unmountedFiltersList=self.telescope.GetUnmountedFiltersList()
	coaddedNeedPerFilter = {}
        for filter in mountedFiltersList+unmountedFiltersList:
            coaddedNeedPerFilter[filter] = 0.0
	(date,mjd,lst_RAD) = self.dateProfile
#	for proposal in self.interProposalRank.keys():
	for proposal in self.proposals_list:
	    if proposal.IsActive (date, self.nightCnt) == False:
		continue

	    ProgressPerFilter = proposal.GetProgressPerFilter()
	    propPriority = proposal.GetPriority()
	    for filter in mountedFiltersList+unmountedFiltersList:
		if filter in ProgressPerFilter.keys():
		    coaddedNeedPerFilter[filter] += propPriority*(1.0-ProgressPerFilter[filter])
		else:
		    # filter is not needed by the proposal
		    coaddedNeedPerFilter[filter] += 0.0
        if ( self.log ):
            for filter in coaddedNeedPerFilter.keys():
                self.log.info('obsScheduler: SwapExtraFilterIn() Filter coadded need: %10s = %.3f' % (filter, 100.0*coaddedNeedPerFilter[filter]))

	# Creates a sorted queue for the removable filters, least needed first.
	removequeue = []
	for filter in removableFiltersList:
	    heapq.heappush(removequeue, (coaddedNeedPerFilter[filter], filter))

        # Creates a sorted queue for the insertable filters, most needed first.
        insertqueue = []
        for filter in unmountedFiltersList:
            heapq.heappush(insertqueue, (-coaddedNeedPerFilter[filter], filter))

	self.LastRemovedFilters = []
	self.LastInsertedFilters = []
	# Selects the NminFiltersToSwap,
	# the N with the lowest need in the removable list,
	# and the N with the highest need in the insertable list.
	for k in range(min(self.NminFiltersToSwap,len(removequeue),len(insertqueue))):
	    self.LastRemovedFilters.append(heapq.heappop(removequeue)[1])
	    self.LastInsertedFilters.append(heapq.heappop(insertqueue)[1])

	# If NmaxFiltersToSwap > NminFiltersToSwap, selects additional filters to swap,
	# if there are insertable filters in more need than the removable ones.
        for k in range(min(self.NmaxFiltersToSwap-self.NminFiltersToSwap,len(removequeue),len(insertqueue))):
            removable = heapq.heappop(removequeue)
	    removable_need    =   removable[0]
	    removable_filter  =   removable[1]
	    insertable= heapq.heappop(insertqueue)
	    insertable_need   = -insertable[0]
	    insertable_filter =  insertable[1]
	    if removable_need < insertable_need:
		self.LastRemovedFilters.append(removable_filter)
		self.LastInsertedFilters.append(insertable_filter)

	# Performs the filter swapping
	for k in range(len(self.LastRemovedFilters)):
	    self.telescope.MountFilter(self.LastInsertedFilters[k], self.LastRemovedFilters[k])
	
	return

    def SwapExtraFilterOut(self):

        if (self.log):
            self.log.info('obsScheduler: SwapExtraFilterOut()')

        for k in range(len(self.LastRemovedFilters)):
            self.telescope.MountFilter(self.LastRemovedFilters[k], self.LastInsertedFilters[k])

        return

#    def applyCuts (self):
#        """
#        Discard fields by applying pre-defined cuts. It is assumed 
#        that cuts are to be appied as of now().
#        
#        This method is invoked by suggestObs() and should not be 
#        called directly.
#        """
#        return
    
    
#    def applyBonuses (self):
#        """
#        Assign fields a ranking (in absolute scale) by applying 
#        pre-defined bonus rules. It is assumed that bonuses are to be 
#        evaluated as of now().
#        
#        This method is invoked by suggestObs() and should not be 
#        called directly.
#        """
#        return
    
    
    def suggestObservation (self, dateProfile, moonProfile, twilightProfile,
			cloudiness):
        """
        Return the rank of (currently) highest ranking observation as 
        of date (in seconds since Jan 1 of the simulated year).
        
        Input
            dateProfile    Precomputed values relating to current simdate/time:
                                date
                                mjd
                                lst_RAD
            moonProfile    precomputed values relating to moon phase:
                                moonRA_RAD
                                moonDec_RAD
                                moonPhase_PERCENT
	    cloudiness	   cloudiness for time t at site
        Return
        (rank, exposureTime, slewTime)
        """

        #if ( self.log) :
        #    self.log.info("obsScheduler:suggestObservation: date: %f recalcSky: %d" % (date, self.recalcSky))

        self.dateProfile = dateProfile
        (date,mjd,lst_RAD) = dateProfile
        self.moonProfile = moonProfile
	self.twilightProfile = twilightProfile
        self.transparency = cloudiness

	(sdnight, sdtime) = self.schedulingData.findNightAndTime(date)

#	self.log.info("ObsScheduler:suggestObservation: reuseRanking=%d" % self.reuseRanking)
	if self.reuseRanking <= 0:
          # Dictionary of {fieldID: {filter: totRank}}
          self.targetRank = {}
	  self.targetXblk = {}
            
          # Recompute sky data?
          if self.recalcSky <= 0:
            # Fetch raw seeing data 
            seeing = self.weather.getSeeing (date)
            self.rawSeeing = seeing

            # Adjust seeing if too good to be true
            if seeing < self.tooGoodSeeingLimit:
                if ( self.log) :
                    self.log.info("obsScheduler:suggestObservation: seeing (%f) too good, reset to %f date:%d." % (seeing, self.tooGoodSeeingLimit, date))
                seeing = self.tooGoodSeeingLimit
    
            # factor in the seeing fudge for the weather data supplied
            self.seeing =  seeing * self.runSeeingFudge
        
            # Compute sky quantities for each field
#            self.targetProfiles = map (self.computeTargetProfiles, self.targets)
            self.recalcSky = self.recalcSkyCount

          # Build proximity array betwn cur tel position & potential fields
          # first: build FieldPosition (peerFields) list ordered identically 
          #   to FieldID (targets) list
#          sortedFieldID = []
#          sortedFieldRaDec = []
#	  for aField in sorted(self.targets.iterkeys()):
#            sortedFieldID.append(aField)
#            sortedFieldRaDec.append((self.targets[aField][0]*DEG2RAD, 
#                                     self.targets[aField][1]*DEG2RAD)) 
          # Second: build proximity array
#          (ra_RAD,dec_RAD) = self.telescope.GetCurrentTelescopePosition\
#                                                (dateProfile)
#          proximity = distance((ra_RAD,dec_RAD), sortedFieldRaDec)

          totPotentialTargets = 0

	  for proposal in self.proposals_list:
	    if not proposal.IsActive(date, self.nightCnt):
		continue

            # note: since proximity is ordered accd sortedFieldID--need to
            #       pass that array instead of self.targets.
            targetObs = proposal.suggestObs(self.dateProfile,
#                                            self.moonProfile,
                                            self.numSuggObsPerProp, 
#                                            sortedFieldID, 
#                                            proximity,
#                                            self.targetProfiles,
					    self.exclusiveObs,
					    self.minDistance2Moon,
					    self.rawSeeing,
					    self.seeing,
					    self.transparency,
					    sdnight, sdtime)
            if not targetObs:
                continue
                
            self.expTime = proposal.exposureTime
            propID = proposal.propID

            for obs in targetObs:
                fieldID = obs.fieldID
                rank = obs.propRank
                filter = obs.filter

#                self.log.info("ObsScheduler.suggestObservations(): propID=%d fieldID=%d rank=%f filter=%s exclusive=%s" % (propID, fieldID, rank, filter, obs.exclusiveBlockRequired))

                ra = obs.ra
                dec = obs.dec
		if obs.exclusiveBlockRequired:
		    propIDforXblk = propID
		else:
		    propIDforXblk = None

		if fieldID not in self.targetRank:
		    self.targetRank[fieldID] = {filter: rank}
		    self.targetXblk[fieldID] = {filter: propIDforXblk}
                    totPotentialTargets += 1
		else:
		    if filter not in self.targetRank[fieldID]:
			self.targetRank[fieldID][filter] = rank
			self.targetXblk[fieldID][filter] = propIDforXblk
			totPotentialTargets += 1
		    else:
			self.targetRank[fieldID][filter] += rank
			if (propIDforXblk != None):
			    self.targetXblk[fieldID][filter] = propIDforXblk

#          self.log.info("totPotentialTargets = %d" % totPotentialTargets)

	  if totPotentialTargets == 0:
            if ( self.log) :
                self.log.info("obsScheduler:suggestObservation: No suggestions from proposals")
  
	  if totPotentialTargets < self.reuseRankingCount:
	    self.reuseRanking = totPotentialTargets
	  else:
	    self.reuseRanking = self.reuseRankingCount
	
        # Choose the best target (taking slew time into consideration)
        maxrank = 0
        self.winner = None
        t=0
        s=0

	fields = sorted(self.targetRank.iterkeys())
        for fieldID in fields:
	    keyList = sorted(self.targetRank[fieldID].iterkeys())
            for key in keyList:
                rank = self.targetRank[fieldID][key]
                if rank <= 0.0 :
                    continue;
                filter = key
	        expTime = float(self.expTime)
		propIDforXblk = self.targetXblk[fieldID][filter]
		ra  = self.targets[fieldID][0]
		dec = self.targets[fieldID][1]

                # Compute slew time 
                slewTime = self.telescope.GetDelayForTarget( 
                                    ra_RAD  = ra*DEG2RAD,
                                    dec_RAD = dec*DEG2RAD,
                                    dateProfile = self.dateProfile,
                                    exposureTime = expTime,
                                    filter = filter)
                # slewTime <0 means an invalid position for the telescope
                #                       too low or too close to zenith
                if slewTime >= 0.0:
                    # Now, divide the field rank by the slew time
                    slewRank = rank + self.maxSlewTimeBonus * max(44.0/(slewTime+40.0)-0.1,0.0)
#		    self.log.info("candidate fieldID=%s filter=%s rank=%f slewTime=%f slewRank=%f" % (fieldID, filter, rank, slewTime, slewRank))
                    if (slewRank > maxrank):
                        maxrank = slewRank
                        # Save current winner details for later Obs instan
                        win_slewTime = slewTime
                        win_exposureTime = expTime
                        win_fieldID=int(fieldID)
                        win_filter = filter
			win_propXblk = propIDforXblk
                        win_ra = ra
                        win_dec = dec
        
        # Return the best ranking
        if (maxrank > 0):
            win_exposureTime *= self.filters.ExposureFactor[win_filter]
	    t = win_exposureTime
            s = win_slewTime
            self.winner = Observation (ra = win_ra,
                                dec = win_dec,
                                fieldID = win_fieldID,
                                filter = win_filter,
                                slewTime = win_slewTime,
                                exposureTime = win_exposureTime,
				exclusiveBlockRequired = (win_propXblk != None),
				propID = win_propXblk,
                                dateProfile = self.dateProfile,
                                moonProfile = self.moonProfile)
            self.winner.finRank = maxrank
            self.winner.rawSeeing = self.rawSeeing
	    self.winner.transparency = self.transparency
#            self.log.info("WINNER date = %d fieldID = %d filter=%s maxrank=%f propID=%s" % (date,win_fieldID,win_filter,maxrank,win_propXblk))

	    if self.winner.exclusiveBlockRequired == True:
		self.exclusiveObs = copy.deepcopy(self.winner)
		self.recalcSky = 0
		self.reuseRanking = 0
	    else:
		self.exclusiveObs = None
		self.recalcSky -= 1
		self.reuseRanking -= 1
        else:
            t = 0
            s=0
            self.recalcSky = 0
	    self.reuseRanking = 0

#        self.log.info("reuseRanking=%d" % self.reuseRanking)

#        return (maxrank, t, s)
	return self.winner    

#    def computeTargetProfiles (self, fieldID):
        """
        Precompute quantities relating to a Field for subsequent use 
        Given a fieldID, query self.sky for the airmass and sky brightness,
        query self.filter for filterlist based on sky brightness.

        Input
            fieldID     identifier of Field to profile
            peerFields  

        Output
            targetProfile   an array containing
                airmass
                skyBrightness
                filterlist
                transparency
                cloudSeeing
                distance2moon
                altitude_RAD

        """
#        ra, dec = self.targets[fieldID]

#        dateProfile = self.dateProfile
#        (airmass,altitude_RAD,azimuth_RAD,pa_RAD) = self.sky.airmass (dateProfile, ra, dec)
#        (date,mjd,lst_RAD) = dateProfile
#        cloudSeeing=0.0

        # throw away brightProfile for now.  We'll get it when we store
        # the winner. - MM
#        (skyBrightness,distance2moon,moonAlt_RAD, brightProfile) = \
#                self.sky.getSkyBrightness (fieldID,
#                                           ra, dec,
#                                           altitude_RAD,
#                                           dateProfile=dateProfile, 
#                                           moonProfile=self.moonProfile,
#					   twilightProfile=self.twilightProfile)

#	filterlist=self.filters.computeFilterSeeing(self.seeing,airmass)

#        return (airmass, skyBrightness, filterlist, self.transparency,
#                 cloudSeeing,distance2moon,altitude_RAD,self.rawSeeing,
#                 moonAlt_RAD,azimuth_RAD)

    
    def closeObservation (self, winner):
        """
        Notify the various proposals that suggested the winner
        observation that that observation took place.

        Needs to pass along the required slew time since not embeded in Obs
        """
        # Move the telescope
        (delay,rotatorSkyPos_RAD,rotatorTelPos_RAD,alt_RAD,az_RAD, slewdata, slewinitstate, slewfinalstate, slewmaxspeeds, listslewactivities) = self.telescope.Observe(\
                                                    winner.ra*DEG2RAD,
                                                    winner.dec*DEG2RAD,
                                                    self.dateProfile,
                                                    winner.exposureTime,
                                                    winner.filter,
                                                    winner.slewTime)
        #print "SUCCESS: delay:%f rotSkyPos:%f rotTelPos:%f" % (delay,rotator_skypos_RAD,rotator_telpos_RAD)

        # MM - debug error check
        if delay != winner.slewTime:
            print "WARNING: ObsScheduler.closeObservation delay:%f != winner.slewTime:%f" % (delay,winner.slewTime)
        
        # install final parameters in the winning observation
        winner.rotatorSkyPos = rotatorSkyPos_RAD
        winner.rotatorTelPos = rotatorTelPos_RAD
        winner.altitude = alt_RAD
        winner.azimuth  = az_RAD
	winner.parallactic = slewfinalstate.pa

        (sunAlt,sunAz) = self.sky.getSunAltAz(self.dateProfile)
        winner.airmass = 1/math.cos(1.5708 - alt_RAD)

        winner.sunAlt = sunAlt
        winner.sunAz  = sunAz

        winner.night = self.nightCnt

        # Adjust date to start of exposure by accounting for slew time - MM
        # Is self.dateProfile == self.winner.dateProfile here?
        (date,mjd,lst_RAD) = self.dateProfile
#        if date != winner.date:
#            print "WARNING: ObsScheduler.closeObservation date:%d != winner.date:%d" % (date,winner.date)

        t = date + delay
	dateProfile = self.sky.computeDateProfile(t)
        (winner.date, winner.mjd, winner.lst) = dateProfile
	moonProfileAltAz = self.sky.computeMoonProfileAltAz(t)
        (winner.moonRA_RAD, winner.moonDec_RAD, winner.moonPhase, winner.moonAlt, winner.moonAz) = moonProfileAltAz
	moonProfile = (winner.moonRA_RAD, winner.moonDec_RAD, winner.moonPhase)

        (skyBright,distance2moon,moonAlt_RAD,brightProfile) = self.sky.getSkyBrightness(winner.fieldID, winner.ra, winner.dec, winner.altitude, dateProfile, moonProfile, self.twilightProfile)
        winner.skyBrightness = skyBright
        winner.distance2moon = distance2moon
        (winner.phaseAngle, winner.extinction, winner.rScatter,
        winner.mieScatter, winner.moonIllum,
	winner.moonBright, winner.darkBright) = brightProfile

	winner.filterSkyBright = self.filters.computeSkyBrightnessForFilter(winner.filter, skyBright, t, self.twilightProfile, moonProfileAltAz)
	filterSeeingList = self.filters.computeFilterSeeing(self.seeing, winner.airmass)
	winner.seeing = filterSeeingList[winner.filter]

	# calculate current solar elongation in DEGREES
        target = (winner.ra*DEG2RAD, winner.dec*DEG2RAD)
        solarElong_RAD = self.sky.getPlanetDistance ('Sun',target, winner.date)
        winner.solarElong = math.degrees(solarElong_RAD)

        self.log.info("visit=%i night=%i date=%i field=%i filter=%s expTime=%f visitTime=%f lst=%f" % (slewdata.slewCount, winner.night, winner.date, winner.fieldID, winner.filter, winner.exposureTime, winner.visitTime, winner.lst))
        self.log.info("    finRank=%f airmass=%f brightness=%f filtBright=%f rawSeeing=%f seeing=%f" % (winner.finRank, winner.airmass, winner.skyBrightness, winner.filterSkyBright, winner.rawSeeing, winner.seeing))
        self.log.info("    alt=%f az=%f pa=%f moonRA=%f moonDec=%f moonPh=%f dist2moon=%f transp=%f" % (winner.altitude, winner.azimuth, winner.parallactic, winner.moonRA_RAD, winner.moonDec_RAD, winner.moonPhase, winner.distance2moon, winner.transparency))
        self.log.info("    solarE=%f sunAlt=%f sunAz=%f moonAlt=%f moonAz=%f moonBright=%f darkBright=%f" % (winner.solarElong, winner.sunAlt, winner.sunAz, winner.moonAlt, winner.moonAz, winner.moonBright, winner.darkBright))

        obsHist = self.lsstDB.addObservation(slewdata.slewCount, winner.filter, winner.date, winner.mjd,
				winner.night, winner.visitTime, winner.exposureTime,
				winner.finRank, winner.seeing,
				winner.transparency, winner.airmass,
				winner.skyBrightness, winner.filterSkyBright,
				winner.rotatorSkyPos, winner.lst,
				winner.altitude, winner.azimuth,
				winner.distance2moon, winner.solarElong,
		                winner.moonRA_RAD, winner.moonDec_RAD,
		                winner.moonAlt, winner.moonAz, winner.moonPhase,
		                winner.sunAlt, winner.sunAz,
		                winner.phaseAngle, winner.rScatter,
		                winner.mieScatter, winner.moonIllum,
		                winner.moonBright, winner.darkBright,
				winner.rawSeeing,
                                0.0, 0.0, self.sessionID, winner.fieldID) # need to ask Francisco about rawSeeing, sending 0.0 right now and also about wind and humidity
        slewHist = self.lsstDB.addSlewHistory(slewdata.slewCount,
				slewdata.startDate,
				slewdata.endDate,
				slewdata.slewTime,
				slewdata.slewDist,
				obsHist.obsHistID,
                obsHist.Session_sessionID)

        self.lsstDB.addSlewState(slewinitstate.slewStateDate,
        			slewinitstate.tra,
        			slewinitstate.tdec,
        			slewinitstate.tracking,
        			slewinitstate.alt,
        			slewinitstate.az,
        			slewinitstate.pa,
        			slewinitstate.DomAlt,
        			slewinitstate.DomAz,
        			slewinitstate.TelAlt,
        			slewinitstate.TelAz,
        			slewinitstate.RotTelPos,
        			slewinitstate.Filter,
        			slewinitstate.state,
                    slewHist.slewID)
        self.lsstDB.addSlewState(slewfinalstate.slewStateDate,
                                slewfinalstate.tra,
                                slewfinalstate.tdec,
                                slewfinalstate.tracking,
                                slewfinalstate.alt,
                                slewfinalstate.az,
                                slewfinalstate.pa,
                                slewfinalstate.DomAlt,
                                slewfinalstate.DomAz,
                                slewfinalstate.TelAlt,
                                slewfinalstate.TelAz,
                                slewfinalstate.RotTelPos,
                                slewfinalstate.Filter,
                                slewfinalstate.state,
                                slewHist.slewID)

        self.lsstDB.addSlewMaxSpeeds(slewmaxspeeds.DomAltSpd,
				slewmaxspeeds.DomAzSpd,
				slewmaxspeeds.TelAltSpd,
				slewmaxspeeds.TelAzSpd,
				slewmaxspeeds.RotSpd,
				slewHist.slewID)

        for act in listslewactivities:
            self.lsstDB.addSlewActivities(act.activity, act.actDelay, act.inCriticalPath, slewHist.slewID)

        # Take observation. Delete winning Field/Filters from masterTargets.
        # Could reset rank to 0.0 as done previously.  Let's see if this works.
        # for proposal in self.interProposalRank.keys ():

        for proposal in self.proposals_list:
            if proposal.IsActive(date, self.nightCnt):
                obs = proposal.closeObservation (winner, obsHist.obsHistID, self.twilightProfile)
                #print "ObsScheduler.closeObs(): In proposal?: fieldID: %d date: %d propID: %d" % (self.winner.fieldID, t, proposal.propID)

                #                if obs != None:
                #                    fieldFilter = "%d:%s" % (obs.fieldID, obs.filter)
                    #print "ObsScheduler.closeObs(): FOUND: fieldID: %d date: %d propID: %d" % (obs.fieldID, t, proposal.propID)

                    # serendipitious obs will not be in proposal top targets
                #                    if fieldFilter in self.masterTargets[obs.propID]:
                #                        del self.masterTargets[obs.propID][fieldFilter]
        self.targetRank[winner.fieldID][winner.filter] = 0.0

        return
   
    
    def addProposal (self, proposal, rank=0):
        """
        Add the Proposal instance proposal (and its rank) to 
        self.interProposalRank.
        
        Input
        proposal:   a Proposal instance
        rank:       a number indicating the importance of proposal (on
                    an absolute scale). rank defaults to 0 (i.e. 
                    proposal ignored).
        
        Return
        None
        
        Raise
        ParamTypeError  if proposal is not a Proposal object
        """
        if (not isinstance (proposal, Proposal)):
            raise (ParamTypeError, 'proposal needs to be an instance \
                                    of the Proposal class')
        
        # Add proposal to self.interProposalRank, replacing any previous entry
#        self.interProposalRank[proposal] = rank
	self.proposals_list.append(proposal)
        #  B U G    B U G    B U G    B U G   B U G   B U G
        if proposal.exposureTime > self.maxExposureTime:
            self.maxExposureTime = proposal.exposureTime
        #  B U G    B U G    B U G    B U G   B U G   B U G
        return
    
    
    def removeProposal (self, proposal):
        """
        Remove the Proposal instance proposal from self.interProposalRank. This
        method quits quitely if proposal is not active (i.e. not in
        self.interProposalRank).
        
        Input
        proposal:   a Proposal instance
        
        Return
        None
        
        Raise
        ParamTypeError  if proposal is not a Proposal object
        """
        if (not isinstance (proposal, Proposal)):
            raise (ParamTypeError, 'proposal needs to be an instance \
                                    of the Proposal class')
        
        try:
#            del (self.interProposalRank[proposal])
	    self.proposals_list.remove(proposal)
        except:
            pass
        return
    
    
    def setProposalPriority (self, proposal, rank=0):
        """
        Change the ranking or the Proposal instance proposal. This 
        method is simply an alias for self.addProposal ().
        
        Input
        proposal:   a Proposal instance
        rank:       a number indicating the importance of proposal (on
                    an absolute scale). rank defaults to 0 (i.e. 
                    proposal ignored).
        
        Return
        None
        
        Raise
        ParamTypeError  if proposal is not a Proposal object
        """
        self.addProposal (proposal, rank)
        return

    def closeProposals(self, time):
        
        #	for proposal in self.interProposalRank.keys ():
        for proposal in self.proposals_list:
            proposal.closeProposal(time)
        return


