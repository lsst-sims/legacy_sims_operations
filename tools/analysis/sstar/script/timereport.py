#!/usr/bin/env python

import sys, re, time, socket
import math
import MySQLdb as mysqldb

def connect_db(hostname='localhost', username='www', passwdname='zxcvbnm', dbname='OpsimDB'):   
    # connect to lsst_pointings (or other) mysql db, using account that has 'alter table' privileges
    # connect to the database - this is modular to allow for easier modification from machine/machine    
    db = mysqldb.connect(host=hostname, user=username, passwd=passwdname, db=dbname)
    cursor = db.cursor()
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

def timereport(database, sessionID):

    NightStart   = []
    TwilightEnd  = []
    TwilightStart= []
    NightEnd     = []
    eof = False

    sql = 'use %s' % (database)
    ret = getDbData(database, sql);

    sql = 'select * from TimeHistory where Session_sessionID=%d order by date' % (sessionID)
    TIME_HISTORY = getDbData(database, sql)
	##  TimeHistory Events
	##  ==================
	##  START_NIGHT = 0
	##  MOON_WANING = 1         # New lunation, too
	##  MOON_WAXING = 2
	##  NEW_YEAR = 3
	##  END_DUSK    = 4
	##  START_DAWN  = 5
	##  END_NIGHT   = 6 
	##  ==================
	##  |       1481 |         1 | 31452355 |   49717 |     0 |
	##  |       1482 |         1 | 31454472 | 49717.1 |     4 |
	##  |       1483 |         1 | 31478964 | 49717.3 |     5 |
	##  |       1484 |         1 | 31481115 | 49717.4 |     6 |    

    for k in range(len(TIME_HISTORY)):
		if ( TIME_HISTORY[k][4] == 0 ):
			NightStart.append(TIME_HISTORY[k][2])
		elif ( TIME_HISTORY[k][4] == 4 ):
			TwilightEnd.append(TIME_HISTORY[k][2])
		elif ( TIME_HISTORY[k][4] == 5 ):
			TwilightStart.append(TIME_HISTORY[k][2])
		elif ( TIME_HISTORY[k][4] == 6 ):	
			NightEnd.append(TIME_HISTORY[k][2])

    NumNights = len(NightEnd)
    NumYears  = float(NumNights)/365
    
    twilTime = 0
    darkTime = 0
    for k in range(NumNights):
		twilTime += TwilightEnd[k]-NightStart[k] + NightEnd[k]-TwilightStart[k]
		darkTime += TwilightStart[k]-TwilightEnd[k]
    nightTime = twilTime+darkTime

#    sql = 'select paramValue from Config where sessionID=%d and paramName="cloudTbl"' % (sessionID)
#    CLOUDTABLE = getDbData(sql)[0][0]
#    sql = 'select c_date,cloud from %s where c_date>%d and c_date<%d order by c_date' % (CLOUDTABLE, NightStart[0], NightEnd[NumNights-1])
#    cloudValues = getDbData(sql)

#    sql = 'select paramValue from Config where sessionID=%d and paramName="seeingTbl"' % (sessionID)
#    SEEINGTABLE = getDbData(sql)[0][0]

    cloudLimit = 0.7
    readoutTime= 2.0
    seeingLimits = [0.44, 0.59, 0.81]

    sql = 'select expStartTime,expDelay,cloudiness from NOBHist where sessionID=%d order by expStartTime' % (sessionID)
    cloudedTable = getDbData(database, sql)

    night = 0
    darkCloudTime = 0
    twilCloudTime = 0
    darkNotargetTime = 0
    twilNotargetTime = 0
    for k in range(len(cloudedTable)):
	date  = int(cloudedTable[k][0])
	delay = int(cloudedTable[k][1])
	clouds = float(cloudedTable[k][2])
	while date > NightEnd[night]:
	    night += 1
	if NightStart[night] <= date <= TwilightEnd[night] or TwilightStart[night] <= date <= NightEnd[night]:
	    if clouds >= cloudLimit:
			twilCloudTime += delay
	    else:
			twilNotargetTime += delay
        elif TwilightEnd[night] < date < TwilightStart[night]:
            if clouds >= cloudLimit:
                darkCloudTime += delay
	    else:
			darkNotargetTime += delay

    totdarkObs = 0
    tottwilObs = 0
    totdarkExp = 0
    tottwilExp = 0
    totdarkSlew = 0
    tottwilSlew = 0
    totdarkUnivOnly = 0
    tottwilUnivOnly = 0
    totdarkSeeingBetterThan = {}
    tottwilSeeingBetterThan = {}
    for seeing in seeingLimits:
        totdarkSeeingBetterThan[seeing] = 0.0
        tottwilSeeingBetterThan[seeing] = 0.0
    sql = 'select distinct filter from ObsHistory where sessionID=%d' % (sessionID)
    filterList = getDbData(database, sql)
    for k in range(len(filterList)):
        filter = filterList[k][0]
	sql = 'select expDate,slewTime,expTime,rawSeeing,count(*),propID from ObsHistory where sessionID=%d and filter="%s" group by expDate' % (sessionID,filter)
	filter_sorted_obs = getDbData(database, sql)
	night = 0
	darkObs = 0
	twilObs = 0
	darkExp = 0
	twilExp = 0
	darkSlew = 0
	twilSlew = 0
	darkUnivOnly = 0
	twilUnivOnly = 0
	darkSeeingBetterThan = {}
	twilSeeingBetterThan = {}
	for seeing in seeingLimits:
		darkSeeingBetterThan[seeing] = 0.0
		twilSeeingBetterThan[seeing] = 0.0
	for k in range(len(filter_sorted_obs)):
	    expDate = filter_sorted_obs[k][0]
	    slewTime= filter_sorted_obs[k][1]
	    expTime = filter_sorted_obs[k][2]
	    rawSeeing=filter_sorted_obs[k][3]
	    numprops =filter_sorted_obs[k][4]
	    propID   =filter_sorted_obs[k][5]

#	while expDate > NightEnd[night]:
#		print expDate, NightEnd[night];
#		night += 1
	if TwilightEnd[night] < expDate < TwilightStart[night]:
		darkObs  += 1
		darkSlew += slewTime
		darkExp  += expTime

	for seeing in seeingLimits:
		if rawSeeing < seeing:
			darkSeeingBetterThan[seeing] += slewTime+expTime
	if numprops==1 and propID==universal:
		darkUnivOnly += slewTime+expTime
	else:
		twilObs  += 1
		twilSlew += slewTime
		twilExp  += expTime
	for seeing in seeingLimits:
		if rawSeeing < seeing:
		    twilSeeingBetterThan[seeing] += slewTime+expTime
		if numprops==1 and propID==universal:
		    twilUnivOnly += slewTime+expTime
	print "======================================================"
	print "time report for filter = %s" % (filter)
	print "Dark     Visits per year = %.0f" % (darkObs/NumYears)
	print "Twilight Visits per year = %.0f" % (twilObs/NumYears)
	print "TOTAL    Visits per year = %.0f" % ((darkObs+twilObs)/NumYears)
	print "Dark     Exposed Hours per year = %.1f" % (float(darkExp-darkObs*readoutTime)/3600 / NumYears)
	print "Twilight Exposed Hours per year = %.1f" % (float(twilExp-twilObs*readoutTime)/3600 / NumYears)
	print "TOTAL    Exposed Hours per year = %.1f" % (float(darkExp-darkObs*readoutTime+twilExp-twilObs*readoutTime)/3600 / NumYears)
	print "Dark     Slew/Filter Hours per year = %.1f" % (float(darkSlew+darkObs*readoutTime)/3600 / NumYears)
	print "Twilight Slew/Filter Hours per year = %.1f" % (float(twilSlew+twilObs*readoutTime)/3600 / NumYears)
	print "TOTAL    Slew/Filter Hours per year = %.1f" % (float(darkSlew+darkObs*readoutTime+twilSlew+twilObs*readoutTime)/3600 / NumYears)
	print "Dark     Active Hours per year = %.1f" % (float(darkSlew+darkExp)/3600 / NumYears)
	print "Twilight Active Hours per year = %.1f" % (float(twilSlew+twilExp)/3600 / NumYears)
	print "TOTAL    Active Hours per year = %.1f" % (float(darkSlew+darkExp+twilSlew+twilExp)/3600 / NumYears)
	for seeing in seeingLimits:
		print "Dark     Hours with seeing better than %.2f per year = %.1f" % (seeing, darkSeeingBetterThan[seeing]/3600/NumYears)
		print "Twilight Hours with seeing better than %.2f per year = %.1f" % (seeing, twilSeeingBetterThan[seeing]/3600/NumYears)
		print "TOTAL    Hours with seeing better than %.2f per year = %.1f" % (seeing, (darkSeeingBetterThan[seeing]+twilSeeingBetterThan[seeing])/3600/NumYears)
		totdarkSeeingBetterThan[seeing] += darkSeeingBetterThan[seeing]
		tottwilSeeingBetterThan[seeing] += twilSeeingBetterThan[seeing]
	if universal>0:
		print "Dark     Hours in Universal only per year = %.1f" % (float(darkUnivOnly)/3600 / NumYears)
		print "Twilight Hours in Universal only per year = %.1f" % (float(twilUnivOnly)/3600 / NumYears)
		print "TOTAL    Hours in Universal only per year = %.1f" % (float(darkUnivOnly+twilUnivOnly)/3600 / NumYears)
	totdarkObs += darkObs
	tottwilObs += twilObs
	totdarkExp += darkExp
	tottwilExp += twilExp
	totdarkSlew += darkSlew
	tottwilSlew += twilSlew
    totdarkUnivOnly += darkUnivOnly
    tottwilUnivOnly += twilUnivOnly
   
    print "======================================================"
    print "TOTALS for the run"
    print "Dark     Hours per year = %6.1f" % ( float(darkTime)/3600 / NumYears )
    print "Twilight Hours per year = %6.1f" % ( float(twilTime)/3600 / NumYears )
    print "TOTAL    Hours per year = %6.1f" % ( float(darkTime+twilTime)/3600 / NumYears )
    print "Dark     Clouded Hours per year = %6.1f" % ( float(darkCloudTime)/3600 / NumYears )
    print "Twilight Clouded Hours per year = %6.1f" % ( float(twilCloudTime)/3600 / NumYears )
    print "TOTAL    Clouded Hours per year = %6.1f" % ( float(darkCloudTime+twilCloudTime)/3600 / NumYears )
    print "Dark     No target Hours per year = %6.1f" % ( float(darkNotargetTime)/3600 / NumYears )
    print "Twilight No target Hours per year = %6.1f" % ( float(twilNotargetTime)/3600 / NumYears )
    print "TOTAL    No target Hours per year = %6.1f" % ( float(darkNotargetTime+twilNotargetTime)/3600 / NumYears )
    print "Dark     Visits per year = %.0f" % (totdarkObs/NumYears)
    print "Twilight Visits per year = %.0f" % (tottwilObs/NumYears)
    print "TOTAL    Visits per year = %.0f" % ((totdarkObs+tottwilObs)/NumYears)
    print "Dark     Exposed Hours per year = %.1f" % (float(totdarkExp-totdarkObs*readoutTime)/3600 / NumYears)
    print "Twilight Exposed Hours per year = %.1f" % (float(tottwilExp-tottwilObs*readoutTime)/3600 / NumYears)
    print "TOTAL    Exposed Hours per year = %.1f" % (float(totdarkExp-totdarkObs*readoutTime+tottwilExp-tottwilObs*readoutTime)/3600 / NumYears)
    print "Dark     Slew/Filter Hours per year = %.1f" % (float(totdarkSlew+totdarkObs*readoutTime)/3600 / NumYears)
    print "Twilight Slew/Filter Hours per year = %.1f" % (float(tottwilSlew+tottwilObs*readoutTime)/3600 / NumYears)
    print "TOTAL    Slew/Filter Hours per year = %.1f" % (float(totdarkSlew+totdarkObs*readoutTime+tottwilSlew+tottwilObs*readoutTime)/3600 / NumYears)
    print "Dark     Active Hours per year = %.1f" % (float(totdarkSlew+totdarkExp)/3600 / NumYears)
    print "Twilight Active Hours per year = %.1f" % (float(tottwilSlew+tottwilExp)/3600 / NumYears)
    print "TOTAL    Active Hours per year = %.1f" % (float(totdarkSlew+totdarkExp+tottwilSlew+tottwilExp)/3600 / NumYears)
    for seeing in seeingLimits:
        print "Dark     Hours with seeing better than %.2f per year = %.1f" % (seeing, totdarkSeeingBetterThan[seeing]/3600/NumYears)
        print "Twilight Hours with seeing better than %.2f per year = %.1f" % (seeing, tottwilSeeingBetterThan[seeing]/3600/NumYears)
        print "TOTAL    Hours with seeing better than %.2f per year = %.1f" % (seeing, (totdarkSeeingBetterThan[seeing]+tottwilSeeingBetterThan[seeing])/3600/NumYears)
    if universal>0:
        print "Dark     Hours in Universal only per year = %.1f" % (float(totdarkUnivOnly)/3600 / NumYears)
        print "Twilight Hours in Universal only per year = %.1f" % (float(tottwilUnivOnly)/3600 / NumYears)
        print "TOTAL    Hours in Universal only per year = %.1f" % (float(totdarkUnivOnly+tottwilUnivOnly)/3600 / NumYears)

try:
    database = sys.argv[1]
    sessionID = int (sys.argv[2])
    val = sys.argv[3:]
    if len(val)>1:
        universal = int (val[1])
    else:
	universal = 0
except:
    print "\n\n..........No session parameter found!"
    print "..........Use timereport.py <database> <sessionID> <universal_propID>\n\n"
    done

timereport(database, sessionID)

