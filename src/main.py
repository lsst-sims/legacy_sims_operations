#!/usr/bin/env python
#try:
#    import psyco
#    psyco.full()
#except:
#    pass

OPSIM_VERSION = '3.0'

from utilities import *
from Simulator import *
#from LSSTDatabase import *
from Database import *
import binascii

import urllib

# globals
USAGE_STR = '[--profile=yes] [--verbose=yes] [--config=../survey/LSST.conf] [--startup_comment="comment"]'

def getSessionID (lsstDB, sessionTbl, code_test, startup_comment):
    """
    Create an entry in the the Session table and fetch the key which
    have been assigned to us.
    
    Input
    sessionTbl     name of DB Session Table
    
    Return
    SessionID
    
    Raise
    Exception if there are errors in the SQL.
    """
    # Get the short hostname
    host = socket.gethostname ().split ('.', 1)[0]
    user = os.environ['USER']
    (yy, mm, dd, h, m, s, wday, yday, dst) = time.gmtime ()
    date = '%d-%d-%d %02d:%02d:%02d' % (yy, mm, dd, h, m, s)
    
    # Remove data from the previous run where user, host and date are
    # the same. This would only happen is the same user restarts the 
    # simulatiomn on the same machine within a second...

#    sql = 'DELETE FROM %s WHERE ' % (sessionTbl)
#    sql += 'sessionUser="%s" AND ' % (user)
#    sql += 'sessionHost="%s" AND ' % (host)
#    sql += 'sessionDate="%s"' % (date)
#    (n, dummy) = lsstDB.executeSQL (sql)
#    
#    # Create a new entry
#    sql = 'INSERT INTO %s VALUES (NULL, '  % (sessionTbl)
#    sql += '"%s", ' % (user)
#    sql += '"%s", ' % (host)
#    sql += '"%s",' % (date)
#    sql += '"%s",' % (OPSIM_VERSION)
#    sql += '"%s")' % (startup_comment)
#    (n, dummy) = lsstDB.executeSQL (sql)
#    
#    # Now fetch the assigned sessionID 
#    sql = 'SELECT sessionID FROM %s WHERE '  % (sessionTbl)
#    sql += 'sessionUser="%s" AND ' % (user)
#    sql += 'sessionHost="%s" AND ' % (host)
#    sql += 'sessionDate="%s"' % (date)
#    (n, res) = lsstDB.executeSQL (sql)
#    sessionID = res[0][0]
    
    oSession = lsstDB.newSession(user, host, date, OPSIM_VERSION, startup_comment)
    sessionID = oSession.sessionID
    
    # the last argument = 1 is the status_id 
    try:
    	track(sessionID, host, user, startup_comment, code_test, 1.0)
    except:
	print ("Unable to contact opsimcvs : Server might be down.")
    # Return the newly found sessionID
    return (sessionID)


def track(sessionID, hostname, user, startup_comment, code_test, status_id):
	url = "http://opsimcvs.tuc.noao.edu/tracking/tracking.php";
	params = urllib.urlencode({'sessionID': sessionID,
                               'hostname': hostname,
                               'user': user,
                               'startup_comment': startup_comment,
                               'code_test': code_test,
                               'status_id': status_id,
                               'run_version': OPSIM_VERSION})
	url = "%s?%s" % (url, params);
	result = urllib.urlopen(url).read();
	print("    Tracking:%s" % (result))


def startLsst( args ):
    """
    Begin LSST telescope observing simulation.

    Command line input
        [--verbose=yes] 
        
        [--config=./LSST.conf]'

        [--profile=yes]

	[--startup_comment="blah"]
    
    Return
        None
    
    Raise
        exit if there are errors 
    """
    # Instantiate DB Object
    # lsstDB = LSSTDatabase()
    lsstDB = Database()

    # Startup comment
    if (args.has_key ('startup_comment')):
	startup_comment = args['startup_comment'];
    else:
	startup_comment = "No comment was entered";

    # Verbose?
    if (args.has_key ('verbose') and 
        args['verbose'].lower () == 'yes'):
        VERBOSE = 1
    else:
        VERBOSE = 0

    # Alternate configuration file?
    if (args.has_key ('config') ):
        confLSST = args['config']
    else:
        confLSST = DefaultLSSTConfigFile

    # Fetch the DB table names so Session DB can be accessed immediately
    configDict, pairs =  readConfFile(confLSST)

    if ( configDict.has_key ('sessionTbl')) :
        sessionTbl =  configDict["sessionTbl"]
        print("    sessionTbl:%s" % (sessionTbl))
    else :
        sessionTbl =  "Session"
        print("    sessionTbl:%s default" % (sessionTbl))

    # Get whether this is a code test
    if ( configDict.has_key ('code_test')) :
    	code_test = configDict['code_test']
    	print("    code_test:%s" % (code_test))
    else :
    	code_test = '1'
    	print("    code_test:%s" % (code_test))
    # Get a Session ID
    try:
        SID = getSessionID (lsstDB, sessionTbl, code_test, startup_comment)
    except:
        fatalError ('Unable to acquire a Session ID. Please check ',
                    'that the DB is up and running on the localhost.')
    
    print ('Session ID: %d' % (SID))

    # store config in DB
    for line in pairs:
        storeParam (lsstDB, SID, 0, 'LSST', line['index'], line['key'], line['val'])

    # Overlay the user's simulation parameters
    print ("Overarching user-defined parameters")

    if ( configDict.has_key ('nRun')) :
        nRun =  configDict["nRun"]
        print("    nRun:%f" % (nRun))
    else :
        nRun =  1.
        print("    nRun:%f default" % (nRun))

    if ( configDict.has_key ('fov')) :
        fov =  configDict["fov"]
        print("    fov:%f" % (fov))
    else :
        fov =  3.5
        print("    fov:%f default" %(fov) )

    if ( configDict.has_key ('idleDelay')) :
        idleDelay =  configDict["idleDelay"]
        print("    idleDelay:%f" % (idleDelay))
    else :
        idleDelay =  30
        print("    idleDelay:%f default" %(idleDelay) )

    if ( configDict.has_key ('simStartDay')) :
        simStartDay =  configDict["simStartDay"]
        print("    simStartDay:%f" % (simStartDay))
    else :
        simStartDay = 0.5
        print("    simStartDay:%f default: 0.5" % (simStartDay))

    if ( configDict.has_key ('targetList')) :
        targetList =  configDict["targetList"]
        print("    targetList: %s" % (targetList))
    else:
        targetList =  './Targets.txt'
        print("    targetList:%s default" % (targetList ))

    if ( configDict.has_key ('maxCloud')) :
        maxCloud =  configDict["maxCloud"]
        print("    maxCloud: %f" % (maxCloud))
    else:
        maxCloud = 0.7
        print("    maxCloud: %f default" % (maxCloud))

    if ( configDict.has_key ('telSeeing')) :
        telSeeing =  configDict["telSeeing"]
        print("    telSeeing:%f" % (telSeeing))
    else :
        print "telSeeing has no setting"
        sys.exit (1)
    
    if ( configDict.has_key ('opticalDesSeeing')) :
        opticalDesSeeing =  configDict["opticalDesSeeing"]
        print("    opticalDesSeeing:%f" % (opticalDesSeeing))
    else:
        print "opticalDesSeeing has no setting - exiting"
        sys.exit (1)

    if ( configDict.has_key ('cameraSeeing')) :
        cameraSeeing =  configDict["cameraSeeing"]
        print("    cameraSeeing:%f" % (cameraSeeing))
    else:
        print "cameraSeeing has no setting - exiting"
        sys.exit (1)

    if ( configDict.has_key ('filtersConf')) :
        filtersConf =  configDict["filtersConf"]
        print("    filtersConf:%s" % (filtersConf))
    else :
        filtersConf = DefaultFiltersConfigFile
        print("    filtersConf:%s default" % (filtersConf))
    
    if ( configDict.has_key ('schedulerConf')) :
        schedulerConf =  configDict["schedulerConf"]
        print("    schedulerConf:%s" % (schedulerConf))
    else :
        schedulerConf = DefaultSchedulerConfigFile
        print("    schedulerConf:%s default" % (schedulerConf))

    if ( configDict.has_key ('schedulingDataConf')) :
        schedulingDataConf =  configDict["schedulingDataConf"]
        print("    schedulindDataConf:%s" % (schedulingDataConf))
    else :
        schedulingDataConf = DefaultSchedulingDataConfigFile
        print("    schedulingDataConf:%s default" % (schedulingDataConf))

    if ( configDict.has_key ('schedDownConf')) :
        schedDownConf =  configDict["schedDownConf"]
        print("    schedDownConf:%s" % (schedDownConf ))
    else :
        print "schedDownConf has no setting"

    if ( configDict.has_key ('unschedDownConf')) :
        unschedDownConf =  configDict["unschedDownConf"]
        print("    unschedDownConf:%s" % (unschedDownConf ))
    else :
        print "unschedDownConf has no setting"

    if ( configDict.has_key ('instrumentConf')) :
        instrumentConf =  configDict["instrumentConf"]
        print("    instrumentConf:%s" % (instrumentConf))
    else :
        instrumentConf =  DefaultInstrumentConfigFile
        print("    instrumentConf:%s default" % (instrumentConf))

    if ( configDict.has_key ('weakLensConf')) :
        weakLensConf =  configDict["weakLensConf"]
        print("    weakLensConf:%s" % (weakLensConf))
    else :
        weakLensConf =  None
        print("    weakLensConf:%s default" % (weakLensConf))

    if (not isinstance(weakLensConf,list)):
        # turn it into a list with one entry
        weakLensConf = [weakLensConf]

    if ( configDict.has_key ('WLpropConf')) :
        WLpropConf =  configDict["WLpropConf"]
        print("    WLpropConf:%s" % (WLpropConf))
    else :
        WLpropConf =  None
        print("    WLpropConf:%s default" % (WLpropConf))
    if (not isinstance(WLpropConf,list)):
        # turn it into a list with one entry
        saveConf = WLpropConf
        WLpropConf = []
        WLpropConf.append(saveConf)

    if ( configDict.has_key ('nearEarthConf')) :
        nearEarthConf =  configDict["nearEarthConf"]
        print("    nearEarthConf:%s" % (nearEarthConf))
    else :
        nearEarthConf =  None
        print("    nearEarthConf:%s default" % (nearEarthConf))

    if ( not isinstance(nearEarthConf,list)):
        # turn it into a list with one entry
        saveConf = nearEarthConf
        nearEarthConf = []
        nearEarthConf.append(saveConf)

    if ( configDict.has_key ('superNovaConf')) :
        superNovaConf =  configDict["superNovaConf"]
        print("    superNovaConf:%s" % (superNovaConf))
    else :
        superNovaConf =  None
        print("    superNovaConf:%s default" % (superNovaConf))

    if (not isinstance(superNovaConf,list)):
        # turn it into a list with one entry
        saveConf = superNovaConf
        superNovaConf = []
        superNovaConf.append(saveConf)

    if ( configDict.has_key ('superNovaSubSeqConf')) :
        superNovaSubSeqConf =  configDict["superNovaSubSeqConf"]
        print("    superNovaSubSeqConf:%s" % (superNovaSubSeqConf))
    else :
        superNovaSubSeqConf =  None
        print("    superNovaSubSeqConf:%s default" % (superNovaSubSeqConf))

    if (not isinstance(superNovaSubSeqConf,list)):
        # turn it into a list with one entry
        saveConf = superNovaSubSeqConf
        superNovaSubSeqConf = []
        superNovaSubSeqConf.append(saveConf)

    if ( configDict.has_key ('kuiperBeltConf')) :
        kuiperBeltConf =  configDict["kuiperBeltConf"]
        print("    kuiperBeltConf:%s" % (kuiperBeltConf))
    else :
        kuiperBeltConf =  None
        print("    kuiperBeltConf:%s default" % (kuiperBeltConf))

    if (not isinstance(kuiperBeltConf,list)):
        # turn it into a list with one entry
        saveConf = kuiperBeltConf
        kuiperBeltConf = []
        kuiperBeltConf.append(saveConf)

    if ( configDict.has_key ('logfile')) :
        logfile =  configDict["logfile"]
        print("    logfile:%s" % (logfile))
    else :
        logfile =  '../log/lsst.log_%s' % (SID)
        print("    logfile:%s default" % (logfile))

    if ( configDict.has_key ('verbose')) :
        verbose =  configDict["verbose"]
        print("    verbose:%d" % (verbose))
    else :
        verbose =  0
        print("    verbose:%d default" % (verbose))

    if ( configDict.has_key ('downHistTbl')) :
        downHistTbl =  configDict["downHistTbl"]
        print("    downHistTbl:%s" % (downHistTbl))
    else :
        downHistTbl =  "DownHist"
        print("    downHistTbl:%s default" % (downHistTbl))

    if ( configDict.has_key ('obsHistTbl')) :
        obsHistTbl =  configDict["obsHistTbl"]
        print("    obsHistTbl:%s" % (obsHistTbl))
    else :
        obsHistTbl =  "ObsHistory"
        print("    obsHistTbl:%s default" % (obsHistTbl))

    if ( configDict.has_key ('timeHistTbl')) :
        timeHistTbl =  configDict["timeHistTbl"]
        print("    timeHistTbl:%s" % (timeHistTbl))
    else :
        timeHistTbl =  "TimeHistory"
        print("    timeHistTbl:%s default" % (timeHistTbl))

    if ( configDict.has_key ('proposalTbl')) :
        proposalTbl =  configDict["proposalTbl"]
        print("    proposalTbl:%s" % (proposalTbl))
    else :
        proposalTbl =  "Proposal"
        print("    proposalTbl:%s default" % (proposalTbl))

    if ( configDict.has_key ('seqHistoryTbl')) :
        seqHistoryTbl =  configDict["seqHistoryTbl"]
        print("    seqHistoryTbl:%s" % (seqHistoryTbl))
    else :
        seqHistoryTbl =  "SeqHistory"
        print("    seqHistoryTbl:%s default" % (seqHistoryTbl))

    if ( configDict.has_key ('fieldTbl')) :
        fieldTbl =  configDict["fieldTbl"]
        print("    fieldTbl:%s" % (fieldTbl))
    else :
        fieldTbl =  "Field"
        print("    fieldTbl:%s default" % (fieldTbl))

    if ( configDict.has_key ('userRegionTbl')) :
        userRegionTbl =  configDict["userRegionTbl"]
        print("    userRegionTbl:%s" % (userRegionTbl))
    else :
        userRegionTbl =  "UserRegion"
        print("    userRegionTbl:%s default" % (userRegionTbl))

    if ( configDict.has_key ('siteConf')) :
        siteConf =  configDict["siteConf"]
        print("    siteConf:%s" % (siteConf))
    else :
        siteConf =  "./SiteCP.conf"
        print("    siteConf:%s default" % (siteConf))


    # Fetch Site Specific Configuration file
    configDict, pairs =  readConfFile(siteConf)

    # store config in DB
    for line in pairs:
        storeParam (lsstDB, SID, 0, 'site', line['index'], line['key'], line['val'])

    if ( configDict.has_key ('seeingEpoch')) :
        seeingEpoch =  configDict["seeingEpoch"]
        print("    seeingEpoch:%f" % (seeingEpoch))
    else :
        seeingEpoch =  49353.
        print("    seeingEpoch:%f default: 1994-01-01T00:00:00.0" % (seeingEpoch))

    if ( configDict.has_key ('latitude')) :
        latitude =  configDict["latitude"]
        print("    latitude:%f" % (latitude))
    else :
        latitude =  -30.16527778
        print("    latitude:%f default (CTIO)" % (latitude) )

    if ( configDict.has_key ('longitude')) :
        longitude =  configDict["longitude" ]
        print("    longitude:%f" % (longitude))
    else :
        longitude =  -70.815
        print("    longitude:%f default (CTIO)" % (longitude))

    if ( configDict.has_key ('height')) :
        height =  configDict["height"]
        print("    height:%f " % (height))
    else :
        height =  2215.
        print("    height:%f default (CTIO)" % (height))

    if ( configDict.has_key ('pressure')) :
        pressure =  configDict["pressure"]
        print("    pressure:%f " % (pressure))
    else :
        pressure =  1010.
        print("    pressure:%f default (CTIO)" % (pressure))

    if ( configDict.has_key ('temperature')) :
        temperature =  configDict["temperature"]
        print("    temperature:%f " % (temperature))
    else :
        temperature =  12.
        print("    temperature:%f default (CTIO)" % (temperature))

    if ( configDict.has_key ('relativeHumidity')) :
        relativeHumidity =  configDict["relativeHumidity"]
        print("    relativeHumidity:%f " % (relativeHumidity))
    else :
        relativeHumidity =  0.
        print("    relativeHumidity:%f default (CTIO)" % (relativeHumidity))

    if ( configDict.has_key ('weatherSeeingFudge')) :
        weatherSeeingFudge =  configDict["weatherSeeingFudge"]
        print("    weatherSeeingFudge:%f" % (weatherSeeingFudge))
    else :
        weatherSeeingFudge =  1.
        print("    weatherSeeingFudge:%f default" % (weatherSeeingFudge))
    
    if ( configDict.has_key ('seeingTbl')) :
        seeingTbl =  configDict["seeingTbl"]
        print("    seeingTbl:%s" % (seeingTbl))
    else :
        seeingTbl =  "SeeingPachon"
        print("    seeingTbl:%s default" % (seeingTbl))

    if ( configDict.has_key ('cloudTbl')) :
        cloudTbl =  configDict["cloudTbl"]
        print("    cloudTbl:%s" % (cloudTbl))
    else :
        cloudTbl =  "CloudPachon"
        print("    cloudTbl:%s default" % (cloudTbl))

    if ( configDict.has_key ('misHistTbl')) :
        misHistTbl =  configDict["misHistTbl"]
        print("    misHistTbl:%s" % (misHistTbl))
    else :
        misHistTbl =  "MissedHistory"
        print("    misHistTbl:%s default" % (misHistTbl))
                                        

    dbTables =  '{"obsHist":"%s","timeHist":"%s","proposal":"%s","session":"%s","seqHistory":"%s","field":"%s","userRegion":"%s","seeing":"%s","cloud":"%s","misHist":"%s", "downHist":"%s"}' %(obsHistTbl,timeHistTbl,proposalTbl,sessionTbl,seqHistoryTbl,fieldTbl,userRegionTbl,seeingTbl,cloudTbl,misHistTbl,downHistTbl)
    print "dbTables: %s" %(dbTables)
    dbTableDict = eval(dbTables)
    for key in dbTableDict:
         print "    Database tables: " + key,dbTableDict[key]

    # ensure that at least one proposal is enabled
    if ( (nearEarthConf == None) & (weakLensConf == None) &
         (superNovaConf == None) & (superNovaSubSeqConf == None) &
	 (kuiperBeltConf == None) & (WLpropConf == None)):
        fatalError("At least one proposal type must be defined")

    # rename in order someday 
    runSeeingFudge = weatherSeeingFudge 

    simEpoch = seeingEpoch + simStartDay;
    
    print ('Session ID: %d' % (SID))


    # Setup logging
    if ( verbose < 0 ) :
        logfile = "/dev/null"
        log=False
    else:
        log = logging.getLogger("lsst")
        hdlr = logging.FileHandler(logfile)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)
        log.setLevel(logging.INFO)

    if ( log ):
        log.info('main:  SessionID:%d' % (SID))
    
    # init SimPy.
    if (VERBOSE):
        t0 = time.time ()
#    Simulation.initialize ()
    
    obsProfile = (longitude *DEG2RAD, latitude *DEG2RAD, height, simEpoch,pressure,temperature,relativeHumidity)
    # Create a Simulator instance
    sim = Simulator (lsstDB=lsstDB,
		     obsProfile=obsProfile,
                     sessionID=SID, 
                     nRun=nRun, 
                     seeingEpoch=seeingEpoch,
                     simStartDay=simStartDay,
                     fov=fov,
                     idleDelay=idleDelay,
                     targetList=targetList,
                     maxCloud=maxCloud,
                     runSeeingFudge=runSeeingFudge,
                     telSeeing=telSeeing,
                     opticalDesSeeing=opticalDesSeeing,
                     cameraSeeing=cameraSeeing,
                     filtersConf=filtersConf,
                     schedDownConf=schedDownConf, 
                     unschedDownConf=unschedDownConf, 
                     nearEarthConf=nearEarthConf, 
                     weakLensConf=weakLensConf, 
                     superNovaConf=superNovaConf, 
                     superNovaSubSeqConf=superNovaSubSeqConf, 
		     kuiperBeltConf=kuiperBeltConf,
		     WLpropConf=WLpropConf,
                     instrumentConf=instrumentConf,
                     schedulerConf=schedulerConf, 
		     schedulingDataConf=schedulingDataConf,
                     dbTableDict=dbTableDict,
                     log=log, 
                     logfile=logfile, 
                     verbose=verbose)
    
    # Activate the Simulator
#    Simulation.activate (sim, sim.start (), 0.0)
    sim.start()

    # Simulate for nRun years. The simulation time is in seconds.
    end = nRun*YEAR
#    Simulation.simulate (until=end)

    # special call for giving the oportunity to each proposal to make some
    # closing activities at the end of the run,
    # for example, recording in the DB the unfinished sequences.

    sim.closeProposals(end)
    if (VERBOSE):
        print ('main: done simulating %f seconds' % (end) )
        dt = time.time () - t0
        print ('      simulation took %.02fs' % (dt))

    #lsstDB.closeConnection()

    return
    
if (__name__ == '__main__'):
    # Parse the command line args
    try:
        args = parseArgs (sys.argv[1:])
    except:
        usage (USAGE_STR)
        sys.stderr.write ('Syntax error\n')
        sys.exit (1)

    # Profiling?
    if (args.has_key ('profile') and args['profile'].lower () == 'yes'):
        print ("Profile data sent to file 'ProfileData'")
        import hotshot
        profiler = hotshot.Profile("ProfileData")
        profiler.runcall(startLsst,args)
    else:
        startLsst(args)

    sys.exit (0)
