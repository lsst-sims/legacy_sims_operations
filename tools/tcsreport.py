#!/usr/bin/env python

import sys, re, time, socket
import math
import MySQLdb
from LSSTDBInit import *

# SeqHistory Sequence completion status
SUCCESS = 0
MAX_MISSED_EVENTS = 1
CYCLE_END = 2

# TimeHistory Events
START_NIGHT = 0
MOON_WANING = 1         # New lunation, too
MOON_WAXING = 2
NEW_YEAR = 3

RAD2DEG = 180.0/math.pi
DEG2RAD = math.pi/180.0

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


def tcsreport(sessionID):

    label = 'session info'
    sql = 'select sessionHost, sessionDate from Session where sessionID=%d' % (sessionID)
    ret = getDbData (sql, label)
    host = ret[0][0]
    startDate = ret[0][1]
    print "Session ID: %d\tHost: %s\tSession Start Date: %s" % (sessionID,host,startDate)

    label = 'config'
    sql   = 'select paramName,paramValue from Config where sessionID=%d and moduleName="LSST" order by paramIndex' % (sessionID)
    config_LSST   = getDbData(sql, label)
    dict_LSST = {}
    for kv in config_LSST:
#	print kv
	dict_LSST[kv[0]] = kv[1]
#    print dict_LSST

    site  = dict_LSST['siteConf']
    print "%s: %s" % (label, site)

    label = 'number of nights'
    sql   = 'select count(event) from TimeHistory where sessionID=%d and event=%d' % (sessionID, START_NIGHT)
    ret   = getDbData(sql, label)
    count_nights = int(ret[0][0])
    print "%s: %s" % (label, count_nights)

    label = 'number of exposures'
    sql   = 'select count(*) from SlewHistory where sessionID=%d' % (sessionID)
    ret   = getDbData(sql, label)
    count_exposures = ret[0][0]
    print "%s: %s" % (label, count_exposures)
    print "exposures/night: %6.1f" % (float(count_exposures)/count_nights)

    notcs = True
    if notcs == False:
	reportAngleStats('TelAlt', sessionID)
	reportAngleStats('TelAz' , sessionID)
	reportAngleStats('RotPos', sessionID)

	reportActivity('DomAlt'     , sessionID, count_exposures)
	reportActivity('DomAz'      , sessionID, count_exposures)
	reportActivity('TelAlt'     , sessionID, count_exposures)
	reportActivity('TelAz'      , sessionID, count_exposures)
	reportActivity('Rotator'    , sessionID, count_exposures)
	reportActivity('Filter'     , sessionID, count_exposures)
	reportActivity('TelOpticsOL', sessionID, count_exposures)
	reportActivity('Readout'    , sessionID, count_exposures)
	reportActivity('Settle'     , sessionID, count_exposures)
	reportActivity('DomSettle'  , sessionID, count_exposures)
	reportActivity('TelOpticsCL', sessionID, count_exposures)

	reportMaxSpeed('DomAlt', sessionID)
	reportMaxSpeed('DomAz' , sessionID)
	reportMaxSpeed('TelAlt', sessionID)
	reportMaxSpeed('TelAz' , sessionID)
	reportMaxSpeed('Rot'   , sessionID)

    reportSlewDistance('TelAlt', sessionID, count_nights)

def reportAngleStats(name, sessionID):

    label = 'statistics for angle %9s' % (name)
    sql   = 'select min(%s),max(%s),avg(%s),std(%s) from SlewFinalState where sessionID=%d' % (name, name, name, name, sessionID)
    ret   = getDbData(sql, label)
    print "%s: min=%6.1fd max=%6.1fd avg=%6.1fd std=%5.1fd" % (label, ret[0][0]*RAD2DEG, ret[0][1]*RAD2DEG, ret[0][2]*RAD2DEG, ret[0][3]*RAD2DEG)
    
def reportActivity(name, sessionID, total):

    label = 'slew activity for %12s' % (name)
    sql   = 'select avg(delay),max(delay),count(delay) from SlewActivities where sessionID=%d and activity="%s" and delay>0' % (sessionID, name)
    ret   = getDbData(sql, label)
    A     = ret[0][0]
    M     = ret[0][1]
    N     = ret[0][2]
    sql   = 'select count(*),avg(delay) from SlewActivities where sessionID=%d and activity="%s" and inCriticalPath="True" and delay>0' % (sessionID, name)
    ret   = getDbData(sql, label)
    C     = ret[0][0]
    CA    = ret[0][1]
    if CA == None:
	CA = 0.0
    if (A != None) and (C != None):
	print "%s: active=%5.1f%% of slews, active avg=%6.2fs, total avg=%6.2fs, max=%6.2fs, in critical path=%5.1f%% with avg=%6.2fs cont=%6.2fs" % (label, 100.0*N/total, A, A*N/total, M, 100.0*C/total, CA, CA*C/total)

def reportMaxSpeed(name, sessionID):

    label = 'slew maximum speed for %8s' % (name)
    sql   = 'select avg(abs(%sSpd)),max(abs(%sSpd)),max(slewCount) from SlewMaxSpeeds where sessionID=%d' % (name, name, sessionID)
    ret   = getDbData(sql, label)
    A     = ret[0][0]
    M     = ret[0][1]
    T     = ret[0][2]
    sql   = 'select count(*) from SlewMaxSpeeds where sessionID=%d and abs(%sSpd)>=%f' % (sessionID, name, 0.99*M)
    ret   = getDbData(sql, label)
    C     = ret[0][0]
    print "%s: avg=%.2fd/s, max=%.2fd/s in %5.1f%% of slews" % (label, A*RAD2DEG, M*RAD2DEG, 100.0*C/T)

    return

def reportSlewDistance(activity, sessionID, count_nights):

    label = 'slew distance report for %8s' % (activity)
    table = 'reportSlewDistance%d%s' % (sessionID, activity)
    step  = 3.5*DEG2RAD

    sql   = 'drop table if exists %s' % (table)
    ret   = getDbData(sql, label)

    sql   = 'create table %s select i.slewCount,abs(f.%s-i.%s) as distance,floor(abs(f.%s-i.%s)/%f)*%f as stepdistance from SlewInitState i,SlewFinalState f where i.sessionID=%d and f.sessionID=%d and i.slewCount=f.slewCount' % (table, activity, activity, activity, activity, step, step, sessionID, sessionID)
    ret   = getDbData(sql, label)

    sql   = 'select stepdistance,count(0) from %s group by stepdistance' % (table)
    H     = getDbData(sql, label)

    for k in range(len(H)):
	h = float(H[k][0])*RAD2DEG
	c = int(H[k][1])
	print "%s slew distance histogram, >=%5.1f <%5.1f degrees = %9d slews" % (activity, h, h+step*RAD2DEG, c)

    sql   = 'select count(0),sum(distance) from %s' % (table)
    S     = getDbData(sql, label)
    totalslews = int(S[0][0])
    sumdist    = float(S[0][1])*RAD2DEG

    print "%s total slews = %d" % (activity, totalslews)
    print "%s total accumulated slew distance = %.0f degrees" % (activity, sumdist)
    print "%s accumulated slew distance per night = %.0f degrees" % (activity, sumdist/count_nights)

    sql   = 'drop table if exists %s' % (table)
    ret   = getDbData(sql, label)

try:
    val = sys.argv[1:]
    sessionID = int (val[0])
except:
    print "\n\n..........No session parameter found!"
    print "..........Use tcsreport.py <sessionID>\n\n"
    done 

tcsreport(sessionID)

