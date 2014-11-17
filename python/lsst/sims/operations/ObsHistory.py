#!/usr/bin/env python

"""
ObsHistory

Inherits from: LSSTObject : object

Class Description
The ObsHistory class is an interface to the ObsHistory database.
It provides methods to ingest data into the database and to retrieve
data from it.

Data is passed to and from this class by means of Observation 
instances.


Method Types
Constructor/Initializers
- __init__

DB Access
- addObservation
- getObservation
- cleanupProposal
"""


from utilities import *
from LSSTObject import *
from Observation import *



class ObsHistory (LSSTObject):
    def __init__ (self, 
                  lsstDB,
		  dbTableDict=None,
                  log=False,
                  logfile='./ObsHistory.log',
                  verbose=0):
        """
        Standard initializer.
        
	lsstDB:     LSST DB access object
        dbTableDict:
        log:        False if not set; else log = logging.getLogger("....")
        logfile:    name (and path) of the desired log file 
                    (defaults to ./ObsHistory.log)
        verbose:    integer specifying the verbosity level (defaults to 0).
                    -1=none, 0=min, 1=wordy, >1=very verbose
 
        """
	self.lsstDB = lsstDB        
	self.dbTableDict = dbTableDict

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up ObsHistory logger"
            log = logging.getLogger("Simulator")
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.INFO)
        self.log = log
        self.logfile = logfile
        self.verbose = verbose

        if ( self.log and self.verbose > 1):
            self.log.info('ObsHistory: init()')
            #for key in self.dbTableDict:
            #    print "ObsHistory:    Database tables: " + key,self.dbTableDict[key]
        return
    
    
    # DB Access methods
    def addObservation (self, 
                        obs,
                        sessionID):
        """
        Ingest the given Observation instance into the database.
        
        Input
        obs         Observation instance.
        sessionID:  An integer identifying this particular run.
        
        Return
        None
        
        Raise
        Exception in case of error in the ingestion procedure.
        """
        if ( self.log and self.verbose > 0):
            self.log.info('ObsHistory: addObs(): field:%d fltr:%s date:%d expTime:%f slew:%f prop:%d' % (obs.fieldID,obs.filter,obs.date,obs.exposureTime,obs.slewTime,obs.propID))

        sql = 'INSERT INTO %s VALUES (NULL, %d, %d, %d, "%s", \
               %d, "%s", %d,\
               %d, %f,\
               %d, %f,\
               %f, %f,\
               %f, %f,\
               %d, %d, %d,\
               %f, %f,\
               %f, %f, %f, \
               %f, %f,\
               %f, %f, %f,\
               %f, %f,\
               %f, %f, %f,\
               %f,\
               %f, %f, %f, %f,\
               %f, %f, \
               %f, %f, \
               %f, %f, %f, \
               %f, %f)' \
            % (self.dbTableDict['obsHist'], \
               sessionID, obs.propID, obs.fieldID, obs.filter, \
               obs.seqn, obs.subsequence, obs.pairNum, \
               obs.date, obs.mjd, \
               obs.night, obs.exposureTime, \
               obs.slewTime, obs.slewDistance, \
               obs.rotatorSkyPos, obs.rotatorTelPos, \
               obs.fieldVisits, obs.fieldInterval, obs.fieldFilterInterval, \
               obs.propRank, obs.finRank, \
               obs.maxSeeing, obs.rawSeeing, obs.seeing, \
               obs.transparency, obs.cloudSeeing, \
               obs.airmass, obs.skyBrightness, obs.filterSkyBright, \
               obs.ra * DEG2RAD, obs.dec * DEG2RAD, \
               obs.lst, obs.altitude, obs.azimuth, \
               obs.distance2moon, \
               obs.moonRA, obs.moonDec, obs.moonAlt, obs.moonPhase, \
               obs.sunAlt, obs.sunAz, \
               obs.phaseAngle, obs.rScatter, \
               obs.mieScatter, obs.moonIllum, obs.moonBright, \
               obs.darkBright, obs.solarElong)

        #(n, dummy) = self.lsstDB.executeSQL (sql)
        return
    
    def getNVisitsPerFilter (self, 
                             propID,
                             sessionID):
        """
        Retrieve the number of visits per proposal, session, filter.
        
        Input
        obs         Observation instance.
        sessionID:  An integer identifying this particular run.
        
        Return
        A dictionary of the form {filter: nVisits}
        
        Raise
        Exception in case of error in the communications with the DB.
        """
        if ( self.log and self.verbose > 1):
            self.log.info('ObsHistory: getNVisitsPerFilter()')

        visits = {}
        
        tmpObsHistDB = self.dbTableDict['obsHist']
        sql = 'SELECT filter, count(*) FROM %s \
            WHERE propID=%d AND sessionID=%d \
            GROUP BY filter' % (tmpObsHistDB,propID,sessionID)

        (n, res) = self.lsstDB.executeSQL (sql)
        
        for row in res:
            filter = row[0].lower ()
            n = int (row[1])
            
            if (not visits.has_key (filter)):
                visits[filter] = n
            else:
                visits[filter] += n
        return (visits)
    
    
    def getNVisitsPerFilterField (self, 
                                  propID,
                                  sessionID,
                                  fieldID=None):
        """
        Retrieve the number of visits per proposal, session, filter 
        and fieldID.
        
        Input
        obs         Observation instance.
        propID      An integer specifying the particular proposal.
        sessionID   An integer identifying this particular run.
        fieldID     The ID of the particular field. If fieldID is
                    None, than all the fields are considered.
        
        Return
        A dictionary of the form {filter: {fieldID: nVisits}}
        
        Raise
        Exception in case of error in the communications with the DB.
        """
        if ( self.log and self.verbose > 1):
            self.log.info('ObsHistory: getNVisitsPerFilter()')

        visits = {}
        
        tmpObsHistDB = self.dbTableDict['obsHist']
        if (fieldID != None):
            tmpField = 'AND fieldID=%d ' % (fieldID)
        else:
            tmpField = ""
        sql = 'SELECT filter, fieldID, count(*) FROM %s \
            WHERE propID=%d AND sessionID=%d %s \
            GROUP BY filter, fieldID' % (tmpObsHistDB,propID,sessionID,tmpField,)

        (n, res) = self.lsstDB.executeSQL (sql)
        
        for row in res:
            filter = row[0].lower ()
            fieldID = int (row[1])
            n = int (row[2])
            
            if (not visits.has_key (filter)):
                visits[filter] = {}
            visits[filter][fieldID] = n
        return (visits)
    
    
    def getNVisitsPerFilterDay (self, 
                                propID,
                                sessionID,
                                dateMin,
                                dateMax):
        """
        Retrieve the number of visits per proposal, session, filter and
        date range.
        
        Input
        obs         Observation instance.
        sessionID:  An integer identifying this particular run.
        dateMin:    Minimum value for date
        dateMax:    Max value for date
                    Dates in seconds from Jan 1 of the simulated year.
        
        Return
        A dictionary of the form {filter: nVisits}
        
        Raise
        Exception in case of error in the communications with the DB.
        """
        if ( self.log and self.verbose > 1):
            self.log.info('ObsHistory: getNVisitsPerFilter()')
        
        visits = {}
        
        tmpObsHistDB = self.dbTableDict['obsHist']
        sql = 'SELECT filter, count(*) FROM %s \
            WHERE propID=%d AND sessionID=%d \
            AND expDate BETWEEN %f AND %f \
            GROUP BY filter' % (tmpObsHistDB,propID,sessionID,dateMin,dateMax)

        (n, res) = self.lsstDB.executeSQL (sql)
        
        for row in res:
            filter = row[0].lower ()
            n = int (row[1])
            
            if (not visits.has_key (filter)):
                visits[filter] = n
            else:
                visits[filter] += n
        return (visits)
    
    
    def getVisitsPerFilter (self, 
                            propID,
                            sessionID):
        """
        Retrieve the visited fields per proposal, session, filter.
        
        Input
        obs         Observation instance.
        sessionID:  An integer identifying this particular run.
        
        Return
        A dictionary of the form {filter: [fieldID, fieldID, ...]}
        
        Raise
        Exception in case of error in the communications with the DB.
        """
        if ( self.verbose > 1):
            self.log.info('ObsHistory: getNVisitsPerFilter()')

        visits = {}
        
        tmpObsHistDB = self.dbTableDict['obsHist']
        sql = 'SELECT filter, fieldID FROM %s \
            WHERE propID=%d AND sessionID=%d \
            GROUP BY filter' % (tmpObsHistDB,propID,sessionID)

        (n, res) = self.lsstDB.executeSQL (sql)
        
        for row in res:
            filter = row[0].lower ()
            fieldID = int (row[1])
            
            if (not visits.has_key (filter)):
                visits[filter] = []
            visits[filter].append (fieldID)
        return (visits)
    
    
    def getNVisitsPerFilterDay (self, 
                                propID,
                                sessionID,
                                dateMin,
                                dateMax):
        """
        Retrieve the visited fields per proposal, session, filter and
        date range.
        
        Input
        obs         Observation instance.
        sessionID:  An integer identifying this particular run.
        dateMin:    Minimum value for date
        dateMax:    Max value for date
                    Dates in seconds from Jan 1 of the simulated year.
        
        Return
        A dictionary of the form {filter: [fieldID, fieldID, ...]}
        
        Raise
        Exception in case of error in the communications with the DB.
        """
        if ( self.verbose > 1):
            self.log.info('ObsHistory: getNVisitsPerFilter()')
        
        visits = {}
        
        tmpObsHistDB = self.dbTableDict['obsHist']
        sql = 'SELECT filter, fieldID FROM %s \
            WHERE propID=%d AND sessionID=%d \
            AND expDate BETWEEN %f AND %f \
            GROUP BY filter' % (tmpObsHistDB,propID,sessionID,dateMin,dateMax)

        (n, res) = self.lsstDB.executeSQL (sql)
        
        for row in res:
            filter = row[0].lower ()
            fieldID = int (row[1])
            
            if (not visits.has_key (filter)):
                visits[filter] = []
            visits[filter].append (fieldID)
        return (visits)
    
    
    
    
    def cleanupProposal (self, 
                         propID, 
                         sessionID):
        """
        Cleans up the ObsHistory database by removing all the entries 
        relative to a given proposal ID.
        
        Input
        propID:     An integer identifying a particular proposal.
        sessionID:  An integer identifying this particular run.
        
        Return
        None
        
        Raise
        Exception in case of error in the ingestion procedure.
        """
        print "propID: ", propID, " sessionID: ", sessionID
        if ( self.log and self.verbose > 1):
            self.log.info('ObsHistory: cleanupProposal()')

#        sql = 'DELETE FROM %s WHERE ' % (self.dbTableDict['obsHist'])
#        sql += 'propID=%d AND ' % (propID)
#        sql += ' sessionID=%d' % (sessionID)
#
#        (n, res) = self.lsstDB.executeSQL (sql)
        return
    
    
# TESTS
if (__name__ == '__main__'):
    pass

