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


def reportPairs(sessionID,propIdOnly,nonuniv,nofilter,IntervalMin,IntervalMax,nofile,filterlist):

    label = 'session info'
    sql = 'select sessionHost, sessionDate from Session where sessionID=%d' % (sessionID)
    ret = getDbData (sql, label)
    host = ret[0][0]
    startDate = ret[0][1]
    print "Session ID: %d\tHost: %s\tSession Start Date: %s" % (sessionID,host,startDate)

    label = 'Pairs counting'
    sql   = 'select propID,propConf,propName from Proposal where sessionID=%d' % (sessionID)
    list_propID = getDbData(sql, label)
    if list_propID == None:
        return

    for p in range(len(list_propID)):
	propID = list_propID[p][0]
	propConf=list_propID[p][1]
	propName=list_propID[p][2]

	if (propIdOnly > 0):
	    if (propID != propIdOnly):
		continue
	elif (nonuniv == False):
	    if (propName != 'WLTSS'):
		continue

	print "================================================================"
	print "%s: propID=%d" % (propConf, propID)

	if (propName == 'WLTSS'):
            sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqFilters" order by paramIndex' % (sessionID, propID)
	    list_filter = getDbData(sql, label)

            sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqInterval" order by paramIndex' % (sessionID, propID)
            list_interval = getDbData(sql, label)
                                                                                                                 
            sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqWindowStart" order by paramIndex' % (sessionID, propID)
            list_windowstart = getDbData(sql, label)
                                                                                                                 
            sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqWindowEnd" order by paramIndex' % (sessionID, propID)
            list_windowend = getDbData(sql, label)

            if (nofilter == True):
                nofilter_intervalmin = 1e7
                nofilter_intervalmax = 0
                for f in range(len(list_filter)):
		    if ((len(filterlist)>0) and (list_filter[f][0] in filterlist)) or ((len(filterlist)==0) and (eval(list_interval[f][0])>0)):
                        nofilter_intervalmin = min(nofilter_intervalmin,eval(list_interval[f][0])*(1+eval(list_windowstart[f][0])))
                        nofilter_intervalmax = max(nofilter_intervalmax,eval(list_interval[f][0])*(1+eval(list_windowend[f][0])))
                list_filter = [['all']]
	else:
	    sql = 'select filter from ObsHistory where sessionID=%d and propID=%d group by filter' % (sessionID, propID)
            list_filter = getDbData(sql, label)
            nofilter_intervalmin = 0
            nofilter_intervalmax = 0
            if (nofilter == True):
                list_filter = [['all']]

	visits_seqnNum_filter = {}
	reqvisits_filter = {}
	list_seqnNum_visits = {}
        list_seqnNum_pairs  = {}
	totalNpairs = 0
	totalNmaxpairs = 0
	if nofile == True:
	    pairsfilename = '/dev/null'
	else:
	    pairsfilename = 'pairs.%s.%d.%d' % (host, sessionID, propID)

	pairsfile = open(pairsfilename, 'w')
	pairsfile.write('#pairs for run %s sessionID=%d proposalID=%d %s\n' % (host, sessionID, propID, propConf))
        pairsfile.write('%8s %8s %12s %12s %4s %4s %14s %14s %10s %10s %8s %7s %7s %6s %6s %6s %6s\n' % ('#seqnNum','fieldID','RA','Dec','fil1','fil2','MJD1','MJD2','expDate1','expDate2','lapse','skb1','skb2','rs1','rs2','cs1','cs2'))

	pairsallfilters = {}
	for f in range(len(list_filter)):
	    filter = list_filter[f][0]

	    if (propName == 'WLTSS') and (filter != 'all'):
	        interval = eval(list_interval[f][0])
	        windowstart = eval(list_windowstart[f][0])
	        windowend   = eval(list_windowend[f][0])
                intervalmin = interval*(1+windowstart)
                intervalmax = interval*(1+windowend)
	    else:
                intervalmin = nofilter_intervalmin
                intervalmax = nofilter_intervalmax
                interval    = (intervalmin+intervalmax)/2

	    if (IntervalMin > 0):
		intervalmin = IntervalMin
		interval = intervalmin

	    if (IntervalMax > 0):
		intervalmax = IntervalMax
		interval = (intervalmin+intervalmax)/2

            sql = 'select seqnNum,expDate,fieldID,fieldRA,fieldDec,expMJD,filter,skyBright,rawSeeing,seeing from ObsHistory where sessionID=%d and propID=%d' % (sessionID, propID)
	    if (filter != 'all'):
		sql += ' and filter="%s"' % (filter)
	    else:
		if len(filterlist)>0:
		    sql += ' and ('
		    for k in range(0,len(filterlist)-1):
		        sql += 'filter="%s" or ' % (filterlist[k])
		    sql += 'filter="%s")' % (filterlist[-1])
	    sql += ' order by seqnNum,fieldID,expDate'
	    #print sql
            list_seqnNum_expDate = getDbData(sql, label)

	    for record in list_seqnNum_expDate:
		fieldID = record[2]
		if visits_seqnNum_filter.has_key(fieldID):
		    if visits_seqnNum_filter[fieldID].has_key(filter):
			visits_seqnNum_filter[fieldID][filter] += 1
		    else:
                        visits_seqnNum_filter[fieldID][filter] = 1
		else:
                    visits_seqnNum_filter[fieldID] = { filter : 1 }

	    if interval>0:
                print "----------------------"
                print "%s: filter=%s intervalmin=%.0f intervalmax=%.0f" % (propConf, filter, intervalmin, intervalmax)

	        sql = 'DROP TABLE IF EXISTS tmpWLTSSpairs'
                ret = getDbData(sql, label)
                sql = 'create table tmpWLTSSpairs select seqnNum,floor(count(0)/2) as maxpairs from ObsHistory where sessionID=%d and propID=%d' % (sessionID, propID)
		if (filter != 'all'):
		    sql += ' and filter="%s"' % (filter)
                else:
                    if len(filterlist)>0:
                        sql += ' and ('
                        for k in range(0,len(filterlist)-1):
                            sql += 'filter="%s" or ' % (filterlist[k])
                        sql += 'filter="%s")' % (filterlist[-1])
		sql += ' group by seqnNum,fieldID'
                ret = getDbData(sql, label)
                sql = 'create index ix_tmpWLTSSpairs_1 on tmpWLTSSpairs (seqnNum)'
                ret = getDbData(sql, label)

                sql = 'select sum(maxpairs) from tmpWLTSSpairs'
                filterNmaxpairs = getDbData(sql, label)[0][0]
		if filterNmaxpairs == None:
		    filterNmaxpairs = 0
		totalNmaxpairs += filterNmaxpairs
                sql = 'DROP TABLE IF EXISTS tmpWLTSSpairs'
                ret = getDbData(sql, label)

		if filterNmaxpairs > 0:
		    pairs = {}
		
  		    nobs = len(list_seqnNum_expDate)
                    filterNpairs = 0
		    k = 0
		    while k<nobs-2:
		        seqnNum1 = list_seqnNum_expDate[k][0]
		        expDate1 = list_seqnNum_expDate[k][1]
			fieldID1 = list_seqnNum_expDate[k][2]
			filter1  = list_seqnNum_expDate[k][6]
                        seqnNum2 = list_seqnNum_expDate[k+1][0]
                        expDate2 = list_seqnNum_expDate[k+1][1]
                        fieldID2 = list_seqnNum_expDate[k+1][2]
                        filter2  = list_seqnNum_expDate[k+1][6]
		        if fieldID1 == fieldID2:
			    if intervalmin <= (expDate2-expDate1) <= intervalmax:
                                if pairs.has_key(fieldID1):
                                    pairs[fieldID1] += 1
                                else:
                                    pairs[fieldID1] = 1
			        if pairsallfilters.has_key(fieldID1):
				    pairsallfilters[fieldID1] += 1
			        else:
				    pairsallfilters[fieldID1] = 1
                                fieldRA = float(list_seqnNum_expDate[k][3])
                                fieldDec= float(list_seqnNum_expDate[k][4])
                                expMJD1 = float(list_seqnNum_expDate[k][5])
                                expMJD2 = float(list_seqnNum_expDate[k+1][5])
	                        skyBrig1 = list_seqnNum_expDate[k][7]
        	                rawSeei1 = list_seqnNum_expDate[k][8]
                	        seeing1  = list_seqnNum_expDate[k][9]
                                skyBrig2 = list_seqnNum_expDate[k+1][7]
                                rawSeei2 = list_seqnNum_expDate[k+1][8]
                                seeing2  = list_seqnNum_expDate[k+1][9]

                                pairsfile.write('%8d %8d %12f %12f %4s %4s %14f %14f %10d %10d %8d %7.2f %7.2f %6.2f %6.2f %6.2f %6.2f\n' % (seqnNum1,fieldID1,fieldRA,fieldDec,filter1,filter2,expMJD1,expMJD2,expDate1,expDate2,expDate2-expDate1,skyBrig1,skyBrig2,rawSeei1,rawSeei2,seeing1,seeing2))
			        k += 1
			        filterNpairs += 1
			        totalNpairs  += 1
		        k += 1
		    histogram = {}
                    accumhist = {}
		    accum = 0
		    for seq in pairs.keys():
		        if histogram.has_key(pairs[seq]):
			    histogram[pairs[seq]] += 1
		        else:
			    histogram[pairs[seq]] = 1
		    print "%s: %d pairs achieved for filter=%s, %4.1f%%" % (propConf, filterNpairs, filter, 100.0*filterNpairs/filterNmaxpairs)
		    hlist = histogram.keys()
		    hlist.sort()
		    for h in hlist:
		        print "%s: pairs histogram filter=%s %d pairs in %d fields" % (propConf, filter, h, histogram[h])
		    hlist.reverse()
                    for h in hlist:
			accum += histogram[h]
			accumhist[h] = accum
		    hlist.sort()
		    for h in hlist:
                        print "%s: pairs histogram filter=%s >=%d pairs in %d fields" % (propConf, filter, h, accumhist[h])

	    sql = 'DROP TABLE IF EXISTS tmpWLTSSvisits'
            ret = getDbData(sql, label)

	pairsfile.close()

	if totalNmaxpairs > 0:
            print "----------------------"
	    print "%s: TOTAL %d pairs achieved, %4.1f%%" % (propConf, totalNpairs, 100.0*totalNpairs/totalNmaxpairs)

	if nofilter == False:
            print "----------------------"
            histogram = {}
            accumhist = {}
            accum = 0
            for seq in pairsallfilters.keys():
                if histogram.has_key(pairsallfilters[seq]):
                    histogram[pairsallfilters[seq]] += 1
                else:
                    histogram[pairsallfilters[seq]] = 1
            hlist = histogram.keys()
            hlist.sort()
            for h in hlist:
                print "%s: pairs histogram all filters %d pairs in %d fields" % (propConf, h, histogram[h])
            hlist.reverse()
            for h in hlist:
                accum += histogram[h]
                accumhist[h] = accum
            hlist.sort()
            for h in hlist:
                print "%s: pairs histogram all filters >=%d pairs in %d fields" % (propConf, h, accumhist[h])

    return


print sys.argv
try:
    val = sys.argv[1:]
    sessionID = int (val[0])
except:
    print "\n\n..........No session parameter found!"
    print "..........Use newextract.py <sessionID> [propID=<propID>] [nofilter] [filters=a,b,c] [intervalmin=<intervalmin_seconds>] [intervalmax=<intervalmax_seconds]\n\n"
    done 

val = sys.argv[2:]

propID = 0
nonuniv = False
nofilter = False
nofile = False
IntervalMin = 0
IntervalMax = 0
filterlist=[]
for k in range(len(val)):
    kv = val[k].split('=')
    if len(kv) == 2:
	if kv[0] == 'propID':
	    propID = int(kv[1])
	elif kv[0] == 'intervalmin':
	    IntervalMin = eval(kv[1])
        elif kv[0] == 'intervalmax':
            IntervalMax = eval(kv[1])
        elif kv[0] == 'filters':
            filterlist = kv[1].split(',')
            nofilter = True
    else:
	if kv[0] == 'univonly':
	    nonuniv = True
	elif kv[0] == 'nofilter':
	    nofilter = True
	elif kv[0] == 'nofile':
	    nofile = True

#print sessionID
#print propID
#print UnivOnly
#print nofilter
#print IntervalMin
#print IntervalMax

reportPairs(sessionID,propID,nonuniv,nofilter,IntervalMin,IntervalMax,nofile,filterlist)

