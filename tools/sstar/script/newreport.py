#!/usr/bin/env python

import sys, re, time, socket
import math
import MySQLdb as mysqldb

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

def connect_db(hostname='localhost', username='www', passwdname='zxcvbnm', dbname='LSST'):   
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

def report(database, sessionID, notcs):

    label = 'session info'
    sql = 'use %s' % (database)
    ret = getDbData(database, sql)

    sql = 'select sessionHost, sessionDate from Session where sessionID=%d' % (sessionID)
    ret = getDbData(database, sql)
    host = ret[0][0]
    startDate = ret[0][1]
    print "Session ID: %d\tHost: %s\tSession Start Date: %s" % (sessionID,host,startDate)

    label = 'config'
    sql   = 'select paramName,paramValue from Config where Session_sessionID=%d and moduleName="LSST" order by paramIndex' % (sessionID)
    config_LSST   = getDbData(database, sql)
    dict_LSST = {}
    for kv in config_LSST:
#	print kv
	dict_LSST[kv[0]] = kv[1]
#    print dict_LSST

    site  = dict_LSST['siteConf']
    print "%s: %s" % (label, site)

    label = 'number of nights'
    sql   = 'select count(event) from TimeHistory where Session_sessionID=%d and event=%d' % (sessionID, START_NIGHT)
    ret   = getDbData(database, sql)
    count_nights = ret[0][0]
    print "%s: %s" % (label, count_nights)

    label = 'number of exposures'
    sql   = 'select count(distinct expDate) from ObsHistory where Session_sessionID=%d' % (sessionID)
    ret   = getDbData(database, sql)
    count_exposures = ret[0][0]
    print "%s: %s" % (label, count_exposures)
    print "exposures/night: %6.1f" % (float(count_exposures)/count_nights)

    label = 'average exposure time'
    sql   = 'select avg(t.expTime) from (select expDate,expTime from ObsHistory where Session_sessionID=%d group by expDate) as t' % (sessionID)
    ret   = getDbData(database, sql)
    avg_exposuretime = ret[0][0]
    print "%s: %5.2fs" % (label, avg_exposuretime)

    label = 'average slew time'
    sql   = 'select avg(t.slewTime) from (select expDate,slewTime from ObsHistory where Session_sessionID=%d group by expDate) as t' % (sessionID)
    ret   = getDbData(database, sql)
    avg_slewtime = ret[0][0]
    print "%s: %5.2fs" % (label, avg_slewtime)

    label = 'number of stopped initial telescope positions'
    sql   = 'select count(*) from SlewInitState where sessionID=%d and tracking="False"' % (sessionID)
    ret   = getDbData(database, sql)
    count_stoppedinitial = ret[0][0]
    print "%s: %s" % (label, count_stoppedinitial)

    if notcs == False:
	reportAngleStats('TelAlt', sessionID)
	reportAngleStats('TelAz' , sessionID)
	reportAngleStats('RotPos', sessionID)

	reportActivity('DomAlt'     , sessionID, count_exposures)
	reportActivity('DomAz'      , sessionID, count_exposures)
	reportActivity('TelAlt'     , sessionID, count_exposures)
	reportActivity('TelAz'      , sessionID, count_exposures)
	reportActivity('Rotator'    , sessionID, count_exposures)
	reportActivity('Filter'     , sessionID, count_exposures)
	reportActivity('TelOpticsOL', sessionID, count_exposures)
	reportActivity('Readout'    , sessionID, count_exposures)
	reportActivity('Settle'     , sessionID, count_exposures)
	reportActivity('DomSettle'  , sessionID, count_exposures)
	reportActivity('TelOpticsCL', sessionID, count_exposures)

	reportMaxSpeed('DomAlt', sessionID)
	reportMaxSpeed('DomAz' , sessionID)
	reportMaxSpeed('TelAlt', sessionID)
	reportMaxSpeed('TelAz' , sessionID)
	reportMaxSpeed('Rot'   , sessionID)

    reportWL(sessionID)
    reportNEA(sessionID)
    reportSN(sessionID)
    reportSNSS(sessionID)
    reportKBO(sessionID)
    reportWLTSS(sessionID, host)

def reportAngleStats(name, sessionID):

    label = 'statistics for angle %9s' % (name)
    sql   = 'select min(%s),max(%s),avg(%s),std(%s) from SlewFinalState where sessionID=%d' % (name, name, name, name, sessionID)
    ret   = getDbData(database, sql)
    print "%s: min=%6.1fd max=%6.1fd avg=%6.1fd std=%5.1fd" % (label, ret[0][0]*RAD2DEG, ret[0][1]*RAD2DEG, ret[0][2]*RAD2DEG, ret[0][3]*RAD2DEG)
    
def reportActivity(name, sessionID, total):

    label = 'slew activity for %12s' % (name)
    sql   = 'select avg(delay),max(delay),count(delay) from SlewActivities where sessionID=%d and activity="%s" and delay>0' % (sessionID, name)
    ret   = getDbData(database, sql)
    A     = ret[0][0]
    M     = ret[0][1]
    N     = ret[0][2]
    sql   = 'select count(*),avg(delay) from SlewActivities where sessionID=%d and activity="%s" and inCriticalPath="True" and delay>0' % (sessionID, name)
    ret   = getDbData(database, sql)
    C     = ret[0][0]
    CA    = ret[0][1]
    if CA == None:
	CA = 0.0
    if (A != None) and (C != None):
	print "%s: active=%5.1f%% of slews, active avg=%6.2fs, total avg=%6.2fs, max=%6.2fs, in critical path=%5.1f%% with avg=%6.2fs cont=%6.2fs" % (label, 100.0*N/total, A, A*N/total, M, 100.0*C/total, CA, CA*C/total)

def reportMaxSpeed(name, sessionID):

    label = 'slew maximum speed for %8s' % (name)
    sql   = 'select avg(abs(%sSpd)),max(abs(%sSpd)),max(slewCount) from SlewMaxSpeeds where sessionID=%d' % (name, name, sessionID)
    ret   = getDbData(database, sql)
    A     = ret[0][0]
    M     = ret[0][1]
    T     = ret[0][2]
    sql   = 'select count(*) from SlewMaxSpeeds where sessionID=%d and abs(%sSpd)>=%f' % (sessionID, name, 0.99*M)
    ret   = getDbData(database, sql)
    C     = ret[0][0]
    print "%s: avg=%.2fd/s, max=%.2fd/s in %5.1f%% of slews" % (label, A*RAD2DEG, M*RAD2DEG, 100.0*C/T)

    return

def reportSequences(label, propID):
                                                                                                                                                                                                                    
    sql = 'select count(*) from SeqHistory where sessionID=%d and propID=%d and endStatus=0' % (sessionID, propID)
    ret   = getDbData(database, sql)
    N_complete = ret[0][0]
                                                                                                                                                                                                                    
    sql = 'select count(*) from SeqHistory where sessionID=%d and propID=%d and endStatus=1' % (sessionID, propID)
    ret   = getDbData(database, sql)
    N_lost_missed = ret[0][0]
                                                                                                                                                                                                                    
    sql = 'select count(*) from SeqHistory where sessionID=%d and propID=%d and endStatus=3 and completion>0' % (sessionID, propID)
    ret   = getDbData(database, sql)
    N_lost_simulation = ret[0][0]
                                                                                                                                                                                                                    
    print "%s: %d complete sequences" % (label, N_complete)
    print "%s: %d lost sequences due to missed event" % (label, N_lost_missed)
    print "%s: %d lost sequences due to end of simulation" % (label, N_lost_simulation)
                                                                                                                                                                                                                    
    sql = 'select completion,count(0) from SeqHistory where sessionID=%d and propID=%d group by completion' % (sessionID, propID)
    ret   = getDbData(database, sql)
    integratedCompletion = {}
    list_icp = range(0,101,5)
    for icp in list_icp:
	integratedCompletion[icp] = 0
    for p in range(len(ret)):
	percentage = ret[p][0]*100
	count      = ret[p][1]
        print "%s: histogram %6.2f%% %d" % (label, percentage, count)
	for icp in list_icp:
	    if icp <= percentage:
		integratedCompletion[icp] += count
    for icp in list_icp:
        print "%s: integrated completion: %4d fields %3.0f%% or more" % (label, integratedCompletion[icp], icp)

    return                                                                                                                                                                                                                    
def reportWL(sessionID):

    label = 'ids_WL'
    sql   = 'select propID,propConf from Proposal where sessionID=%d and propName="WL"' % (sessionID)
    ids_WL   = getDbData(database, sql)
    if ids_WL == None:
        return

    for q in range(len(ids_WL)):
	propID = ids_WL[q][0]
	propConf = ids_WL[q][1]
	label = 'Weak Lensing'
        sql   = 'select paramName,paramValue from Config where sessionID=%d and moduleName="weakLensing" and propID=%d order by paramIndex' % (sessionID,propID)
        config_WL   = getDbData(database, sql)
        dict_WL = {}
        for kv in config_WL:
	    if kv[0] in dict_WL.keys():
	        if isinstance(dict_WL[kv[0]], list):
		    dict_WL[kv[0]].append(kv[1])
         	else:
	            dict_WL[kv[0]] = [dict_WL[kv[0]],kv[1]]
	    else:
                dict_WL[kv[0]] = kv[1]
        #print dict_WL

        Filter = dict_WL['Filter']
        Filter_Visits = {}
        for ix in range(len(Filter)):
            Filter_Visits[Filter[ix]] = eval(dict_WL['Filter_Visits'][ix])

#	f1 = dict_WL['Filter'][0]
#        f2 = dict_WL['Filter'][1]
#        f3 = dict_WL['Filter'][2]
#        f4 = dict_WL['Filter'][3]
#        f5 = dict_WL['Filter'][4]

#        f1Visits = eval(dict_WL[str(f1)+'FilterVisits'])
#        f2Visits = eval(dict_WL[str(f2)+'FilterVisits'])
#        f3Visits = eval(dict_WL[str(f3)+'FilterVisits'])
#        f4Visits = eval(dict_WL[str(f4)+'FilterVisits'])
#	f5Visits = eval(dict_WL[str(f5)+'FilterVisits'])

	print "================================================================"
	print "%s: propID=%d" % (propConf, propID)

	sql = 'DROP TABLE IF EXISTS tmpObs, tmpObs1, tmpVisits'
	ret = getDbData(database, sql)

	sql = 'create table tmpObs select propID,fieldID,fieldRA,fieldDec,filter,expDate from ObsHistory where sessionID=%d and propID=%d group by expDate order by propID,fieldID,filter' % (sessionID, propID)
	ret = getDbData(database, sql)
        sql = 'create index ix_tmpObs_1 on tmpObs (propID)'
        ret = getDbData(database, sql)
        sql = 'create index ix_tmpObs_2 on tmpObs (fieldID)'
        ret = getDbData(database, sql)
        sql = 'create index ix_tmpObs_3 on tmpObs (filter)'
        ret = getDbData(database, sql)

	sql = 'create table tmpObs1 select *,count(filter) as visits from tmpObs group by propID,fieldID,filter order by propID,fieldID,filter'
	ret = getDbData(database, sql)
        sql = 'create index ix_tmpObs1_1 on tmpObs1 (fieldID)'
        ret = getDbData(database, sql)
        sql = 'create index ix_tmpObs1_2 on tmpObs1 (filter)'
        ret = getDbData(database, sql)

	sql = 'create table tmpVisits select fieldID,'
        for ix in range(len(Filter)-1):
            sql+= 'sum(if(filter="%s", visits, 0)) as Nf%s,' % (Filter[ix], Filter[ix])
        sql+= 'sum(if(filter="%s", visits, 0)) as Nf%s' % (Filter[-1], Filter[-1])
#	sql+= 'sum(if(filter="%s", visits, 0)) as Nf1,' % (f1)
#	sql+= 'sum(if(filter="%s", visits, 0)) as Nf2,' % (f2)
#	sql+= 'sum(if(filter="%s", visits, 0)) as Nf3,' % (f3)
#	sql+= 'sum(if(filter="%s", visits, 0)) as Nf4,' % (f4)
#	sql+= 'sum(if(filter="%s", visits, 0)) as Nf5'  % (f5)
	sql+= ' from tmpObs1 group by fieldID'
	ret = getDbData(database, sql)
        sql = 'create index ix_tmpVisits_1 on tmpVisits (fieldID)'
        ret = getDbData(database, sql)

        C = {}
        H = {}
        for filter in Filter:
            sql = 'select count(fieldID) from tmpVisits where Nf%s>=%d'  % (filter, Filter_Visits[filter])
            ret = getDbData(database, sql)
            C[filter] = ret[0][0]

            sql = 'select Nf%s,count(0) from tmpVisits group by Nf%s' % (filter, filter)
            ret = getDbData(database, sql)
            H[filter] = ret
                            
#        sql = 'select count(fieldID) from tmpVisits where Nf1>=%d'  % (f1Visits)
#	ret = getDbData(database, sql)
#	C1  = ret[0][0]
#	sql = 'select count(fieldID) from tmpVisits where Nf2>=%d'  % (f2Visits)
#	ret = getDbData(database, sql)
#	C2  = ret[0][0]
#	sql = 'select count(fieldID) from tmpVisits where Nf3>=%d'  % (f3Visits)
#	ret = getDbData(database, sql)
#	C3  = ret[0][0]
#	sql = 'select count(fieldID) from tmpVisits where Nf4>=%d'  % (f4Visits)
#	ret = getDbData(database, sql)
#	C4  = ret[0][0]
#	sql = 'select count(fieldID) from tmpVisits where Nf5>=%d'  % (f5Visits)
#	ret = getDbData(database, sql)
#	C5  = ret[0][0]

#	sql = 'select Nf1,count(0) from tmpVisits group by Nf1'
#	ret = getDbData(database, sql)
#	H1  = ret
#	sql = 'select Nf2,count(0) from tmpVisits group by Nf2'
#	ret = getDbData(database, sql)
#	H2  = ret
#	sql = 'select Nf3,count(0) from tmpVisits group by Nf3'
#	ret = getDbData(database, sql)
#	H3  = ret
#	sql = 'select Nf4,count(0) from tmpVisits group by Nf4'
#	ret = getDbData(database, sql)
#	H4  = ret
#	sql = 'select Nf5,count(0) from tmpVisits group by Nf5'
#	ret = getDbData(database, sql)
#	H5  = ret

	sql = 'select count(fieldID) from tmpVisits where '
        for ix in range(len(Filter)-1):
            sql+= 'Nf%s>=%d and ' % (Filter[ix], Filter_Visits[Filter[ix]])
        sql+= 'Nf%s>=%d' % (Filter[-1], Filter_Visits[Filter[-1]])

#        sql+= 'Nf1>=%d and ' % (f1Visits)
#	sql+= 'Nf2>=%d and ' % (f2Visits)
#	sql+= 'Nf3>=%d and ' % (f3Visits)
#	sql+= 'Nf4>=%d and ' % (f4Visits)
#	sql+= 'Nf5>=%d'      % (f5Visits)
	ret = getDbData(database, sql)
	Call= ret[0][0]

	print "%s: %d complete fields. Completion per filter:" % (propConf, Call)
        for filter in Filter:
            print "%s: %s %d" % (propConf, filter, C[filter])
#        print "%s: %s %d" % (label, f1, C1)
#	print "%s: %s %d" % (label, f2, C2)
#	print "%s: %s %d" % (label, f3, C3)
#	print "%s: %s %d" % (label, f4, C4)
#	print "%s: %s %d" % (label, f5, C5)
            for p in range(len(H[filter])):
		print "%s: histogram %s %6.2f%% %d" % (propConf, filter, float(H[filter][p][0])*100.0/float(Filter_Visits[filter]), H[filter][p][1])
#                print "%s: histogram %s %6.2f%% %d" % (propConf, filter, H[filter][p][0]*100.0/Filter_Visits[filter], H[filter][p][1])
                        
#        for p in range(len(H1)):
#            print "%s: histogram %s %6.2f%% %d" % (label, f1, H1[p][0]*100.0/f1Visits, H1[p][1])
#        for p in range(len(H2)):
#            print "%s: histogram %s %6.2f%% %d" % (label, f2, H2[p][0]*100.0/f2Visits, H2[p][1])
#        for p in range(len(H3)):
#            print "%s: histogram %s %6.2f%% %d" % (label, f3, H3[p][0]*100.0/f3Visits, H3[p][1])
#        for p in range(len(H4)):
#            print "%s: histogram %s %6.2f%% %d" % (label, f4, H4[p][0]*100.0/f4Visits, H4[p][1])
#        for p in range(len(H5)):
#            print "%s: histogram %s %6.2f%% %d" % (label, f5, H5[p][0]*100.0/f5Visits, H5[p][1])

	sql = 'DROP TABLE IF EXISTS tmpObs, tmpObs1, tmpVisits'
	ret = getDbData(database, sql)

    return

def reportNEA(sessionID):
                                                                                                                                                                      
    label = 'Near Earth Asteroids'
    sql   = 'select propID,propConf from Proposal where sessionID=%d and propName="NEA"' % (sessionID)
    ret   = getDbData(database, sql)
    if ret == None:
        return

    for p in range(len(ret)):
	propID = ret[p][0]
	propConf = ret[p][1]
	print "================================================================"
	print "%s: propID=%d" % (propConf, propID)
	reportSequences(propConf, propID)
	sql = 'select count(*) from SeqHistory where propID=%d and endStatus=2' % (propID)
	endLunation  = getDbData(database, sql)
	N_lost_lunation = endLunation[0][0]
	print "%s: %d lost sequences due to end of lunation" % (propConf, N_lost_lunation)

    return

def reportSN(sessionID):

    label = 'Super Nova'
    sql   = 'select propID,propConf from Proposal where sessionID=%d and propName="SN"' % (sessionID)
    ret   = getDbData(database, sql)
    if ret == None:
        return

    for p in range(len(ret)):
	propConf = ret[p][1]
	propID = ret[p][0]
	print "================================================================"
	print "%s: propID=%d" % (propConf, propID)
	reportSequences(propConf, propID)

    return
    
def reportSNSS(sessionID):
                                                                                                                                                                             
    label = 'Super Nova with Sub-Sequences'
    sql   = 'select propID,propConf from Proposal where sessionID=%d and propName="SNSS"' % (sessionID)
    ret   = getDbData(database, sql)
    if ret == None:
        return
    if len(ret) == 0:
        return

    for p in range(len(ret)):
	propID = ret[p][0]
	propConf = ret[p][1]
	print "================================================================"
	print "%s: propID=%d" % (propConf, propID)
	reportSequences(propConf, propID)

    return

def reportKBO(sessionID):
                                                                                                                                                                             
    label = 'Kuiper Belt Object'
    sql   = 'select propID,propConf from Proposal where sessionID=%d and propName="KBO"' % (sessionID)
    ret   = getDbData(database, sql)
    if ret == None:
        return

    for p in range(len(ret)):
	propID = ret[p][0]
	propConf = ret[p][1]
	print "================================================================"
	print "%s: propID=%d" % (propConf, propID)
	reportSequences(propConf, propID)

    return
                                                                                                                                                                             
def reportWLTSS(sessionID, host):
                                                                                                                                                                             
    label = 'Weak Lensing as Transient with Sub-Sequences'
    sql   = 'select propID,propConf from Proposal where sessionID=%d and propName="WLTSS"' % (sessionID)
    list_propID = getDbData(database, sql)
    if list_propID == None:
        return

    for p in range(len(list_propID)):
	propID = list_propID[p][0]
	propConf=list_propID[p][1]
	print "================================================================"
	print "%s: propID=%d" % (propConf, propID)
	reportSequences(propConf, propID)

	sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqFilters" order by paramIndex' % (sessionID, propID)
	list_filter = getDbData(database, sql)

        sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqEvents" order by paramIndex' % (sessionID, propID)
        list_events = getDbData(database, sql)

        sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqInterval" order by paramIndex' % (sessionID, propID)
        list_interval = getDbData(database, sql)
                                                                                                                 
        sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqWindowStart" order by paramIndex' % (sessionID, propID)
        list_windowstart = getDbData(database, sql)
                                                                                                                 
        sql = 'select paramValue from Config where sessionID=%d and propID=%d and paramName="SubSeqWindowEnd" order by paramIndex' % (sessionID, propID)
        list_windowend = getDbData(database, sql)

	visits_seqnNum_filter = {}
	reqvisits_filter = {}
	list_seqnNum_visits = {}
        list_seqnNum_pairs  = {}
	totalNpairs = 0
	totalNmaxpairs = 0
	pairsfile = open('../output/%s_%d_pairs.%d' % (host, sessionID, propID), 'w')
	pairsfile.write('#pairs for run %s sessionID=%d proposalID=%d %s\n' % (host, sessionID, propID, propConf))
        pairsfile.write('%8s %8s %12s %12s %6s %14s %14s %12s %12s %8s\n' % ('#seqnNum','fieldID','RA','Dec','filter','MJD1','MJD2','expDate1','expDate2','interval'))

	for f in range(len(list_filter)):
	    filter = list_filter[f][0]
	    events = eval(list_events[f][0])
	    interval = eval(list_interval[f][0])
	    windowstart = eval(list_windowstart[f][0])
	    windowend = eval(list_windowend[f][0])

	    intervalmin = interval*(1+windowstart)
	    intervalmax = interval*(1+windowend)

	    print "----------------------"
	    print "%s: filter=%s goal_visits=%d" % (propConf, filter, events)
	    sql = 'DROP TABLE IF EXISTS tmpWLTSSvisits'
	    ret = getDbData(database, sql)
	    sql = 'create table tmpWLTSSvisits select seqnNum,count(*) as visits from ObsHistory where sessionID=%d and propID=%d and filter="%s" group by seqnNum' % (sessionID, propID, filter)
	    list_seqnNum_visits[filter] = getDbData(database, sql)
	    sql = 'create index ix_tmpWLTSSvisits_1 on tmpWLTSSvisits (seqnNum)'
            ret = getDbData(database, sql)

	    sql = 'select visits,count(*) from tmpWLTSSvisits group by visits'
	    histogram = getDbData(database, sql)
	    for h in range(len(histogram)):
		print "%s: histogram filter=%s %6.2f%% %d" % (propConf, filter, histogram[h][0]*100.0/events, histogram[h][1])

            sql = 'select seqnNum,expDate,fieldID,fieldRA,fieldDec,expMJD from ObsHistory where sessionID=%d and propID=%d and filter="%s" order by seqnNum,expDate' % (sessionID, propID, filter)
            list_seqnNum_expDate = getDbData(database, sql)
	    for record in list_seqnNum_expDate:
		seqnNum = record[0]
		if visits_seqnNum_filter.has_key(seqnNum):
		    if visits_seqnNum_filter[seqnNum].has_key(filter):
			visits_seqnNum_filter[seqnNum][filter] += 1
		    else:
                        visits_seqnNum_filter[seqnNum][filter] = 1
		else:
                    visits_seqnNum_filter[seqnNum] = { filter : 1 }
	    reqvisits_filter[filter] = events

	    if interval>0:
#		sql = 'create table tmpWLTSSobspairs select t1.seqnNum,t1.expDate,t2.expDate as expDate2 from ObsHistory t1, ObsHistory t2 where t1.sessionID=%d and t2.sessionID=%d and t1.propID=%d and t2.propID=%d and t1.filter="%s" and t2.filter="%s" and t1.seqnNum=t2.seqnNum and t1.expDate<t2.expDate and (t2.expDate-t1.expDate) between %f and %f' % (sessionID,sessionID, propID,propID, filter,filter, intervalmin, intervalmax)
#		ret = getDbData(database, sql)
#	        sql = 'create table tmpWLTSSpairs select seqnNum,count(*) as pairs from tmpWLTSSobspairs group by seqnNum'
#	        list_seqnNum_pairs[filter] = getDbData(database, sql)
#	        sql = 'select pairs,count(*) from tmpWLTSSpairs group by pairs'
#	        histogram = getDbData(database, sql)
#	        for h in range(len(histogram)):
#	            print "%s: pairs histogram filter=%s %d %d" % (propConf, filter, histogram[h][0], histogram[h][1])

	        sql = 'DROP TABLE IF EXISTS tmpWLTSSpairs'
                ret = getDbData(database, sql)
                sql = 'create table tmpWLTSSpairs select seqnNum,floor(count(0)/2) as maxpairs from ObsHistory where sessionID=%d and propID=%d and filter="%s" group by seqnNum' % (sessionID, propID, filter)
                ret = getDbData(database, sql)
                sql = 'create index ix_tmpWLTSSpairs_1 on tmpWLTSSpairs (seqnNum)'
                ret = getDbData(database, sql)

                sql = 'select sum(maxpairs) from tmpWLTSSpairs'
                filterNmaxpairs = getDbData(database, sql)[0][0]
		if filterNmaxpairs == None:
		    filterNmaxpairs = 0
		totalNmaxpairs += filterNmaxpairs
                sql = 'DROP TABLE IF EXISTS tmpWLTSSpairs'
                ret = getDbData(database, sql)

		if filterNmaxpairs > 0:
#		    sql = 'select seqnNum,expDate from ObsHistory where sessionID=%d and propID=%d and filter="%s" order by seqnNum,expDate' % (sessionID, propID, filter)
#		    list_seqnNum_expDate = getDbData(database, sql)
		    pairs = {}
		
  		    nobs = len(list_seqnNum_expDate)
                    filterNpairs = 0
		    k = 0
		    while k<nobs-2:

		        seqnNum1 = list_seqnNum_expDate[k][0]
		        expDate1 = list_seqnNum_expDate[k][1]
                        seqnNum2 = list_seqnNum_expDate[k+1][0]
                        expDate2 = list_seqnNum_expDate[k+1][1]
		        if seqnNum1 == seqnNum2:
			    if intervalmin <= (expDate2-expDate1) <= intervalmax:
			        if pairs.has_key(seqnNum1):
				    pairs[seqnNum1] += 1
			        else:
				    pairs[seqnNum1] = 1
                                fieldID = int(list_seqnNum_expDate[k][2])
                                fieldRA = float(list_seqnNum_expDate[k][3])
                                fieldDec= float(list_seqnNum_expDate[k][4])
                                expMJD1 = float(list_seqnNum_expDate[k][5])
                                expMJD2 = float(list_seqnNum_expDate[k+1][5])
                                pairsfile.write('%8d %8d %12f %12f %6s %14f %14f %12d %12d %8d\n' % (seqnNum1,fieldID,fieldRA,fieldDec,filter,expMJD1,expMJD2,expDate1,expDate2,expDate2-expDate1))
			        k += 1
			        filterNpairs += 1
			        totalNpairs  += 1
		        k += 1
		    histogram = {}
		    for seq in pairs.keys():
		        if histogram.has_key(pairs[seq]):
			    histogram[pairs[seq]] += 1
		        else:
			    histogram[pairs[seq]] = 1
		    print "%s: %d pairs achieved for filter=%s, %4.1f%%" % (propConf, filterNpairs, filter, 100.0*float(filterNpairs)/float(filterNmaxpairs))
		    for h in histogram.keys():
		        print "%s: pairs histogram filter=%s %d %d" % (propConf, filter, h, histogram[h])

	    sql = 'DROP TABLE IF EXISTS tmpWLTSSvisits'
            ret = getDbData(database, sql)
	pairsfile.close()

	if totalNmaxpairs > 0:
            print "----------------------"
	    print "%s: TOTAL %d pairs achieved, %4.1f%%" % (propConf, totalNpairs, 100.0*float(totalNpairs)/float(totalNmaxpairs))

        print "----------------------"
        histseqlevels = range(0,101,5)
        histseq = {}
        for h in histseqlevels:
            histseq[h] = 0
        for seq in visits_seqnNum_filter.keys():
	    for h in histseqlevels:
	        stilltesting = True
	        for filter in reqvisits_filter.keys():
		    if not visits_seqnNum_filter[seq].has_key(filter):
			visits_seqnNum_filter[seq][filter] = 0
		    if visits_seqnNum_filter[seq][filter] < 0.01*h*reqvisits_filter[filter]:
		        stilltesting = False
		        break
	        if stilltesting:
		    histseq[h] += 1
        for h in histseqlevels:
	    print "%s: Sequences with all filters equal or more than %d%% = %d" % (propConf, h, histseq[h])

    return

try:
    database = sys.argv[1]
    sessionID = int (sys.argv[2])
    val = sys.argv[3:]
except:
    print "\n\n..........No session parameter found!"
    print "..........Use newextract.py <database> <sessionID>\n\n"
    done 
try:
    option1 = val[1]
    if option1 == "notcs":
	notcs = True
    else:
	notcs = False
except:
    notcs = False
report(database, sessionID, notcs)

