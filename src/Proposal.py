#!/usr/bin/env python

"""
Proposal

Inherits from: Simulation.Process : object

Class Description
The Proposal class generates Observation instances. An Observation is
the act of pointing the telescope to a given position and exposing
for a given time, under given conditions (seeing, S/N ratio etc.).

Each Proposal instance is given a list of position on the sky 
(targetList) and a description of an observing strategy (science goals
priorities, cadence rules, requirements of field visibility, filters, 
seeing, transparency etc.).

These rules are interpreted and relevant requirements are embedded 
into each created Observation object.

The main role of each Proposal instance is both to generate 
Observation objects and to assign them appropriate priorities 
(rankings) that are to be updated constantly, depending on the status
of the facility, weather, sky and on the observation history.

Each Proposal instance also keeps track of its observation history.

The Proposal class embodies the functionality of a Ranker: the Ranker 
provides the raw ranking capabilities, on a per field (i.e. position 
on the sky) and per proposal basis.

A Ranker object is initialized by defining its strategy for assigning
"bonus points" and  "cuts" (i.e. reasons to discard a filed) to any
given field/proposal combination. A pointer/identifier to the relevant
proposal observation strategy and history needs to be provided as
well.

Cuts and bonuses depend on internal and external data, such as the
time it would take to move the telescope to that particular field or
the current seeing value versus the required seeing limits for a given
filed/proposal combination. Needless to say, rankings depend strongly
on both the proposal cadence requirements (i.e. observation strategy)
and observation history.

Users define cuts and bonus strategies at start-up time. The way they
do it is irrelevant to Ranker. The only information that Ranker
receives is a cutID and a bonusID referring to pre-defined strategies
as well as a cadenceID pointing to the observation strategy of each
given proposal.

Bonus points are given in an (pre-defined) absolute scale. This allows
for comparisons between ranking of the same field (i.e. position on
the sky) corresponding to different proposals.

It is important to realize that Ranker assigns ranking and discards
fields on a per proposal basis. The MasterScheduler is the object that
will put all the rankings together and choose the next target.


Method Types
Constructor/Initializers
- __init__
- loadTargetList

Destructor
- __del__

Activate a Proposal instance
- start

Read Cuts/Bonuses config
- readConfigFile

Select Fileds
- applyCuts (internal use)
- applyBonuses (internal use)
- suggestObs

Handle Priorities
- closeObservation

Accessors
- getSeeing
- getFieldCoordinates
"""

from math import *
from utilities import *
from LSSTObject import *
from Filters import *
from Observation import *
from ObsHistory import *
from MissedHistory import *
from Distribution import *
from Sequence     import *

import heapq

#skyBrightKeys = [0, 18, 50, 80, 100]
#filterOffset = { }

# Corrections for moonPhase = 0 percent (new moon)
#filterOffset['u',0.] =  0.66
#filterOffset['g',0.] =  0.41
#filterOffset['r',0.] = -0.28
#filterOffset['i',0.] = -1.36
#filterOffset['z',0.] = -2.15

# Corrections for moonPhase = 18 percent
#filterOffset['u',18.] =  0.28
#filterOffset['g',18.] =  0.30
#filterOffset['r',18.] = -0.19
#filterOffset['i',18.] = -1.17
#filterOffset['z',18.] = -1.99

# Corrections for moonPhase = 50 percent
#filterOffset['u',50.] = -1.05
#filterOffset['g',50.] =  0.03
#filterOffset['r',50.] =  0.02
#filterOffset['i',50.] = -0.96
#filterOffset['z',50.] = -1.78

# Corrections for moonPhase = 80 percent
#filterOffset['u',80.] = -1.83
#filterOffset['g',80.] = -0.08
#filterOffset['r',80.] =  0.10
#filterOffset['i',80.] = -0.78
#filterOffset['z',80.] = -1.54

# Corrections for moonPhase = 100 percent (full moon)
#filterOffset['u',100.] = -2.50
#filterOffset['g',100.] = -0.35
#filterOffset['r',100.] =  0.31
#filterOffset['i',100.] = -0.47
#filterOffset['z',100.] = -1.16

#class Proposal (Simulation.Process):
class Proposal (object):
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
                  logfile='./Proposal.log', 
                  verbose=0):
        """
        Standard initializer.
        
	lsstDB	    LSST DB access object        
	propConf    file containing this instance's configuration data
        propName    specific proposal's name
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
                    Defaults "./Instrument.log".
        verbose:    Log verbosity: 0=minimal, 1=wordy, >1=very verbose
        """
#        Simulation.Process.__init__ (self)
        
	self.lsstDB = lsstDB        
	self.sessionID = sessionID
        self.dbTableDict = dbTableDict
        self.propConf = propConf
        self.propName = propName
        self.propFullName = propFullName
        
        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up Proposal logger"
            log = logging.getLogger("Proposal")
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.INFO)
                                                                                
        self.log=log
        self.logfile=logfile
        self.verbose = verbose

        self.missedHistory = MissedHistory (lsstDB=self.lsstDB,
					dbTableDict=self.dbTableDict,
                                        log=self.log,
                                        logfile=self.logfile,
                                        verbose=self.verbose)

        if ( self.log and self.verbose > 1 ):
           self.log.info('Proposal: init()')

        config_dict, pairs = readConfFile(propConf)
        
        try:
            self.relativeProposalPriority = config_dict['RelativeProposalPriority']
        except:
            self.relativeProposalPriority   = 1.0
        if (self.log and self.verbose ):
            self.log.info('%sProp: relative proposal priority = %f' % (self.propFullName, self.relativeProposalPriority))

        try:
            self.targetlist = self.loadTargetList (targetList)
        except:
            if (self.log and self.verbose ):
                self.log.info('Proposal: init: No or invalid target list.')
            self.targetlist = None

        try:
            self.AcceptSerendipity = eval(str(config_dict['AcceptSerendipity']))
        except:
            self.AcceptSerendipity = True
                                                                                                                                                  
        try:
            self.AcceptConsecutiveObs = eval(str(config_dict['AcceptConsecutiveObs']))
        except:
            self.AcceptConsecutiveObs = True

	self.maxSeeing = config_dict["MaxSeeing"] 
#        self.reuseRankingCount   = config_dict['reuseRankingCount']

        try:
            self.hiatusNights = config_dict['HiatusNextNight']
        except:
            self.hiatusNights = 0
        try:            
	    self.twilightBoundary = config['TwilightBoundary']
        except:
            self.twilightBoundary = -18.0

	try:
            filterNames   = config_dict["Filter"]
            filterMinBrig = config_dict["Filter_MinBrig"]
            filterMaxBrig = config_dict["Filter_MaxBrig"]
	except:
            filters_dict, pairs = readConfFile(DefaultFiltersConfigFile)
            filterNames   = filters_dict["Filter_Defined"]
            filterMinBrig = filters_dict["Filter_MinBrig"]
            filterMaxBrig = filters_dict["Filter_MaxBrig"]
        if not isinstance(filterNames, list):
            filterNames = [filterNames]
        if not isinstance(filterMinBrig, list):
            filterMinBrig = [filterMinBrig]
	if not isinstance(filterMaxBrig, list):
	    filterMaxBrig = [filterMaxBrig]
	try:
	    filterMaxSeeing=config_dict["Filter_MaxSeeing"]
	except:
	    filterMaxSeeing = []
	    for i in range(len(filterNames)):
		filterMaxSeeing.append(self.maxSeeing)
        if not isinstance (filterMaxSeeing, list):
            filterMaxSeeing = [filterMaxSeeing]

	self.FilterNames   = []
	self.FilterMinBrig = {}
	self.FilterMaxBrig = {}
	self.FilterMaxSeeing={}
	for ix in range(len(filterNames)):
	    self.FilterNames.append(filterNames[ix])
	    self.FilterMinBrig[filterNames[ix]]=filterMinBrig[ix]
            self.FilterMaxBrig[filterNames[ix]]=filterMaxBrig[ix]
	    self.FilterMaxSeeing[filterNames[ix]]=filterMaxSeeing[ix]
	self.FilterNames = sorted(self.FilterNames)
	self.log.info('propConf=%s filters=%s' % (self.propConf, str(self.FilterNames)))

	try:
	    self.StartTime = eval(str(config_dict["StartTime"]))
	except:
	    self.StartTime = None
        try:
            self.StopTime = eval(str(config_dict["StopTime"]))
        except:
            self.StopTime = None

        # load object instances
        self.sky = sky
        self.filters = filters
        self.weather = weather
        
        # the scheduled observations
        self.observations = []
        
        # the observations that have been already
        # carried out (and removed from self.observations)
        self.completedObservations = []
        
        # the current observation sequence
        self.sequence = []

        self.queue = []
        self.winners = []
        self.loosers = []
        
        self.getPropID ()

        self.log.info('FilterNames     for propID=%d %s = %s' % (self.propID, self.propFullName, str(self.FilterNames)))
        self.log.info('FilterMinBrig   for propID=%d %s = %s' % (self.propID, self.propFullName, repr(self.FilterMinBrig)))
        self.log.info('FilterMaxBrig   for propID=%d %s = %s' % (self.propID, self.propFullName, repr(self.FilterMaxBrig)))
        self.log.info('FilterMaxSeeing for propID=%d %s = %s' % (self.propID, self.propFullName, str(self.FilterMaxSeeing)))

        return
    
    
    def __del__ (self):
        """
        Destructor: close the log file.
        """
        try:
            self.log.close ()
        except:
            pass
        
        super (Proposal, self).__del__ ()
        return

    def IsActive(self, date, nightCnt):
        """
        Is proposal active right now?
        """
      
        if self.StartTime != None:
	    if self.StartTime > date:
		return False
        if self.StopTime != None:
            if self.StopTime < date:
                return False
        # proposal is activated but skips nights
        if self.nextNight != nightCnt:
            return False
	return True

    def IsActiveTonight(self, date, nightCnt):
        """
        Is proposal active sometime tonight?  If so, we will get its target
	list.
        """

        if self.StartTime != None:
            if self.StartTime > date+24*3600:
                return False
        if self.StopTime != None:
            if self.StopTime < date:
                return False
        # proposal is activated but skips nights
        if self.nextNight != nightCnt:
            return False
        return True                                                                                                                                                                                                    
    def GetPriority(self):

	return self.relativeProposalPriority
    
    def buildUserRegionDB(self,regions,fieldTable):
        """
        Build a short-term DB containing a user-specified subset of the FieldDB.
        The DB table will need to be deleted at the end of the run or during
        a subsequent garbage collection run on the DB.

        Input
            regions     list of (ra,dec,diameter) defining cone of interest for
                        a user defined region. All parameters are radians.

            fieldTable  base Field DB table from which to draw the overlapping
                        fields
            
        Output
            tablename   temporary Field DB table name
        """

        # Create short-term overlappingField table
        overlappingField = "OlapField_%d_%d" %(self.sessionID,self.propID)
#        sql = 'drop table if exists %s; ' %(overlappingField)
#        print sql
#        # Send the SQL commmand to the DB
#        (n, res) = self.lsstDB.executeSQL (sql)

#        sql = 'create table %s (fieldID int unsigned not null primary key,' % (overlappingField)
#        sql += 'fieldFov float NOT NULL,fieldRA float NOT NULL,fieldDec float NOT NULL,fieldGL float NOT NULL,fieldGB float NOT NULL,fieldEL float NOT NULL,fieldEB float NOT NULL);'
#        # Send the SQL commmand to the DB
#        (n, res) = self.lsstDB.executeSQL (sql)
        olapTable = self.lsstDB.createOlapTable(overlappingField)

        # Load entire FieldDB in-core
        sql = 'select fieldID,fieldFov,fieldRA,fieldDec,fieldGL,fieldGB,fieldEL,fieldEB from %s order by fieldID;' %(fieldTable)
        # Send the SQL commmand to the DB
        (n, res) = self.lsstDB.executeSQL (sql)

        # for each entry in regions:
        #       parse into components,
        #ra_rad = []
        #dec_rad = []
        #diameter_div2_rad = []
        for k in  range(len(regions)):
            ra_deg,dec_deg,diameter_deg = regions[k].split(',',3)

            ra_rad = float(ra_deg) * DEG2RAD
            dec_rad = float(dec_deg) * DEG2RAD
            diameter_div2_rad = float(diameter_deg) * DEG2RAD/2

            # for each entry in FieldDB
	    closestField = None
	    closestDistance = None
	    for (id,fov,ra,dec,gl,gb,el,eb) in res:
                # convert (ra,dec) to radians
        	ofRa = ra*DEG2RAD
            	ofDec = dec*DEG2RAD
                # Create distance measure to determine overlapping region&field
            	ofFov_div2 = fov*DEG2RAD/2

		distance = dist(ra_rad,dec_rad,ofRa,ofDec)
                if (distance < (ofFov_div2 + diameter_div2_rad)) :
		    if (closestDistance == None):
			closestDistance = distance
			closestField = (id,fov,ra,dec,gl,gb,el,eb)
		    else:
			if (distance < closestDistance):
			    closestDistance = distance
			    closestField = (id,fov,ra,dec,gl,gb,el,eb)
	    if (closestField != None):
		(id,fov,ra,dec,gl,gb,el,eb) = closestField
		self.lsstDB.addOlap(olapTable, id,fov,ra,dec,gl,gb,el,eb)
		self.log.info('Proposal: buildUserRegionDB(): Field=%i, RA=%f DEC=%f' % (id, ra, dec))

        return (olapTable)

    def getPropID (self):
        """
        Create an entry in the self.dbTableDict['proposal'] and fetch the key which
        have been assigned to us.
        
        Raise
        Exception if there are errors in the SQL or if the connection 
        to the database fails.
        """
        if ( self.log and self.verbose > 1 ):
           self.log.info('Proposal: getPropID()')
        
        # Get the short hostname
        self.host = socket.gethostname ().split ('.', 1)[0]
        
        # Get the object ID of self
        self.objID = id (self)
        
        ## Remove data from the previous run where session, host and object are
        ## the same. This should not happen but seems to sometimes .... 
        #sql = 'DELETE FROM %s WHERE ' % (self.dbTableDict["proposal"])
        #sql += 'sessionId=%d AND ' % (self.sessionID)
        #sql += 'objectHost="%s" AND ' % (self.host)
        #sql += 'objectID=%d' % (self.objID)
        #(n,res) = self.lsstDB.executeSQL (sql)

        # Create a new entry
#        sql = 'INSERT INTO %s VALUES (NULL, ' % (self.dbTableDict["proposal"])
#        sql += '"%s", ' % (self.propConf)
#        sql += '"%s", ' % (self.propName)
#        sql += '%d,  ' % (self.sessionID)
#        sql += '%d,  ' % (self.objID)
#        sql += '"%s" )' % (self.host)
#        (n,res) = self.lsstDB.executeSQL (sql)
#
#        # Now fetch the propID we got assigned
#        sql = 'SELECT propID FROM %s WHERE '  % (self.dbTableDict["proposal"])
#        sql += 'propConf="%s" AND ' % (self.propConf)
#        sql += 'propName="%s" AND ' % (self.propName)
#        sql += 'sessionID=%d AND ' % (self.sessionID)
#        sql += 'objectHost="%s" AND ' % (self.host)
#        sql += 'objectID=%d' % (self.objID)
#        (n,res) = self.lsstDB.executeSQL (sql)
#        self.propID = res[0][0]
               
        oProposal = self.lsstDB.addProposal(self.propConf, self.propName, self.sessionID, self.host, self.objID)
        self.propID = oProposal.propID

        return
    
    
    def transparencyOK(self,currentTransparency):
        """
        Routine to determine if current cloud transparency is within 
        range of proposal's  minimum cloud transparency.

        Input
            currentTransparency    value from Cloud DB for current timestep
        Output
            True, if within proposal's limit; else, False
        """
        if  currentTransparency < self.minTransparency :
            return (True)
        return (False)


    def startNewYear (self):
        """
        Routine to handle all year-end requirements
        """
        self.log.info("Proposal:startNewYear")
        return

    def startNight (self,dateProfile,moonProfile,startNewLunation, mountedFiltersList):
        """
        Update the target list and do any other beginning of Night setup step.
        
        Input
            dateProfile: current profile of date as list:
                        (date, mjd,lst_RAD) where:
                            date in seconds from Jan 1 of simulated year.
                            mjd - modified Julian date
                            lst_RAD - local sidereal time at site (radians)
            moonProfile: current profile of the moon as list:
                        (moonRA_RAD,moonDec_RAD, moonPhase_PERCENT)

            startNewLunation: True -> new lunation starting, False otherwise
        
        Return
            None
        """
        self.log.info("Proposal:startNight propID=%d" %(self.propID))

        # Create a pool of Observation instances (& garbage collect old Obs?)
        self.obsPool = {}

        for fieldID in self.targets.keys ():
            (ra, dec) = self.targets[fieldID]
            self.obsPool[fieldID] = {}
            for filter in self.filters.filterNames:
                self.obsPool[fieldID][filter] = Observation (dateProfile=dateProfile,
                                                    moonProfile=moonProfile,
                                                    proposal = self,
                                                    ra = ra,
                                                    dec = dec,
                                                    filter = filter,
                                                    maxSeeing = self.maxSeeing,
                                                    exposureTime = self.exposureTime,
                                                    fieldID = fieldID,
                                                    slewTime = -1.,
                                                    log = self.log,
                                                    logfile = self.logfile,
                                                    verbose = self.verbose)

	self.last_observed_fieldID = None
	self.last_observed_filter  = None
	self.last_observed_wasForThisProposal = False

        self.mountedFiltersList = mountedFiltersList
 
        # rank all targets
#        self.reuseRanking = 0

        return
    
    def start (self):
        """
        Activate the Proposal instance in the simulation and create 
        the appropriate number of Observation objects.
        Activate each Observation object and configure them.
        """
        if ( self.log and self.verbose > 1 ):
           self.log.info('Proposal: start() propID=%d' %(self.propID))

        mu = AVGPRIORITY
        sigma = mu * (SIGMAPERCENT / 100.)
        for target in self.targets:
            ra = target[0]
            dec = target[1]
            id = target[2]
            t = EXPTIME
            pri = random.normalvariate (mu, sigma)
            
            # create the observation with the desired exposure time
            # and priority.
            self.observations.append (Observation (proposal=self, 
                                                   ra=ra, 
                                                   dec=dec, 
                                                   exposureTime=t, 
                                                   priority=pri, 
                                                   verbose=self.verbose))
            
            # wait 1 second before sumbitting the next observation
#            yield hold, self
        return
    
    
    def loadTargetList (self, fileName=None):
        """
        load a target list (RA Dec ID) from fileName.
        """
        if ( self.log and self.verbose > 1 ):
           self.log.info('Proposal: loadTargetList(): Targets file = %s' % (fileName))
           
        t = []
        list = file (fileName).readlines ()
        for line in list:
            line = string.strip (line)
            
            # skip comments (identified by a #)
            if (line[0] == '#'):
                continue
            
            # try and parse the line, skip the line 
            # in case of error (silently)
            try:
                (ra, dec, id) = string.split (line)
            except:
                continue

            ra  = float(ra)
            dec = float(dec)
            id  = int(float(id))

            if ( self.log and self.verbose > 2 ):
                self.log.info("ra=%f dec=%f id=%d" % (ra, dec, id))
                
            t.append ((ra, dec, id))
        return (t)
    
    
    # Accessor Methods
    def getSeeing (self):
        """
        Query the Weather instance for the current seeing value.
        """
        return (self.weather.getSeeing (now ()))
    
    
    # Ranker Functionality
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
    
    
    def suggestObs (self, 
                    dateProfile, 
                    moonProfile,
                    n=1, 
                    fieldID=None, 
                    AmSbFlS=None):
        """
        Return the list of the n (currently) higher ranking fields.
        
        This method is the public interface to the Proposal class.
        
        Input
        dateProfile     current date profile of:
                            (date,mjd,lst_RAD) where:
                                    date    simulated time (s)
                                    mjd
                                    lst_RAD local sidereal time (radians)
        moonProfile     current moon profile of:
                            (moonRA_RAD,moonDec_RAD,moonPhase_PERCENT)
        n               number of observations to return.
        fieldID:        array of fieldIDs
        AmSbFlS: array of [AirMass, Sky brightness, Filterlist, Seeing] values 
                        (synced to fieldID)
        
        Return
        An array of n Observation objects.
        """
        if ( self.log and self.verbose > 1 ):
           self.log.info('Proposal: suggestObs()')

#        self.applyCuts ()
#        self.applyBonuses ()
        return

    
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
    
    
    def closeObservation (self, obs, obsHistID, twilightProfile):
        """
        Remove the corresponding field from self.targets
        
        Input
        obs     temp Observation instance containing only essential identifying
                data to match with real/complete Proposal Observation records
        winSlewTime  the slew time required by the winning Observation
        finRank  ...
        
        Return
        None
        
        Raise
        Exception if Observation History update fails
        """
        if ( self.log and self.verbose > 1 ):
           self.log.info('Proposal: closeObservation() propID=%d' %(self.propID))

        #self.log.info("Proposal:closeObs: #winners:%d #losers:%d" %( len(self.winners),len(self.loosers)))

        self.last_observed_fieldID = obs.fieldID
        self.last_observed_filter  = obs.filter
        self.last_observed_wasForThisProposal = False

        winner = None
        # Find obs in self.winners
        for o in self.winners:
#            if (o.fieldID == obs.fieldID and o.filter == obs.filter and o.exposureTime == obs.exposureTime):
            if (o.fieldID == obs.fieldID and o.filter == obs.filter):
                winner = o
                #print "Proposal: closeObs date=%d field=%d filter=%s propID=%d dist2moon=%f" % (obs.date, obs.fieldID, obs.filter, self.propID, o.distance2moon)
		self.winners.remove(o)
                break
        # If the observation was not found among the winners,
        # look for it in the losers set.
        if winner == None :
            for o in self.loosers:
#                if (o.fieldID == obs.fieldID and o.filter == obs.filter and o.exposureTime >= obs.exposureTime):
                if (o.fieldID == obs.fieldID and o.filter == obs.filter):
                    winner = o
		    self.loosers.remove(o)
                    break
#            if winner != None:
                # It found it! Serendipitus
#                if ( self.log and self.verbose > 0 ):
#                    self.log.info('Proposal: closeObservation() propID=%d SERENDIPITOUS' %(self.propID))

        if winner != None:
	    self.last_observed_wasForThisProposal = True

	    self.lsstDB.addObsHistoryProposal(self.propID, obsHistID, self.sessionID, winner.propRank)

	    self.log.info("propID=%i night=%i date=%i field=%i filter=%s expTime=%f visitTime=%f lst=%f" % (self.propID, winner.night, winner.date, winner.fieldID, winner.filter, winner.exposureTime, winner.visitTime, winner.lst))
            self.log.info("    propRank=%f airmass=%f brightness=%f filtBright=%f rawSeeing=%f seeing=%f" % (winner.propRank, winner.airmass, winner.skyBrightness, winner.filterSkyBright, winner.rawSeeing, winner.seeing))
	    self.log.info("    alt=%f az=%f pa=%f moonRA=%f moonDec=%f moonPh=%f dist2moon=%f transp=%f" % (winner.altitude, winner.azimuth, winner.parallactic, winner.moonRA_RAD, winner.moonDec_RAD, winner.moonPhase, winner.distance2moon, winner.transparency))
#            self.log.info("    solarE=%f sunAlt=%f sunAz=%f moonAlt=%f moonAz=%f moonBright=%f darkBright=%f" % (winner.solarElong, winner.sunAlt, winner.sunAz, winner.moonAlt, winner.moonAz, winner.moonBright, winner.darkBright))



            # Update suggested Observation with actual observing conditions 
#            obsfound.date = obs.date
#            obsfound.mjd = obs.mjd
#            obsfound.lst = obs.lst
#            obsfound.finRank = obs.finRank
#            obsfound.slewTime = obs.slewTime
#            obsfound.rotatorSkyPos = obs.rotatorSkyPos
#            obsfound.rotatorTelPos = obs.rotatorTelPos
#            obsfound.altitude = obs.altitude
#            obsfound.azimuth = obs.azimuth
#            obsfound.sunAlt = obs.sunAlt
#            obsfound.sunAz = obs.sunAz
#            obsfound.exposureTime = obs.exposureTime
#            obsfound.night = obs.night

            # get most current skyBrightness 
#            dateProfile = obs.date, obs.mjd, obs.lst
#            moonProfile = (obsfound.moonRA_RAD, obsfound.moonDec_RAD, 
#                           obsfound.moonPhase)
#            (skyBright,distance2moon,moonAlt_RAD,brightProfile) = \
#                        self.sky.getSkyBrightness (obsfound.fieldID,
#                                      obsfound.ra, obsfound.dec,
#                                      obsfound.altitude, 
#                                      dateProfile,
#                                      moonProfile,
#                                      twilightProfile)

            #print "latest skyBright = %f\toriginal skyBright = %f" % (skyBright, obsfound.skyBrightness)

#            (obsfound.phaseAngle, obsfound.extinction, obsfound.rScatter, 
#                 obsfound.mieScatter, obsfound.moonIllum, 
#                 obsfound.moonBright, obsfound.darkBright) = brightProfile

            # store new value since it is most accurate
#            obsfound.skyBrightness = skyBright
#            obsfound.distance2moon = distance2moon
#            obsfound.moonAlt = moonAlt_RAD
 
            # calculate airmass of actual observation 
#            obsfound.airmass = 1/math.cos(1.5708 - obsfound.altitude)

            # calculate current solar elongation in DEGREES
#            target = (obsfound.ra*DEG2RAD, obsfound.dec*DEG2RAD)
#            solarElong_RAD = self.sky.getPlanetDistance ('Sun',target, obs.date)
#            obsfound.solarElong = math.degrees(solarElong_RAD)

            # Derive skyBrightness for filter.  Interpolate if needed. - MM
#            (sunrise, sunset) = twilightProfile

            # set y skybrightness for any kind of sky
#            if (obsfound.filter == 'y'):
#               obsfound.filterSkyBright = 17.3  
#            else:      # g,r,i,z,u
               # If moon below horizon, use new moon offset for filter
               # brightness - MM
#               if (math.degrees(obsfound.moonAlt) <= -6.0):
#                  adjustBright = filterOffset[obsfound.filter,0.]

               # Interpolate if needed. Note: moonPhase is a float not int
#               elif (obsfound.moonPhase not in skyBrightKeys):
#                  i = 0
#                  while (skyBrightKeys[i] < obsfound.moonPhase):
#                     i = i+1

                  # find upper and lower bound
#                  upperMoonPhase = skyBrightKeys[i]
#                  lowerMoonPhase = skyBrightKeys[i-1]
#                  lowerAdjustBright = filterOffset[obsfound.filter,lowerMoonPhase]
#                  upperAdjustBright = filterOffset[obsfound.filter,upperMoonPhase]
                  # linear interpolation
#                  adjustBright = lowerAdjustBright + (((obsfound.moonPhase - lowerMoonPhase)*(upperAdjustBright - lowerAdjustBright))/(upperMoonPhase - lowerMoonPhase))
   
#               else:          # moon not set and moon phase is key
#                  adjustBright = filterOffset[obsfound.filter, obsfound.moonPhase]
#               obsfound.filterSkyBright = obsfound.skyBrightness + adjustBright

               # z sky brightness should never be under 17.0
#               if (obsfound.filter == 'z') and (obsfound.filterSkyBright < 17.0):
#                  obsfound.filterSkyBright = 17.0

	    # If twilight, set brightness for z and y
#            if ( obs.date < sunset) or (obs.date > sunrise):
#	       if (obsfound.filter == 'z') or (obsfound.filter == 'y'):
#		   obsfound.filterSkyBright = 17.0

	    # build visit history
            fieldID = obs.fieldID
            filter = obs.filter
            try:
                self.fieldVisits[fieldID] += 1
            except:
                self.fieldVisits[fieldID] = 0
            winner.fieldVisits = self.fieldVisits[fieldID]

            try:
                winner.fieldInterval = obs.date-self.lastFieldVisit[fieldID]
            except:
                winner.fieldInterval = 0
            self.lastFieldVisit[fieldID] = obs.date

            if not self.lastFieldFilterVisit.has_key(fieldID):
                self.lastFieldFilterVisit[fieldID] = {filter:obs.date}
            else:
                if not self.lastFieldFilterVisit[fieldID].has_key(filter):
                    self.lastFieldFilterVisit[fieldID][filter] = obs.date
            winner.fieldFilterInterval = obs.date - self.lastFieldFilterVisit[fieldID][filter]
            self.lastFieldFilterVisit[fieldID][filter] = obs.date

#            obsfound.slewDistance = slalib.sla_dsep(self.lastTarget[0],self.lastTarget[1],obsfound.ra*DEG2RAD,obsfound.dec*DEG2RAD)
            self.lastTarget = (winner.ra*DEG2RAD,winner.dec*DEG2RAD)

            # update the ObsHistory DB with the new observation
#            self.obsHistory.addObservation (obsfound, self.sessionID)
        
        return winner

    def missObservation(self, obs):

        self.missedHistory.addMissed(obs, self.sessionID)
        
        return
        
    def clearSuggestList(self):

        self.queue = []

        return

    def addToSuggestList(self, observation):#, proximity):

        # Compute an internal rank considering proximity and use it as
        # the sorting key to the heap.
#        rankProximity = self.maxProximityBonus/(proximity+0.1)/0.1
        rankInternal  = observation.propRank# + rankProximity
       
	# Add the relative proposal priority coefficient.
	observation.propRank *= self.relativeProposalPriority
 
        # Add it to queue (heappush places min on top, so invert rank)
        heapq.heappush(self.queue, (-rankInternal, observation))

        return

    def getSuggestList(self, n=1):
        
        # Choose the n highest ranking observations

        self.winners = []
        for i in range (n):
            try:
                self.winners.append (heapq.heappop (self.queue)[1])
                if self.log and self.verbose>1:
                    self.log.info('Proposal: suggestObs() propID=%d field=%i propRank=%.2f' % (self.propID,self.winners[-1].fieldID, self.winners[-1].propRank))
            except:
                break

        # ZZZ - MM commented out. Why should we sort the list by fieldID?
        #self.winners.sort(compareWinners)
        self.loosers = []
        while self.AcceptSerendipity == True:
            try:
                self.loosers.append (heapq.heappop (self.queue)[1])
            except:
                break

        return (self.winners)

    def computeTargetsHAatTwilight(self, lst_twilight_RAD):

	self.ha_twilight = {}
#	for field in self.targets.keys():
        for field in sorted(self.targets.iterkeys()):
	    (ra,dec) = self.targets[field]
	    ha = (lst_twilight_RAD - ra*DEG2RAD) * 12.0/math.pi
	    if (ha < -12.0):
		ha +=24
	    elif (ha > 12):
		ha -=24
	    self.ha_twilight[field] = ha

    def allowedFiltersForBrightness(self, brightness):
        """
        Computes a list of adequate filters according to the sky brightness
        """
        # NOTE Require sky brightness to be precomputed and passed as parameter

        filterList = []

	for filter in self.FilterNames:
	    if (filter in self.mountedFiltersList) and (self.FilterMinBrig[filter] < brightness < self.FilterMaxBrig[filter]):
		filterList.append(filter)

	return filterList

