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


def seqReport(propID):
                                                                                                                                                                            
    label = 'Filter hits in lost sequences due to too many missed events'
    sql   = 'select sequenceID,fieldID,startDate,actualEvents from SeqHistory where propID=%d and endStatus=1' % (propID)
    print sql
    ret   = getDbData(sql, label)
    if ret == None:
        return
    if len(ret) == 0:
        return

    print 'building sequences dictionary'
    seqTable = {}
    for ix in range(len(ret)):
	(sequenceID,fieldID,startDate,actualEvents) = ret[ix]
	if startDate != 0 or actualEvents != 0:
	    seqTable[startDate] = (sequenceID,fieldID,actualEvents)
    print '%s: analyzing %d sequences' % (label,len(seqTable))

    sql   = 'select seqnNum,fieldID,filter,expDate,count(0) from ObsHistory where propID=%d group by seqnNum,filter' % (propID)
    print sql
    ret   = getDbData(sql, label)

    print 'building observations dictionary'
    obsTable = {}
    prev_seqnNum = 0
    for ix in range(len(ret)):
	(seqnNum,fieldID,filter,expDate,hits) = ret[ix]
	if seqnNum != prev_seqnNum:
	    if prev_seqnNum != 0:
		obsTable[firstDate] = pattern
	    prev_seqnNum = seqnNum
	    firstDate = expDate
	    pattern = '%s:%d' % (filter,hits)
	else:
	    firstDate = min(firstDate,expDate)
	    pattern += ' %s:%d' % (filter,hits)
    obsTable[firstDate] = pattern

    print 'building patterns dictionary'
    counts = {}
    for t in seqTable.keys():
	pattern = obsTable[t]
	if pattern in counts.keys():
	    counts[pattern] += 1
	else:
	    counts[pattern] = 1
#	    print 'new pattern: %s' % (str(pattern))

    patternlist = counts.keys()
    patternlist.sort()
    for pattern in patternlist:
	print 'pattern count: %4d   %s' % (counts[pattern],str(pattern))

    return

# command syntax:  ./newextract.py <sessionID> 
try:
    val = sys.argv[1:]
    propID = int (val[0])
except:
    print "\n\n..........No proposal parameter found!"
    print "..........Use newextract.py <propID>\n\n"
    done 

print "Proposal ID: %d " % (propID)

seqReport(propID)

