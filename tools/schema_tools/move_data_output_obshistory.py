#!/usr/bin/env python

import sys, re, time, socket
import math
import MySQLdb as mysqldb
import os
from ETC import ETC
from socket import gethostname
try:
	import slalib
except:
    import pysla as slalib

def connect_db(hostname='localhost', username='www', passwdname='zxcvbnm', dbname='OpsimDB'):   
    # connect to lsst_pointings (or other) mysql db, using account that has 'alter table' privileges
    # connect to the database - this is modular to allow for easier modification from machine/machine    
    db = mysqldb.connect(host=hostname, user=username, passwd=passwdname, db=dbname)
    cursor = db.cursor()
    db.autocommit(True)
    return cursor

def getDbData(database, sql):
    global sessionID
    cursor = connect_db(dbname=database)
    # Fetch the data from the DB
    ret = {}
    try:
        n = cursor.execute (sql)
	ret = cursor.fetchall ()
    except:
        sys.stderr.write('Unable to execute SQL query (%s)\n' % (sql) )
    # Close the connection
    cursor.close ()
    del (cursor)
    return (ret)

def insertDbData(database, sql):
	global sessionID
	cursor = connect_db(dbname=database)
	try:
		cursor.execute(sql)
	except:
		sys.stderr.write('Unable to execute SQL query (%s)\n' % (sql) )
	# Close the connection
	cursor.close ()
	del (cursor)

def copy_data_over(hname, database, sessionID):
	# print 'Copying data over'
	sql = 'use %s' % (database)
        ret = getDbData(database, sql)
	sql = 'select obsHistID, fivesigma, hexdithRA, hexdithDec from output_%s_%d' % (hname, sessionID)
	ret = getDbData(database, sql)
	
	for k in range(len(ret)):
		obsHistID = ret[k][0]
		fiveSigmaDepth = ret[k][1]
		ditheredRA = ret[k][2]
		ditheredDec = ret[k][3]
		sql = 'update tObsHistory_%s_%d set fiveSigmaDepth=%f, ditheredRA=%f, ditheredDec=%f where obsHistID=%d' % (hname, sessionID, fiveSigmaDepth, ditheredRA, ditheredDec, obsHistID)
		insertDbData(database, sql)

if __name__ == "__main__":
    import sys
    if len(sys.argv)<4:
        print "Usage : './move_data_output_obshistory.py <realhostname> <databasename> <sessionID>'"
        sys.exit(1)
    hname = sys.argv[1]
    database = sys.argv[2]
    sessionID = sys.argv[3]
    copy_data_over(hname, database, int(sessionID));

