# !/bin/python

import sqlite3
import string
import os

def import_table(conn, tableName, hname, sessionID):
	print "Creating %s...." % tableName
#	foldername = "hewelhog_1016_datexport"
	if hname == "" :
#		fname = "%s/%s.dat" % (foldername, tableName)
		fname = "%s.dat" % (tableName)
	else :
#		fname = "%s/%s_%s_%s.dat" % (foldername, tableName, hname, sessionID)
		fname = "%s_%s_%s.dat" % (tableName, hname, sessionID)
	
	f = open(fname, "r")
	
	i = 0
	for line in f:
		if i == 0:
			colArray = line.rstrip('\n').split("\t")
			colList = ','.join(colArray)
			#print colList
		else:
			valArray = line.rstrip('\n').split("\t")
			#print valArray
			valList = ",".join(valArray)
			sql = 'insert into %s (%s) values (' % (tableName, colList)
			for j in range(0, len(valArray)):
				if j == len(valArray) - 1:
					sql = '%s"%s")' % (sql, valArray[j])
				else:
					sql = '%s"%s",' % (sql, valArray[j])
			#print sql
			cursor.execute(sql)
		i = i + 1

if __name__ == '__main__':
	import sys
	if len(sys.argv)<3:
		print "Usage : './createSQLite.py <realhostname> <sessionID>'"
		sys.exit(1)
	hname = sys.argv[1]
	sessionID = sys.argv[2]
	sql_fname = "%s_%s_sqlite.db" % (hname, sessionID)
	conn = sqlite3.connect(sql_fname)	
	cursor = conn.cursor()
	
	command_string = "sqlite3 %s_%s_sqlite.db < v3_0-sqlite.sql" % (hname, sessionID)
	os.system(command_string) 

	import_table(cursor, "Cloud", "", "")
	import_table(cursor, "Field", "", "")
	import_table(cursor, "Seeing", "", "")

	import_table(cursor, "Config_File", hname, sessionID)
	import_table(cursor, "Config", hname, sessionID)
	import_table(cursor, "Log", hname, sessionID)
	import_table(cursor, "MissedHistory", hname, sessionID)
	import_table(cursor, "ObsHistory", hname, sessionID)
	import_table(cursor, "ObsHistory_Proposal", hname, sessionID)
	import_table(cursor, "Summary", hname, sessionID)
	import_table(cursor, "Proposal_Field", hname, sessionID)
	import_table(cursor, "Proposal", hname, sessionID)
	import_table(cursor, "SeqHistory", hname, sessionID)
	import_table(cursor, "SeqHistory_MissedHistory", hname, sessionID)
	import_table(cursor, "SeqHistory_ObsHistory", hname, sessionID)
	import_table(cursor, "Session", hname, sessionID)
	import_table(cursor, "SlewActivities", hname, sessionID)
	import_table(cursor, "SlewHistory", hname, sessionID)
	import_table(cursor, "SlewMaxSpeeds", hname, sessionID)
	import_table(cursor, "SlewState", hname, sessionID)
	import_table(cursor, "TimeHistory", hname, sessionID)

	conn.commit()
	conn.close()

