#!/usr/bin/env python

from TransientProp import *

class SuperNovaProp (TransientProp):
    """
    This class is here to describe a Super Nova Objects (SN) case scenario. 
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
                  logfile='./SuperNovaProp.log',
                  verbose=0,
                  superNovaConf=DefaultSNConfigFile):
        """
        Standard initializer.
        
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
                    Defaults "./SuperNovaProp.log".
        verbose:    Log verbosity: -1=none, 0=minimal, 1=wordy, >1=verbose
        superNovaConf: Super Nova Configuration file

        """
        super (SuperNovaProp, self).__init__ (lsstDB=lsstDB,
					      propConf=superNovaConf,
                                              propName='SN',
					      propFullName='SuperNova',
                                              sky=sky, 
                                              weather=weather,
                                              sessionID=sessionID,
                                              filters=filters,
                                              targetList=targetList,
                                              dbTableDict=dbTableDict,
                                              log=log,
                                              logfile=logfile,
                                              verbose=verbose,
					      transientConf=superNovaConf)
        
        config_dict, pairs = readConfFile(superNovaConf)

        self.lsstDB = lsstDB
	self.nextNight = 0
        self.maxSeeing      = eval(str(config_dict['MaxSeeing']))

        self.maxAirmass     = eval(str(config_dict['MaxAirmass']))
        self.ha_maxairmass = sky.getHAforAirmass(self.maxAirmass)

        self.expTime        = eval(str(config_dict['ExposureTime']))
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
	if not isinstance(self.seqFilters, list):
            self.seqFilters = [self.seqFilters]

	#print "SN FILTERS = "+str(self.seqFilters)

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

        # original SN read config fields
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

        try:
            self.twilightBoundary = config_dict['TwilightBoundary']
        except: 
            self.twilightBoundary = -18.0

        # Save the SN configuration parameters to the DB
        for line in pairs:
            storeParam (self.lsstDB, self.sessionID, self.propID, 'sn', line['index'],
                        line['key'], line['val'])

        self.dbField = dbTableDict['field']
        # If user-defined regions have been defined, build new FieldDB
        if not (self.userRegion[0] == None) :
            self.dbField = self.buildUserRegionDB(self.userRegion,self.dbField)
                                                                                
        print "SuperNovaProp:init: dbField: %s" % (self.dbField)


	Nfilters          = len(self.filters.filterNamesSorted)
	self.maxIXfilter  = float(Nfilters-1)
	self.halfIXfilter = Nfilters/2

        # Setup FieldFilter visit history for later ObsHistory DB  ingest
        self.fieldVisits = {}
        self.lastFieldVisit = {}
        self.lastFieldFilterVisit = {}
        self.lastTarget = (0.0,0.0)

	self.TransientType = 'SuperNova'

        return

    def CheckObservingCycle(self, date):

	return True

    def IsObservingCycle(self):
                                                                                                                                                 
        return True
                                                                                                                                                 
    def RankFilters(self, fieldID, filterSeeingList, allowedFilterList):

	rankForFilters = {}

        lastfilters = self.sequences[fieldID].GetLastFilters()
        for filter in allowedFilterList:

            if (filterSeeingList[filter] > self.maxSeeing):
                if self.log and self.verbose>1:
                    self.log.info ('SuperNovaProp: RankFilters() propID=%d field %i bad seeing:%f' %(self.propID,fieldID,filterSeeingList[filter]))
                continue
            # Check if the proposed filter is in the list
            # of allowed filters for the SuperNova configuration.
            if not filter in self.seqFilters:
                continue

            if lastfilters==[]:
                rankFilter = 0.0
            elif filter in lastfilters:
                rankFilter = (lastfilters.index(filter)-self.halfIXfilter)/self.maxIXfilter
            else:
                rankFilter = 1.0

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
           self.log.info('SuperNova: closeObservation() for propID=%d' %(self.propID))

        obs = super (SuperNovaProp, self).closeObservation(observation,
                                                     twilightProfile)

        return obs

    def updateTargetList (self, dateProfile, obsProfile, sky, fov):
       """
       Update the list of potentially visible fields given a LST and
       a latitude. The range in coordinates of the selected fields is
       RA:  [LST-60; LST+60] (degrees)
       Dec: [lat-60; lat+60] (degrees)

       This version uses Sun.py and computes RA limits at the
       astronomical twilight.

       Input:
       dateProfile  ...
       obsProfile   ...
       sky         AstronomicalSky instance
       fov         Field of view of the telescope

       Return
       fields      A dictionary of the form {fieldID: (ra, dec)}
       """
       ## Benchmark memory use - start
       #m0 = memory()
       #r0 = resident()
       #s0 = stacksize()
       ##self.log.info("SN: updateTargetList entry: mem: %d resMem: %d stack: %d" % (m0, r0, s0))

       dbFov = 'fieldFov'
       dbRA = 'fieldRA'
       dbDec = 'fieldDec'
       dbID = 'fieldID'


       (date,mjd,lst_RAD) = dateProfile
       (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = obsProfile

       # MJD -> calendar date
       (yy, mm, dd) = mjd2gre (mjd)[:3]

       s = Sun.Sun ()
       (sunRise, sunSet) = s.__sunriset__ (yy, mm, dd, lon_RAD*RAD2DEG, lat_RAD*RAD2DEG,self.twilightBoundary,0)            

       #RAA Following overkill for simulation
       #if (date >= sunSet):            # Beginning of the night
       #    (sunRise, dummy) = s.nauticalTwilight (yy, mm, dd+1, lon_DEG, lat_DEG)
       #else:                           # End of the night
       #    (dummy, sunSet) = s.nauticalTwilight (yy, mm, dd-1, lon_DEG, lat_DEG)
       #print "Sunset:%f Sunrise:%f" % (sunSet,sunRise)

       # Compute RA min (at twilight)
       date_MJD = int (mjd) + (sunSet / 24.)
       #WL/NEA: raMin = ((slalib.sla_gmst(date_MJD) * RAD2DEG) + lon_DEG) - 60
       #SN:     raMin = lst + self.newFieldsLimitEast_afterLSTatSunset
       raMin = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG)  - self.deltaLST
       raMinNewSeq = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG)  + self.newFieldsLimitEast_afterLSTatSunset
                                                                                
       # Compute RA max (at twilight)
       date_MJD = int (mjd) + (sunRise / 24.)
       #WL/NEA: raMax = ((slalib.sla_gmst(date_MJD) * RAD2DEG) + lon_DEG) + 60
       #NS:     raMax = lst - self.newFieldsLimitWest_beforeLSTatSunrise
       raMax = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG) + self.deltaLST
       raMaxNewSeq = ((slalib.sla_gmst(date_MJD) + lon_RAD) * RAD2DEG) - self.newFieldsLimitWest_beforeLSTatSunrise

       # Make sure that both raMin and raMax are in the [0; 360] range
       raMin = normalize (angle=raMin, min=0., max=360, degrees=True)
       raMax = normalize (angle=raMax, min=0., max=360, degrees=True)
       raMinNewSeq = normalize (angle=raMinNewSeq, min=0., max=360, degrees=True)
       raMaxNewSeq = normalize (angle=raMaxNewSeq, min=0., max=360, degrees=True)

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

       DecLimit = math.acos(1./float(self.maxAirmass))  * RAD2DEG
       sql += '%s BETWEEN %f AND %f  and %f < %s < %f' % (dbDec,
                                        (lat_RAD*RAD2DEG)-DecLimit,
                                        (lat_RAD*RAD2DEG)+DecLimit,
                                        -abs(self.maxReach),dbDec,abs(self.maxReach))
       sqlNewSeq += '%s BETWEEN %f AND %f  and %f < %s < %f' % (dbDec,
                                        (lat_RAD*RAD2DEG)-DecLimit,
                                        (lat_RAD*RAD2DEG)+DecLimit,
                                        -abs(self.maxReach),dbDec,abs(self.maxReach))

       # Send the query to the DB
       (n, res) = self.lsstDB.executeSQL (sql)

       # Build the output dictionary
       for (ra, dec, fieldID) in res:
           fields[fieldID] = (ra, dec)

       self.targets = fields.copy()

       self.computeTargetsHAatTwilight(lst_RAD)

       #print (sql)
       print ('*** Found %d SN fields for propID=%d***' % (len (res),self.propID))

       (n, res) = self.lsstDB.executeSQL (sqlNewSeq)
       fields = {}
       for (ra, dec, fieldID) in res:
           fields[fieldID] = (ra, dec)
       self.targetsNewSeq = fields.copy()
       print ('*** Found %d SN fields for propID=%d for new sequences ***' % (len (res),self.propID))

       ## Benchmark memory use - exit
       #m1 = memory()
       #r1 = resident()
       #s1 = stacksize()
       ##self.log.info("WL: updateTargetList:(entry:exit) mem: %d:%d resMem: %d:%d stack: %d:%d" % (m0,m1, r0,r1, s0,s1))
       #print("SN: updateTargetList:(entry:exit) mem: %d:%d resMem: %d:%d stack: %d:%d" % (m0,m1, r0,r1, s0,s1))

       return (self.targets)


