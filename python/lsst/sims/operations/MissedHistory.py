#!/usr/bin/env python

"""

Method Types
Constructor/Initializers
- __init__

DB Access
"""


from utilities import *
from LSSTObject import *
from Observation import *



class MissedHistory (LSSTObject):
    def __init__ (self,
		  lsstDB, 
                  dbTableDict=None,
                  log=False,
                  logfile='./MissedHistory.log',
                  verbose=0):
        """
        Standard initializer.
        
	lsstDB      LSST DB access object        
	dbTableDict:
        log:        False if not set; else log = logging.getLogger("....")
        logfile:    name (and path) of the desired log file 
                    (defaults to ./MissedHistory.log)
        verbose:    integer specifying the verbosity level (defaults to 0).
                    -1=none, 0=min, 1=wordy, >1=very verbose
 
        """
	self.lsstDB = lsstDB        
	self.dbTableDict = dbTableDict

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up MissedHistory logger"
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
            self.log.info('MissedHistory: init()')
        return
    
    
    # DB Access methods
    def addMissed (self, 
                        obs,
                        sessionID):
        """
        Ingest the given Missed Observation instance into the database.
        
        Input
        obs         Observation instance.
        sessionID:  An integer identifying this particular run.
        
        Return
        None
        
        Raise
        Exception in case of error in the ingestion procedure.
        """
        if ( self.log and self.verbose > 0):
            self.log.info('MissedHistory: addObs(): field:%d fltr:%s date:%d prop:%d' % (obs.fieldID,obs.filter,obs.date,obs.propID))

        sql = 'INSERT INTO %s VALUES (NULL, \
                %d, %d, %d, "%s", \
                %d, "%s", %d, \
                %d, %f, \
                %f, %f)' \
            % (self.dbTableDict['misHist'], \
               sessionID, obs.propID, obs.fieldID, obs.filter, \
               obs.seqn, obs.subsequence, obs.pairNum, \
               obs.date, obs.mjd, \
               obs.ra * DEG2RAD, obs.dec * DEG2RAD)

        #(n, dummy) = self.lsstDB.executeSQL (sql)
        return
    
    
# TESTS
if (__name__ == '__main__'):
    pass

