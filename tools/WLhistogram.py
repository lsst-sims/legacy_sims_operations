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


def reportWLhist(propID):

    label = 'Weak Lensing Histogram'
    sql   = 'select paramName,paramValue from Config where propID=%d order by paramIndex' % (propID)
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

    f1 = dict_WL['Filter'][0]
    f2 = dict_WL['Filter'][1]
    f3 = dict_WL['Filter'][2]
    f4 = dict_WL['Filter'][3]
    f5 = dict_WL['Filter'][4]
                                                                                
    f1Visits = eval(dict_WL[str(f1)+'FilterVisits'])
    f2Visits = eval(dict_WL[str(f2)+'FilterVisits'])
    f3Visits = eval(dict_WL[str(f3)+'FilterVisits'])
    f4Visits = eval(dict_WL[str(f4)+'FilterVisits'])
    f5Visits = eval(dict_WL[str(f5)+'FilterVisits'])


    sql = 'DROP TABLE IF EXISTS tmpObs, tmpObs1, tmpVisits'
    ret = getDbData(sql, label)

    sql = 'create table tmpObs select propID,fieldID,fieldRA,fieldDec,filter,expDate from ObsHistory where propID=%d group by expDate order by propID,fieldID,filter' % (propID)
    ret = getDbData(sql, label)

    sql = 'create table tmpObs1 select *,count(filter) as visits from tmpObs group by propID,fieldID,filter order by propID,fieldID,filter'
    ret = getDbData(sql, label)

    sql = 'create table tmpVisits select fieldID,'
    sql+= 'sum(if(filter="%s", visits, 0)) as Nf1,' % (f1)
    sql+= 'sum(if(filter="%s", visits, 0)) as Nf2,' % (f2)
    sql+= 'sum(if(filter="%s", visits, 0)) as Nf3,' % (f3)
    sql+= 'sum(if(filter="%s", visits, 0)) as Nf4,' % (f4)
    sql+= 'sum(if(filter="%s", visits, 0)) as Nf5'  % (f5)
    sql+= ' from tmpObs1 group by fieldID'
    ret = getDbData(sql, label)

    sql = 'select Nf1,count(0) from tmpVisits group by Nf1'
    ret = getDbData(sql, label)
    H1  = ret
    sql = 'select Nf2,count(0) from tmpVisits group by Nf2'
    ret = getDbData(sql, label)
    H2  = ret
    sql = 'select Nf3,count(0) from tmpVisits group by Nf3'
    ret = getDbData(sql, label)
    H3  = ret
    sql = 'select Nf4,count(0) from tmpVisits group by Nf4'
    ret = getDbData(sql, label)
    H4  = ret
    sql = 'select Nf5,count(0) from tmpVisits group by Nf5'
    ret = getDbData(sql, label)
    H5  = ret

    if f1Visits>0:
	for p in range(len(H1)):
	    print "%s %6.2f%% %d" % (f1, H1[p][0]*100.0/f1Visits, H1[p][1])
    if f2Visits>0:
    	for p in range(len(H2)):
            print "%s %6.2f%% %d" % (f2, H2[p][0]*100.0/f2Visits, H2[p][1])
    if f3Visits>0:
	for p in range(len(H3)):
            print "%s %6.2f%% %d" % (f3, H3[p][0]*100.0/f3Visits, H3[p][1])
    if f4Visits>0:
    	for p in range(len(H4)):
            print "%s %6.2f%% %d" % (f4, H4[p][0]*100.0/f4Visits, H4[p][1])
    if f5Visits>0:
    	for p in range(len(H5)):
            print "%s %6.2f%% %d" % (f5, H5[p][0]*100.0/f5Visits, H5[p][1])

    sql = 'DROP TABLE IF EXISTS tmpObs, tmpObs1, tmpVisits'
    ret = getDbData(sql, label)

    return

# command syntax:  ./newextract.py <sessionID> 
try:
    val = sys.argv[1:]
    propID = int (val[0])
except:
    print "\n\n..........No proposal parameter found!"
    print "..........Use WLhistogram.py <propID>\n\n"
    done 

reportWLhist(propID)

