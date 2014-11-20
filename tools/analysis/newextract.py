#!/usr/bin/env python

# Philip A. Pinto 22 October 2004

import pygtk
pygtk.require('2.0')
import gtk

import math
from Numeric import *
from matplotlib.mlab import *
import sys, re, time, socket
import MySQLdb
from optparse import OptionParser

from pylab import *

# Database specific stuff
from LSSTDBInit import *
OBSHIST = 'ObsHistory'
SEQHIST = 'SeqHistory'
FIELD = 'Field'
#LSSTCONF = 'LsstConf'
LSSTCONF = 'Config'
PROPOSAL = 'Proposal'
TIMEHIST = 'TimeHistory'
SESSION = 'Session'

CONF = {'WL' : 'WLConf', 'SN' : 'SNConf' , 'SNSS' : 'SNSSConf', 'KBO' : 'SNSSConf', 'WLTSS' : 'WLTSSConf'}

# SeqHistory Sequence completion status
SUCCESS = 0
MAX_MISSED_EVENTS = 1
CYCLE_END = 2

# TimeHistory Events
START_NIGHT = 0
MOON_WANING = 1         # New lunation, too
MOON_WAXING = 2
NEW_YEAR = 3
 
# Color redefinitions to get brighter colors
BLACK = "#000000"
BLUE = "#0055ff"
CYAN = "#00ffff"
GREEN = "#00ff00"
YELLOW = "#ffff00"
RED = "#ff0000"
MAGENTA = "#ff00ff"
WHITE = "#ffffff"

# only two fonts used
bigfont = {'fontname'   : 'Courier',
            'color'      : 'r',
            'fontweight' : 'bold',
            'fontsize'   : 11}

smallfont = {'fontname'   : 'Courier',
            'color'      : 'r',
            'fontweight' : 'bold',
            'fontsize'   : 9}

# here begins graphics diagnostic routines sometimes used in refresh6
def get_refcounts():
    d = {}
    sys.modules
    # collect all classes
    for m in sys.modules.values():
        for sym in dir(m):
            o = getattr (m, sym)
            if type(o) is types.ClassType:
                d[o] = sys.getrefcount (o)
    # sort by refcount
    pairs = map (lambda x: (x[1],x[0]), d.items())
    pairs.sort()
    pairs.reverse()
    return pairs

def print_top(len):
    for n, c in get_refcounts()[:len]:
        print '%10d %s' % (n, c.__name__)
    return


# here begins the data munging


def getDbData(sql,label):
    global sessionID
    
    # Get a connection to the DB
    connection = openConnection ()
    cursor = connection.cursor ()
    
    # Fetch the data from the DB
    #print "Fetching %s ..." % (label),
    
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write(
            'Unable to execute SQL query (%s).' % (sql) )
        sys.exit()

    try:
        ret = cursor.fetchall ()
        #print "done."
    except:
        sys.stderr.write ('No %s for Session %d' \
            % (label,sessionID))
        sys.exit()

    # Close the connection
    cursor.close ()
    connection.close ()
    del (cursor)
    del (connection)

    return (ret)


def getPairsDictionary(sessionID):

    label = 'Pairs Harvesting'
    sql   = 'select propID,propConf from Proposal where sessionID=%d and propName="WLTSS"' % (sessionID)
    list_propID = getDbData(sql, label)
    if list_propID == None:
        list_propID = []

    pairs = {}
    totalNpairs = 0
    for p in range(len(list_propID)):
        propID = list_propID[p][0]
        propConf=list_propID[p][1]

        sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqFilters" order by paramIndex' % (sessionID, propID)
        list_filter = getDbData(sql, label)
        sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqEvents" order by paramIndex' % (sessionID, propID)
        list_events = getDbData(sql, label)
        sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqInterval" order by paramIndex' % (sessionID, propID)
        list_interval = getDbData(sql, label)
        sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqWindowStart" order by paramIndex' % (sessionID, propID)
        list_windowstart = getDbData(sql, label)
        sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqWindowEnd" order by paramIndex' % (sessionID, propID)
        list_windowend = getDbData(sql, label)

	pairs_thisproposal = {}
        for f in range(len(list_filter)):
            interval = eval(list_interval[f][0])
	    if interval <= 0.0:
		continue

            filter = list_filter[f][0]
            windowstart = eval(list_windowstart[f][0])
            windowend = eval(list_windowend[f][0])
            intervalmin = interval*(1+windowstart)
            intervalmax = interval*(1+windowend)

            sql = 'select seqnNum,expDate,fieldID from ObsHistory where sessionID=%d and propID=%d and filter="%s" order by seqnNum,expDate' % (sessionID, propID, filter)
            list_seqnNum_expDate = getDbData(sql, label)
	    if list_seqnNum_expDate == None:
		list_seqnNum = []

            pairs_thisproposal_thisfilter = {}
            nobs = len(list_seqnNum_expDate)
            filterNpairs = 0
            k = 0
            while k<nobs-2:
                seqnNum1 = list_seqnNum_expDate[k][0]
                expDate1 = list_seqnNum_expDate[k][1]
		fieldID  = list_seqnNum_expDate[k][2]
                seqnNum2 = list_seqnNum_expDate[k+1][0]
                expDate2 = list_seqnNum_expDate[k+1][1]
                if seqnNum1 == seqnNum2:
                    if intervalmin <= (expDate2-expDate1) <= intervalmax:
			pairs_thisproposal_thisfilter[fieldID] = pairs_thisproposal_thisfilter.get(fieldID,0) + 1
                        k += 1
                        totalNpairs  += 1
                k += 1
	    pairs_thisproposal[filter] = pairs_thisproposal_thisfilter
	pairs[propID] = pairs_thisproposal

    return pairs

def createDataset():

    global resObs, resSeq, sessionID, propID, pairsDictionary

    # Get a connection to the DB
    connection = openConnection ()
    cursor = connection.cursor ()

    # If the current session is active, need to ensure that all data is
    # consistant - so cap the expDate at the most recent entry as of 
    # the following sql query.
    # Fetch the largest expDate
    sql = 'select max(expDate) from %s where sessionID=%d ' %(OBSHIST,sessionID)
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write(
            'Unable to execute ObsHistory SQL query (%s).' % (sql) )
        sys.exit()

    try:
        result = cursor.fetchall ()
	maxExpDate = float(result[0][0])
    except:
        maxExpDate = 0
        
    # print "done."

    # Remember that the ObsHistory records the same observation up to N times
    # where N is the number of active proposals (serendipitous obs!). In 
    # particular, some proposals accept any serendipitous observation, other
    # don't. We need to figure out the max spatial coverage.
    # Fetch all the data for this Session ID, if any
    #
    sql = 'create temporary table tmpO select f.fieldRA,f.fieldDec,f.fieldID, o.filter,'
    sql +='o.expDate from %s f, %s o where o.sessionID=%d ' % (FIELD,OBSHIST,sessionID)
    sql += 'and f.fieldID=o.fieldID and o.expDate <= %f ' % (maxExpDate)
    sql += 'and o.expDate >= %f and o.expDate <= %f ' %(interval[0],interval[1])
    if len(propID) != 0:
        sql += 'AND ('
        for n in propID[:-1]:
            sql += 'o.propID = %d OR ' % n
        sql += 'o.propID = %d ) ' % propID[len(propID)-1]
    sql += 'group by o.expDate; ' 
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write(
            'Unable to execute ObsHistory SQL query (%s).' % (sql) )
        sys.exit()

    sql = 'select fieldRA,fieldDec,fieldID,filter,count(expDate) from tmpO group by filter,fieldID order by filter, fieldID; '
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write(
            'Unable to execute ObsHistory SQL query (%s).' % (sql) )
        sys.exit()
    try:
        resObs = cursor.fetchall ()
        # print "done."
    except:
        sys.stderr.write ('No data for Session %d' \
            % (sessionID))
        sys.exit()

    # Fetch the data from the DB
    print "Fetching data from the ObsHist DB...",
    
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write(
            'Unable to execute ObsHistory SQL query (%s).' % (sql) )
        sys.exit()

        
    # Fetch all the Sequence data for this Session ID, if any
    sql = 'select f.fieldRA,f.fieldDec,f.fieldID,p.propName,count(s.propID) '
    sql +='from %s f, %s s, %s p ' % (FIELD,SEQHIST,PROPOSAL)
    sql += 'where s.sessionID=%d and p.sessionID=%d ' % (sessionID,sessionID)
    sql += 'and f.fieldID=s.fieldID and s.completion>= 1 and p.propID=s.propID '
    sql += 'and s.expDate <= %f ' % (maxExpDate)
    sql += 'and s.expDate >= %f and s.expDate <= %f ' %(interval[0],interval[1])
    if len(propID) != 0:
        sql += 'AND ('
        for n in propID[:-1]:
            sql += 's.propID = %d OR ' % n
        sql += 's.propID = %d ) ' % propID[len(propID)-1]
    sql += 'group by p.propName,s.fieldID order by p.propName, s.fieldID; ' 
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write(
            'Unable to execute SeqHistory SQL query (%s).' % (sql) )
        sys.exit()

    try:
        resSeq = cursor.fetchall ()
    except:
        resSeq = None

    # print "done."
    

    # Close the connection
    cursor.close ()
    connection.close ()
    del (cursor)
    del (connection)

    pairsDictionary = getPairsDictionary(sessionID)

    return


def summary():

    global resObs, resSeq, interval, availableProps, propSeq, pairsDictionary

    # Cumulative number of visits per fieldID over the interval
    grizy = {}
    g = {}
    r = {}
    i = {}
    z = {}
    y = {}
    u = {}
    seq = {}
    pairs = {}
    grizy = {'g':g, 'r':r, 'i':i, 'z':z, 'y':y, 'u':u, 'seq':seq, 'pairs':pairs}
    wl = {}
    nea = {}
    sn = {}
    snss = {}
    kbo = {}
    wltss = {}
    propSeq = {'WL':wl, 'NEA':nea, 'SN':sn, 'SNSS':snss, 'KBO':kbo, 'WLTSS':wltss}
    
    # Utility dictionary {fieldID: (ra, dec)}
    targets = {}

    # optimize...
    thk = targets.has_key
    
    # Start with the observations
    # Each row has the format
    #       (ra,     dec,    fieldID, filter, count)
    #       (row[0], row[1], row[2],  row[3], row[4] )
    #           and is within the time interval specified
    if len(resObs) <= 0:
        sys.stderr.write("No Observations found for session. Aborting....\n")
        sys.exit()

    for row in resObs:
        # We want RA in decimal hours...
        targets[row[2]] = targets.get(row[2],(float(row[0])/15.0, float(row[1])))
        grizy[row[3]][row[2]] = int(row[4])

    # Now the (completed) NEA sequences
    # Each row has the format
    #       (ra,     dec,    fieldID, propName, count)
    #       (row[0], row[1], row[2],  row[3], row[4])
    #           and is within the time interval specified
    for row in resSeq:
            # Obs comes before Sequence, so 'targets' is already initialized
            # Note: 'seq' is directly loaded into array 'grizy'
            seq[row[2]] = seq.get(row[2],0) + int(row[4])
            propSeq[row[3]][row[2]] = int(row[4])
    for propID in pairsDictionary.keys():
	for filter in pairsDictionary[propID].keys():
	    for fieldID in pairsDictionary[propID][filter].keys():
		pairs[fieldID] = pairs.get(fieldID,0) + pairsDictionary[propID][filter][fieldID]

    return (targets, grizy, propSeq)


def makeData():
    """
    Summarize the results
    """

    global resObs, resSeq, interval

    (targets, grizy,propSeq) = summary()

    ra = array([targets[fieldID][0] for fieldID in targets.keys()])
    dec = array([targets[fieldID][1] for fieldID in targets.keys()])

    nums = {}
    tkeys = targets.keys() 
    for k in grizy.keys():
        nums[k] = array([grizy[k].get(fieldID,0) for fieldID in tkeys])

    for k in propSeq.keys():
        nums[k] = array([propSeq[k].get(fieldID,0) for fieldID in tkeys])

    return (ra, dec, nums)

def getWLSequencesCount(propNumber):

    label = 'WL SEQ'
    sql   = 'select paramName,paramValue from Config where moduleName="weakLensing" and propID=%d order by paramIndex' % (propNumber)
    config_WL   = getDbData(sql, label)
    dict_WL = {}
    for kv in config_WL:
        if kv[0] in dict_WL.keys():
            if isinstance(dict_WL[kv[0]], list):
                dict_WL[kv[0]].append(kv[1])
            else:
                dict_WL[kv[0]] = [dict_WL[kv[0]],kv[1]]
        else:
            dict_WL[kv[0]] = kv[1]

    Filter = dict_WL['Filter']
    Filter_Visits = {}
    for ix in range(len(Filter)):
        Filter_Visits[Filter[ix]] = eval(dict_WL['Filter_Visits'][ix])

    sql = 'DROP TABLE IF EXISTS tmpObs, tmpObs1, tmpVisits'
    ret = getDbData(sql, label)

    sql = 'create table tmpObs select propID,fieldID,fieldRA,fieldDec,filter,expDate from ObsHistory where sessionID=%d and propID=%d group by expDate order by propID,fieldID,filter' % (sessionID,propNumber)
    ret = getDbData(sql, label)

    sql = 'create table tmpObs1 select *,count(filter) as visits from tmpObs group by propID,fieldID,filter order by propID,fieldID,filter'
    ret = getDbData(sql, label)

    sql = 'create table tmpVisits select fieldID,'
    for ix in range(len(Filter)-1):
        sql+= 'sum(if(filter="%s", visits, 0)) as Nf%s,' % (Filter[ix], Filter[ix])
    sql+= 'sum(if(filter="%s", visits, 0)) as Nf%s' % (Filter[-1], Filter[-1])
    sql+= ' from tmpObs1 group by fieldID'
    ret = getDbData(sql, label)


    sql = 'select count(fieldID) from tmpVisits where '
    for ix in range(len(Filter)-1):
        sql+= 'Nf%s>=%d and ' % (Filter[ix], Filter_Visits[Filter[ix]])
    sql+= 'Nf%s>=%d' % (Filter[-1], Filter_Visits[Filter[-1]])
    ret = getDbData(sql, label)
    Complete = int(ret[0][0])

    sql = 'select count(fieldID) from tmpVisits where '
    for ix in range(len(Filter)-1):
        sql+= 'Nf%s<%d or ' % (Filter[ix], Filter_Visits[Filter[ix]])
    sql+= 'Nf%s<%d' % (Filter[-1], Filter_Visits[Filter[-1]])
    ret = getDbData(sql, label)
    Incomplete = int(ret[0][0])

    sql = 'DROP TABLE IF EXISTS tmpObs, tmpObs1, tmpVisits'
    ret = getDbData(sql, label)

    return (Complete, Incomplete)

def cumulativeCountSummary():

    global availableProps, FOV, cumulativeData, sessionID, galaxyExclusion, galaxyExclusion0, sessDate, excludeGalaxy, propName, propNumber, propCompleted, propLostMissedEvent, propLostCycleEnd

    # acquire sessionDate for session
    label = 'Session Date'
    sql = 'SELECT sessionDate from %s where sessionID = %d ' % (SESSION, sessionID)
    ret = getDbData(sql,label)
    sessDate = ret[0][0]
    print "%s: %s" % (label, sessDate)

    # acquire the # of lunations for the run
    label = 'Lunation Count'
    sql = 'SELECT count(event) from %s where sessionID = %d AND event = %d ' % (TIMEHIST, sessionID,MOON_WANING)
    ret = getDbData(sql,label)
    nlun = int(ret[0][0])
    print "%s: %d" % (label,nlun)

    # acquire the # of nights for the run
    label = 'StartNight Count'
    sql = 'SELECT count(event) from %s where sessionID = %d AND event = "StartNight" ' % (TIMEHIST, sessionID)
    ret = getDbData(sql,label)
    nnights = int(ret[0][0])
    print "%s: %d" % (label,nnights)

    # acquire the available proposal ids
    label = 'Available Proposals'
    sql = 'SELECT o.propID, p.propName,p.propConf from %s o, %s p where o.sessionID = %d AND o.propID = p.propID group by propID' % (OBSHIST, PROPOSAL, sessionID)
    availableProps = getDbData(sql,label)
    print "%s:" %(label)
    for n in availableProps:
        print "     %d %s(%s) " % (int(n[0]),n[1],n[2]) 

    # get the galactic exclusion parameters; use WL's values, if available
    excludeGalaxy = False
    label = 'id_WL'
    sql   = 'select propID from Proposal where sessionID=%d and (propName="WL" or propName="WLTSS")' % (sessionID)
    ids_WL   = getDbData(sql, label)

    for WL_prop in ids_WL:
        sql   = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="taperB"' % (sessionID, WL_prop[0])
        ret = getDbData(sql, label)
	if len(ret) != 0:
        	taperB = float(ret[0][0])
        	if taperB == 0.0:
            		#print "TaperB is zero, proposal = %d, Get next prop" % (WL_prop[0])
            		continue
        	else:
            		#print "TaperB is valid, proposal = %d" % (WL_prop[0])
            		excludeGalaxy = True
            		break

    if excludeGalaxy:
        sql   = 'select paramName,paramValue from Config where sessionID=%d and propID=%d order by paramIndex' % (sessionID,WL_prop[0])
        config_WL   = getDbData(sql, label)
        dict_WL = {}
        for kv in config_WL:
            if kv[0] in dict_WL.keys():
                if isinstance(dict_WL[kv[0]], list):
                    dict_WL[kv[0]].append(kv[1])
                else:
                    dict_WL[kv[0]] = [dict_WL[kv[0]],kv[1]]
            else:
                dict_WL[kv[0]] = kv[1]

        #taperB=180.
        #taperL=0.
        #peakL=0.
    
        taperB = eval(dict_WL['taperB'])
        taperL = eval(dict_WL['taperL'])
        peakL  = eval(dict_WL['peakL'])
        print "taperB: %f taperL: %f peakL:%f" % (taperB,taperL,peakL)

#   i foundConf = "NONE"
#    for prop in availableProps:
#        if (prop[1] == 'WL') or (prop[1] == 'SN') or (prop[1] == 'SNSS') or (prop[1] == 'KBO') or (prop[1] == 'WLTSS'):
#            foundConf = CONF[prop[1]]
#            break
#    if foundConf != "NONE":        
#        label = 'taperB'
#        sql = 'SELECT  taperB from %s where sessionID = %d' % (foundConf,
#               sessionID)
#        ret = getDbData(sql,label)
#        taperB=float(ret[0][0])

#        label = 'taperL'
#        sql = 'SELECT  taperL from %s where sessionID = %d' % (foundConf,
#               sessionID)
#        ret = getDbData(sql,label)
#        taperL=float(ret[0][0])

#        label = 'peakL'
#        sql = 'SELECT  peakL from %s where sessionID = %d' % (foundConf,
#               sessionID)
#        ret = getDbData(sql,label)
#        peakL=float(ret[0][0])

    # acquire the Telescope Field of View (FOV)
    label = 'FOV'
    sql = 'SELECT paramValue from %s where sessionID = %d and paramName="fov" limit 1' % (LSSTCONF,
            sessionID)
    ret = getDbData(sql,label)
    #print "FOV ret:%s" %(ret)
    #FOV = float(n[0][0])
    for n in ret:
        FOV = (float(n[0]))
    print "%s: %f" % (label,FOV)

    # acquire total number of proposal hits including serendipitous hits
    label = 'Count of Hits (includes serendipitous hits)'
    sql = 'select count(expDate) from %s where sessionID=%d ' % (OBSHIST,
            sessionID)
    ret = getDbData(sql,label)
    totalProposalHits = int(ret[0][0])
    print "%s:%d" % (label,totalProposalHits)

    # acquire total number of unique observations
    label = 'Count of Observations'
    sql = 'select count(distinct expDate) from %s where sessionID=%d'%(OBSHIST,
            sessionID)
    ret = getDbData(sql,label)
    totalObs = int(ret[0][0])
    print "%s:%d" % (label,totalObs)
    nobs = totalObs

    # acquire Total Proposal Counts by Proposal (includes` serendipitous 'obs')
    label = 'Count of Hits by Proposal'
    sql = 'select p.propName, p.propConf, count(*) from %s p, %s o where o.sessionID=%d and p.propID=o.propID group by p.propID' % (PROPOSAL,OBSHIST,sessionID)
    hitsByProposal = getDbData(sql,label)
    print "%s:" % (label)
    for n in hitsByProposal:
        print "   %s(%s)   %d" % (n[0], n[1], int(n[2]))

    # acquire Total Proposal Counts by Filter (includes` serendipitous 'obs')
    label = 'Count of Hits by Filter'
    sql = 'select filter, count(*) from %s where sessionID=%d group by filter' % (OBSHIST,sessionID)
    hitsByFilter = getDbData(sql,label)
    print "%s:" % (label)
    for n in hitsByFilter:
        print "     %s  %d" % (n[0], int(n[1]))

    # acquire Total Observation Counts by Filter
    label = 'Count of Observations by Filter'
    sql = 'select filter, count(distinct expDate) from %s where sessionID=%d group by filter' % (OBSHIST,sessionID)
    obsByFilter = getDbData(sql,label)
    print "%s:" % (label)
    for n in obsByFilter:
        print "     %s  %d" % (n[0], int(n[1]))

    # acquire count of Hits per proposal and per filter (includes serendipitous)
    label = 'Count of Hits per Proposal per Filter'
    sql = 'select p.propName,p.propConf,o.filter,count(o.expDate) from %s o, %s p where o.sessionID=%d and p.propID=o.propID group by p.propID,filter order by p.propID,filter' % (OBSHIST,PROPOSAL,sessionID)
    hitsByProposalByFilter = getDbData(sql,label)
    print "%s:" % (label)
    for n in hitsByProposalByFilter:
            print "     %s(%s)  %s  %d" % (n[0], n[1], n[2], int(n[3]))

    # acquire count of Hits per filter and per proposal (includes serendipitous)
    label = 'Count of Hits per Filter per Proposal'
    sql = 'select p.propName,p.propConf,o.filter,count(o.expDate) from %s o, %s p where o.sessionID=%d and p.propID=o.propID group by filter, p.propID order by filter,p.propID' % (OBSHIST,PROPOSAL,sessionID)
    hitsByFilterByProposal = getDbData(sql,label)
    print "%s:" % (label)
    for n in hitsByFilterByProposal:
            print "     %s  %s(%s) %d" % (n[2], n[0], n[1], int(n[3]))

    # acquire total number of Fields Observed
    label = 'Count of Fields Observed'
    sql = 'select count(distinct fieldID) from %s where sessionID=%d'%(OBSHIST,
            sessionID)
    ret = getDbData(sql,label)
    totalFields = int(ret[0][0])
    print "%s:%d" % (label,totalFields)

    # acquire total number of sequences started
    label = 'Sequences Started '
    #   first record could have startDate=0; unlikely to have completion=0, too
    sql = 'select count(*) from %s where sessionID=%d and (startDate > 0 or completion>0)'%(SEQHIST, sessionID)
    ret = getDbData(sql,label)
    totalSeqStart = int(ret[0][0])
    print "%s:%d" % (label,totalSeqStart)

    # acquire total number of sequences completed
    label = 'Sequences Completed'
    sql = 'select count(*) from %s where sessionID=%d and completion >= 1'%(SEQHIST, sessionID)
    ret = getDbData(sql,label)
    totalSeqComplete = int(ret[0][0])
    print "%s:%d" % (label,totalSeqComplete)
    ncompl = totalSeqComplete
    nlost = totalSeqStart - totalSeqComplete
    print "Sequences abandoned: %d" % ( nlost)

    propNumber = {}
    propName   = {}
    propType   = {}
    propCompleted = {}
    propLostMissedEvent = {}
    propLostCycleEnd = {}
    sql   = 'select propID,propConf,propName from Proposal where sessionID=%d' % (sessionID)
    propTable = getDbData(sql,label)
    for k in range(len(propTable)):
	propNumber[k] = propTable[k][0]
	propName[k]   = propTable[k][1]
	propType[k]   = propTable[k][2]

#    totalNEASeqComplete=0
#    totalNEAAlmostSeq=0
#    totalNEAAbortSeq=0
#    totalNEAMissedSeq =0

#    totalSNSeqComplete=0
#    totalSNMissedSeq=0

#    totalSNSSSeqComplete=0
#    totalSNSSMissedSeq=0

#    totalKBOSeqComplete=0
#    totalKBOMissedSeq=0

#    totalWLTSSSeqComplete=0
#    totalWLTSSMissedSeq=0
                                                                                                                                       
    # acquire total number of completed sequences by Proposal
    label = 'Sequences by Proposal'
    print "%s:" % (label)
    for k in range(len(propName)):
	if propType[k] == 'WL':
	    (propCompleted[k], propLostCycleEnd[k]) = getWLSequencesCount(propNumber[k])
	    propLostMissedEvent[k] = 0
	else:
	    sql = 'select count(*) from %s where sessionID=%d and propID=%d and completion>=1' % (SEQHIST, sessionID, propNumber[k])
	    ret = getDbData(sql,label)
	    propCompleted[k] = int(ret[0][0])

            sql = 'select count(*) from SeqHistory where propID=%d and endStatus=1' % (propNumber[k])
            ret   = getDbData(sql, label)
            propLostMissedEvent[k] = int(ret[0][0])

            sql = 'select count(*) from SeqHistory where propID=%d and (endStatus=2 or (endStatus=3 and completion>0))' % (propNumber[k])
            ret   = getDbData(sql, label)
            propLostCycleEnd[k] = int(ret[0][0])
        print "     %s  %d completed" % (propName[k], propCompleted[k])
        print "     %s  %d lost missed event" % (propName[k], propLostMissedEvent[k])
        print "     %s  %d lost cycle end" % (propName[k], propLostCycleEnd[k])


#    for prop in availableProps:
#        if prop[1] == 'NEA':
#            sql = 'select count(*) from %s where sessionID=%d and completion >= 1 and propID = %d'%(SEQHIST, sessionID,prop[0])
#            ret = getDbData(sql,label)
#            totalNEASeqComplete = int(ret[0][0])
#            print "     %s(%s)  %d" % (prop[1],prop[2],totalNEASeqComplete)
#        elif prop[1] == 'SN':
#            sql = 'select count(*) from %s where sessionID=%d and completion >= 1 and propID = %d'%(SEQHIST, sessionID,prop[0])
#            ret = getDbData(sql,label)
#            totalSNSeqComplete = int(ret[0][0])
#            print "     %s(%s) %d" % (prop[1],prop[2],totalSNSeqComplete)
#        elif prop[1] == 'SNSS':
#            sql = 'select count(*) from %s where sessionID=%d and completion >= 1 and propID = %d'%(SEQHIST, sessionID,prop[0])
#            ret = getDbData(sql,label)
#            totalSNSSSeqComplete = int(ret[0][0])
#            print "     %s(%s) %d" % (prop[1],prop[2],totalSNSSSeqComplete)
#        elif prop[1] == 'KBO':
#            sql = 'select count(*) from %s where sessionID=%d and completion >= 1 and propID = %d'%(SEQHIST, sessionID,prop[0])
#            ret = getDbData(sql,label)
#            totalKBOSeqComplete = int(ret[0][0])
#            print "     %s(%s) %d" % (prop[1],prop[2],totalKBOSeqComplete)
#        elif prop[1] == 'WLTSS':
#            sql = 'select count(*) from %s where sessionID=%d and completion >= 1 and propID = %d'%(SEQHIST, sessionID,prop[0])
#            ret = getDbData(sql,label)
#            totalWLTSSSeqComplete = int(ret[0][0])
#            print "     %s(%s) %d" % (prop[1],prop[2],totalWLTSSSeqComplete)

    # acquire total number of Abandoned Sequences by Proposal

#        sql = 'select count(*) from %s where sessionID=%d and propID=%d and completion>=1' % (SEQHIST, sessionID, propNumber[k])
#        ret = getDbData(sql,label)
#        propCompleted[k] = int(ret[0][0])
#        print "     %s  %d" % (propName[k], propCompleted[k])


#    for prop in availableProps:
#        if prop[1] == 'NEA':
#            sql = 'select count(*) from %s where sessionID=%d and propID = %d and startDate > 0 and endStatus=%d'%(SEQHIST, sessionID,prop[0],MAX_MISSED_EVENTS)
#            ret = getDbData(sql,label)
#            totalNEAMissedSeq = int(ret[0][0])
#            sql = 'select count(*) from %s where sessionID=%d and propID = %d and startDate = 0 and endStatus=%d'%(SEQHIST, sessionID,prop[0],CYCLE_END)
#            ret = getDbData(sql,label)
#            totalNEAAlmostSeq = int(ret[0][0])
#            sql = 'select count(*) from %s where sessionID=%d and propID = %d and startDate > 0 and endStatus=%d'%(SEQHIST, sessionID,prop[0],CYCLE_END)
#            ret = getDbData(sql,label)
#            totalNEAAbortSeq = int(ret[0][0])
#            print "     %s(%s)  TooManyMissed:%d CycleEnd:%d AlmostStarted:%d" % (prop[1], prop[2], totalNEAMissedSeq, totalNEAAbortSeq, totalNEAAlmostSeq)
#        elif prop[1] == 'SN':
#            sql = 'select count(*) from %s where sessionID=%d and propID = %d and completion < 1'%(SEQHIST, sessionID,prop[0])
#            ret = getDbData(sql,label)
#            totalSNMissedSeq = int(ret[0][0])
#            print "     %s(%s)  TooManyMissed:%d" % (prop[1],prop[2],totalSNMissedSeq)
#        elif prop[1] == 'SNSS':
#            sql = 'select count(*) from %s where sessionID=%d and propID = %d and completion < 1'%(SEQHIST, sessionID,prop[0])
#            ret = getDbData(sql,label)
#            totalSNSSMissedSeq = int(ret[0][0])
#            print "     %s(%s)  TooManyMissed:%d" % (prop[1],prop[2],totalSNSSMissedSeq)
#        elif prop[1] == 'KBO':
#            sql = 'select count(*) from %s where sessionID=%d and propID = %d and completion < 1'%(SEQHIST, sessionID,prop[0])
#            ret = getDbData(sql,label)
#            totalKBOMissedSeq = int(ret[0][0])
#            print "     %s(%s)  TooManyMissed:%d" % (prop[1],prop[2],totalKBOMissedSeq)
#        elif prop[1] == 'WLTSS':
#            sql = 'select count(*) from %s where sessionID=%d and propID = %d and completion < 1'%(SEQHIST, sessionID,prop[0])
#            ret = getDbData(sql,label)
#            totalWLTSSMissedSeq = int(ret[0][0])
#            print "     %s(%s)  TooManyMissed:%d" % (prop[1],prop[2],totalWLTSSMissedSeq)

#    nea_neventlost = totalNEAMissedSeq
#    nea_nlunlost = totalNEAAbortSeq
#    kbo_neventlost =  totalSNSSMissedSeq
#    kbo_nlunlost = 0                 # never terminates due to cycle end
#    snss_neventlost =  totalSNSSMissedSeq
#    snss_nlunlost = 0                 # never terminates due to cycle end
#    sn_neventlost =  totalSNMissedSeq
#    sn_nlunlost = 0                 # never terminates due to cycle end
#    wltss_neventlost =  totalWLTSSMissedSeq
#    wltss_nlunlost = 0                 # never terminates due to cycle end


    #-----------------------------------------------------------------------
    #       Additional SQL commands of interest
    #-----------------------------------------------------------------------
    # acquire Count of Hits per Field
    #label = 'Hits per Field'
    #sql = 'select fieldID, fieldRA,fieldDec, count(fieldID) from %s where 
    #       sessionID=%d group by fieldID'%(OBSHIST, sessionID)'
    #ret = getDbData(sql,label)
    #print "%s:" %(label)
    #for n in ret:
    #    #hitsPerField = int(ret[0][0])
    #    print "     Field:%d RA/Dec:(%f,%f) hits:%d" % (n[0], n[1], n[2], n[3])

    # acquire Count of Hits per Filter per Field  
    # SQL commands:
    #    first compress multiple proposals per obs into single unique entry
    #    second count up unique entries for each filter/field pair
    #    third, sort them by filter and field
    # create temporary table tmpO select fieldID,fieldRA,fieldDec,filter,expDate from ObsHistory where sessionID=2 group by expDate;
    # select *,count(expDate) from tmpO group by filter,fieldID order by filter, fieldID;
    # drop table tmpO;


    cumulativeData = {'nnights':nnights, 'nlun':nlun, 'nobs':nobs,
               'ncompl':ncompl}
#, 'sn_nlunlost':sn_nlunlost, 
#               'sn_neventlost':sn_neventlost, 'snss_nlunlost':snss_nlunlost,
#               'snss_neventlost':snss_neventlost,
#               'kbo_neventlost':kbo_neventlost, 'kbo_nlunlost':kbo_nlunlost,
#               'nea_neventlost':nea_neventlost, 'nea_nlunlost':nea_nlunlost,
#	       'wltss_neventlost':wltss_neventlost, 'wltss_nlunlost':wltss_nlunlost}

    if (excludeGalaxy == True):
        galaxyExclusion = {'taperL': taperL, 'taperB':taperB, 'peakL':peakL}
        galaxyExclusion0 = {'taperL': taperL, 'taperB':taperB, 'peakL':peakL}

    #print " done."

    return


# here begins the plotting code

def eqgal(l,b):
    # convert (l,b) to (ra,dec)
    l = l*math.pi/180.0
    b = b*math.pi/180.0
    sind = sin(b)*cos(1.0926)+ cos(b)*sin(l-0.5760)*sin(1.0926)
    sind = clip(sind,-1.0,1.0)
    dec = arcsin(sind)
    sinra = (cos(b)*sin(l - 0.5760)*cos(1.0926) - \
                    sin(b)*sin(1.0926))/cos(dec)
    cosra = cos(b)*cos(l - 0.5760)/cos(dec)
    cosra = clip(cosra,-1.0,1.0)
    ra = arccos(cosra)
    ra = where(sinra<0, 2.0*math.pi -ra, ra)
    dec = dec*180.0/math.pi
    ra = ra*180.0/math.pi + 282.25
    ra = where(ra>360.0,ra - 360.0, ra)
    ra = ra / 15.0

    return (ra, dec)


def project(ra, dec):
    """
    do the Aitoff projection
    (compromise between shape and scale distortion)
    """
                                                                               
    a = ra*math.pi/180.0
    d = dec*math.pi/180.0
    z = sqrt((1+cos(d)*cos(a/2.0))*0.5)+0.00001
    x = 2.0*cos(d)*sin(a/2.0)/z
    y = sin(d)/z
    del a, d, z
                                                                               
    return x, y


def meridian(ra):
    """
    create a meridian line at given ra
    """
    phi = arrayrange(-90,90)
    lam = zeros(len(phi)) + ra
 
    return lam, phi

 
def parallel(dec):
    """
    create a longitude line at given dec
    """
    lam = arrayrange(-180,180)
    phi = zeros(len(lam)) + dec
 
    return lam, phi

 
def aitoff():
    """
    plot the ra/dec grid on all plots
    with the ecliptic on the seq plot
    """
    
    global ax

    for dd in xrange(-90,91,30):
        [lam, phi] = parallel(dd)
        [x, y] = project(lam, phi)
        for k in ax.keys():
            ax[k].plot(x,y,color=WHITE)
         
    for rr in xrange(-180,181,30):
        [lam, phi] = meridian(rr)
        [x, y] = project(lam, phi)
        for k in ax.keys():
            ax[k].plot(x,y,color=WHITE)

    r = arrayrange(-180.0,181.0,30.0)
    d = arctan(sin(r*math.pi/180.0)*tan(23.43333*math.pi/180.0))*180.0/math.pi
    [x, y] = project(r, d)
    ax['seq'].plot(x, y, linewidth=3, color=WHITE)

    del d, r, lam, phi, x, y
    return


def excludePlot():
    global ax, galaxyExclusion

    pL = galaxyExclusion['peakL']
    tL = galaxyExclusion['taperL']
    tB = galaxyExclusion['taperB']
    band = pL - tL
 
    galL = arrayrange(-180.0, 181.0, 1.0)
    # top (in b) of galaxy exclusion zone
    xb = pL - band*abs(galL)/tB
    (Ra, Dec) = eqgal(galL, xb)
    Ra = Ra * 15.0
    Ra = where(Ra>180.0, Ra-360.0, Ra)
    [x, y] = project(Ra, Dec)
    for k in ax.keys():
        ax[k].plot(x,y,'w.')

    # bottom (in b) of galaxy exclusion zone
    (Ra, Dec) = eqgal(galL, -xb)
    Ra = Ra * 15.0
    Ra = where(Ra>180.0, Ra-360.0, Ra)
    [x, y] = project(Ra, Dec)
    for k in ax.keys():
        ax[k].plot(x,y,'w.')

    del galL, Ra, Dec, x, y, xb
    return


def docir(ra, dec, size, color, no, key):
    """
    plot a shaded circle (on the sky) at
    the given ra and dec
    """

    global ax

    db = []
    rb = []
    x = []
    y = []
    phi = arrayrange(0.0,361.0,30.0)
    for i in xrange(len(ra)):
        if color[i] != no:
            db = dec[i] + size*cos(phi*math.pi/180.0)
            rb = ra[i] - size*sin(phi*math.pi/180.0)/cos(db*math.pi/180.0)
            [x, y] = project(rb, db)
            ax[key].fill(x, y,  color[i], linewidth=0)

    del phi, db, rb, x, y

    return


def infoWrite(numFields, numsum, numPairs):
    """
    write the information panel
    """

    global ainfo, cumulativeData, interval, propName, propNumber, propCompleted, propLostMissedEvent, propLostCycleEnd

    left = 0
    right = 0.35
    row = 1.1
    string = "%d nights computed" % cumulativeData['nnights']
    ainfo.text(left, row, string, bigfont, horizontalalignment='left', \
               color=WHITE)
    string = "%d lunations computed" % cumulativeData['nlun']
    ainfo.text(right, row, string, bigfont, horizontalalignment='left', \
               color=WHITE)

    row -= 0.15
    if interval[0] == 0 and interval[1]/86400.0 > 10000:
        string = "showing all"
    elif interval[1]/86400.0 > 10000:
        string = "showing from %5.1f to end" % (interval[0]/86400.0)
    else:
        string = "showing from %5.1f to %5.1f" % \
                 (interval[0]/86400.0, interval[1]/86400.0)
    ainfo.text(left, row, string, bigfont, horizontalalignment='left', \
               color=WHITE)
    string = "showing from %d to %d" % (0, cumulativeData['nlun'])
    ainfo.text(right, row, string, bigfont, horizontalalignment='left', \
               color=WHITE)
    
    row -= 0.15

    right1 = right
#    right2 = right1 + 0.18
#    right3 = right2 + 0.10
#    right4 = right3 + 0.10
#    right5 = right4 + 0.10
#    right6 = right5 + 0.10

    string = "%d fields observed" % numFields
    ainfo.text(left, row,string,bigfont,horizontalalignment='left', \
               color=WHITE)
    #string = "Proposals "
    #ainfo.text(right1, row,string,smallfont,horizontalalignment='left', \
    #           color=WHITE)
#    string = "NEA"
    column = {}
    for k in range(len(propName)):
	column[k] = right1+0.18+0.12*k
	string = propName[k]
	string = string.replace('./','')
	string = string.replace('SubSeq','')
	string = string.replace('Prop','')
	string = string.replace('.conf','')
	ainfo.text(column[k], row-0.1*(k%2),string,smallfont,horizontalalignment='left', \
	           color=WHITE)
#    string = "SN"
#    ainfo.text(right3, row,string,smallfont,horizontalalignment='left', \
#               color=WHITE)
#    string = "SNSS"
#    ainfo.text(right4, row,string,smallfont,horizontalalignment='left', \
#               color=WHITE)
#    string = "KBO"
#    ainfo.text(right5, row,string,smallfont,horizontalalignment='left', \
#               color=WHITE)
#    string = "WLTSS"
#    ainfo.text(right6, row,string,smallfont,horizontalalignment='left', \
#               color=WHITE)
    row -= 0.2
    string = "Completed" 
    ainfo.text(right1, row,string,smallfont,horizontalalignment='left', \
               color=WHITE)
#    string = "%d" % numsum['NEA']
    for k in range(len(propName)):
	string = "%d" % propCompleted[k]
	ainfo.text(column[k], row,string,smallfont,horizontalalignment='left', \
		   color=WHITE)
#    string = "%d" % numsum['SN']
#    ainfo.text(right3, row,string,smallfont,horizontalalignment='left', \
#               color=WHITE)
#    string = "%d" % numsum['SNSS']
#    ainfo.text(right4, row,string,smallfont,horizontalalignment='left', \
#               color=WHITE)
#    string = "%d" % numsum['KBO']
#    ainfo.text(right5, row,string,smallfont,horizontalalignment='left', \
#               color=WHITE)
#    string = "%d" % numsum['WLTSS']
#    ainfo.text(right6, row,string,smallfont,horizontalalignment='left', \
#               color=WHITE)

    left1 = left
    left2 = left1 + 0.15
    row -= 0.1
    string = "Observations"
    ainfo.text(left1, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
    string = "Lost Sequences"
    ainfo.text(right1, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
    row -= 0.1
    string = "r: %d" % numsum['r']
    ainfo.text(left1, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
    string = "z: %d" % numsum['z']
    ainfo.text(left2, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
    string = "      Cycle End" 
    ainfo.text(right1, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
#    string = "%d" % cumulativeData['nea_nlunlost']
    for k in range(len(propName)):
	string = "%d" % propLostCycleEnd[k]
	ainfo.text(column[k], row, string, smallfont, horizontalalignment='left', \
		   color=WHITE)
#    string = "%d" % cumulativeData['sn_nlunlost']
#    ainfo.text(right3, row, string, smallfont, horizontalalignment='left', \
#               color=WHITE)
#    string = "%d" % cumulativeData['snss_nlunlost']
#    ainfo.text(right4, row, string, smallfont, horizontalalignment='left', \
#               color=WHITE)
#    string = "%d" % cumulativeData['kbo_nlunlost']
#    ainfo.text(right5, row, string, smallfont, horizontalalignment='left', \
#               color=WHITE)
#    string = "%d" % cumulativeData['wltss_nlunlost']
#    ainfo.text(right6, row, string, smallfont, horizontalalignment='left', \
#               color=WHITE)
    row -= 0.1
    string = "g: %d" % numsum['g']
    ainfo.text(left1, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
    string = "y: %d" % numsum['y']
    ainfo.text(left2, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
    string = "      Missed Event" 
    ainfo.text(right1, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
#    string = "%d" % cumulativeData['nea_neventlost']
    for k in range(len(propName)):
	string = "%d" % propLostMissedEvent[k]
	ainfo.text(column[k], row, string, smallfont, horizontalalignment='left', \
		   color=WHITE)
#    string = "%d" % cumulativeData['sn_neventlost']
#    ainfo.text(right3, row, string, smallfont, horizontalalignment='left', \
#               color=WHITE)
#    string = "%d" % cumulativeData['snss_neventlost']
#    ainfo.text(right4, row, string, smallfont, horizontalalignment='left', \
#               color=WHITE)
#    string = "%d" % cumulativeData['kbo_neventlost']
#    ainfo.text(right5, row, string, smallfont, horizontalalignment='left', \
#               color=WHITE)
#    string = "%d" % cumulativeData['wltss_neventlost']
#    ainfo.text(right6, row, string, smallfont, horizontalalignment='left', \
#               color=WHITE)
    row -= 0.1
    string = "i: %d" % numsum['i']
    ainfo.text(left1, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
    string = "u: %d" % numsum['u']
    ainfo.text(left2, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)
    row -= 0.2
    string = "%d pairs" % numPairs
    ainfo.text(left, row,string,bigfont,horizontalalignment='left', \
               color=WHITE)

    row -= 0.3
    props = "    "
    for n in propID:
         props += "%d " % (n)
    string = "session ID: %d FOV: %4.2f proposal IDs: %s" % (sessionID,FOV, props)
    ainfo.text(left1, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)

    row -= 0.15
# mm - change date here
    string = "Session Date: %s " % (sessDate) + socket.gethostname()
    #string = time.ctime(time.time()) + "  " + socket.gethostname()
    ainfo.text(left1, row, string, smallfont, horizontalalignment='left', \
               color=WHITE)


    ainfo.set_axis_off()
    ainfo.set_xlim([0,1])
    ainfo.set_ylim([0,1])

    return


def leglab(title, word, nmin, nmax, a):
    """
    make labels for and draw the colormaps
    """

    x0 = -2.9
    dx = 5.7
    y0 = -1.74
    dy = 0.1
    
    i = -1

    colors = get_cmap()
    
    delx = 0.01*dx
    for ix in xrange(100):
        cx = ix * 0.01
        xpos = cx*dx + x0
        ccc = matplotlib.colors.rgb2hex(colors(cx)[:-1])
        x = [xpos,xpos+delx,xpos+delx,xpos]
        y = [y0, y0, y0+dy, y0+dy]
        fill(x,y,ccc,edgecolor=ccc,linewidth=0)

    str = "%d" % int(nmin)
    a.text(x0,y0-dy,str, smallfont, horizontalalignment='center', color=WHITE)
    str = "%d" % int(nmax)
    a.text(x0+dx,y0-dy,str, smallfont, horizontalalignment='center', color=WHITE)

    a.text(0.0,-1.6,title, bigfont, horizontalalignment='center', color=WHITE)
    
    a.set_axis_off()
    a.set_xlim([-3,3])
    a.set_ylim([-2.1,-1.55])
    
    return

def refresh6():
    """
    create the graphics
    """

    global ax, ainfo, acmapf, acmaps, pnum, collim, excludeGalaxy, MAX

    print "refresh start:", time.asctime()
    pnum['u'] = 621
    pnum['g'] = 622
    pnum['r'] = 623
    pnum['i'] = 624
    pnum['z'] = 625
    pnum['y'] = 626
    pnum['pairs'] = 627
    pnum['seq'] = 628

    # the sky panels
    for k in ax.keys():
        ax[k].cla()
    for k in pnum.keys():
        ax[k] = subplot(pnum[k])

    (ra, dec, nums) = makeData()

    ra = ra * 15.0
    ra = where(ra>180.0,ra-360.0,ra)

    colors = get_cmap()
    no = matplotlib.colors.rgb2hex(colors(0.0)[:-1])

    # Determine range of Filter Hits for color strip
#    big = float(max([max(nums[k]) for k in ['u','g','r','i','z','y']]))
#    if collim['obsmax'] == 0:
#        collim['obsmax'] = big
#        collim['obsmin'] = 0

#    siz = (collim['obsmax']-collim['obsmin'])

    siz = {}
    for k in ['u','g','r','i','z','y']:
	big = float(max(nums[k]))
#	if collim['obsmax'] == 0:
	if MAX[k] == 0:
	    collim[k] = big
	    collim['obsmin'] = 0
	    siz[k] = (collim[k]-collim['obsmin'])
 	else:
#            siz[k] = (collim['obsmax']-collim['obsmin'])
	    siz[k] = (MAX[k]-collim['obsmin'])

    for k in ['u','g','r','i','z','y']:
	if siz[k]>0:
            x = clip([(float(q)-collim['obsmin'])/siz[k] for q in nums[k]],0.0,1.0)
            cols = [matplotlib.colors.rgb2hex(colors(q)[:-1]) for q in x]
            docir(ra, dec, FOV/2.0, cols, no, k)
        label = "Visits/Field: %s max=%d" % (k, siz[k])
        ax[k].text(0, 1.51, label, bigfont, horizontalalignment='center')


    # the colormap panel
#    try:
#        acmapf.cla()
#    except NameError:
#        pass

#    acmapf = subplot(12,2,19)
#    leglab("Visits/Field", "epochs", \
#           collim['obsmin'], collim['u'], acmapf)


    # Determine range of Completed Sequences for color strip
    big = float(max(nums['seq']))
    if collim['seqobsmax'] == 0:
        collim['seqobsmax'] = big
        collim['seqobsmin'] = 0


    siz = (collim['seqobsmax']-collim['seqobsmin'])
    if siz == 0 :
	siz=1

    x = clip([(float(q)-collim['seqobsmin'])/siz for q in nums['seq']],0.0,1.0)
    cols = [matplotlib.colors.rgb2hex(colors(q)[:-1]) for q in x]
    docir(ra, dec, FOV/2.0, cols, no, 'seq')
    label = "Sequences"
    ax['seq'].text(0, 1.51, label, bigfont, horizontalalignment='center')

    try:
        acmaps.cla()
    except NameError:
        pass

    acmaps = subplot(12,2,18)
    leglab("Sequences", "sequences",\
           collim['seqobsmin'], collim['seqobsmax'], acmaps)

###################################
    # Determine range of Pairs count for color strip
    big = float(max(nums['pairs']))
    print "maxnumspairs = %d" % (big)
    if collim['pairsmax'] == 0:
        collim['pairsmax'] = big
        collim['pairsmin'] = 0
                                                                                                                 
                                                                                                                 
    siz = (collim['pairsmax']-collim['pairsmin'])
    if siz == 0 :
        siz=1
                                                                                                                 
    x = clip([(float(q)-collim['pairsmin'])/siz for q in nums['pairs']],0.0,1.0)
    cols = [matplotlib.colors.rgb2hex(colors(q)[:-1]) for q in x]
    docir(ra, dec, FOV/2.0, cols, no, 'pairs')
    label = "Pairs"
    ax['pairs'].text(0, 1.51, label, bigfont, horizontalalignment='center')

    # the colormap panel
    try:
        acmapp.cla()
    except NameError:
        pass
                                                                                                                                                                                                     
    acmapp = subplot(12,2,17)
    leglab("Pairs/Field", "epochs", \
           collim['pairsmin'], collim['pairsmax'], acmapp)
                                                                                                                 
#####################################

    aitoff()

    if (excludeGalaxy == True):
       excludePlot()

    for k in ax.keys():
        ax[k].set_xlim([-3,3])
        ax[k].set_ylim([-1.5,1.5])
        ax[k].set_axis_off()

    
    # the information panel
    try:
        ainfo.cla()
    except NameError:
        pass

    ainfo = subplot(6,1,6)
    numFields = len(ra)
    numsum = {}
    for k in pnum.keys():
        numsum[k] = sum(nums[k])

    # Determine each Sequence type's total number of completions
    #   RAA: this could be done more generically with an overarching list of 
    #       Sequence-based proposal names but this suffices for now...
    numsum['SNSS']= sum(nums['SNSS'])
    numsum['KBO']= sum(nums['KBO'])
    numsum['SN']= sum(nums['SN'])
    numsum['NEA']= sum(nums['NEA'])
    numsum['WLTSS']=sum(nums['WLTSS'])

    numPairs=sum(nums['pairs'])

    infoWrite(numFields, numsum, numPairs)

    print "refresh end:", time.asctime()
    return


def parseInput():
    global interval, galaxyExclusion, galaxyExclusion0
    global propID, availableProps, collim, MAX
    
    done = False
    
    while not done:
        success = False
        while not success:
            print ">>> ",
            a = sys.stdin.readline()
            args = a.split()
            if len(args) == 0:
                success = True

            elif args[0] == 'h' or args[0] == 'help':
                print " "
                print "commands are:"
		print " max [filter number] to change filter colormap max scale"
		print "     [no args] to reset to each max visits count"
                print " color [number number] to change field colormap interval"
                print " color (no args) to reset field colormap interval"
                print " ncolor [number number] to change seq colormap interval"
                print " ncolor (no args) to reset seq colormap interval"
                print " days [number number] to change range of days"
                print "      (no args) to reset to all days"
                print " exclude to set galaxy exclusion values"
                print " reread to re-read the database"
                print " prop [list of integers] to select these propIDs"
                print "      [all] to select all propIDs"
                print "      (no args) to see a list of availabls propIDs"
                print "      >> don't forget to reread after prop <<"
                print " plot to replot"
                print " save <filename> [dpi] to save a plot"
                print "      filename extension determines type of file:"
                print "      png, ps, eps, svg"
                print " q to quit"
                print " "
                success = True

	    elif args[0] == 'max':
		if len(args) >= 3:
		    MAX[args[1]] = int(args[2])
		else:
		    for f in ['u','g','r','i','z','y']:
			MAX[f] = 0
		success = True
            elif args[0] == 'color':
                if len(args) == 3:
                    collim['obsmin'] = float(args[1])
                    collim['obsmax'] = float(args[2])
                    success = True
                elif len(args) == 1:
                    collim['obsmax'] = 0
                    success = True
                    

            elif args[0] == 'ncolor':
                if len(args) == 3:
                    collim['seqobsmin'] = float(args[1])
                    collim['seqobsmax'] = float(args[2])
                    success = True
                elif len(args) == 1:
                    collim['seqobsmax'] = 0
                    success = True

            elif args[0] == 'reread':
                createDataset()
                cumulativeCountSummary()
                success = True

            elif args[0] == 'prop':
                if len(args) == 1:
                    print "available proposal IDs are: ",
                    for n in availableProps:
                        print "%d (%s)  " % (int(n[0]),n[1]) ,
                    print ""
                    success = True
                elif args[1] == "all":
                    for n in availableProps:
                        propID.append(int(n[0]))
                    print "don't forget to reread DB"
                    success = True
                else:
                    try:
                        propID = [int(x) for x in args[1:]]
                        success = True
                        print "don't forget to reread DB"
                    except:
                        pass

            elif args[0] == 'days':
                if len(args) > 1:
                    aa = re.match(r"[0-9]+[.]?[0-9]*",args[1])
                    if aa != None:
                        interval[0] = eval(args[1])
                        aa = re.match(r"[0-9]+[.]?[0-9]*",args[2])
                        if aa != None:
                            interval[1] = eval(args[2])
                            if interval[0] < interval[1]:
                                success = True
                                print "setting interval to ", interval
                                interval = interval*86400.0
                else:
                    print "selecting full interval"
                    interval = array([0.0,1000000.0])*86400.0
                    success = True

            elif args[0] == 'exclude':
                print "Setting galaxy exclusion:"
                print "r to reset, or"
                print "width above and below galactic center: ",
                aa = sys.stdin.readline()
                if re.match(r"r",aa)!= None:
                    print "resetting to original values"
                    for k in galaxyExclusion.keys():
                        galaxyExclusion[k] = galaxyExclusion0[k]
                else:
                    galaxyExclusion['peakL'] = eval(aa)
                    print "extent in galactic longitude: ",
                    aa = sys.stdin.readline()
                    galaxyExclusion['taperB'] = eval(aa)
                    print "width above and below at maximum longitude: ",
                    aa = sys.stdin.readline()
                    galaxyExclusion['taperL'] = eval(aa)

                success = True

            elif args[0] == 'plot':                        
                print "plotting..."
                success = True
                done = True

            elif args[0] == 'save':
                if len(args) > 1:
                    filename = args[1]
                    print "saving to file", filename,
                    res = 60
                    if len(args) > 2:
                        res = int(args[2])
                        print "at %d dpi" %(res)
                    else:
                        print

                    savefig(filename, dpi=res, facecolor='k',
                            edgecolor='k',orientation='portrait')
                    success = True
                    done = True

            elif args[0] == 'q' or args[0] == 'quit':
                sys.exit()

            if not success: print "bad input: ", a

    return


def updatefig(*args):
    """
    called by gtk
    """
    print "updatefig start:", time.asctime()

    parseInput()
    print "updatefig aft parseInput:", time.asctime()

    refresh6()
    print "updatefig aft refresh6:", time.asctime()
    
    # print_top(10)

    manager.canvas.draw()
    print "updatefig aft canvasdraw:", time.asctime()
 
    return gtk.TRUE
 

fig = figure(num=1, figsize=(9,11), facecolor='k', edgecolor='k')
pnum = {}
ax = {}

# command syntax:  ./newextract.py <sessionID> 
try:
    val = sys.argv[1:]
    sessionID = int (val[0])
except:
    print "\n\n..........No session parameter found!"
    print "..........Use newextract.py <sessionID>\n\n"
    done 

print "Session ID: %d " % (sessionID)
interval = array([0.0,1000000.0])*86400.0
interval = interval*86400.0
collim = {}
collim['obsmin'] = 0
collim['obsmax'] = 0
collim['seqobsmin'] = 0
collim['seqobsmax'] = 0
collim['pairsmin'] = 0
collim['pairsmax'] = 0
MAX = {}
for k in ['u','g','r','i','z','y']:
    MAX[k] = 0

cumulativeCountSummary()
propID = [int(n[0]) for n in availableProps]
createDataset()

refresh6()
print " type h for help"

manager = get_current_fig_manager()
 
#gtk.timeout_add(250, updatefig)
gtk.timeout_add(500, updatefig)
show()
