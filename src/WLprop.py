#!/usr/bin/env python

from TransSubSeqProp import *

class WLprop (TransSubSeqProp):
    """
    This class is here to describe a Super Nova Objects (SN) case scenario. 
    """
    def __init__ (self, 
                  lsstDB,
		  schedulingData,
		  sky, 
                  weather,
                  sessionID,
                  filters,
                  targetList=None, 
                  dbTableDict=None,
                  log=False,
                  logfile='./WLprop.log',
                  verbose=0,
                  WLpropConf=DefaultWLConfigFile):
        """
        Standard initializer.
        
	lsstDB:	    LSST DB access object        
	sky:        an AsronomycalSky instance.
        weather:    a Weather instance.
        sessionID:  An integer identifying this particular run.
        filters:    ....
        targetList: the name (with path) of the TEXT file containing
                    the field list. It is assumed that the target list
                    is a three column list of RA, Dec and field ID.
                    RA and Dec are assumed to be in decimal degrees; 
                    filed ID is assumed to be an integer uniquely
                    identifying any give field.
        dbTableDict:
        log         False if not set, else: log = logging.getLogger("...")
        logfile     Name (and path) of the desired log file.
                    Defaults "./SuperNovaSubSeqProp.log".
        verbose:    Log verbosity: -1=none, 0=minimal, 1=wordy, >1=verbose
        superNovaConf: Super Nova Configuration file

        """
        super (WLprop, self).__init__ (lsstDB=lsstDB,
					      propConf=WLpropConf,
                                              propName='WLTSS',
					      propFullName='WeakLensingTSS',
                                              sky=sky, 
                                              weather=weather,
                                              sessionID=sessionID,
                                              filters=filters,
                                              targetList=targetList,
                                              dbTableDict=dbTableDict,
                                              log=log,
                                              logfile=logfile,
                                              verbose=verbose,
					      transientConf=WLpropConf)
        
        config_dict, pairs = readConfFile(WLpropConf)

	self.lsstDB = lsstDB        
	self.schedulingData = schedulingData
	self.nextNight = 0
        self.maxSeeing = {}
        try:
            defaultMaxSeeing = eval(str(config_dict['MaxSeeing']))
        except:
            pass
        try:
            self.maxSeeing['r'] = config_dict['rMaxSeeing']
        except:
            self.maxSeeing['r'] = defaultMaxSeeing
        try:
            self.maxSeeing['g'] = config_dict['gMaxSeeing']
        except:
            self.maxSeeing['g'] = defaultMaxSeeing
        try:
            self.maxSeeing['y'] = config_dict['yMaxSeeing']
        except:
            self.maxSeeing['y'] = defaultMaxSeeing
        try:
            self.maxSeeing['i'] = config_dict['iMaxSeeing']
        except:
            self.maxSeeing['i'] = defaultMaxSeeing
        try:
            self.maxSeeing['z'] = config_dict['zMaxSeeing']
        except:
            self.maxSeeing['z'] = defaultMaxSeeing

        self.maxAirmass = eval(str(config_dict['MaxAirmass']))
        self.ha_maxairmass = sky.getHAforAirmass(self.maxAirmass)

        try:  
            self.masterSubSequence = eval(str(config_dict['MasterSubSequence']))
        except: 
            self.masterSubSequence = None 

        self.subSeqFilters     = (config_dict['SubSeqFilters'])
        if not isinstance(self.subSeqFilters, list):
            self.subSeqFilters = [self.subSeqFilters]

        try:
            self.subSeqName = (config_dict['SubSeqName'])
        except:
            self.subSeqName = self.subSeqFilters
        if not isinstance(self.subSeqName, list):
            self.subSeqName = [self.subSeqName]
        #print 'subsequences names = '+str(self.subSeqName[:])

        try:
            self.subSeqNested = (config_dict['SubSeqNested'])
        except:
           self.subSeqNested = []
           for s in self.subSeqName:
               self.subSeqNested.append(None)
        if not isinstance(self.subSeqNested, list):
            self.subSeqNested = [self.subSeqNested]

        try:
            self.subSeqExposures = (config_dict['SubSeqExposures'])
        except:
            self.subSeqExposures = []
            for i in self.subSeqFilters:
                self.subSeqExposures.append(1)
        if not isinstance(self.subSeqExposures, list):
            self.subSeqExposures = [self.subSeqExposures]

        self.subSeqEvents      = eval(str(config_dict['SubSeqEvents']))
        if not isinstance(self.subSeqEvents, list):
            self.subSeqEvents = [self.subSeqEvents]

        self.subSeqMaxMissed   = eval(str(config_dict['SubSeqMaxMissed']))
        if not isinstance(self.subSeqMaxMissed, list):
            self.subSeqMaxMissed = [self.subSeqMaxMissed]

        self.subSeqInterval    = eval(str(config_dict['SubSeqInterval']))
        if not isinstance(self.subSeqInterval, list):
            self.subSeqInterval = [self.subSeqInterval]

        self.subSeqWindowStart = eval(str(config_dict['SubSeqWindowStart']))
        if not isinstance(self.subSeqWindowStart, list):
            self.subSeqWindowStart = [self.subSeqWindowStart]

        self.subSeqWindowMax   = eval(str(config_dict['SubSeqWindowMax']))
        if not isinstance(self.subSeqWindowMax, list):
            self.subSeqWindowMax = [self.subSeqWindowMax]

        self.subSeqWindowEnd   = eval(str(config_dict['SubSeqWindowEnd']))
        if not isinstance(self.subSeqWindowEnd, list):
            self.subSeqWindowEnd = [self.subSeqWindowEnd]
        self.rankTimeMax    = eval(str(config_dict['RankTimeMax']))
        self.rankIdleSeq    = eval(str(config_dict['RankIdleSeq']))
        self.rankLossRiskMax= eval(str(config_dict['RankLossRiskMax']))

        self.log.info('proposal configfile=%s subsequences:' % (str(WLpropConf)))
        self.log.info('         SubSeqName=%s' % (str(self.subSeqName)))
        self.log.info('         SubSeqNested=%s' % (str(self.subSeqNested)))
        self.log.info('         SubSeqFilters=%s' % (str(self.subSeqFilters)))
        self.log.info('         SubSeqExposures=%s' % (str(self.subSeqExposures)))
        self.log.info('         SubSeqEvents=%s' % (str(self.subSeqEvents)))
        self.log.info('         SubSeqMaxMissed=%s' % (str(self.subSeqMaxMissed)))
        self.log.info('         SubSeqInterval=%s' % (str(self.subSeqInterval)))
        self.log.info('         SubSeqWindowStart=%s' % (str(self.subSeqWindowStart)))
        self.log.info('         SubSeqWindowMax=%s' % (str(self.subSeqWindowMax)))
        self.log.info('         SubSeqWindowEnd=%s' % (str(self.subSeqWindowEnd)))

        try:
            self.rankDaysLeftMax= eval(str(config_dict['RankDaysLeftMax']))
        except:
            self.rankDaysLeftMax= 0.0

        try:
            self.DaysLeftToStartBoost = eval(str(config_dict['DaysLeftToStartBoost']))
        except:
            self.DaysLeftToStartBoost = 0

        try:
            self.restartLostSequences = eval(str(config_dict['RestartLostSequences']))
        except:
            self.restartLostSequences = False

        try:
            self.restartCompleteSequences = eval(str(config_dict['RestartCompleteSequences']))
        except:
            self.restartCompleteSequences = False

        self.maxNumberActiveSequences = eval(str(config_dict['MaxNumberActiveSequences']))
        try:
            self.minNumberActiveSequences = eval(str(config_dict['MinNumberActiveSequences']))
        except:
            self.minNumberActiveSequences = self.maxNumberActiveSequences

        try:
            self.WLtype = eval(str(config_dict['WLtype']))
        except:
            self.WLtype = False
        try:
            self.overflowLevel = eval(str(config_dict['OverflowLevel']))
        except:
            self.overflowLevel = 0.0
        try:
            self.progressToStartBoost = eval(str(config_dict['ProgressToStartBoost']))
        except:
            self.progressToStartBoost = 1.0
        try:
            self.maxBoostToComplete   = eval(str(config_dict['MaxBoostToComplete']))
        except:
            self.maxBoostToComplete   = 0.0

        if self.WLtype == True and self.overflowLevel > 0.0:
            self.overflow = True
        else:
            self.overflow = False

        # original WLprop read config file
        try:
            self.newFieldsLimitEast_afterLSTatSunset = config_dict['newFieldsLimitEast_afterLSTatSunset']
        except:
            self.newFieldsLimitEast_afterLSTatSunset   = 0.0

        try:
            self.newFieldsLimitWest_beforeLSTatSunrise = config_dict['newFieldsLimitWest_beforeLSTatSunrise']
        except:
            self.newFieldsLimitWest_beforeLSTatSunrise = 0.0

        try:
            self.exposureTime = config_dict['ExposureTime']
        except:
            self.exposureTime = 30.

        try:
            self.deltaLST = config_dict['deltaLST']
        except:
            self.deltaLST = 60.

        try:
            self.minAbsRA = config_dict['minAbsRA']
        except:
            self.minAbsRA = 0.

        try:
            self.maxAbsRA = config_dict['maxAbsRA']
        except:
            self.maxAbsRA = 360.

        try:
            self.minTransparency = config_dict['minTransparency']
        except:
            self.minTransparency = 9.

        try:
            self.taperB = config_dict['taperB']
        except:
            self.taperB = 180.

        try:
            self.taperL = config_dict['taperL']
        except:
            self.taperL = 5.

        try:
            self.peakL = config_dict['peakL']
        except:
            self.peakL = 25.
        try:
            self.maxReach = config_dict['maxReach']
        except:
            self.maxReach = 80.

        if ( config_dict.has_key ('userRegion')) :
            self.userRegion =  config_dict["userRegion"]
        else :
            self.userRegion =  None
             
        if (not isinstance(self.userRegion,list)):
            # turn it into a list with one entry
            save = self.userRegion
            self.userRegion = []
            self.userRegion.append(save)

        try:
            self.maxProximityBonus = config_dict['MaxProximityBonus']
        except:
            self.maxProximityBonus = 1.0

        # store config to DB
        for line in pairs:
            storeParam (self.lsstDB, self.sessionID, self.propID, 'WLprop', line['index'],
                        line['key'], line['val'])

        self.dbField = dbTableDict['field']
        # If user-defined regions have been defined, build new FieldDB
        if not (self.userRegion[0] == None) :
            self.dbField = self.buildUserRegionDB(self.userRegion,self.dbField)
                                                                                
        # Setup FieldFilter visit history for later ObsHistory DB  ingest
        self.fieldVisits = {}
        self.lastFieldVisit = {}
        self.lastFieldFilterVisit = {}
        self.lastTarget = (0.0,0.0)


        return

    def CheckObservingCycle(self, date):

	return True

    def IsObservingCycle(self):
                                                                                                                                                 
        return True
                                                                                                                                                 
#    def RankFilters(self, fieldID, filterSeeingList, allowedFilterList):

#	rankForFilters = {}

#        for filter in allowedFilterList:

#            if (filterSeeingList[filter] > self.maxSeeing):
#                continue
            # Check if the proposed filter is in the list
            # of allowed filters for the SuperNova configuration.
#            if not filter in self.subSeqFilters:
#                continue

#	    rankForFilters[filter] = 1.0

#        return rankForFilters

    
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

        if ( self.log and self.verbose > 1 ):
           self.log.info('%sProp: closeObservation() for propID=%d' %(self.propFullName, self.propID))

        obs = super (WLprop, self).closeObservation(observation, obsHistID, twilightProfile)

        return obs

    def updateTargetList (self, dateProfile, obsProfile, sky, fov):
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
                                                                                                                            
        dbFov = 'fieldFov'
        dbRA = 'fieldRA'
        dbDec = 'fieldDec'
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
        #raMin = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG) - self.deltaLST
        raMin = ((pal.gmst(date_MJD) + lon_RAD) * RAD2DEG) - self.deltaLST
        #raMinNewSeq = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG)  + self.newFieldsLimitEast_afterLSTatSunset
        raMinNewSeq = ((pal.gmst(date_MJD) + lon_RAD) * RAD2DEG)  + self.newFieldsLimitEast_afterLSTatSunset
                                                                                                                            
        # Compute RA max (at twilight)
        date_MJD = int (mjd) + (sunRise / 24.)
        #raMax = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG) + self.deltaLST
        raMax = ((pal.gmst(date_MJD) + lon_RAD) * RAD2DEG) + self.deltaLST
        #raMaxNewSeq = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG) - self.newFieldsLimitWest_beforeLSTatSunrise
        raMaxNewSeq = ((pal.gmst(date_MJD) + lon_RAD) * RAD2DEG) - self.newFieldsLimitWest_beforeLSTatSunrise
                                                                                                                            
        # Make sure that both raMin and raMax are in the [0; 360] range
        raMin = normalize (angle=raMin, min=0., max=360, degrees=True)
        raMax = normalize (angle=raMax, min=0., max=360, degrees=True)
        raMinNewSeq = normalize (angle=raMinNewSeq, min=0., max=360, degrees=True)
        raMaxNewSeq = normalize (angle=raMaxNewSeq, min=0., max=360, degrees=True)
        raAbsMin = normalize (angle=self.minAbsRA, min=0., max=360, degrees=True)
        raAbsMax = normalize (angle=self.maxAbsRA, min=0., max=360, degrees=True)
                                                                                                                            
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
        # select reduced range for starting new sequences
        sqlNewSeq = sql
        if (raMaxNewSeq > raMinNewSeq):
            sqlNewSeq += '%s BETWEEN %f AND %f AND ' % (dbRA,
                                                  raMinNewSeq,
                                                  raMaxNewSeq)
        elif (raMaxNewSeq < raMinNewSeq):
            sqlNewSeq += '(%s BETWEEN %f AND 360.0 OR ' % (dbRA,
                                                     raMinNewSeq)
            sqlNewSeq += '%s BETWEEN 0.0 AND %f) AND ' % (dbRA,
                                                    raMaxNewSeq)
        else:
            sqlNewSeq += '%s BETWEEN 0.0 AND 360.0 AND ' % (dbRA)

	if (raAbsMax >= raAbsMax):
	    sql += '%s BETWEEN %f AND %f AND ' % (dbRA,
	    					raAbsMin,
	    					raAbsMax)
	    sqlNewSeq += '%s BETWEEN %f AND %f AND ' % (dbRA,
        	                                        raAbsMin,
                	                                raAbsMax)
	else:
            sql += '(%s BETWEEN %f AND 360.0 OR ' % (dbRA,
                                                     raAbsMin)
            sql += '%s BETWEEN 0.0 AND %f) AND ' % (dbRA,
                                                    raAbsMax)
            sqlNewSeq += '(%s BETWEEN %f AND 360.0 OR ' % (dbRA,
                                                     raAbsMin)
            sqlNewSeq += '%s BETWEEN 0.0 AND %f) AND ' % (dbRA,
                                                    raAbsMax)
                                                                                                                     
        sql += '%s BETWEEN %f AND %f order by FieldRA,FieldDec' % (dbDec,
                                          (lat_RAD*RAD2DEG)-abs(self.maxReach),
                                          (lat_RAD*RAD2DEG)+abs(self.maxReach))
        sqlNewSeq += '%s BETWEEN %f AND %f order by FieldRA,FieldDec' % (dbDec,
                                         (lat_RAD*RAD2DEG)-abs(self.maxReach),
                                         (lat_RAD*RAD2DEG)+abs(self.maxReach))
                                                                                                                             
        # Send the query to the DB
        (n, res) = self.lsstDB.executeSQL (sql)
                                                                                                                            
        # Build the output dictionary
        for (ra, dec, fieldID) in res:
            fields[fieldID] = (ra, dec)
                                                                                                                            
        self.targets = fields

        self.computeTargetsHAatTwilight(lst_RAD)

        #print (sql)
        print ('*** Found %d WLTSS fields for propID=%d***' % (len (res),self.propID))

        (n, res) = self.lsstDB.executeSQL (sqlNewSeq)
        fields = {}
        for (ra, dec, fieldID) in res:
            fields[fieldID] = (ra, dec)
        self.targetsNewSeq = fields.copy()
        print ('*** Found %d WLTSS fields for propID=%d for new sequences ***' % (len (res),self.propID))

        ## Benchmark memory use - exit
        #m1 = memory()
        #r1 = resident()
        #s1 = stacksize()
        ##self.log.info("WL: updateTargetList:(entry:exit) mem: %d:%d resMem: %d:%d stack: %d:%d" % (m0,m1, r0,r1, s0,s1))
        #print("WL: updateTargetList:(entry:exit) mem: %d:%d resMem: %d:%d stack: %d:%d" % (m0,m1, r0,r1, s0,s1))
                                                                                                                            
	self.schedulingData.updateTargets(self.targets, self.propID, dateProfile, self.maxAirmass, self.FilterMinBrig, self.FilterMaxBrig)

        return (self.targets)

