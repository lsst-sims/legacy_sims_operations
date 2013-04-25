from utilities import *
from LSSTObject import *
from Filters import *
from Observation import *
from ObsHistory import *
from Distribution import *
from Sequence     import *
from Proposal import *
import math


class WeakLensingProp (Proposal):
    """
    This class is here to describe a simple case scenario: a Proposal 
    type of object that only cares about seeing values and slew time.
    It does not care about particular fields, filters or anythin else,
    just seeing and slew time.
    """
    def __init__ (self, 
                  lsstDB,
		  schedulingData,
		  sky, 
                  weather,
                  sessionID,
                  filters,
                  fov,
                  weakLensConf=DefaultWLConfigFile,
                  targetList=None, 
                  dbTableDict=None,
                  log=True,
                  logfile='./Proposal.log',
                  verbose=0):
        """
        Standard initializer.
        
	lsstDB:     LSST DB Access object        
	sky:        an AsronomycalSky instance.
        weather:    a Weather instance.
        sessionID:  An integer identifying this particular run.
        filters:    ...
        fov:        FoV of the instrument.
        weakLensConf: Weak Lensing Proposal Configuration file
        exposureTime:    Exposure time in seconds.
        maxSeeing:  Maximum acceptable seeing.
        targetList: the name (with path) of the TEXT file containing
                    the field list. It is assumed that the target list
                    is a three column list of RA, Dec and field ID.
                    RA and Dec are assumed to be in decimal degrees; 
                    filed ID is assumed to be an integer uniquely
                    identifying any give field.
        dbTableDict:
        log         ...
        logfile     ...
        verbose:    integer specifying the verbosity level (defaults 
                    to 0 meaning quite).
        """

        super (WeakLensingProp, self).__init__ (lsstDB=lsstDB,
						propConf=weakLensConf,
                                                propName='WL',
						propFullName='WeakLensing',
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
	if (self.log and self.verbose > 1):
           self.log.info('WeakLensingProp: init() propID=%d' %(self.propID))
        
	self.schedulingData = schedulingData
        self.weakLensConf = weakLensConf
        self.GoalVisitsFieldFilter = {}
        self.sky = sky

        config, pairs = readConfFile (weakLensConf)
        
        self.nextNight = 0
        try:
            self.maxAirmass = config['MaxAirmass']
        except:
            pass

        try:
            self.exposureTime = config['ExposureTime']
        except:
            pass

        try:
            self.goalNVisits = config['NVisits']
        except:
            self.goalNVisits = 30.
        try:
            filterVisits = config["Filter_Visits"]
        except:
            filterVisits = []
            for filter in self.FilterNames:
                filterVisits.append(self.goalNVisits)
        # if singleton, make into a list of one
        if not isinstance (filterVisits, list):
            filterVisits = [filterVisits]

        for ix in range(len(self.FilterNames)):
            self.GoalVisitsFieldFilter[self.FilterNames[ix]] = filterVisits[ix]
#        print 'GoalVisitsFieldFilter for propID=%d %s = %s' % (self.propID, self.propFullName, str(self.GoalVisitsFieldFilter))
        
        try:
            self.maxNeedAfterOverflow = config['MaxNeedAfterOverflow']
        except:
            self.maxNeedAfterOverflow = 0.5

        try:
            self.ProgressToStartBoost = config['ProgressToStartBoost']
        except:
            self.ProgressToStartBoost = 1.0
                                                                                                           
        try:
            self.MaxBoostToComplete   = config['MaxBoostToComplete']
        except:
            self.MaxBoostToComplete   = 0.0
                                                                                                           
        try:
            self.scale = config['RankScale']
        except:
            self.scale = 0.1

        try:
            self.taperB = config['taperB']
        except:
            self.taperB = 180.
        try:
            self.taperL = config['taperL']
        except:
            self.taperL = 5.
        try:
            self.peakL = config['peakL']
        except:
            self.peakL = 25.
        try:
            self.deltaLST = config['deltaLST']
        except:
            self.deltaLST = 60.
        try:
            self.maxReach = config['maxReach']
        except:
            self.maxReach = 80.
        try:
            self.minTransparency = config['minTransparency']
        except:
            self.minTransparency = 9.

        if ( config.has_key ('userRegion')) :
            self.userRegion =  config["userRegion"]
        else :
            self.userRegion =  None
            
        if (not isinstance(self.userRegion,list)):
            # turn it into a list with one entry
            save = self.userRegion
            self.userRegion = []
            self.userRegion.append(save)

        try:
            self.maxProximityBonus = config['MaxProximityBonus']
        except:
            self.maxProximityBonus = 1.0

        # store config to DB
        for line in pairs:
            storeParam (self.lsstDB, self.sessionID, self.propID, 'weakLensing',
                        line['index'], line['key'], line['val'])

        self.dbField = dbTableDict['field']

        if (self.goalNVisits <= 0):
            self.goalNVisits = 1.

        # Setup FieldFilter visit history for later ObsHistory DB  ingest
        self.fieldVisits = {}
        self.lastFieldVisit = {}
        self.lastFieldFilterVisit = {}
        self.lastTarget = (0.0,0.0)

        
        # Setup the relative importance of each filter. For 
        # convenience we use a dictionary of the form {filter: N}
        # where N is the desired fraction of the total number of 
        # observations for that particular filter. If all the filters
        # were equally desirable, then N would be always equal to 
        # 1. / total_number_of_filters.
        n = 0.

        # filterNames now is assigned in the parent class using the
        # filters' configuration file.
        # If this proposal wants to observe in a subset of this filter
        # list, this subset should be specified in the proposal's
        # configuration file.

        self.visits={}
        self.GoalVisitsField=0

        for filter in (self.FilterNames):
	    if filter in self.GoalVisitsFieldFilter.keys():
                self.visits[filter]={}
                self.GoalVisitsField += self.GoalVisitsFieldFilter[filter]
#        print('GoalVisitsField = %i' % (self.GoalVisitsField))

        # DataBase specifics
        self.dbTableDict = dbTableDict

        self.dbField = self.dbTableDict['field']
        # If user-defined regions have been defined, build new FieldDB
        if not (self.userRegion[0] == None) :
            self.dbField = self.buildUserRegionDB(self.userRegion,self.dbField)

        print "WeakLensingProp:init: dbField: %s" % (self.dbField)
        
        self.winners = []
                
        self.obsHistory = None
        self.sessionID = sessionID
        
        # self.targets is a convenience dictionary. Its keys are 
        # fieldIDs, its values are the corresponding RA and Dec.
        self.targets = {}
        
        # Create the ObsHistory instance and cleanup any leftover
        self.obsHistory = ObsHistory (lsstDB=self.lsstDB,
				      dbTableDict=self.dbTableDict,
                                      log=self.log,
                                      logfile=self.logfile,
                                      verbose=self.verbose)

        self.obsHistory.cleanupProposal (self.propID, self.sessionID)

        self.ha_maxairmass = sky.getHAforAirmass(self.maxAirmass)
                
        return
    
    def start (self):
        """
        Activate the WeakLensingProp instance.
        """
        if (self.log and self.verbose > 1):
           self.log.info('WeakLensingProp: start() propID=%d' %(self.propID))

        
        # PAUSE
#        yield hold, self
        return
    
    def startNight(self,dateProfile,moonProfile,startNewLunation,randomizeSequencesSelection, nRun, mountedFiltersList):

        super (WeakLensingProp, self).startNight (dateProfile,moonProfile,startNewLunation, mountedFiltersList)

    def GetProgressPerFilter(self):

        coaddedFilterProgress = {}
	allfields = []
	filters = self.visits.keys()
        for filter in filters:
            coaddedFilterProgress[filter] = 0
	    fields = self.visits[filter].keys()
	    allfields += fields
	    for fieldID in fields:
		coaddedFilterProgress[filter] += self.visits[filter][fieldID]

        progressFilter = {}
	for filter in filters:
	    if self.GoalVisitsFieldFilter[filter] > 0:
		if len(allfields) > 0:
		    progressFilter[filter] = float(coaddedFilterProgress[filter])/len(allfields)/self.GoalVisitsFieldFilter[filter]
		else:
		    # no fileds observed for this filter
		    progressFilter[filter] = 0.0
	    else:
		# no observations required for this filter
		progress[filter] = 1.0

        if ( self.log ):
            for filter in progressFilter.keys():
                self.log.info('%sProp: GetProgressPerFilter() propID=%d Filter progress: %10s = %.3f%%' % (self.propFullName, self.propID, filter, 100*progressFilter[filter]))

	return progressFilter

    def suggestObs (self, 
                    dateProfile, 
#                    moonProfile,
                    n=1,
                    skyfields=None, 
                    proximity=None,
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
                                moonAltitude]
                        values (dictionary-keyed to fieldID)
        
        Return
        An array of the (at most) n highest ranking observations, 
        ordered from the highest ranking obs to the lowest.
        """
        if (self.log and self.verbose > 1):
           self.log.info('WeakLensingProp: suggestObs() propID=%d' %(self.propID))

        # If in an exclusive block, no new observation candidates. Return null.
#        if (exclusiveObservation != None):
            # adjust counter for one obs
#            self.reuseRanking -= 1
#            return []
#        else:
            # If not time to rerank fields, return no suggestions.
#            if self.reuseRanking > 1:
#                self.reuseRanking -= 1
#                return []

        if (exclusiveObservation != None):
            if exclusiveObservation.fieldID in self.targets.keys():
                listOfFieldsToEvaluate = [exclusiveObservation.fieldID]
            else:
                listOfFieldsToEvaluate = []
            numberOfObsToPropose = 0
        else:
            listOfFieldsToEvaluate = sorted(self.targets.iterkeys())
            numberOfObsToPropose = n

#        listOfFieldsToEvaluate = self.targets.keys()
#	listOfFieldsToEvaluate = sorted(self.targets.iterkeys())
#        numberOfObsToPropose = n

        # Create a priority queue to choose the best n obs
        self.clearSuggestList()
        
        # Copy the input vars
        inFieldID = skyfields
        inproximity = proximity
#        intargetProfiles = targetProfiles
        (date,mjd,lst_RAD) = dateProfile
        (moonRA_RAD,moonDec_RAD,moonPhase_PERCENT) = self.schedulingData.moonProfile[sdnight]

        
        # Get the number of times we observed in each field
        # The idea here is to make sure that, over one year, we end up
        # with a balanced set of observations. For the Weak Lensing
        # proposal, we want to observe each field-filter combo approx.
        # GOAL times/year. This means that we do not want to observe 
        # each field-filter more than 6 times per lunation or once per
        # night.
        # numVisits is a dict of the form {filter: {fieldID: n}}
#        visits = self.obsHistory.getNVisitsPerFilterField (self.propID,
#                                    self.sessionID, fieldID=None)
        

        #..................   T o   D o  .................................
        # Compute the normalization constant for SignalToNoise (SNR) ranking
        #..................   T o   D o  .................................

	fields_received   = len(listOfFieldsToEvaluate)
	fields_invisible  = 0
	fields_moon       = 0
	ffilter_allowed   = 0
	ffilter_badseeing = 0
	ffilter_proposed  = 0

        # Adjust the partial rank so that we end with 
        # self.sumFieldFilterGoal for all field/filter combos
        # Adjust the scaling
	needTonight = self.GoalVisitsTonight - self.VisitsTonight
	if needTonight > 0:
	    GlobalNeedFactor = float(needTonight) / self.GoalVisitsTonight
	else:
	    GlobalNeedFactor = (self.maxNeedAfterOverflow/(self.VisitsTonight-self.GoalVisitsTonight+1)) / self.GoalVisitsTonight

        for fieldID in listOfFieldsToEvaluate:
            i = inFieldID.index(fieldID)
            ra = self.targets[fieldID][0]
            dec = self.targets[fieldID][1]

            if (fieldID==self.last_observed_fieldID) and (self.last_observed_wasForThisProposal) and (not self.AcceptConsecutiveObs):
                continue
                
            #-----------------------------------------------------------
            #       Field cuts
            #-----------------------------------------------------------
            # First, discard all the targets which are not visible right now.
            airmass = self.schedulingData.airmass[fieldID][sdtime]
            if airmass > self.maxAirmass :
		fields_invisible += 1
                if self.log and self.verbose>1 :
                    self.log.info('TOSS: propID=%d field=%d  WeakLensingProp: suggestObs(): too low:%f' % (self.propID,fieldID,airmass))
                #DBGprint "Toss: Field: %d ra:%f dec:%f am:%f > 5 " % (fieldID,ra,dec,airmass) 
                continue

	    distance2moon = self.schedulingData.dist2moon[fieldID][sdtime]
            if distance2moon < minDistance2Moon:
                fields_moon += 1
		# remove the target for the rest of the night if it is too close to the moon
		del self.targets[fieldID]
                continue
	
	    nVisits  = {}
	    progress = {}
	    progress_avg = 0.0
	    for filter in self.FilterNames:
                try:
                    nVisits[filter] = self.visits[filter][fieldID]
                except:
                    nVisits[filter] = 0.
		progress[filter] = nVisits[filter] / self.GoalVisitsFieldFilter[filter]
		progress_avg += min(progress[filter],1.0)/len(self.FilterNames)

	    FieldNeedFactor = 1.0 - progress_avg
	    if self.ProgressToStartBoost < progress_avg < 1.0:
		FieldNeedFactor += self.MaxBoostToComplete*(progress_avg-self.ProgressToStartBoost)/(1.0-self.ProgressToStartBoost)

            skyBrightness = self.schedulingData.brightness[fieldID][sdtime]
            allowedFilterList = self.allowedFiltersForBrightness(skyBrightness)
	    #self.log.info('%s brightness=%f allowedFilterList=%s' % (self.weakLensConf, skyBrightness, str(allowedFilterList)))
            filterSeeingList = self.filters.computeFilterSeeing(seeing,airmass)
            #print ".....field:%d ra:%f dec:%f am:%f phs:%f brite:%f" % (fieldID, ra,dec, airmass, moonPhase, intargetProfiles[i][1]) , filterSeeingList
            
            for filter in allowedFilterList:
		ffilter_allowed += 1
                #-----------------------------------------------------------
                #       Field/filter cuts
                #-----------------------------------------------------------
                if filterSeeingList[filter]  > self.FilterMaxSeeing[filter] :
		    ffilter_badseeing += 1
                    #DBGprint "TOSS: fld:%d fltr:%s ra:%f dec%f airms:%f phs:%f  airAdjSee:%f > maxSee:%f" % (fieldID,filter,ra,dec,airmass,moonPhase,filterSeeingList[filter],self.FilterMaxSeeing[filter])
                    if self.log and self.verbose>1 :
                        self.log.info('TOSS: propID=%d field=%d  filter=%s  WeakLensingProp: suggestObs(): bad seeing:%f' % (self.propID,fieldID,filter,filterSeeingList[filter]))
                    continue

                #-----------------------------------------------------------
                #           Ranking
                #-----------------------------------------------------------
                # Assign the priority to the fields. The priority/rank is
                # reflecting the fact that we want to end up observing in
                # each filter with a given frequency (see above).
                    
                # The partial rank for this field/filter varies between 
                # 0 and 1. It is 0 if we already have self.filterVisits[filter] 
                # visits. It is 1 if we have no visit...
		if GlobalNeedFactor > 0.0:
		    if FieldNeedFactor > 0.0:
			if progress[filter] < 1.0:
			    FilterNeedFactor = 1.0 - progress[filter]
			    rank = self.scale * 0.5*(FieldNeedFactor + FilterNeedFactor) / GlobalNeedFactor
			else:
			    rank = 0.0
		    else:
			FilterNeedFactor = (self.maxNeedAfterOverflow/(nVisits[filter]-self.GoalVisitsFieldFilter[filter]+1)) / self.GoalVisitsFieldFilter[filter]
		        rank = self.scale * FilterNeedFactor / GlobalNeedFactor
		else:
		    rank = 0.0

 
                if (rank >0.0):
		    ffilter_proposed += 1
                    #print "WeakLensing", intargetProfiles[i]
                    # Edit corresponding Observation instance in self.obsPool
                    recordFieldFilter = self.obsPool[fieldID][filter]
                    #recordFieldFilter.sessionID = sessionID
                    #recordFieldFilter.propID = propID
                    #recordFieldFilter.fieldID = fieldID
                    #recordFieldFilter.filter = filter
                    #recordFieldFilter.seqn = seqn
                    recordFieldFilter.date = date
                    recordFieldFilter.mjd = mjd
		    recordFieldFilter.night = sdnight
                    #recordFieldFilter.exposureTime = exposureTime
                    #recordFieldFilter.slewTime = slewTime
                    #recordFieldFilter.rotatorSkyPos = 0.0
                    #recordFieldFilter.rotatorTelPos = 0.0
                    recordFieldFilter.propRank = rank
                    #recordFieldFilter.finRank = finRank
#                    recordFieldFilter.maxSeeing = self.FilterMaxSeeing[filter]
                    recordFieldFilter.rawSeeing = rawSeeing
                    recordFieldFilter.seeing = filterSeeingList[filter]
                    recordFieldFilter.transparency = transparency
#                    recordFieldFilter.cloudSeeing = intargetProfiles[i][4]
                    recordFieldFilter.airmass = airmass
                    recordFieldFilter.skyBrightness = skyBrightness
		    recordFieldFilter.filterSkyBright = 0.0
                    #recordFieldFilter.ra = ra
                    #recordFieldFilter.dec = dec
                    recordFieldFilter.lst = lst_RAD
                    recordFieldFilter.altitude = self.schedulingData.alt[fieldID][sdtime]
                    recordFieldFilter.azimuth  = self.schedulingData.az[fieldID][sdtime]
                    recordFieldFilter.parallactic = self.schedulingData.pa[fieldID][sdtime]
                    recordFieldFilter.distance2moon = distance2moon
                    recordFieldFilter.moonRA = moonRA_RAD
                    recordFieldFilter.moonDec = moonDec_RAD
#                    recordFieldFilter.moonAlt = intargetProfiles[i][8]
                    recordFieldFilter.moonPhase = moonPhase_PERCENT

                    self.addToSuggestList(recordFieldFilter, inproximity[i])
                #print "WLRANK: f:%d am:%f see:%f brt:%f phs:%f dt:%d flt:%s rnk:%f" % (fieldID, airmass,filterSeeingList[filter],intargetProfiles[i][1],moonPhase, date, filter, rank)

        if self.log and self.verbose>0:
	    self.log.info('%sProp: suggestObs() propID=%d : Fields received=%i invisible=%i moon=%i Field-Filters allowed=%i badseeing=%i proposed=%i' % (self.propFullName, self.propID, fields_received, fields_invisible, fields_moon, ffilter_allowed, ffilter_badseeing, ffilter_proposed))

        # Chose the n highest ranking observations
#        self.reuseRanking = self.reuseRankingCount
        return self.getSuggestList(numberOfObsToPropose)
    
    
    def closeObservation (self, observation, obsHistID, twilightProfile):

#        if (self.log and self.verbose > 1):
#           self.log.info('WeakLensingProp: closeObservation() propID=%d' %(self.propID))

        obs = super (WeakLensingProp, self).closeObservation(observation, obsHistID, twilightProfile)

        if obs != None:
            try:
                self.visits[obs.filter][obs.fieldID] += 1
            except:
                self.visits[obs.filter][obs.fieldID]  = 1
            self.VisitsTonight += 1
 
	    progress = self.visits[obs.filter][obs.fieldID]/self.GoalVisitsFieldFilter[obs.filter]

#            if (self.log and self.verbose>0):
#                t_secs = obs.date%60
#                t_mins = (obs.date%3600)/60
#                t_hour = (obs.date%86400)/3600
#                t_days = (obs.date)/86400

#                self.log.info('WeakLensingProp: closeObservation() propID=%d field=%d filter=%s propRank=%.4f finRank=%.4f t=%dd%02dh%02dm%02ds progress=%d%%' % (self.propID, obs.fieldID, obs.filter, obs.propRank, obs.finRank, t_days, t_hour, t_mins, t_secs, int(100*progress)))

            #print ('%i %i' % (self.visits[obs.filter][obs.fieldID], self.VisitsTonight))
        return obs
        

    def updateTargetList (self, dateProfile, obsProfile, sky, fov ):
        """
        Update the list of potentially visible fields given a LST and
        a latitude. The range in coordinates of the selected fields is
        RA:  [LST-60; LST+60] (degrees)
        Dec: [lat-60; lat+60] (degrees)

        This version uses Sun.py and computes RA limits at the
        nautical twilight.

        Input:
        dateProfile ....
        obsProfile  ....
        sky         AstronomicalSky instance
        fov         Field of view of the telescope

        Return
        fields      A dictionary of the form {fieldID: (ra, dec)}
        """
        ## Benchmark memory use - start
        #m0 = memory()
        #r0 = resident()
        #s0 = stacksize()
        ##self.log.info("WL: updateTargetList entry: mem: %d resMem: %d stack: %d" % (m0, r0, s0))

        if ( self.log):
            self.log.info ('Proposal:updateTargetList propID=%d' %(self.propID))
        dbFov = 'fieldFov'
        dbRA = 'fieldRA'
        dbDec = 'fieldDec'
        #dbL = 'fieldGL'
        #dbB = 'fieldGB'
        dbID = 'fieldID'
         
        (date,mjd,lst_RAD) = dateProfile
        (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = obsProfile

        # MJD -> calendar date
        (yy, mm, dd) = mjd2gre (mjd)[:3]

        # determine twilight times based on user param: TwilightBoundary
        s = Sun.Sun ()
        (sunRise, sunSet) = s.__sunriset__ (yy, mm, dd, lon_RAD*RAD2DEG, lat_RAD*RAD2DEG,self.twilightBoundary,0)
        #(sunRise, sunSet) = s.nauticalTwilight (yy, mm, dd, lon_RAD*RAD2DEG, lat_RAD*RAD2DEG)

        # RAA following overkill for simulation
        #if (date >= sunSet):            # Beginning of the night
        #    (sunRise, dummy) = s.nauticalTwilight (yy, mm, dd+1, lon_DEG, lat_DEG)
        #else:                           # End of the night
        #    (dummy, sunSet) = s.nauticalTwilight (yy, mm, dd-1, lon_DEG, lat_DEG)

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

        sql = 'SELECT %s, %s, %s from %s ' % (dbRA,
                                              dbDec,
                                              dbID,
                                              self.dbField)

        sql += 'WHERE %s BETWEEN %f AND %f AND ' % (dbFov,
                                                    fovEpsilon1,
                                                    fovEpsilon2)

        # subtract galactic exclusion zone
        taperB = self.taperB
        taperL = self.taperL
        peakL = self.peakL
        band = peakL - taperL
        if ( (taperB != 0.) & (taperL != 0.) ) :
           sql += '( (fieldGL < 180. AND abs(fieldGB) > (%f - (%f * abs(fieldGL)) / %f) ) OR ' % (peakL,
                    band,
                    taperB)
           sql += '(fieldGL > 180. AND abs(fieldGB) > (%f - (%f * abs(fieldGL-360.)) / %f))) AND ' % (peakL,
                    band,
                    taperB)
        # subtract un-viewable sky
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

        DecLimit = math.acos(1./float(self.maxAirmass)) * RAD2DEG
        sql += '%s BETWEEN %f AND %f  and %f < %s < %f order by FieldRA,FieldDec' % (dbDec,
                                         (lat_RAD*RAD2DEG)-DecLimit,
                                         (lat_RAD*RAD2DEG)+DecLimit,
                                         -abs(self.maxReach),dbDec,abs(self.maxReach))

        # Send the query to the DB
        (n, res) = self.lsstDB.executeSQL (sql)

        # Build the output dictionary
        for (ra, dec, fieldID) in res:
            fields[fieldID] = (ra, dec)

        self.targets = fields

        self.computeTargetsHAatTwilight(lst_RAD)

        self.NumberOfFieldsTonight = len(self.targets)
        #print('NumberOfFieldsTonight = %i' % (self.NumberOfFieldsTonight))
        self.GoalVisitsTonight = self.GoalVisitsField * self.NumberOfFieldsTonight
        #print('Goal Visits with Tonight targets = %i' % (self.GoalVisitsTonight))
        self.VisitsTonight = 0
        for filter in self.visits.keys():
            #print('visits in %s = %i' % (filter, len(self.visits[filter].keys())))
            for field in self.visits[filter].keys():
                if self.targets.has_key(field):
                    self.VisitsTonight += self.visits[filter][field]
                    #print field
        #print('Visits up to Tonight for propID=%d for current targets = %i' % (self.propID,self.VisitsTonight))
        print ('*** Found %d WL fields for propID=%d ***' % (len (res),self.propID))

        ## Benchmark memory use - exit
        #m1 = memory()
        #r1 = resident()
        #s1 = stacksize()
        ##self.log.info("WL: updateTargetList:(entry:exit) mem: %d:%d resMem: %d:%d stack: %d:%d" % (m0,m1, r0,r1, s0,s1))
        #print("WL: updateTargetList:(entry:exit) mem: %d:%d resMem: %d:%d stack: %d:%d" % (m0,m1, r0,r1, s0,s1))

	self.schedulingData.updateTargets(fields, self.propID, dateProfile)

        return (fields)

    def closeProposal(self, time):

        # delete OlapField user-defined region table
        if not (self.userRegion[0] == None):
            overlappingField = "OlapField_%d_%d" %(self.sessionID,self.propID)
            result = self.lsstDB.dropTable(overlappingField)

	return
