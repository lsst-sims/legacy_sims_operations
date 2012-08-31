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

def testSeqBug(propID):

    label = 'sequences'

    sql   = 'select sequenceID,fieldID,startDate,actualEvents from SeqHistory where propID=%d' % (propID)
    print sql
    ret   = getDbData(sql, label)
    seqTable = {}
    for ix in range(len(ret)):
	(sequenceID,fieldID,startDate,actualEvents) = ret[ix]
	if startDate != 0 or actualEvents != 0:
	    seqTable[startDate] = (sequenceID,fieldID,actualEvents)

    sql   = 'select fieldID,expDate,seqnNum,count(0) from ObsHistory where propID=%d group by seqnNum' % (propID)
    print sql
    ret   = getDbData(sql, label)
    obsTable = {}
    for ix in range(len(ret)):
	(fieldID,expDate,seqnNum,count) = ret[ix]
	obsTable[expDate] = (seqnNum,fieldID,count)
 
    correct = wrong = 0
    for t in seqTable.keys():
	actualEvents = seqTable[t][2]
	observations = obsTable[t][2]
	if observations == actualEvents:
            correct+=1
        else:
            wrong  +=1
	    sequenceID = seqTable[t][0]
	    sfieldID   = seqTable[t][1]
	    seqnNum    = obsTable[t][0]
	    ofieldID   = obsTable[t][1]
	    print 'wrong sequenceID=%d, seqnNum=%d, fieldID=%d=%d, actualEvents=%d, observations=%d' % (sequenceID,seqnNum,sfieldID,ofieldID,actualEvents,observations)
    print 'correct sequences=%d, wrong sequences=%d' % (correct,wrong)

try:
    val = sys.argv[1:]
    propID = int (val[0])
except:
    print "\n\n..........No proposal parameter found!"
    print "..........Use testSeqBug.py <propID>\n\n"
    done 

print "Proposal ID: %d " % (propID)

testSeqBug(propID)

