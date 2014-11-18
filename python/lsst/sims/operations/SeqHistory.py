#!/usr/bin/env python

"""
SeqHistory

Inherits from: LSSTObject : object

Class Description
The SeqHistory class is an interface to the SeqHistory database.
It provides methods to ingest data into the database and to retrieve
data from it.


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



class SeqHistory (LSSTObject):
    def __init__ (self,
		  lsstDB, 
                  dbTableDict=None,
                  log=False,
                  logfile='./SeqHistory.log',
                  verbose=0):
        """
        Standard initializer.
        
	lsstDB      LSST DB access object        
	dbTableDict:
        log:        False if not set; else log = logging.getLogger("....")
        logfile:    name (and path) of the desired log file 
                    (defaults to ./SeqHistory.log)
        verbose:    integer specifying the verbosity level (defaults to 0).
                    -1=none, 0=min, 1=wordy, >1=very verbose
 
        """
	self.lsstDB = lsstDB        
	self.dbTableDict = dbTableDict

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up SeqHistory logger"
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
            self.log.info('SeqHistory: init()')
            #for key in self.dbTableDict:
            #    print "SeqHistory:    Database tables: " + key,self.dbTableDict[key]
        return
    
    
    # DB Access methods
    def addSequence (self, seq, fieldID, sessionID,obsdate,status):
        """
        Ingest the given Observation instance into the database.
        
        Input
        seq         Sequence instance.
        sessionID:  An integer identifying this particular run.
        obsdate:    date of final event
        status:     reason for sequence completion
        
        Return
        None
        
        Raise
        Exception in case of error in the ingestion procedure.
        """
        if ( self.log and self.verbose > 1):
            self.log.info('SeqHistory: addObservation(): dbTableKey:%s' % (self.dbTableDict['seqHistory']))
        
        numRequestedEvents = seq.GetNumTargetEvents()
        numActualEvents    = seq.GetNumActualEvents()
        tmpSeqHistoryDB = self.dbTableDict['seqHistory']
        sql = "INSERT INTO %s VALUES (NULL, %d, %d, %d, %d, %d, %d, %f, %d, %d, '%d')" \
            % ( self.dbTableDict['seqHistory'],\
                sessionID,\
                seq.date,\
                obsdate,\
                seq.propID,\
                fieldID,\
		seq.seqNum,
                seq.GetProgress(),
                numRequestedEvents,
                numActualEvents,
                status)
        
#        (n, dummy) = self.lsstDB.executeSQL (sql)
        return
    
    
    def cleanupProposal (self, 
                         propID, 
                         sessionID):
        """
        Cleans up the SeqHistory database by removing all the entries 
        relative to a given proposal ID.
        
        Input
        propID:     An integer identifying a particular proposal.
        sessionID:  An integer identifying this particular run.
        
        Return
        None
        
        Raise
        Exception in case of error in the ingestion procedure.
        """
        if ( self.log and self.verbose > 1):
            self.log.info('SeqHistory: cleanupProposal()')

#        sql = 'DELETE FROM %s WHERE ' % (self.dbTableDict['seqHistory'])
#        sql += 'propID=%d AND ' % (propID)
#        sql += ' sessionID=%d' % (sessionID)
#
#        (n, res) = self.lsstDB.executeSQL (sql)
        return
    
    
# TESTS
if (__name__ == '__main__'):
    pass
