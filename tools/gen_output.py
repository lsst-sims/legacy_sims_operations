#!/usr/bin/env python

import sys, re, time, socket
import math
import MySQLdb
import os
from LSSTDBInit import *
from socket import gethostname

def getDbData(sql):
    global sessionID
    # Get a connection to the DB
    connection = openConnection ()
    cursor = connection.cursor ()
    # Fetch the data from the DB
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
        sys.stderr.write ('No database records for Session %d' % sessionID)
        sys.exit()
    # Close the connection
    cursor.close ()
    connection.close ()
    del (cursor)
    del (connection)
    return (ret)

def create_output_table(sessionID):
	hname = gethostname()
	print 'Creating/Recreating Output Table ...'
	sql = 'DROP TABLE IF EXISTS output_%s_%d' % (hname, sessionID)
	ret = getDbData(sql)
	sql = 'create table output_%s_%d select * from ObsHistory where sessionID=%d' % (hname, sessionID, sessionID)
	ret = getDbData(sql)

def gen_output(sessionID):
	hname = gethostname()
	create_output_table (sessionID)
	print 'Getting Data for SessionID = %d ...' % (sessionID)
	
	# Please remove the "-u www -p" if you already have the my.cnf setup in the following line
	cmd = 'mysql -u www -p -e "select * from LSST.output_%s_%d" > output_%s_%d.dat' % (hname, sessionID, hname, sessionID)
	
	os.system(cmd)
	print 'Creating MysqlDump File ...' 
	
	# Please remove the "-u www -p" if you already have the my.cnf setup in the following line
	cmd = 'mysqldump -u www -p LSST output_%s_%d > output_%s_%d.sql' % (hname, sessionID, hname, sessionID)
	
	os.system(cmd)

try:
    val = sys.argv[1:]
    sessionID = int (val[0])
except:
    print "\n\n..........No session parameter found!"
    print "..........Use gen_result.py <sessionID>\n\n"
    done

gen_output(sessionID)

