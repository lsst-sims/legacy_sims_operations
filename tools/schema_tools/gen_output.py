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
    ret = {}
    n = cursor.execute(sql)
    ret = cursor.fetchall()
    return ret

def insertDbData(cursor, sql):
    global sessionID
    cursor.execute(sql)

def check_columns_if_they_exist(hname, database, cursor, sessionID):
    columns = ("obsHistID", "sessionID", "fieldID", "fieldRA", "fieldDec", "filter", "expDate", "expMJD", "night", "visitTime", "visitExpTime", "finRank", "finSeeing", "transparency", "airmass", "vSkyBright", "filtSkyBright", "rotSkyPos", "lst", "altitude", "azimuth", "dist2Moon", "solarElong", "moonRA", "moonDec", "moonAlt", "moonAZ", "moonPhase", "sunAlt", "sunAz", "phaseAngle", "rScatter", "mieScatter", "moonIllum", "moonBright", "darkBright", "rawSeeing", "wind", "humidity", "slewDist", "slewTime", "fiveSigmaDepth");
    simname = "summary_%s_%d" % (hname, sessionID);
    sqlquery = "describe %s.%s" % (database, simname);
    columnsexistbool = True
    # An exception occurs when the summary table doesn't exist.
    try:
        ret = getDbData(cursor, sqlquery)
    except mysqldb.ProgrammingError:
        ret = {}
    columnsexist = {}
    for ind in columns:
		columnsexist[ind] = False

    for result in ret:
		if (result[0] in columnsexist.keys()): # is this index one of the ones we're looking for?
			columnsexist[result[0]] = True

    for ind in columns:
		if (columnsexist[ind] == False):
			columnsexistbool = False
    return columnsexistbool

def create_output_table(hname, database, cursor, sessionID):
	# print 'Creating/Recreating Summary Table ...'
	sql = 'use %s' % (database)
	ret = getDbData(cursor, sql)
	sql = 'create table summary_%s_%d (obsHistID int(10) unsigned not null, sessionID int(10) unsigned not null, propID int(10), fieldID int(10) unsigned not null, fieldRA double, fieldDec double, filter varchar(8), expDate int(10) unsigned, expMJD double, night int(10) unsigned, visitTime double, visitExpTime double, finRank double, finSeeing double, transparency double, airmass double, vSkyBright double, filtSkyBrightness double, rotSkyPos double, lst double, altitude double, azimuth double, dist2Moon double, solarElong double, moonRA double, moonDec double, moonAlt double, moonAZ double, moonPhase double, sunAlt double, sunAz double, phaseAngle double, rScatter double, mieScatter double, moonIllum double, moonBright double, darkBright double, rawSeeing double, wind double, humidity double, slewDist double, slewTime double, fiveSigmaDepth double);' % (hname, sessionID)
	ret = getDbData(cursor, sql)
	sql = 'select obsHistID, Session_sessionID as sessionID, Field_fieldID as fieldID, filter, expDate, expMJD, night, visitTime, visitExpTime, finRank, finSeeing, transparency, airmass, vSkyBright, filtSkyBright as filtSkyBrightness, rotSkyPos, lst, alt as altitude, az as azimuth, dist2Moon, solarElong, moonRA, moonDec, moonAlt, moonAZ, moonPhase, sunAlt, sunAz, phaseAngle, rScatter, mieScatter, moonIllum, moonBright, darkBright, rawSeeing, wind, humidity from ObsHistory where Session_sessionID = %d;' % (sessionID)
	ret = getDbData(cursor, sql)

	ctioHeight = 2215.;
	ctioLat = -30.16527778;
	ctioLon = 70.815;
	extC = .172;
	DEG2RAD = 0.0174532925;
	RAD2DEG = 57.2957795;

	for k in range(len(ret)):
		obsHistID = ret[k][0]
		fieldID = ret[k][2]
		sql = 'select fieldRA, fieldDec from Field where fieldID = %d' % fieldID
		fld = getDbData(cursor, sql)
		sql = 'select slewTime, slewDist from SlewHistory where ObsHistory_Session_sessionID = %d and ObsHistory_obsHistID = %d' % (sessionID, obsHistID)
		slw = getDbData(cursor, sql)
		sql = 'select Proposal_propID as propID from ObsHistory_Proposal where ObsHistory_Session_sessionID = %d and ObsHistory_obsHistID = %d' % (sessionID, obsHistID)
		prp = getDbData(cursor, sql)

		for i in range(len(prp)):
			#etc = ETC();
			filter = ret[k][3];
			bandindex = -1;
			if filter == 'u':
				bandindex=0;
			elif filter == 'g':
				bandindex=1;
			elif filter == 'r':
				bandindex=2;
			elif filter == 'i':
				bandindex=3;
			elif filter == 'z':
				bandindex=4;
			elif filter == 'y':
				bandindex=5;
			MJD = float(ret[k][5]);
			alt_RAD = float(ret[k][17]);
			az_RAD = float(ret[k][18]);

			moonRA_RAD = float(ret[k][21]);
			moonDec_RAD = float(ret[k][22]);
			lst_RAD = float(ret[k][16]);
			moonha_RAD = lst_RAD - moonRA_RAD;
			malt_RAD = float(ret[k][23]);
			mphase = float(ret[k][25]);
			saz = float(ret[k][27]);
			salt = float(ret[k][26]);
			mphase = math.acos((mphase/50)-1)*180/math.pi;
			# 5 sigma calculations
			seeing = float(ret[k][10]);
			airmass = float(ret[k][12]);
			filtsky = float(ret[k][14]);
			expTime = float(ret[k][8]);
			Cm = -1.;
			kAtm = -1.;
			if filter == 'u':
				Cm = 23.60;
				kAtm = 0.48;
			elif filter == 'g':
				Cm = 24.57;
				kAtm = 0.21;
			elif filter == 'r':
				Cm = 24.57;
				kAtm  = 0.10;
			elif filter == 'i':
				Cm = 24.47;
				kAtm = 0.07;
			elif filter == 'z':
				Cm = 24.19;
				kAtm = 0.06;
			elif filter == 'y':
				Cm = 23.45;
				kAtm = 0.06;
			elif filter == 'y1':
				Cm = 23.74;
				kAtm = 0.11;

			tauCloud = 0.;
			#expTime = (expTime - 4.00);
			m5_1 = Cm + 0.50*(filtsky-21) + 2.5*math.log10(0.7/seeing) +1.25*math.log10(expTime/30) - kAtm*(airmass-1) + 1.1*tauCloud; # Using Kem's SkyBrightness
			# Feature 120: Add 2 columns: skybrightness (ETC for dark and filtsky for z & y filters for twilight) and 5 sigma from this column
			if (salt*RAD2DEG) > -18.0 and (filter == 'y' or filter == 'z'):
				# This is if it is twilight that is that sunalt > -18.0 and filter is either y or z
				sql = 'insert into summary_%s_%d (obsHistID, sessionID, propID, fieldID, fieldRA, fieldDec, filter, expDate, expMJD, night, visitTime, visitExpTime, finRank, finSeeing, transparency, airmass, vSkyBright, filtSkyBrightness, rotSkyPos, lst, altitude, azimuth, dist2Moon, solarElong, moonRA, moonDec, moonAlt, moonAZ, moonPhase, sunAlt, sunAz, phaseAngle, rScatter, mieScatter, moonIllum, moonBright, darkBright, rawSeeing, wind, humidity, slewDist, slewTime, fiveSigmaDepth) values (%d, %d, %d, %d, %f, %f, "%s", %d, %f, %d, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f)' % (hname, sessionID, ret[k][0], ret[k][1], prp[i][0], ret[k][2], math.radians(fld[0][0]), math.radians(fld[0][1]), ret[k][3], ret[k][4], ret[k][5], ret[k][6], ret[k][7], ret[k][8], ret[k][9], ret[k][10], ret[k][11], ret[k][12], ret[k][13], ret[k][14], ret[k][15], ret[k][16], ret[k][17], ret[k][18], ret[k][19], ret[k][20], ret[k][21], ret[k][22], ret[k][23], ret[k][24], ret[k][25], ret[k][26], ret[k][27], ret[k][28], ret[k][29], ret[k][30], ret[k][31], ret[k][32], ret[k][33], ret[k][34], ret[k][35], ret[k][36], slw[0][1], slw[0][0], m5_1);
			else :
				sql = 'insert into summary_%s_%d (obsHistID, sessionID, propID, fieldID, fieldRA, fieldDec, filter, expDate, expMJD, night, visitTime, visitExpTime, finRank, finSeeing, transparency, airmass, vSkyBright, filtSkyBrightness, rotSkyPos, lst, altitude, azimuth, dist2Moon, solarElong, moonRA, moonDec, moonAlt, moonAZ, moonPhase, sunAlt, sunAz, phaseAngle, rScatter, mieScatter, moonIllum, moonBright, darkBright, rawSeeing, wind, humidity, slewDist, slewTime, fiveSigmaDepth) values (%d, %d, %d, %d, %f, %f, "%s", %d, %f, %d, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f)' % (hname, sessionID, ret[k][0], ret[k][1], prp[i][0], ret[k][2], math.radians(fld[0][0]), math.radians(fld[0][1]), ret[k][3], ret[k][4], ret[k][5], ret[k][6], ret[k][7], ret[k][8], ret[k][9], ret[k][10], ret[k][11], ret[k][12], ret[k][13], ret[k][14], ret[k][15], ret[k][16], ret[k][17], ret[k][18], ret[k][19], ret[k][20], ret[k][21], ret[k][22], ret[k][23], ret[k][24], ret[k][25], ret[k][26], ret[k][27], ret[k][28], ret[k][29], ret[k][30], ret[k][31], ret[k][32], ret[k][33], ret[k][34], ret[k][35], ret[k][36], slw[0][1], slw[0][0], m5_1);
			#print sql
			insertDbData(cursor, sql)

if __name__ == "__main__":
    import sys
    if len(sys.argv)<4:
        print "Usage : './gen_output.py <realhostname> <databasename> <sessionID>'"
        sys.exit(1)
    hname = sys.argv[1]
    database = sys.argv[2]
    sessionID = sys.argv[3]
    cursor = connect_db(dbname=database)
    if (check_columns_if_they_exist(hname, database, cursor, int(sessionID)) == False):
		create_output_table(hname, database, cursor, int(sessionID));
