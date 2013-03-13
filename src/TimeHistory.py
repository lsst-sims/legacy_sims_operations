#!/usr/bin/env python

"""
TimeHistory

Inherits from: LSSTObject : object

Class Description
The TimeHistory class is an interface to the TimeHistory database.
It provides methods to ingest data into the database and to retrieve
data from it.

Method Types
Constructor/Initializers
- __init__

DB Access
- add
"""

from utilities import *
from LSSTObject import *



class TimeHistory (LSSTObject):
    def __init__ (self, 
                  lsstDB,
		  dbTableDict=None,
                  log=False,
                  logfile='./TimeHistory.log',
                  verbose=0):
        """
        Standard initializer.
        
       	lsstDB:     LSST DB access object
	dbTableDict:
        log:        False if not set; else log = logging.getLogger("....")
        logfile:    name (and path) of the desired log file 
                    (defaults to ./TimeHistory.log)
        verbose:    integer specifying the verbosity level (defaults to 0).
                    -1=none, 0=min, 1=wordy, >1=very verbose
 
        """
	self.lsstDB = lsstDB        
	self.dbTableDict = dbTableDict

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up TimeHistory logger"
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
            self.log.info('TimeHistory: init()')
            #for key in self.dbTableDict:
            #    print "TimeHistory:    Database tables: " + key,self.dbTableDict[key]
        return
    
    
    # DB Access methods
    def add (self, 
             sessionID,
             nightCnt,
             dateProfile,
             event):
        """
        Ingest the given Observation instance into the database.
        
        Input
            sessionID:      An integer identifying this particular run.
            dateProfile:    An array containing
                date:     elapsed time in seconds from Jan 1 of simulated year.
                mjd:      modified Julian date
                lst_RAD:  local sidereal time at site (radians)
            event:  = one of {START_NIGHT, MOON_WAXING, MOON_WANING, NEW_YEAR}
        
        Return
            None
        
        Raise
        Exception in case of error in the ingestion procedure.
        """
        (date, mjd, lst_RAD) = dateProfile
        if ( self.log and self.verbose > 0):
            self.log.info('TimeHistory: add(): date:%d mjd:%f event:%d ' % (date,mjd,event))
        
#        sql = 'INSERT INTO %s VALUES (NULL, %d, %d, %f, %d, %d )' \
#            % (self.dbTableDict['timeHist'], \
#               sessionID, date, mjd, nightCnt, event)
#        (n, dummy) = self.lsstDB.executeSQL (sql)
        self.lsstDB.addTimeHistory(sessionID, date, mjd, nightCnt, event)
        return
    
    
    def cleanup(self, 
                         sessionID):
        """
        Cleans up the TimeHistory database by removing all the entries 
        relative to a given proposal ID.
        
        Input
        propID:     An integer identifying a particular proposal.
        sessionID:  An integer identifying this particular run.
        
        Return
        None
        
        Raise
        Exception in case of error in the ingestion procedure.
        """
        print "sessionID: ", sessionID
        if ( self.log and self.verbose > 1):
            self.log.info('TimeHistory: cleanup()')

        sql = 'DELETE FROM %s WHERE ' % (self.dbTableDict['timeHist'])
        sql += ' sessionID=%d' % (sessionID)

        (n, res) = self.lsstDB.executeSQL (sql)
        return
    
    
# TESTS
if (__name__ == '__main__'):
    pass

