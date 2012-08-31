#!/usr/bin/env python

import sys, re, time, socket
import math
import MySQLdb
from LSSTDBInit import *

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
                                                                                                                                                                                                     
def timereport(sessionID):

#    logfile = open('../src/lsst.log_%d' % (sessionID))

    NightStart   = []
    TwilightEnd  = []
    TwilightStart= []
    NightEnd     = []
    eof = False
    
## Srini's Code (04/10/2007)
    sql = 'select * from TimeHistory where sessionID=%d order by date' % (sessionID)
    TIME_HISTORY = getDbData(sql)
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
## 2007-04-24 00:36:20,808 INFO Simulator: NightStart=17881264 TwilightEnd=17882972 Midnight=17902117 TwilightStart=17921261 NightEnd=17922968    
    for k in range(len(TIME_HISTORY)):
	#print TIME_HISTORY[k][4];
	if ( TIME_HISTORY[k][4] == 0 ):
		NightStart.append(TIME_HISTORY[k][2])
	elif ( TIME_HISTORY[k][4] == 4 ):
		TwilightEnd.append(TIME_HISTORY[k][2])
	elif ( TIME_HISTORY[k][4] == 5 ):
		TwilightStart.append(TIME_HISTORY[k][2])
	elif ( TIME_HISTORY[k][4] == 6 ):	
		NightEnd.append(TIME_HISTORY[k][2])
#    	print TIME_HISTORY[k]
#    print len(TIME_HISTORY)
## End of Srini's Code (04/10/2007)
    
#    while eof==False:
#	lineStr = logfile.readline()
#	if lineStr == '':
#	    eof = True
#	elif lineStr.find('NightStart') != -1:
#	    lineWords = lineStr.split(' ')
#	    NightStart.append(int(lineWords[4].split('=')[1]))
#           TwilightEnd.append(int(lineWords[5].split('=')[1]))
#           TwilightStart.append(int(lineWords[7].split('=')[1]))
#           NightEnd.append(int(lineWords[8].split('=')[1]))
#    logfile.close()

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
    cloudedTable = getDbData(sql)

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

    TABLE = 'timereport_%d_tmpObs' % (sessionID)
    sql = 'DROP TABLE IF EXISTS %s' % (TABLE)
    ret = getDbData(sql)
    sql = 'create table %s select expDate,fieldID,filter,slewTime,expTime,rawSeeing,propID,count(*) as numprops from ObsHistory where sessionID=%d group by expDate' % (TABLE, sessionID)
    ret = getDbData(sql)
    sql = 'create index ix_expDate on %s (expDate)' % (TABLE)
    ret = getDbData(sql)

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
    for filter in ['u','g','r','i','z','y']:
	sql = 'select expDate,slewTime,expTime,rawSeeing,numprops,propID from %s where filter="%s" order by expDate' % (TABLE,filter)
	filter_sorted_obs = getDbData(sql)
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
	    while expDate > NightEnd[night]:
		night += 1
# @Srini (Please UnComment to see debug  --- print TwilightEnd[night], expDate, TwilightStart[night]
# @Srini (04/24/07) Not sure if this is a problem (expDate from DB is never between the TwilightEnd and TwilightStart) from the TimeHistory table
# @Francisco - Could you please check if the TwilightEnd/TwilightStart are calculated correctly. I think they are but I am not sure.	    
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
    val = sys.argv[1:]
    sessionID = int (val[0])
    if len(val)>1:
        universal = int (val[1])
    else:
	universal = 0
except:
    print "\n\n..........No session parameter found!"
    print "..........Use timereport.py <sessionID> <universal_propID>\n\n"
    done
                                                                                                                                                                                                     
timereport(sessionID)

