#!/usr/bin/env python

import sys, re, time, socket
import math
import MySQLdb as mysqldb
import os
from socket import gethostname

def connect_db(hostname='localhost', username='www', passwdname='zxcvbnm', dbname='OpsimDB'):
    # connect to lsst_pointings (or other) mysql db, using account that has 'alter table' privileges
    # connect to the database - this is modular to allow for easier modification from machine/machine
    db = None
    conf_file = os.path.join(os.getenv("HOME"), ".my.cnf")
    if os.path.isfile(conf_file):
        db = mysqldb.connect(read_default_file=conf_file, db=dbname)
    else:
        db = mysqldb.connect(host=hostname, user=username, passwd=passwdname, db=dbname)
    cursor = db.cursor()
    db.autocommit(True)
    return cursor

def getDbData(cursor, sql):
    global sessionID
    # Fetch the data from the DB
    ret = {}
    n = cursor.execute(sql)
    ret = cursor.fetchall()
    return ret

def insertDbData(cursor, sql):
	global sessionID
	cursor.execute(sql)

def copy_data_over(hname, database, cursor, sessionID):
	# print 'Copying data over'
    sql = 'use %s' % (database)
    ret = getDbData(cursor, sql)
    sql = 'select obsHistID, fiveSigmaDepth, ditheredRA, ditheredDec from summary_%s_%d' % (hname, sessionID)
    ret = getDbData(cursor, sql)

    for k in range(len(ret)):
	   obsHistID = ret[k][0]
	   fiveSigmaDepth = ret[k][1]
	   ditheredRA = ret[k][2]
	   ditheredDec = ret[k][3]
	   sql = 'update tObsHistory_%s_%d set fiveSigmaDepth=%f, ditheredRA=%f, ditheredDec=%f where obsHistID=%d' % (hname, sessionID, fiveSigmaDepth, ditheredRA, ditheredDec, obsHistID)
	   insertDbData(cursor, sql)

if __name__ == "__main__":
    import sys
    if len(sys.argv)<4:
        print "Usage : './move_data_output_obshistory.py <realhostname> <databasename> <sessionID>'"
        sys.exit(1)
    hname = sys.argv[1]
    database = sys.argv[2]
    sessionID = sys.argv[3]
    cursor = connect_db(dbname=database)
    copy_data_over(hname, database, cursor, int(sessionID));
