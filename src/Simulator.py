#!/usr/bin/env python

"""
Simulator

Inherits from: Simulation.Process : object

Class Description
The Simulator class represents the control center of the whole 
simulation. It has exclusive access to the three top level objects in 
the simulation: NonObsScheduler, ObsScheduler and the telescope
resource.

Every time the telescope is available, the Simulator object queries 
the active ObsScheduler for a filed+filter combination. It then 
queries NonObsScheduler to check whether it is time for some non
science observation or random down-time. The decision of 
NonObsScheduler might have precendence over the recommendations of
the ObsScheduler.

Based on its internal logic, Simulator acquires access to the 
telescope, thus simulating either an observation (scientific or 
calibartion) or down-time. In case a scientific observation is carried
out, Simulator notifies ObsScheduler. Otherwise NonObsScheduler 
is notified.


Method Types
Constructor/Initializers
- __init__

Activate a Simulator instance
- start

Utility Methods
- setupSimulation
"""
from utilities import *
from LSSTObject import *
from AstronomicalSky import *
from ObsScheduler import *
from TAC import *
from Weather import *
from Instrument import *
from Filters import *
from SchedulingData import *

#class Simulator (Simulation.Process):
class Simulator(object):
    def __init__ (self, 
                  lsstDB,
		  obsProfile,
                  sessionID,
                  nRun,
                  seeingEpoch,
                  simStartDay,
                  fov,
                  idleDelay,
                  targetList,
                  maxCloud,
                  runSeeingFudge,
                  telSeeing,
                  opticalDesSeeing,
 	          cameraSeeing,
                  filtersConf,
                  schedDownConf,
                  unschedDownConf,
                  nearEarthConf,
                  weakLensConf,
                  superNovaConf,
                  superNovaSubSeqConf,
		  kuiperBeltConf,
		  WLpropConf,
                  instrumentConf,
                  schedulerConf,
		  schedulingDataConf,
                  dbTableDict,
                  log=False,
                  logfile='./Simulator.log',
                  verbose=0):
        """
        Standard initializer.
        
        lsstDB      It is the DB access object for executing SQL
        obsProfile  profile of Observatory site where:
                        latitude_RAD:   Latitude (radians) of the dome
                        longitude_RAD:  Longitude (radians) of the dome
                        height:     Meters above the sea level
                        simEpoch:   Start MJD of the simulation
        targetList: name of the file containing the list of RA, Dec 
                    and field IDs.
        sessionID:  An integer identifying this particular run.
        nRun:       Number of years to simulate
        seeingEpoch: Jan 1 of year seeing data was collected; units = MJD.
        simStartDay: day relative to seeingEpoch for simulation to commence
        fov:        Field of View (degrees) of the telescope
        idleDelay:  seconds to delay new target selection when no target 
                    available on current check
        targetList:
        runSeeingFudge:
        telSeeing:
        filtersConf:
	schedDownConf:  Scheduled downtime config file
        unschedDownConf:  Unscheduled/random downtime config file
        nearEarthConf:  Near Earth Asteroid config file
        weakLensConf:   Weak Lensing config file
        superNovaConf:  Simple Super Nova config file
        superNovaSubSeqConf: SuperNova with sub sequences config file
        instrumentConf: Instrument config file
        schedulerConf:
        dbTableDict:    DB table names
        log:        False if not set; else log = logging.getLogger("....")
        logfile:    name (and path) of the desired log file (defaults to None)
        verbose:    integer specifying the verbosity level (defaults to 0). 
                    -1=none, 0=min, 1=wordy, >1=very verbose
        """
#        Simulation.Process.__init__ (self)
        
	self.lsstDB = lsstDB        
	# Load the simulation parameters
        self.obsProfile = obsProfile    # profile of Observatory site
        self.sessionID = sessionID
        self.nRun =  nRun               # number of years to simulate
        self.seeingEpoch = seeingEpoch  # jan 1 of seeing data in MJD
        self.simStartDay = simStartDay  # day rel to seeingEpoch for sim 2 start
        self.fov = fov                  # field of view  (degrees)
        self.idleDelay = idleDelay      # wait time if no target available
        self.targetList = targetList    # pathname to target lists (ra dec id)
        self.maxCloud = maxCloud
        self.runSeeingFudge = runSeeingFudge
        self.telSeeing = telSeeing
        self.opticalDesSeeing = opticalDesSeeing
        self.cameraSeeing = cameraSeeing
        self.filtersConf = filtersConf
        self.nearEarthConf = nearEarthConf     # NEA configuration file
        self.weakLensConf = weakLensConf       # Weak Lensing configuration file
        self.superNovaConf = superNovaConf   
        self.superNovaSubSeqConf = superNovaSubSeqConf   
	self.kuiperBeltConf = kuiperBeltConf
	self.WLpropConf = WLpropConf
        self.instrumentConf = instrumentConf   # Instrument config file
        self.schedulerConf = schedulerConf
	self.schedulingDataConf = schedulingDataConf
        self.dbTableDict = dbTableDict  # dictionary of SQL table names

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up Simulator logger"
            log = logging.getLogger("Simulator")
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.INFO)
        self.log = log
        self.logfile = logfile
        self.verbose = verbose  
        
        if ( self.log ):
            self.log.info('Simulator: init(): SessionID:%s' % (sessionID))
        
        self.done = False
        (self.latitude_RAD, self.longitude_RAD, self.height, self.simEpoch,self.pressure,self.temperature,self.relHumidity) = obsProfile
        
        # Read scheduled downtime configuration file
        config_dict, pairs = readConfFile (schedDownConf)
        try:
            self.schedDownActivity = (config_dict['activity'])
        except:
            print "error reading activity in schedDownConf"

        try:
            self.schedDownStart = (config_dict['startNight'])
        except:
            print "error reading startNight in schedDownConf"

        try:
            self.schedDownDuration = (config_dict['duration'])
        except:
            print "error reading duration in schedDownConf"

        # store config to DB
        for line in pairs:
            storeParam (self.lsstDB, sessionID, 0, schedDownConf, line['index'],
                            line['key'], line['val'])

        # Read unscheduled downtime configuration file
        config_dict, pairs = readConfFile (unschedDownConf)
        try:
            self.unschedDownActivity = (config_dict['activity'])
        except:
            print "error reading activity in unschedDownConf"

        try:
            self.unschedDownStart = (config_dict['startNight'])
        except:
            print "error reading startNight in unschedDownConf"

        try:
            self.unschedDownDuration = (config_dict['duration'])
        except:
            print "error reading duration in unschedDownConf"

        # store config to DB
        for line in pairs:
            storeParam (self.lsstDB, sessionID, 0, unschedDownConf, line['index'],
                            line['key'], line['val'])

        self.setupSimulation ()

        # initialize the count of lunations - needed to track year boundaries
        self.lunationCount = 0
        # init count of nights
        self.nightCnt = -1

        #self.printDowntime()

        # prepare for TimeHistory recording
        self.timeHist = TimeHistory(lsstDB=self.lsstDB,
				    dbTableDict=self.dbTableDict,
                                    log=self.log,
                                    logfile=self.logfile,
                                    verbose=self.verbose)

        return
    
    
    def start (self):
        """
        Activate the Simulator instance and all the objects we need.
        """
        # OK, OK. This method is incredibly long. The problem is that, 
        # apparently, SimPy (and the current implementation of generators
        # in Python, I guess) do NOT allow instance methods  of the 
        # current object to be called in this method. Weird, sad but true.
        # 
        # This is why this routine is so boringly long. Apologies.

        if ( self.log and self.verbose > 1):
             self.log.info('Simulator: start()')
        
        # TAC
#        Simulation.activate (self.tac, self.tac.start (), 0.0)
        self.tac.start()
#        yield hold, self
        
        if ( self.log and self.verbose > 1):
             self.log.info("Simulator: start(): sessionID:%d " % (self.sessionID));
#        yield hold, self
#        lastEvent = now()
        lastEvent = 0

	# get next scheduled and unscheduled downtime
        if len (self.schedDownStart) != 0:
            self.nextSchedDown = self.schedDownStart.pop(0)
        else:
            self.nextSchedDown = -1

        if len (self.unschedDownStart) != 0:
            self.nextUnschedDown = self.unschedDownStart.pop(0)
        else:
            self.nextUnschedDown = -1

        # Align time to NightTime
#        t = now ()
        t = lastEvent

        # sunRise < sunSet
        # This is what is happening:
        #  <---------------DAY------------------->
        # --------|----------------------|-------------->
        #      sunRise                 sunSet          t
        (sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = self.sky.getTwilightSunriseSunset (t)
        
        # Get a hold of the telescope
#        yield request, self, self.telResource
        
        # Let the time pass, if needed
        if (t > sunRise and t < sunSet):    # Middle of the day
            #  <---------------DAY------------------->
            # -----|-------*--------------|-------------->
            #   sunRise    t            sunSet          t
            
            # Wait until night
#            yield hold, self, sunSet - t
            t = sunSet
            
            # Now:
            #  <---------------DAY------------------->
            # --------|----------------------|-----*-------->
            #      sunRise                 sunSet  t       t

	    tonightSunsetTwil = sunSetTwil            
            # Update sunRise, sunSet to reflect the values for tomorrow
            (sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = self.sky.getTwilightSunriseSunset (t + DAY)

        elif (t >= sunSet):                 # Next night
            #  <---------------DAY------------------->
            # --------|----------------------|-----*-------->
            #      sunRise                 sunSet  t       t
            
            tonightSunsetTwil = sunSetTwil
            # Update sunRise, sunSet to reflect the values for tomorrow
            (sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = self.sky.getTwilightSunriseSunset (t + DAY)
            
            # No need to block
#            yield hold, self, 0
        elif (t <= sunRise):                # Previous night
            #  <---------------DAY------------------->
            # --*-----|----------------------|-------------->
            #   t  sunRise                 sunSet         t

            ## LD: need to check if we're before previous day's sunset.  
            #  <---------------DAY------------------->
            # --*-----|----------------------|------------->
            #   t  sunSet                  sunRise        t
            yesterday_sunRise,yesterday_sunSet,yesterday_sunRiseMJD,yesterday_sunSetMJD, yesterday_sunRiseTwil,yesterday_sunSetTwil = \
                self.sky.getTwilightSunriseSunset(t - DAY)

            tonightSunsetTwil = yesterday_sunSetTwil
            # Adjust sunset to yesterday's (the next) sunset.
            # Leave sunrise as the next sunrise.
            if t < yesterday_sunSet:
#                yield hold, self, t - yesterday_sunSet
                t = yesterday_sunSet
            
            # No need to block
#            yield hold, self, 0
        
        # Release the telescope
#        yield release, self, self.telResource

        # OK, now sunRise and sunSet are the NEXT 
        # Sun rise and set times: simTime:t is marching towards sunRise.

#        t = now()
	midnight = (tonightSunsetTwil + sunRiseTwil)/2        
        self.initMoonPhase(midnight) 

        
        # Start Scheduling - while more nights
#        while (not self.done):
        while (t < self.nRun*YEAR):
	    self.twilightProfile = (sunRiseTwil, tonightSunsetTwil)
             
            #print "nightCnt = %d nextSchedDown = %d nextUnschedDown = %d" % (self.nightCnt, self.nextSchedDown, self.nextUnschedDown)

            # Is there scheduled or unscheduled downtime? Process block.
            if (self.nightCnt == self.nextSchedDown) or (self.nightCnt == self.nextUnschedDown): 
                if self.nightCnt == self.nextSchedDown:
                    daysDown = self.schedDownDuration.pop(0)
                    activityDown = self.schedDownActivity.pop(0)
                    schedDown = True
                else:
                    daysDown = self.unschedDownDuration.pop(0)
                    activityDown = self.unschedDownActivity.pop(0)
                    schedDown = False
                    #print "Simulator: doing unscheduled downtime"

                startDownTime = t
                startDownNight = self.nightCnt
                duration = 0
                cloudiness = self.weather.getTransparency(t)
                while daysDown > 0:

                    # start night and hold telescope until end of night
                    self.startNight (t, midnight, sunRise)
#                    yield request, self, self.telResource
#                    yield hold, self, sunRise - t
                    t = sunRise
#                    yield release, self, self.telResource
                    duration += sunRise - t
                    self.startDay (sunRise)
#                    t = now ()

                    # Hold telescope until beginning of new night
#                    yield request, self, self.telResource
#                    yield hold, self, sunSet - t
                    t = sunSet
#                    yield release, self, self.telResource
#                    t = now()
                    self.log.info ('Simulator: start(): t = %d (should be sunSet)' % t)
                    # Update sunRise and sunSet for next night
                    tonightSunsetTwil = sunSetTwil
                    self.log.info( "Simulator: time:%d floor sunSetMJD:%f floor sunRiseMJD:%f" % (t,math.floor(sunSetMJD),math.floor(sunRiseMJD)))
                    if ( math.floor(sunSetMJD) != math.floor(sunRiseMJD)):
                        (sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = self.sky.getTwilightSunriseSunset (t)
                    else:
                        (sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = self.sky.getTwilightSunriseSunset (t + DAY)
                    midnight = (tonightSunsetTwil + sunRiseTwil)/2
                    self.log.info ('Simulator: start(): t = %d (should be sunRise) sunSet = %d downtime_days = %d' % (t, sunSet, daysDown-1))
	            self.twilightProfile = (sunRiseTwil, tonightSunsetTwil)

                    daysDown -= 1
        
                # record entire downtime in one DB entry
                        #sql = 'INSERT INTO %s VALUES (NULL, %d, "%s", %d, %d, %d, %d, %d, %f, "%s")' % (self.dbTableDict['downHist'], 
                #  self.sessionID, activityDown, duration, startDownTime, t, startDownNight, self.nightCnt, cloudiness, schedDown)
            #(n, dummy) = self.lsstDB.executeSQL (sql)
            # This has been commented out for discussion with Francisco 
            
                if schedDown:
                    # get next scheduled downtime starttime
                    if len (self.schedDownStart) != 0:
                        self.nextSchedDown = self.schedDownStart.pop(0)
                    else:
                        self.nextSchedDown = -1
                else:
                    # get next unscheduled downtime starttime
                    if len (self.unschedDownStart) != 0:
                        self.nextUnschedDown = self.unschedDownStart.pop(0)
                    else:
                        self.nextUnschedDown = -1
                
                #self.printDowntime()

                # overlapping downtimes?
                while self.nextSchedDown != -1 and self.nextSchedDown < self.nightCnt:
                    # If we totally missed it, delete entries. Else finish it.
                    if self.nextSchedDown + self.schedDownDuration[0] <= self.nightCnt:
                        del self.schedDownActivity[0]
                        del self.schedDownDuration[0]
                        self.log.info ('Overlapping scheduled downtime specified: totally missed')
                        # get next scheduled downtime starttime
                        if len (self.schedDownStart) != 0:
                            self.nextSchedDown = self.schedDownStart.pop(0)
                        else:
                            self.nextSchedDown = -1

                    else:
                        partialDown = self.nextSchedDown+self.schedDownDuration[0] -self.nightCnt
                        self.schedDownDuration[0] = partialDown
                        self.nextSchedDown = self.nightCnt
                        self.log.info ('Overlapping scheduled downtime specified: partial = %d' % partialDown)

                while self.nextUnschedDown != -1 and self.nextUnschedDown < self.nightCnt:
                    # If we totally missed it, delete entries. Else finish it.
                    if self.nextUnschedDown + self.unschedDownDuration[0] <= self.nightCnt:
                        del self.unschedDownActivity[0]
                        del self.unschedDownDuration[0]
                        self.log.info ('Overlapping unscheduled downtime specified: totally missed')
                        # get next unscheduled downtime starttime
                        if len (self.unschedDownStart) != 0:
                            self.nextUnschedDown = self.unschedDownStart.pop(0)
                        else:
                            self.nextUnschedDown = -1
                    else:
                        partialDown = self.nextUnschedDown+self.unschedDownDuration[0] -self.nightCnt
                        self.unschedDownDuration[0] = partialDown
                        self.nextUnschedDown = self.nightCnt
                        self.log.info ('Overlapping unscheduled downtime specified: partial = %d' % partialDown)
        
            # regular observing
            else:
                self.startNight (t, midnight, sunRise)
                self.weather.getNightClouds (t, sunRise)
                self.weather.getNightSeeing (t, sunRise)
                self.sky.flushCache()

                # still night
                while (t < sunRise):
                    # Too cloudy to observe?
                    cloudiness = self.weather.getTransparency(t)
                    if cloudiness > self.maxCloud:
                        if self.log:
                            self.log.info("Simulator: Cloudy above %0.3f (date:%d), skip time slice" % (self.maxCloud, t))
                        self.telescope.Park ()
#                        yield hold, self, self.idleDelay
                        t = t + self.idleDelay

                        eventTime = self.idleDelay
#                        sql = 'INSERT INTO %s VALUES (NULL, %d, "%s", %d, %d, \
#                              %d, %d, %d, %f, "%s")' %  \
#                              (self.dbTableDict['downHist'], 
#                              self.sessionID, 'cloudy', eventTime, 
##                              t, now(), self.nightCnt, self.nightCnt,
#                              t-self.idleDelay, t, self.nightCnt, self.nightCnt,
#                              cloudiness, 'False')
#                        (n, dummy) = self.lsstDB.executeSQL (sql)

                    # Observe next field
                    else:
                        self.dateProfile = self.sky.computeDateProfile(t)
#                        (oRank, oExp, oSlew) = \
                        winner_obs = self.obsScheduler.suggestObservation (self.dateProfile,
                                        self.moonProfile, self.twilightProfile,
                                        cloudiness)
			if (winner_obs != None):
			    oRank = winner_obs.finRank
			    oExp  = winner_obs.exposureTime
			    oSlew = winner_obs.slewTime
                            oTime = oExp + oSlew
            		else:
			    oRank = 0
                        # Request telescope resource (semaphore)
#                        yield request, self, self.telResource
           
                        if oRank != 0:
#                            yield hold, self, oTime
                            t = t + oTime
#                            idle = now() - lastEvent - oTime
                            idle = t - lastEvent - oTime
                            eventTime = oTime
                            self.obsScheduler.closeObservation(winner_obs)
                            if ( self.log ) :
                                self.log.info ('Simulator: observing: last event: %d; idle %d sec; slew %d sec; expose %d sec' % (t, idle, oSlew,oExp))
                        else:
#                            yield hold, self, self.idleDelay
                            t = t + self.idleDelay
                            eventTime = self.idleDelay
            
                        # Release the telescope
#                        yield release, self, self.telResource

#                    t = now()

                    # Check for end of sunrise/start of darktime - MM
                    if (t >tonightSunsetTwil) and (lastEvent <tonightSunsetTwil):
                        self.dateProfile = self.sky.computeDateProfile(tonightSunsetTwil)
			(date, MJD, lst_RAD) = self.dateProfile
			self.lsstDB.addTimeHistory(self.sessionID, date, MJD, self.nightCnt, END_DUSK)
#                        self.timeHist.add (self.sessionID, self.nightCnt,
#                                   self.dateProfile, END_DUSK)
                        self.obsScheduler.flushSkyCache()

                    # Check for dawn - MM
                    elif (t > sunRiseTwil) and (lastEvent < sunRiseTwil):
                        self.dateProfile = self.sky.computeDateProfile(sunRiseTwil)
                        (date, MJD, lst_RAD) = self.dateProfile
                        self.lsstDB.addTimeHistory(self.sessionID, date, MJD, self.nightCnt, START_DAWN)
#                        self.timeHist.add (self.sessionID, self.nightCnt,
#                                   self.dateProfile, START_DAWN)
                        self.obsScheduler.flushSkyCache()

                    # end if
                    lastEvent = t   

                # End of night while loop: park the telescope
                self.telescope.Park ()

                # Record sunrise time, not end of last exposure - MM
		self.startDay (sunRise)
                
                # Get a hold of the telescope
 #               yield request, self, self.telResource
                
                # Wait until night
 #               yield hold, self, sunSet - t
                t = sunSet
                
                # Release the telescope
#                yield release, self, self.telResource
                
#                t = now ()
                # Update tonight's sunset to new night
                tonightSunsetTwil = sunSetTwil

                # Update sunRise and sunSet (sunset is next day's)
		self.log.info( "Simulator: time:%d floor sunSetMJD:%f floor sunRiseMJD:%f" % (t,math.floor(sunSetMJD),math.floor(sunRiseMJD)))
		if (math.floor(sunSetMJD) != math.floor(sunRiseMJD)):
                    (sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = self.sky.getTwilightSunriseSunset (t)
		else:
                    (sunRise,sunSet,sunRiseMJD,sunSetMJD, sunRiseTwil,sunSetTwil) = self.sky.getTwilightSunriseSunset (t + DAY)

		midnight = (tonightSunsetTwil + sunRiseTwil)/2
                
        return

    def initMoonPhase(self, date):
        """
        Initialize moon phase flags

        Input
            date        elapsed simulation time in seconds

        Output
            none
        """
        # First need to determine if moon is waxing or waning
        (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = self.obsProfile
        mjd = (float (date) / float (DAY)) + epoch_MJD
        previousDayPhase = self.sky.getMoonPhase(mjd-1)
        currentPhase = self.sky.getMoonPhase(mjd)
        nextDayPhase = self.sky.getMoonPhase(mjd+1)

        if (previousDayPhase <= currentPhase) :
                self.moonTrendToFull = True
        else:   # previousDayPhase >= currentPhase
                self.moonTrendToFull = False
        print "MoonPhasing: past:%f present:%f future:%f trendtoFull:%s" % (previousDayPhase,currentPhase,nextDayPhase,self.moonTrendToFull)

        self.lastNightPhase = previousDayPhase
        return

#    def computeMoonProfile(self, date):
#        """
#        Precompute quantities relating to the moon used by subsequent routines

#        Input
#            dateProfile:    an array containing
#                date
#                mjd
#                lst_RAD
#        Output
#            moonProfile:    an array containing
#                moonRA_RAD
#                moonDec_RAD
#                moonPhase_PERCENT
#        """
#        (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = self.obsProfile
#        mjd = (float (date) / float (DAY)) + epoch_MJD

        # Get the Moon RA/Dec  in radians
#        (moonRA_RAD,moonDec_RAD,moonDiam) =  slalib.sla_rdplan(mjd,
#                                                    3,
#                                                    lon_RAD,
#                                                    lat_RAD)
#        moonPhase_PERCENT = self.sky.getMoonPhase(mjd)

#        return(moonRA_RAD,moonDec_RAD,moonPhase_PERCENT)


    def startNight (self, date, midnight, sunRise):
        """
        Perform any necessary setup for the start of the night.
        
        Input
            date    elapsed simulation time
        
        Return
            None
        """
        if (self.log and self.verbose > 1) :
            self.log.info("Simulator:startNight")

        self.nightCnt += 1

        # compute the moonProfile and dateProfile for the current simdate
        self.dateProfile = self.sky.computeDateProfile(date)
        (date, MJD, lst_RAD) = self.dateProfile

        self.moonProfile = self.sky.computeMoonProfile(midnight)
        (moonRA_RAD, moonDec_RAD, moonPhase_PERCENT) = self.moonProfile

        # Determine if new lunation indicated by change in moon phase trend
        startNewYear = False
        startNewLunation = False
        if self.moonTrendToFull == True:  # i.e. previous moon was waxing
            if self.lastNightPhase > moonPhase_PERCENT :
                startNewLunation = True
                # record Moon event
                self.lsstDB.addTimeHistory(self.sessionID, date, MJD, self.nightCnt, MOON_WANING)
#                self.timeHist.add (self.sessionID, self.nightCnt,
#                                   self.dateProfile, MOON_WANING)
                if self.lunationCount > 0 and self.lunationCount % 12 == 0:
                    startNewYear = True
                    # record new year event
                    self.lsstDB.addTimeHistory(self.sessionID, date, MJD, self.nightCnt, NEW_YEAR)
#                    self.timeHist.add (self.sessionID, self.nightCnt, 
#		                       self.dateProfile, NEW_YEAR)
                self.lunationCount += 1
                self.moonTrendToFull = False
                self.log.info( "New Lunation: Moon phase switching to waning: date:%d lastphase:%f newphase:%f startNewLunation:%d" %(date,self.lastNightPhase,moonPhase_PERCENT,startNewLunation))
        else: # moonTrendToFull is False i.e. previous moon was waning 
            if moonPhase_PERCENT > self.lastNightPhase :
                self.moonTrendToFull = True
                # record moon event
                self.lsstDB.addTimeHistory(self.sessionID, date, MJD, self.nightCnt, MOON_WAXING)
#                self.timeHist.add (self.sessionID, self.nightCnt, 
#                                   self.dateProfile, MOON_WAXING)
                self.log.info("Moon phase switching to waxing: date:%d lastphase:%f newphase:%f startNewLunation:%d" %(date,self.lastNightPhase,moonPhase_PERCENT,startNewLunation))
        self.lastNightPhase = moonPhase_PERCENT

        # record PassingOfTime events
        self.lsstDB.addTimeHistory(self.sessionID, date, MJD, self.nightCnt, START_NIGHT)
#        self.timeHist.add (self.sessionID, self.nightCnt, self.dateProfile,
#			   START_NIGHT)

        # Finally:  let ObsScheduler know about the startNight
        self.obsScheduler.startNight(self.dateProfile,self.moonProfile, 
                                     startNewLunation, startNewYear, 
                                     self.fov, self.nRun, self.nightCnt)

        (sunRiseTwil, tonightSunsetTwil) = self.twilightProfile
        if self.log:
#            self.log.info ('Simulator: NightStart=%d t=%d tonightSunsetTwil=%d Midnight=%d sunRiseTwil=%d sunRise=%d' % (now(), date, tonightSunsetTwil, midnight, sunRiseTwil, sunRise))
            self.log.info ('Simulator: NightStart t=%d tonightSunsetTwil=%d Midnight=%d sunRiseTwil=%d sunRise=%d' % (date, tonightSunsetTwil, midnight, sunRiseTwil, sunRise))

        return

    def startDay(self, date):
	"""
	Perform any necessary setup for the end of the night,
	triggering filters swap for now.
	"""
        self.dateProfile = self.sky.computeDateProfile(date)
        (date, MJD, lst_RAD) = self.dateProfile
        self.lsstDB.addTimeHistory(self.sessionID, date, MJD, self.nightCnt, END_NIGHT)
#        self.timeHist.add (self.sessionID, self.nightCnt, self.dateProfile,
#                           END_NIGHT)
        
        self.moonProfile = self.sky.computeMoonProfile(date)
	self.obsScheduler.startDay(self.moonProfile)

	return
    
    def setupSimulation (self):
        """
        Utility method to create all the needed objects.
        """
        if ( self.log and self.verbose > 1):
             self.log.info('Simulator: setupSimulation(): instConf:%s ' % (self.instrumentConf))
        
        # Instantiate the Instrument class
        self.telescope = Instrument (lsstDB=self.lsstDB,
				sessionID=self.sessionID,
                                dbTableDict=self.dbTableDict,
                                obsProfile=self.obsProfile,
                                instrumentConf=self.instrumentConf,
                                log=self.log,
                                logfile=self.logfile,
                                verbose=self.verbose)
        self.telescope.Park ()
        
        # Init the Filters class
        self.filters = Filters ( lsstDB=self.lsstDB,
				filtersConf=self.filtersConf,
                                sessionID=self.sessionID,
                                dbTableDict=self.dbTableDict,
                                telSeeing=self.telSeeing,
                                #telSeeing,
                                opticalDesSeeing=self.opticalDesSeeing,
                                cameraSeeing=self.cameraSeeing,
                                log=self.log,
                                logfile=self.logfile,
                                verbose=self.verbose)
        
        # Init the Astronomical Sky
        self.sky = AstronomicalSky (lsstDB=self.lsstDB,
			            obsProfile=self.obsProfile, 
                                    date=0., 
                                    sessionID=self.sessionID,
                                    dbTableDict=self.dbTableDict,
                                    log=self.log,
                                    logfile=self.logfile,
                                    verbose=self.verbose)
        
        self.schedulingData = SchedulingData(self.schedulingDataConf,
                                                0,
                                                self.nRun*YEAR,
						self.sky,
						self.lsstDB,
						self.sessionID)

        # Init the Weather Simulator
        self.weather = Weather (lsstDB=self.lsstDB,
				date=0., 
                                dbTableDict=self.dbTableDict,
                                seeingEpoch=self.seeingEpoch,
                                simStartDay=self.simStartDay,
                                log=self.log,
                                logfile=self.logfile,
                                verbose=self.verbose)
        
        # Define the telescope as a Resource with a priority queue.
#        self.telResource = Simulation.Resource ()
        
        # We also need a Obs Scheduler
        self.obsScheduler = ObsScheduler (lsstDB=self.lsstDB,
				schedulingData=self.schedulingData,
				obsProfile=self.obsProfile,
                                dbTableDict=self.dbTableDict,
                                telescope=self.telescope,
                                weather=self.weather,
                                sky=self.sky, 
                                filters=self.filters, 
                                sessionID=self.sessionID,
                                runSeeingFudge=self.runSeeingFudge,
                                schedulerConf=self.schedulerConf,
                                log=self.log,
                                logfile=self.logfile,
                                verbose=self.verbose)
        
        # Create a TAC object and activate it.
        self.tac = TAC (lsstDB=self.lsstDB,
			nRun=self.nRun,
			schedulingData=self.schedulingData,
                        sky=self.sky, 
                        weather=self.weather, 
                        obsScheduler=self.obsScheduler,
                        sessionID=self.sessionID,
                        fov=self.fov,
                        filters=self.filters,
                        nearEarthConf=self.nearEarthConf,
                        weakLensConf=self.weakLensConf,
                        superNovaConf=self.superNovaConf,
                        superNovaSubSeqConf=self.superNovaSubSeqConf,
			kuiperBeltConf=self.kuiperBeltConf,
			WLpropConf=self.WLpropConf,
                        targetList=self.targetList, 
                        dbTableDict=self.dbTableDict,
                        log=self.log,
                        logfile=self.logfile,
                        verbose=self.verbose)
        return

    def closeProposals(self, time):
	self.obsScheduler.closeProposals(time)
	return

    def printDowntime(self):
        print "schedDownStart:"
        print self.schedDownStart
        print "schedDownActivity:"
        print self.schedDownActivity
        print "schedDownDuration:"
        print self.schedDownDuration
        print "unschedDownStart:"
        print self.unschedDownStart
        print "unschedDownActivity:"
        print self.unschedDownActivity
        print "unschedDownDuration:"
        print self.unschedDownDuration
