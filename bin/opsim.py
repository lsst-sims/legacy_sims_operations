#!/usr/bin/env python
import logging
import os
import requests
import subprocess
import time

from lsst.sims.operations import __version__
OPSIM_VERSION = __version__

from lsst.sims.operations.utilities import *
from lsst.sims.operations.Simulator import *
#from LSSTDatabase import *
from lsst.sims.operations.Database import *

# globals
use = ["[options...]"]
use.append("Options:")
use.append("--startup_comment=<string>\tUse for a descriptive comment for the run.")
use.append("\t" * 4 + "This goes into the run tracking DB.")
use.append("\t" * 4 + "Default is \"No comment was entered\".")
use.append("--config=<file>" + "\t" * 3 + "Path to the main configuration file.")
use.append("\t" * 4 + "Default is $SIMS_OPERATIONS_DIR/conf/survey/LSST.conf.")
use.append("--track=<val>" + "\t" * 3 + "Track simulation in OpSim Team run tracking DB.")
use.append("\t" * 4 + "Default is yes. Adds an entry to tracking DB.")
use.append("\t" * 4 + "Use --track=no to not track the run.")
use.append("--verbose=<val>" + "\t" * 3 + "Print total time for the simulation to stdout.")
use.append("\t" * 4 + "Default is no. ")
use.append("--profile=<val>" + "\t" * 3 + "Profile the code. Default is no.")
use.append("\t" * 4 + "Use --profile=yes to profile code.")
use.append("\t" * 4 + "Only use with short runs.")
use.append("-h, --help" + "\t" * 3 + "Print help and exit.")

USAGE_STR = os.linesep.join(use)

def getSessionID(lsstDB, sessionTbl, code_test, track_run, startup_comment):
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
    # Get the hostname and username
    host = os.getenv('OPSIM_HOSTNAME')
    if host is None or host == "":
        import socket
        host = socket.gethostname()
    host = host.split('.')[0]
    host = host.replace('-', '_')
    user = os.getenv('USER')
    (yy, mm, dd, h, m, s, wday, yday, dst) = time.gmtime()
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
    if track_run:
        try:
            track(sessionID, host, user, startup_comment, code_test, 1.0)
        except:
            print ("Unable to contact opsimcvs : Server might be down.")
    # Return the newly found sessionID
    return (sessionID)


def track(sessionID, hostname, user, startup_comment, code_test, status_id):
    url = "http://opsimcvs.tuc.noao.edu/tracking/tracking.php"
    #params = urllib.urlencode({'sessionID': sessionID,
        #                       'hostname': hostname,
        #                       'user': user,
        #                       'startup_comment': startup_comment,
        #                       'code_test': code_test,
        #                       'status_id': status_id,
        #                       'run_version': OPSIM_VERSION})
    #url = "%s?%s" % (url, params);
    #result = urllib.urlopen(url).read();
    payload = {'sessionID': sessionID, 'hostname': hostname, 'user': user, 'startup_comment': startup_comment,
               'code_test': code_test, 'status_id': status_id, 'run_version': OPSIM_VERSION}
    result = requests.get(url, params=payload, timeout=3.0)
    print("    Tracking:%s" % (result))


def startLsst(args):
    """
    Begin LSST telescope observing simulation.

    Command line input
        [--verbose=yes]

        [--track=no]

        [--config=./LSST.conf]'

        [--profile=yes]

        [--startup_comment="blah"]

    Return
        None

    Raise
        exit if there are errors
    """

    # Startup comment
    if 'startup_comment' in args:
        startup_comment = args['startup_comment']
    else:
        startup_comment = "No comment was entered"

    # Verbose?
    if 'verbose' in args and args['verbose'].lower() == 'yes':
        VERBOSE = 1
    else:
        VERBOSE = 0

    if 'track' in args and args['track'].lower() == 'no':
        track_run = False
    else:
        track_run = True

    # Alternate configuration file?
    if 'config' in args:
        confLSST = args['config']
    else:
        confLSST = DefaultLSSTConfigFile
    confLSST = os.path.expanduser(os.path.expandvars(confLSST))

    # Fetch the DB table names so Session DB can be accessed immediately
    configDict, pairs = readConfFile(confLSST)

    if 'dbWrite' in configDict:
        if configDict["dbWrite"]:
            dbWrite = True
        else:
            dbWrite = False
    else:
        dbWrite = True

    if 'sessionTbl' in configDict:
        sessionTbl = configDict["sessionTbl"]
        print("    sessionTbl:%s" % (sessionTbl))
    else:
        sessionTbl = "Session"
        print("    sessionTbl:%s default" % (sessionTbl))

    # Get whether this is a code test
    if 'code_test' in configDict:
        code_test = configDict['code_test']
        print("    code_test:%s" % (code_test))
    else:
        code_test = '1'
        print("    code_test:%s" % (code_test))

    # Instantiate DB Object
    # lsstDB = LSSTDatabase()
    lsstDB = Database(dbWrite)

    # Get a Session ID
    try:
        SID = getSessionID(lsstDB, sessionTbl, code_test, track_run, startup_comment)
    except:
        fatalError('Unable to acquire a Session ID. Please check ',
                   'that the DB is up and running on the localhost.')

    print ('Session ID: %d' % (SID))

    # Adding lsstConf
    storeParam(lsstDB, SID, 0, 'File', 0, "lsstConf", confLSST)

    # Adding startupComment
    storeParam(lsstDB, SID, 0, 'Comment', 0, "startupComment", startup_comment)

    # Find the SHA1 of the configuration and add it to the Config table.
    top_dir, _ = confLSST.split('survey')
    top_dir = os.path.realpath(top_dir)
    old_dir = os.path.realpath(os.curdir)
    os.chdir(top_dir)

    try:
        p = subprocess.Popen(["git", "log", "-n 1", "--pretty=format:%h"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()

        if len(out) == 0 or p.returncode != 0:
            sha1 = "unknown"
        else:
            sha1 = out

        storeParam(lsstDB, SID, 0, 'Config', 0, "sha1", sha1)
    except OSError:
        raise RuntimeError("The git command is not found. If you are using the correct configuration "
                           "you need to have git.")

    # Check to see if there are any changed files.
    p = subprocess.Popen(["git", "status", "--short"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()

    if len(out) == 0:
        changed_files = "None"
    elif p.returncode != 0:
        changed_files = "Files Changed"
    else:
        changed_files = out

    storeParam(lsstDB, SID, 0, 'Config', 0, "changedFiles", changed_files)

    cfiles = [j.strip() for j in changed_files.strip().split(os.linesep)]
    for i, cfile in enumerate(cfiles):
        if cfile.startswith("M "):
            cfile = cfile.strip("M ")
            p = subprocess.Popen(["git", "diff", "-U0", "-w", cfile], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out, err = p.communicate()

            if p.returncode != 0:
                diff_out = "Diff found"
            else:
                diff_out = out

            storeParam(lsstDB, SID, 0, 'Config', i, "fileDiff", cfile, comment=diff_out[:512])

    os.chdir(old_dir)

    # store LSST config in DB
    for line in pairs:
        storeParam(lsstDB, SID, 0, 'LSST', line['index'], line['key'], line['val'])

    # Overlay the user's simulation parameters
    print ("Overarching user-defined parameters")

    if 'nRun' in configDict:
        nRun = configDict["nRun"]
        print("    nRun:%f" % (nRun))
    else:
        fatalError('no nRun parameter defined for length of simulation run')

    if 'fov' in configDict:
        fov = configDict["fov"]
        print("    fov:%f" % (fov))
    else:
        fov = 3.5
        print("    fov:%f default" % (fov))

    if 'idleDelay' in configDict:
        idleDelay = configDict["idleDelay"]
        print("    idleDelay:%f" % (idleDelay))
    else:
        idleDelay = 30
        print("    idleDelay:%f default" % (idleDelay))

    if 'simStartDay' in configDict:
        simStartDay = configDict["simStartDay"]
        print("    simStartDay:%f" % (simStartDay))
    else:
        simStartDay = 0.5
        print("    simStartDay:%f default: 0.5" % (simStartDay))

    if 'targetList' in configDict:
        targetList = configDict["targetList"]
        print("    targetList: %s" % (targetList))
    else:
        targetList = './Targets.txt'
        print("    targetList:%s default" % (targetList))

    if 'maxCloud' in configDict:
        maxCloud = configDict["maxCloud"]
        print("    maxCloud: %f" % (maxCloud))
    else:
        maxCloud = 0.7
        print("    maxCloud: %f default" % (maxCloud))

    if 'telSeeing' in configDict:
        telSeeing = configDict["telSeeing"]
        print("    telSeeing:%f" % (telSeeing))
    else:
        print "telSeeing has no setting"
        sys.exit(1)

    if 'opticalDesSeeing' in configDict:
        opticalDesSeeing = configDict["opticalDesSeeing"]
        print("    opticalDesSeeing:%f" % (opticalDesSeeing))
    else:
        print "opticalDesSeeing has no setting - exiting"
        sys.exit(1)

    if 'cameraSeeing' in configDict:
        cameraSeeing = configDict["cameraSeeing"]
        print("    cameraSeeing:%f" % (cameraSeeing))
    else:
        print "cameraSeeing has no setting - exiting"
        sys.exit(1)

    if 'scaleToNeff' in configDict:
        scaleToNeff = configDict["scaleToNeff"]
        print("    scaleToNeff:%f" % (scaleToNeff))
    else:
        print "scaleToNeff has no setting - exiting"
        sys.exit(1)

    if 'atmNeffFactor' in configDict:
        atmNeffFactor = configDict["atmNeffFactor"]
        print("    atmNeffFactor:%f" % (atmNeffFactor))
    else:
        print "atmNeffFactor has no setting - exiting"
        sys.exit(1)

    if 'filtersConf' in configDict:
        filtersConf = configDict["filtersConf"]
        print("    filtersConf:%s" % (filtersConf))
    else:
        filtersConf = DefaultFiltersConfigFile
        print("    filtersConf:%s default" % (filtersConf))

    if 'schedulerConf' in configDict:
        schedulerConf = configDict["schedulerConf"]
        print("    schedulerConf:%s" % (schedulerConf))
    else:
        schedulerConf = DefaultSchedulerConfigFile
        print("    schedulerConf:%s default" % (schedulerConf))

    if 'schedulingDataConf' in configDict:
        schedulingDataConf = configDict["schedulingDataConf"]
        print("    schedulindDataConf:%s" % (schedulingDataConf))
    else:
        schedulingDataConf = DefaultSchedulingDataConfigFile
        print("    schedulingDataConf:%s default" % (schedulingDataConf))

    if 'schedDownConf' in configDict:
        schedDownConf = configDict["schedDownConf"]
        print("    schedDownConf:%s" % (schedDownConf))
    else:
        print "schedDownConf has no setting"

    if 'unschedDownConf' in configDict:
        unschedDownConf = configDict["unschedDownConf"]
        print("    unschedDownConf:%s" % (unschedDownConf))
    else:
        print "unschedDownConf has no setting"

    if 'instrumentConf' in configDict:
        instrumentConf = configDict["instrumentConf"]
        print("    instrumentConf:%s" % (instrumentConf))
    else:
        instrumentConf = DefaultInstrumentConfigFile
        print("    instrumentConf:%s default" % (instrumentConf))

    if 'astroskyConf' in configDict:
        astroskyConf = configDict["astroskyConf"]
        print("    astroskyConf:%s" % (astroskyConf))
    else:
        astroskyConf = DefaultASConfigFile
        print("    astroskyConf:%s default" % (astroskyConf))

    if 'weakLensConf' in configDict:
        weakLensConf = configDict["weakLensConf"]
        print("    weakLensConf:%s" % (weakLensConf))
    else:
        weakLensConf = None
        print("    weakLensConf:%s default" % (weakLensConf))

    if not isinstance(weakLensConf, list):
        # turn it into a list with one entry
        weakLensConf = [weakLensConf]

    if 'WLpropConf' in configDict:
        WLpropConf = configDict["WLpropConf"]
        print("    WLpropConf:%s" % (WLpropConf))
    else:
        WLpropConf = None
        print("    WLpropConf:%s default" % (WLpropConf))
    if not isinstance(WLpropConf, list):
        # turn it into a list with one entry
        saveConf = WLpropConf
        WLpropConf = []
        WLpropConf.append(saveConf)

    if None in weakLensConf and None in WLpropConf:
        raise RuntimeError("Please uncomment proposals in the {0} file!".format(confLSST))

    if 'nearEarthConf' in configDict:
        nearEarthConf = configDict["nearEarthConf"]
        print("    nearEarthConf:%s" % (nearEarthConf))
    else:
        nearEarthConf = None
        print("    nearEarthConf:%s default" % (nearEarthConf))

    if not isinstance(nearEarthConf, list):
        # turn it into a list with one entry
        saveConf = nearEarthConf
        nearEarthConf = []
        nearEarthConf.append(saveConf)

    if 'superNovaConf' in configDict:
        superNovaConf = configDict["superNovaConf"]
        print("    superNovaConf:%s" % (superNovaConf))
    else:
        superNovaConf = None
        print("    superNovaConf:%s default" % (superNovaConf))

    if not isinstance(superNovaConf, list):
        # turn it into a list with one entry
        saveConf = superNovaConf
        superNovaConf = []
        superNovaConf.append(saveConf)

    if 'superNovaSubSeqConf' in configDict:
        superNovaSubSeqConf = configDict["superNovaSubSeqConf"]
        print("    superNovaSubSeqConf:%s" % (superNovaSubSeqConf))
    else:
        superNovaSubSeqConf = None
        print("    superNovaSubSeqConf:%s default" % (superNovaSubSeqConf))

    if not isinstance(superNovaSubSeqConf, list):
        # turn it into a list with one entry
        saveConf = superNovaSubSeqConf
        superNovaSubSeqConf = []
        superNovaSubSeqConf.append(saveConf)

    if 'kuiperBeltConf' in configDict:
        kuiperBeltConf = configDict["kuiperBeltConf"]
        print("    kuiperBeltConf:%s" % (kuiperBeltConf))
    else:
        kuiperBeltConf = None
        print("    kuiperBeltConf:%s default" % (kuiperBeltConf))

    if not isinstance(kuiperBeltConf, list):
        # turn it into a list with one entry
        saveConf = kuiperBeltConf
        kuiperBeltConf = []
        kuiperBeltConf.append(saveConf)

    if 'logfile' in configDict:
        logfile = configDict["logfile"]
        print("    logfile:%s" % (logfile))
    else:
        logfile = 'lsst.log_%s' % (SID)
        if os.path.exists('log'):
            logfile = os.path.join('log', logfile)
        print("    logfile:%s default" % (logfile))

    if 'verbose' in configDict:
        verbose = configDict["verbose"]
        print("    verbose:%d" % (verbose))
    else:
        verbose = 0
        print("    verbose:%d default" % (verbose))

    if 'downHistTbl' in configDict:
        downHistTbl = configDict["downHistTbl"]
        print("    downHistTbl:%s" % (downHistTbl))
    else:
        downHistTbl = "DownHist"
        print("    downHistTbl:%s default" % (downHistTbl))

    if 'obsHistTbl' in configDict:
        obsHistTbl = configDict["obsHistTbl"]
        print("    obsHistTbl:%s" % (obsHistTbl))
    else:
        obsHistTbl = "ObsHistory"
        print("    obsHistTbl:%s default" % (obsHistTbl))

    if 'timeHistTbl' in configDict:
        timeHistTbl = configDict["timeHistTbl"]
        print("    timeHistTbl:%s" % (timeHistTbl))
    else:
        timeHistTbl = "TimeHistory"
        print("    timeHistTbl:%s default" % (timeHistTbl))

    if 'proposalTbl' in configDict:
        proposalTbl = configDict["proposalTbl"]
        print("    proposalTbl:%s" % (proposalTbl))
    else:
        proposalTbl = "Proposal"
        print("    proposalTbl:%s default" % (proposalTbl))

    if 'seqHistoryTbl' in configDict:
        seqHistoryTbl = configDict["seqHistoryTbl"]
        print("    seqHistoryTbl:%s" % (seqHistoryTbl))
    else:
        seqHistoryTbl = "SeqHistory"
        print("    seqHistoryTbl:%s default" % (seqHistoryTbl))

    if 'fieldTbl' in configDict:
        fieldTbl = configDict["fieldTbl"]
        print("    fieldTbl:%s" % (fieldTbl))
    else:
        fieldTbl = "Field"
        print("    fieldTbl:%s default" % (fieldTbl))

    if 'userRegionTbl' in configDict:
        userRegionTbl = configDict["userRegionTbl"]
        print("    userRegionTbl:%s" % (userRegionTbl))
    else:
        userRegionTbl = "UserRegion"
        print("    userRegionTbl:%s default" % (userRegionTbl))

    if 'siteConf' in configDict:
        siteConf = configDict["siteConf"]
        print("    siteConf:%s" % (siteConf))
    else:
        siteConf = "./SiteCP.conf"
        print("    siteConf:%s default" % (siteConf))

    # Need to fix up all of the configuration files to be in the same location as the LSST conf file.
    siteConf = os.path.join(top_dir, siteConf)
    instrumentConf = os.path.join(top_dir, instrumentConf)
    unschedDownConf = os.path.join(top_dir, unschedDownConf)
    schedDownConf = os.path.join(top_dir, schedDownConf)
    schedulerConf = os.path.join(top_dir, schedulerConf)
    schedulingDataConf = os.path.join(top_dir, schedulingDataConf)
    astroskyConf = os.path.join(top_dir, astroskyConf)
    filtersConf = os.path.join(top_dir, filtersConf)
    if None not in weakLensConf:
        for i in range(len(weakLensConf)):
            weakLensConf[i] = os.path.join(top_dir, weakLensConf[i])
    if None not in WLpropConf:
        for i in range(len(WLpropConf)):
            WLpropConf[i] = os.path.join(top_dir, WLpropConf[i])

    try:
        # Fetch Site Specific Configuration file
        configDict, pairs = readConfFile(siteConf)
    except IOError:
        message = []
        message.append("Please make sure you have copied LSST.conf from $SIMS_OPERATIONS_DIR/conf/survey")
        message.append("and modify all of the config file paths to point to the full path of")
        message.append("$SIMS_OPERATIONS_DIR/conf")
        raise RuntimeError(" ".join(message))

    # store config in DB
    for line in pairs:
        storeParam(lsstDB, SID, 0, 'site', line['index'], line['key'], line['val'])

    if 'seeingEpoch' in configDict:
        seeingEpoch = configDict["seeingEpoch"]
        print("    seeingEpoch:%f" % (seeingEpoch))
    else:
        seeingEpoch = 49353.
        print("    seeingEpoch:%f default: 1994-01-01T00:00:00.0" % (seeingEpoch))

    if 'latitude' in configDict:
        latitude = configDict["latitude"]
        print("    latitude:%f" % (latitude))
    else:
        latitude = -30.16527778
        print("    latitude:%f default (CTIO)" % (latitude))

    if 'longitude' in configDict:
        longitude = configDict["longitude"]
        print("    longitude:%f" % (longitude))
    else:
        longitude = -70.815
        print("    longitude:%f default (CTIO)" % (longitude))

    if 'height' in configDict:
        height = configDict["height"]
        print("    height:%f " % (height))
    else:
        height = 2215.
        print("    height:%f default (CTIO)" % (height))

    if 'pressure' in configDict:
        pressure = configDict["pressure"]
        print("    pressure:%f " % (pressure))
    else:
        pressure = 1010.
        print("    pressure:%f default (CTIO)" % (pressure))

    if 'temperature' in configDict:
        temperature = configDict["temperature"]
        print("    temperature:%f " % (temperature))
    else:
        temperature = 12.
        print("    temperature:%f default (CTIO)" % (temperature))

    if 'relativeHumidity' in configDict:
        relativeHumidity = configDict["relativeHumidity"]
        print("    relativeHumidity:%f " % (relativeHumidity))
    else:
        relativeHumidity = 0.
        print("    relativeHumidity:%f default (CTIO)" % (relativeHumidity))

    if 'weatherSeeingFudge' in configDict:
        weatherSeeingFudge = configDict["weatherSeeingFudge"]
        print("    weatherSeeingFudge:%f" % (weatherSeeingFudge))
    else:
        weatherSeeingFudge = 1.
        print("    weatherSeeingFudge:%f default" % (weatherSeeingFudge))

    if 'seeingTbl' in configDict:
        seeingTbl = configDict["seeingTbl"]
        print("    seeingTbl:%s" % (seeingTbl))
    else:
        seeingTbl = "SeeingPachon"
        print("    seeingTbl:%s default" % (seeingTbl))

    if 'cloudTbl' in configDict:
        cloudTbl = configDict["cloudTbl"]
        print("    cloudTbl:%s" % (cloudTbl))
    else:
        cloudTbl = "CloudPachon"
        print("    cloudTbl:%s default" % (cloudTbl))

    if 'misHistTbl' in configDict:
        misHistTbl = configDict["misHistTbl"]
        print("    misHistTbl:%s" % (misHistTbl))
    else:
        misHistTbl = "MissedHistory"
        print("    misHistTbl:%s default" % (misHistTbl))

    dbTablesKeys = ["obsHist", "timeHist", "proposal", "session", "seqHistory", "field", "userRegion",
                    "seeing", "cloud", "misHist", "downHist"]
    dbTables = (obsHistTbl, timeHistTbl, proposalTbl, sessionTbl, seqHistoryTbl, fieldTbl, userRegionTbl,
                seeingTbl, cloudTbl, misHistTbl, downHistTbl)
    import itertools
    dbTableDict = dict((key, value) for key, value in itertools.izip(dbTablesKeys, dbTables))
    for key in dbTableDict:
        print "    Database tables: " + key, dbTableDict[key]

    # ensure that at least one proposal is enabled
    if nearEarthConf is None and weakLensConf is None and superNovaConf is None and \
            superNovaSubSeqConf is None and kuiperBeltConf is None and WLpropConf is None:
        fatalError("At least one proposal type must be defined")

    # rename in order someday
    runSeeingFudge = weatherSeeingFudge

    simEpoch = seeingEpoch + simStartDay

    print('Session ID: %d' % (SID))

    # Setup logging
    if verbose < 0:
        logfile = "/dev/null"
        log = False
    else:
        log = logging.getLogger("lsst")
        hdlr = logging.FileHandler(logfile)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)
        log.setLevel(logging.INFO)

    if log:
        log.info('main:  SessionID:%d' % (SID))

    # init SimPy.
    if VERBOSE:
        t0 = time.time()
#    Simulation.initialize ()

    obsProfile = (longitude * DEG2RAD, latitude * DEG2RAD, height, simEpoch, pressure, temperature,
                  relativeHumidity)
    # Create a Simulator instance
    sim = Simulator(lsstDB=lsstDB, obsProfile=obsProfile, sessionID=SID, nRun=nRun, seeingEpoch=seeingEpoch,
                    simStartDay=simStartDay, fov=fov, idleDelay=idleDelay, targetList=targetList,
                    maxCloud=maxCloud, runSeeingFudge=runSeeingFudge, telSeeing=telSeeing,
                    opticalDesSeeing=opticalDesSeeing, cameraSeeing=cameraSeeing, scaleToNeff=scaleToNeff,
                    atmNeffFactor=atmNeffFactor, filtersConf=filtersConf,
                    schedDownConf=schedDownConf, unschedDownConf=unschedDownConf, nearEarthConf=nearEarthConf,
                    weakLensConf=weakLensConf, superNovaConf=superNovaConf,
                    superNovaSubSeqConf=superNovaSubSeqConf, kuiperBeltConf=kuiperBeltConf,
                    WLpropConf=WLpropConf, instrumentConf=instrumentConf, schedulerConf=schedulerConf,
                    schedulingDataConf=schedulingDataConf, astroskyConf=astroskyConf, dbTableDict=dbTableDict,
                    log=log, logfile=logfile, verbose=verbose)

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
    if VERBOSE:
        print('main: done simulating %f seconds' % (end))
        dt = time.time() - t0
        print('      simulation took %.02fs' % (dt))

    #lsstDB.closeConnection()

    return

if (__name__ == '__main__'):
    # Parse the command line args
    try:
        args = parseArgs(sys.argv[1:])
    except UserWarning:
        usage(USAGE_STR)
        sys.exit(0)
    except:
        usage(USAGE_STR)
        sys.stderr.write('Syntax error\n')
        sys.exit(1)

    # Profiling?
    if 'profile' in args and args['profile'].lower() == 'yes':
        print("Profile data sent to file 'ProfileData'")
        import hotshot
        profiler = hotshot.Profile("ProfileData")
        profiler.runcall(startLsst, args)
    else:
        startLsst(args)

    sys.exit(0)
