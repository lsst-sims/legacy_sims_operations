#!/usr/bin/env python

"""
Weather

Inherits from: LSSTObject : object

Class Description
The Weather class is an interface to the weather data database/model.
It provides current values for comon weather related parameters such 
as seeing and sky transparency.


Method Types
Constructor/Initializers
- __init__

Accessors
- getSeeing
"""


from utilities import *
from LSSTObject import *




class Weather (LSSTObject):
    def __init__ (self, 
                  lsstDB,
		  date=None, 
                  dbTableDict=None,
                  seeingEpoch=None,
                  simStartDay=None,
                  log=False, 
                  logfile='./Weather.log', 
                  verbose=-1):
        """
        Standard initializer.
        
	lsstDB      It is the DB access object for executing SQL        
	date:       date, in seconds from January 1st (start of the 
                    simulated year).
        dbTableDict:
        seeingEpoch:
        simStartDay:
        log         False if not set, else: log = logging.getLogger("...")
        logfile     Name (and path) of the desired log file.
                    Defaults "./Weather.log".
        verbose:    Log verbosity: none=-1, 0=minimal, 1=wordy, >1=verbose
                    Default is -1

        """
	self.lsstDB = lsstDB        
	self.date = date
        self.dbTableDict = dbTableDict
        self.seeingEpoch = seeingEpoch
        self.simStartDay = simStartDay
        self.simStartSeconds  = simStartDay * DAY
        self.tonightClouds = {}     # dict tonight's clouds (c_date, cloud)
        self.currentDate = 0	# last adjusted date that data was requested
        self.currentCloud = 0

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up Weather logger"
            log = logging.getLogger("Weather")
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.INFO)
                                                                                
        self.log=log
        self.logfile=logfile
        self.verbose = verbose
    
        # load into self the number of seconds of cloud data in the DB
        tmpCloudDB = self.dbTableDict['cloud']
        sql = 'SELECT max(c_date) FROM %s ' % (tmpCloudDB)
                                                                                
        # Send the query to the DB
        (n, res) = self.lsstDB.executeSQL (sql)
        self.modCloud = res[0][0]
                                                                                
        # load into self the number of days of seeing data in the DB
        tmpSeeingDB = self.dbTableDict['seeing']
        sql = 'SELECT max(s_date) FROM %s ' % (tmpSeeingDB)
                                                                                
        # Send the query to the DB
        (n, res) = self.lsstDB.executeSQL (sql)
        self.modSeeing = res[0][0]
        return
                                                                                
    def getNightSeeing (self, startNight, endNight):
        """
        Get entire night's cloud data
        """

        self.tonightSee = {}     # clear dict tonight's seeing
        adjustedStart = (self.simStartSeconds + startNight) % self.modSeeing
        adjustedEnd = (self.simStartSeconds + endNight) % self.modSeeing

        # find closest starting entry in DB for night
        sql = 'SELECT s_date FROM %s \
            WHERE ABS(s_date - %d) = (SELECT MIN(ABS(s_date - %d)) \
            FROM %s)' % (self.dbTableDict['seeing'], adjustedStart, adjustedStart,
            self.dbTableDict['seeing'])
        (n, res) = self.lsstDB.executeSQL (sql)
        adjustedStart = (res[0][0])
        #print "n = %d, adjustedStart = %s" % (n, res)
       
        # find closest ending entry in DB for night
        sql = 'SELECT s_date FROM %s \
            WHERE ABS(s_date - %d) = (SELECT MIN(ABS(s_date - %d)) \
            FROM %s)' % (self.dbTableDict['seeing'], adjustedEnd, adjustedEnd,
            self.dbTableDict['seeing'])
        (n, res) = self.lsstDB.executeSQL (sql)
        adjustedEnd = (res[0][0])
        #print "n = %d, adjustedEnd = %s" % (n, res)
       
        #  Acquire the seeing data
        sql = 'SELECT s_date, seeing FROM %s WHERE s_date >= %d AND s_date <= %d' \
                  % (self.dbTableDict['seeing'], adjustedStart, adjustedEnd)
        (n, res) = self.lsstDB.executeSQL (sql)
        #print "n = %d, res = %s" % (n, res)

        i = 1
        self.curSeeIdx = i
        for (s_date, seeing) in res:
            self.tonightSee[i] = (s_date, seeing)
            i += 1

        #print "Weather.tonightSee for start=%d to end=%d" % (startNight, endNight)
        #print self.tonightSee

        if len (self.tonightSee) != 0:
            (self.curSeeDate, self.currentSee) = self.tonightSee.pop (self.curSeeIdx)
            self.curSeeIdx += 1
            nextSeeDate = self.tonightSee[self.curSeeIdx][0]
            self.seeInterval = (nextSeeDate - self.curSeeDate) / 2
            #print "after pop self.tonightSee()"
            #print self.tonightSee
            #print "nextSeeDate = %d, seeInterval = %d" % (nextSeeDate, self.seeInterval)
        #  ?? else:
            
        return 

    def getSeeing (self, date=None):
        """
        Return the average seeing for a given date (in seconds from 
        the beginning of the simulated year).
        """
        adjustedDate = (self.simStartSeconds + date) % self.modSeeing
        #print "Weather.getSeeing(): date = %d adjustDate = %d self.curSeeDate = %d" % (date, adjustedDate, self.curSeeDate)
 
	# Seeing is no longer current. Pop until entry in right date range.
        while (date > self.curSeeDate + self.seeInterval) and len (self.tonightSee) != 0:
            (self.curSeeDate, self.currentSee) = self.tonightSee.pop (self.curSeeIdx)
            self.curSeeIdx += 1

            if len (self.tonightSee) != 0:
                nextSeeDate = self.tonightSee[self.curSeeIdx][0]
                self.seeInterval = (nextSeeDate - self.curSeeDate)/ 2
                #print "nextSeeDate = %d self.seeInterval = %d" % (nextSeeDate, self.seeInterval)
            else:
                self.seeInterval = 0
        #print "self.curSeeDate = %d use current seeing = %f" % (self.curSeeDate, self.currentSee)

        return (self.currentSee)

    def getNightClouds (self, startNight, endNight):
        """
        Get entire night's cloud data
        """

        self.tonightClouds = {}     # clear dict tonight's clouds
        adjustedStart = (self.simStartSeconds + startNight) % self.modCloud
        adjustedEnd = (self.simStartSeconds + endNight) % self.modCloud

        # find closest starting entry in DB for night
        sql = 'SELECT c_date FROM %s \
            WHERE ABS(c_date - %d) = (SELECT MIN(ABS(c_date - %d)) \
            FROM %s)' % (self.dbTableDict['cloud'], adjustedStart, adjustedStart,
            self.dbTableDict['cloud'])
        (n, res) = self.lsstDB.executeSQL (sql)
        adjustedStart = (res[0][0])
        #print "n = %d, adjustedStart = %s" % (n, res)
       
        # find closest ending entry in DB for night
        sql = 'SELECT c_date FROM %s \
            WHERE ABS(c_date - %d) = (SELECT MIN(ABS(c_date - %d)) \
            FROM %s)' % (self.dbTableDict['cloud'], adjustedEnd, adjustedEnd,
            self.dbTableDict['cloud'])
        (n, res) = self.lsstDB.executeSQL (sql)
        adjustedEnd = (res[0][0])
        #print "n = %d, adjustedEnd = %s" % (n, res)
       
        #  Acquire the cloud data
        sql = 'SELECT c_date, cloud FROM %s WHERE c_date >= %d AND c_date <= %d' \
                  % (self.dbTableDict['cloud'], adjustedStart, adjustedEnd)
        (n, res) = self.lsstDB.executeSQL (sql)
        #print "n = %d, res = %s" % (n, res)
    
        i = 1
        self.currentIdx = i
        for (c_date, cloud) in res:
            self.tonightClouds[i] = (c_date, cloud)
            i += 1

        #print "Weather.tonightClouds for start=%d to end=%d" % (startNight, endNight)
        #print self.tonightClouds

        if len (self.tonightClouds) != 0:
            (self.currentDate, self.currentCloud) = self.tonightClouds.pop (self.currentIdx)
            nextDate = self.tonightClouds[self.currentIdx+1][0]
            self.interval = (nextDate - self.currentDate) / 2
            self.currentIdx += 1
            #print "after pop self.tonightClouds()"
            #print self.tonightClouds
            #print "nextDate = %d, interval = %d" % (nextDate, self.interval)
        return 

    def getTransparency (self, date):
        """
        Return the cloud transparency for a given date (in seconds from 
        the beginning of the simulated year).
        """
        adjustedDate = (self.simStartSeconds + date) % self.modCloud
        #print "Weather.getTransparency(): date = %d adjustDate = %d self.currentDate = %d" % (date, adjustedDate, self.currentDate)

        # Weather is no longer current. Pop until entry in right date range.
        while (date > self.currentDate + self.interval) and len (self.tonightClouds) != 0:
            (self.currentDate,self.currentCloud) = self.tonightClouds.pop(self.currentIdx)
            self.currentIdx += 1

            # calculate time interval between this and next entry
            if len (self.tonightClouds) != 0:
                nextDate = self.tonightClouds[self.currentIdx][0]
                self.interval = (nextDate - self.currentDate) / 2
                #print "nextDate = %d, interval = %d" % (nextDate, self.interval)
            # there is no next entry
            else: 
                self.interval = 0

        #print "use current cloud = %f currentIdx = %d " % (self.currentCloud, self.currentIdx)
        return (self.currentCloud)
        
# TESTS
if (__name__ == '__main__'):
    message = 'Instantiating Weather class: '
    try:
        w = Weather ()
        status = 'ok'
    except:
        status = 'FAILED'
    print (message + status)
    if (status != 'ok'):
        sys.exit (1)
    
    stop = 86400 * 365      # seconds in one year
    step = 86400            # seconds in one day
    success = 0
    failed = 0
    date = 0
    while (date <= stop):
        message = 'Seeing at %d' % (date)
        try:
            s = str (w.getSeeing (date))
            success += 1
        except:
            s = 'FAILED'
            failed += 1
        print ('%s: %s' % (message, s))
        date += step
    
    tot = failed + success
    print ('OK:     %d/%d' % (success, tot))
    print ('FAILED: %d/%d' % (failed, tot))
