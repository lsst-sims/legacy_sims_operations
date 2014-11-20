####################################################################
#  MODIFIED
#  Srinivasan Chandrasekharan (9/11/2009)
#
#   quick plots from opsim 
#      airmass
#      seeing
#      skybrightness
# 
####################################################################
####################################################################
#  Written by: Lynne Jones - UW - v0.1   
#  Questions or comments, email : ljones@astro.washington.edu
####################################################################

import MySQLdb as mysql
import numpy
import pylab

rad2deg = 180.0/numpy.pi
deg2rad = numpy.pi/180.0
daysperyear = 365.24
minexpmjd = 49353

def opsimConnect(hostname='localhost', username='www', passwdname = 'zxcvbnm', dbname='OpsimDB'): 
    """ Connect to opsim mysql database """
    db = mysql.connect(host=hostname, user=username, passwd = passwdname, db=dbname)
    return db.cursor()

def opsimQuery(cursor, sqlquery, verbose=True):
    """ Execute a sql query  """
    # sqlquery is the sql-format query you want to execute, as a string
    if verbose:
        print '#', sqlquery
    cursor.execute(sqlquery)
    return cursor.fetchall()

def createLimitSQL(opsimdb, unipropids, topic):
    query = "select %s from %s where " % (topic, opsimdb)

    for i in range(0, len(unipropids)):
        if (i == len(unipropids) - 1):
	    query = query + "propID=%d" % unipropids[i]
        else:
            query = query + "propID=%d or " % unipropids[i]
    query = query + " order by %s" % (topic)
    return query

def createTopicSQL(opsimdb, filter, unipropids, topic):
    # query = "select %s from (select %s, filter, propid from %s group by expDate) as t where filter='%s' and (" % (topic, topic, opsimdb, filter)
    query = "select %s from %s where filter='%s' and (" % (topic, opsimdb, filter)

    for i in range(0, len(unipropids)):
        if (i == len(unipropids) - 1):
	    query = query + "propID=%d)" % unipropids[i]
        else:
            query = query + "propID=%d or " % unipropids[i]
    query = query + " order by %s" % (topic)
    return query

def readCoadded(unique_id, filter):
	""" hewelhog_56_coadded_raw.dat  """
	filename = "../output/%s_coadded_raw.dat" % (unique_id)
	file = open(filename, "r")
	coadded_filter = []
	
	for line in file.readlines() :
		data = line.split()
		if ( data[1] == filter ) :
			coadded_filter.append(float(data[2]))
	return coadded_filter

def readCoaddedWFD(unique_id, filter):
	""" hewelhog_56_coadded_wfd.dat  """
	filename = "../output/%s_coadded_wfd.dat" % (unique_id)
	file = open(filename, "r")
	coadded_filter = []
	
	for line in file.readlines() :
		data = line.split()
		if ( data[1] == filter ) :
			coadded_filter.append(float(data[2]))
	return coadded_filter

def analyze_seeing(opsimdb, cursor, filters, unipropids, savefig=False, figname='seeing'):
    """ Test seeing distribution """
    seeingvalues = {}
    per25 = {}
    per75= {}
    median = {}

    # find limits for histogram bins, compute binsize, and bin range
    query = createLimitSQL(opsimdb, unipropids, 'finSeeing')
    seeinglim =  opsimQuery(cursor, query)
    seeinglim =  numpy.array(seeinglim)
    lo = numpy.floor(numpy.min(seeinglim)*100)/100
    hi = numpy.ceil(numpy.max(seeinglim)*100)/100
    b = numpy.arange(lo,hi,0.02)

    for filter in filters:
        query = createTopicSQL(opsimdb, filter, unipropids, 'finSeeing')
        #query = "select seeing from %s where filter = '%s' and propid=%d order by seeing" %(opsimdb, filter, unipropids)
        seeingvalues[filter] = opsimQuery(cursor, query)
        seeingvalues[filter] = numpy.array(seeingvalues[filter])
        seeingvalues[filter] = numpy.sort(seeingvalues[filter])
        if len(seeingvalues[filter]) == 0:
            per25[filter] = 0
            median[filter] = 0
            per75[filter] = 0
            continue;
        max = seeingvalues[filter].max()
        min = seeingvalues[filter].min()
        median[filter] = numpy.median(seeingvalues[filter])
        mean = seeingvalues[filter].mean()
        stdev = numpy.std(seeingvalues[filter])
        per25[filter] = seeingvalues[filter][int(len(seeingvalues[filter])*.25)]
        per75[filter] = seeingvalues[filter][int(len(seeingvalues[filter])*.75)]
        print "In filter %s" %(filter)
        print "Maximum seeing is %f" %(max)
        print "Minimum seeing is %f" %(min)
        print "Median seeing  is %f" %(median[filter])
        print "Seeing at 25 percentile %f" %(per25[filter])
        print "Seeing at 75 percentile %f" %(per75[filter])
        print "Mean seeing is %f" %(mean)
        print "Standard deviation of seeing is %f" %(stdev)
        print "Total number of seeing measurements: %d" %(len(seeingvalues[filter]))
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    usefilter = 'u'
    leg = "%s : %.2f / %.2f / %.2f" %(usefilter, per25[usefilter], median[usefilter], per75[usefilter])
    #colors = ('m', 'b', 'g', 'y', 'r', 'k', 'c', 'm')
    colors = ('#9966CC', '#3366CC', '#339933', '#CCCC33', '#FF6600', '#CC3333', 'c', '#666666')
    if len(seeingvalues['u']) != 0:
        keynum, keybins, keypatches = pylab.hist(seeingvalues[usefilter], bins=b, label=leg, facecolor='none', edgecolor=colors[0], linewidth=2, histtype='step')
        maxy = keynum.max()
    else:
        maxy = 0
    i=1
    for filter in filters:
        if len(seeingvalues[filter]) == 0:
            continue;
        if filter == usefilter:
            continue
        else:
            leg = "%s : %.2f / %.2f / %.2f" %(filter, per25[filter], median[filter], per75[filter])
            numtemp, bintemp, patchestemp = pylab.hist(seeingvalues[filter], bins=b, label=leg, facecolor='none', edgecolor=colors[i], linewidth=2, histtype='step')
            temp = numtemp.max()
            if temp>maxy:
                maxy = temp
            i=i+1
    #pylab.legend(loc=0)
    pylab.legend(loc=(1.05,0.45))
    pylab.ylim(0, maxy*1.1)
    pylab.xlabel("Seeing (FWHM in arcsec)", fontsize=18)
    pylab.ylabel("Number of Visits", fontsize=18)
    #figlabel = "Seeing in various Filters"
    #pylab.figtext(0.15, 0.92, figlabel)
    if savefig:
        fname = figname + '.png'
        pylab.savefig(fname, format='png')
    return

def analyze_airmass(opsimdb, cursor, filters, unipropids, savefig=False, figname='airmass'):
    """ Test airmass distribution """
    airmassvalues = {}
    median = {}
    per25 = {}
    per75 = {}


    # find limits for histogram bins, compute binsize, and bin range
    query = createLimitSQL(opsimdb, unipropids, 'airmass')
    airmasslim =  opsimQuery(cursor, query)
    airmasslim =  numpy.array(airmasslim)
    lo = numpy.floor(numpy.min(airmasslim)*1000)/1000
    hi = numpy.ceil(numpy.max(airmasslim)*1000)/1000
    hi = 1.8
    b = numpy.arange(lo,hi,0.01)

    #airmasslimits = (1, 2.2) # a bit random, change if necessary
    for filter in filters:
        query = createTopicSQL(opsimdb, filter, unipropids, 'airmass')
        #query = "select airmass from %s where filter = '%s' and propid=%d order by airmass" %(opsimdb, filter, unipropids)
        airmassvalues[filter] = opsimQuery(cursor, query)
        airmassvalues[filter] = numpy.array(airmassvalues[filter])
        airmassvalues[filter] = numpy.sort(airmassvalues[filter])
        if len(airmassvalues[filter]) == 0:
            per25[filter] = 0
            median[filter] = 0
            per75[filter] = 0
            continue;
        max = airmassvalues[filter].max()
        min = airmassvalues[filter].min()
        median[filter] = numpy.median(airmassvalues[filter])
        mean = airmassvalues[filter].mean()
        stdev = numpy.std(airmassvalues[filter])
        per25[filter] = airmassvalues[filter][int(len(airmassvalues[filter])*.25)]
        per75[filter] = airmassvalues[filter][int(len(airmassvalues[filter])*.75)]
        print "In filter %s" %(filter)
        print "Maximum airmass is %f" %(max)
        print "Minimum airmass is %f" %(min)
        print "Median airmass  is %f" %(median[filter])
        print "Airmass at 25 percentile %f" %(per25[filter])
        print "Airmass at 75 percentile %f" %(per75[filter])
        print "Mean airmass is %f" %(mean)
        print "Standard deviation of airmass is %f" %(stdev)
        print "Total number of airmass measurements: %d" %(len(airmassvalues[filter]))
    # make the plot
    #pylab.figure()
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.1,0.1,0.65,0.82])
    usefilter = 'u'
    leg = "%s : %.2f / %.2f / %.2f" %(usefilter, per25[usefilter], median[usefilter], per75[usefilter])
    #colors = ('m', 'b', 'g', 'y', 'r', 'k', 'c', 'm')
    colors = ('#9966CC', '#3366CC', '#339933', '#CCCC33', '#FF6600', '#CC3333', 'c', '#666666')
    if len(airmassvalues['u']) != 0:
        keynum, keybins, keypatches = pylab.hist(airmassvalues[usefilter], bins=b, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[0], linewidth=2)
        maxy = keynum.max()
    else:
        maxy = 0
    i = 1
    for filter in filters:
        if len(airmassvalues[filter]) == 0:
            continue
        if filter == usefilter:
            continue
        else:
            leg = "%s : %.2f / %.2f / %.2f" %(filter,  per25[filter], median[filter], per75[filter])
            numtemp, bintemp, patchestemp = pylab.hist(airmassvalues[filter], bins=b, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[i], linewidth=2)
            temp = numtemp.max()
            if temp>maxy:
                maxy = temp
            i = i+1
    #pylab.legend(loc=0)
    pylab.legend(loc=(1.05,0.45))
    pylab.ylim(0, maxy*1.1)
    pylab.xlabel("Airmass", fontsize=18)
    pylab.ylabel("Number of Visits", fontsize=18)
    #figlabel = "Airmass Distribution in Filters"
    #pylab.figtext(0.17, 0.92, figlabel)
    if savefig:
        fname = figname + '.png'
        pylab.savefig(fname, format='png')
    return

def analyze_skyb(opsimdb, cursor, filters, unipropids, savefig=False, figname='skyb'):
    """ Test Skybrightness distribution """
    skybvalues = {}
    median = {}
    per25 = {}
    per75 = {}

    #skyblimits = (18.0, 25.0) # a bit random, change if necessary
    # find limits for histogram bins, compute binsize, and bin range
    query = createLimitSQL(opsimdb, unipropids, 'perry_skybrightness')
    skyblim =  opsimQuery(cursor, query)
    skyblim =  numpy.array(skyblim)
    lo = numpy.floor(numpy.min(skyblim)*100)/100
    hi = numpy.ceil(numpy.max(skyblim)*100)/100
    b = numpy.arange(lo,hi,0.05)
    
    for filter in filters:
        query = createTopicSQL(opsimdb, filter, unipropids, 'perry_skybrightness')
        #query = "select perry_skybrightness from %s where filter = '%s' and propid=%d order by perry_skybrightness" %(opsimdb, filter, unipropids)
        skybvalues[filter] = opsimQuery(cursor, query)
        skybvalues[filter] = numpy.array(skybvalues[filter])
        skybvalues[filter] = numpy.sort(skybvalues[filter])
        if len(skybvalues[filter]) == 0:
            per25[filter] = 0
            median[filter] = 0
            per75[filter] = 0
            max = 0
            min = 0
            continue;
        max = skybvalues[filter].max()
        min = skybvalues[filter].min()
        median[filter] = numpy.median(skybvalues[filter])
        mean = skybvalues[filter].mean()
        stdev = numpy.std(skybvalues[filter])
        per25[filter] = skybvalues[filter][int(len(skybvalues[filter])*.25)]
        per75[filter] = skybvalues[filter][int(len(skybvalues[filter])*.75)]
        print "In filter %s" %(filter)
        print "Maximum sky brightness is %f" %(max)
        print "Minimum sky brightness is %f" %(min)
        print "Median sky brightness is %f" %(median[filter])
        print "Sky Brightness at 25 percentile %f" %(per25[filter])
        print "Sky Brightness at 75 percentile %f" %(per75[filter])
        print "Mean sky brightness is %f" %(mean)
        print "Standard deviation of sky brightness is %f" %(stdev)
        print "Total number of sky brightness measurements: %d" %(len(skybvalues[filter]))
    # make the plot
    #pylab.figure()
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    usefilter = 'u'
    leg = "%s : %.2f / %.2f / %.2f" %(usefilter, per25[usefilter], median[usefilter], per75[usefilter])
    #colors = ('m', 'b', 'g', 'y', 'r', 'k', 'c', 'm')
    colors = ('#9966CC', '#3366CC', '#339933', '#CCCC33', '#FF6600', '#CC3333', 'c', '#666666')
    if len(skybvalues['u']) != 0:
        keynum, keybins, keypatches = pylab.hist(skybvalues[usefilter], bins=b, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[0], linewidth=2)
        maxy = keynum.max()
    else:
        maxy = 0
    i = 1
    for filter in filters:
        if len(skybvalues[filter]) == 0:
            continue
        if filter == usefilter:
            continue
        else:
            leg = "%s : %.2f / %.2f / %.2f" %(filter,  per25[filter], median[filter], per75[filter])
            numtemp, bintemp, patchestemp = pylab.hist(skybvalues[filter], bins=b, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[i], linewidth=2)
            temp = numtemp.max()
            if temp>maxy:
                maxy = temp
            i = i+1
    #pylab.legend(loc=0)
    pylab.legend(loc=(1.05,0.45))
    pylab.ylim(0, maxy*1.1)
    pylab.xlabel("Sky Brightness", fontsize=18)
    pylab.ylabel("Number of Visits", fontsize=18)
    #figlabel = "Sky Brightness Distribution in Filters"
    #pylab.figtext(0.17, 0.92, figlabel)
    if savefig:
        fname = figname + '.png'
        pylab.savefig(fname, format='png')
    return

def analyze_m5(opsimdb, cursor, filters, unipropids, savefig=False, figname='m5'):
    """ Test 5 Sigma Single Visit Depth distribution """
    m5values = {}
    median = {}
    per25 = {}
    per75 = {}

    #m5limits = (18.0, 25.0) # a bit random, change if necessary
    # find limits for histogram bins, compute binsize, and bin range
    query = createLimitSQL(opsimdb, unipropids, 'fivesigma_ps')
    sigmalim =  opsimQuery(cursor, query)
    sigmalim =  numpy.array(sigmalim)
    lo = numpy.floor(numpy.min(sigmalim)*100)/100
    hi = numpy.ceil(numpy.max(sigmalim)*100)/100
    b = numpy.arange(lo,hi,0.05)

    for filter in filters:
        query = createTopicSQL(opsimdb, filter, unipropids, 'fivesigma_ps')
        #query = "select 5sigma_ps from %s where filter='%s' and propid=%d order by 5sigma_ps" %(opsimdb, filter, unipropids)
        m5values[filter] = opsimQuery(cursor, query)
        m5values[filter] = numpy.array(m5values[filter])
        m5values[filter] = numpy.sort(m5values[filter])
        if len(m5values[filter]) == 0:
            per25[filter] = 0
            median[filter] = 0
            per75[filter] = 0
            continue;
        max = m5values[filter].max()
        min = m5values[filter].min()
        median[filter] = numpy.median(m5values[filter])
        mean = m5values[filter].mean()
        stdev = numpy.std(m5values[filter])
        per25[filter] = m5values[filter][int(len(m5values[filter])*.25)]
        per75[filter] = m5values[filter][int(len(m5values[filter])*.75)]
        print "In filter %s" %(filter)
        print "Maximum 5sigma is %f" %(max)
        print "Minimum 5sigma is %f" %(min)
        print "Median 5sigma is %f" %(median[filter])
        print "5sigma at 25 percentile %f" %(per25[filter])
        print "5sigma at 75 percentile %f" %(per75[filter])
        print "Mean 5sigma is %f" %(mean)
        print "Standard deviation of 5sigma is %f" %(stdev)
        print "Total number of 5sigma measurements: %d" %(len(m5values[filter]))
    # make the plot
    #pylab.figure()
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    usefilter = 'u'
    leg = "%s : %.2f / %.2f / %.2f" %(usefilter, per25[usefilter], median[usefilter], per75[usefilter])
    #colors = ('m', 'b', 'g', 'y', 'r', 'k', 'c', 'm')
    colors = ('#9966CC', '#3366CC', '#339933', '#CCCC33', '#FF6600', '#CC3333', 'c', '#666666')
    if len(m5values['u']) != 0:
        keynum, keybins, keypatches = pylab.hist(m5values[usefilter], bins=b, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[0], linewidth=2)
        maxy = keynum.max()
    else :
        maxy = 0
    i = 1
    for filter in filters:
        if len(m5values[filter]) == 0:
            continue
        if filter == usefilter:
            continue
        else:
            leg = "%s : %.2f / %.2f / %.2f" %(filter,  per25[filter], median[filter], per75[filter])
            numtemp, bintemp, patchestemp = pylab.hist(m5values[filter], bins=b, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[i], linewidth=2)
            temp = numtemp.max()
            if temp>maxy:
                maxy = temp
            i = i+1
    #pylab.legend(loc=0)
    pylab.legend(loc=(1.05,0.45))
    #pylab.xlim(m5limits)
    pylab.ylim(0, maxy*1.1)
    pylab.xlabel("Single Visit Depth", fontsize=18)
    pylab.ylabel("Number of Visits", fontsize=18)
    #figlabel = "5sigma Single Visit Distribution in Filters"
    #pylab.figtext(0.17, 0.92, figlabel)
    if savefig:
        fname = figname + '.png'
        pylab.savefig(fname, format='png')
    return

def analyze_visits(opsimdb, cursor, filters, unipropids, savefig=False, figname='visits'):
    """ Test Visits distribution """
    visitvalues = {}
    median = {}
    per25 = {}
    per75 = {}
    bmax = {}
    bmin = {}

    for filter in filters:
        query = "select count(*) as t from %s where filter='%s' and " % (opsimdb, filter)
        for i in range(0, len(unipropids)):
            if (i == len(unipropids) - 1):
                query = query + "propID=%d" % unipropids[i]
            else:
                query = query + "propID=%d or " % unipropids[i]
        query = query + " group by fieldID order by t"
        #query = "select count(*) as t from %s where filter='%s' and propid=%d group by fieldID order by t" %(opsimdb, filter, unipropids)
        visitvalues[filter] = opsimQuery(cursor, query)
        visitvalues[filter] = numpy.array(visitvalues[filter])
        visitvalues[filter] = numpy.sort(visitvalues[filter])
        if len(visitvalues[filter]) == 0:
            per25[filter] = 0
            median[filter] = 0
            per75[filter] = 0
            bmax[filter] = 0
            bmin[filter] = 0
            continue;
        bmax[filter] = visitvalues[filter].max()
        bmin[filter] = visitvalues[filter].min()
        median[filter] = numpy.median(visitvalues[filter])
        mean = visitvalues[filter].mean()
        stdev = numpy.std(visitvalues[filter])
        per25[filter] = visitvalues[filter][int(len(visitvalues[filter])*.25)]
        per75[filter] = visitvalues[filter][int(len(visitvalues[filter])*.75)]
        print "In filter %s" %(filter)
        print "Maximum Visits is %f" %(bmax[filter])
        print "Minimum Visits is %f" %(bmin[filter])
        print "Median Visits is %f" %(median[filter])
        print "Visits at 25 percentile %f" %(per25[filter])
        print "Visits at 75 percentile %f" %(per75[filter])
        print "Mean Visits is %f" %(mean)
        print "Standard deviation of Visits is %f" %(stdev)
        print "Total number of Visits measurements: %d" %(len(visitvalues[filter]))
    # make the plot
    # find limits for histogram bins, compute binsize, and bin range
    xlo=10000
    xhi=-1
    for filter in filters:
       if  xlo>=bmin[filter]:
           xlo = bmin[filter]
       if xhi<=bmax[filter]:
           xhi = bmax[filter]
    xbins = numpy.arange(0,xhi+5,5)
    print "Low= %f; High=%f" %(xlo, xhi)
    print xbins
    #set up figure
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    usefilter = 'u'
    leg = "%s : %.0f / %.0f / %.0f" %(usefilter, per25[usefilter], median[usefilter], per75[usefilter])
    #colors = ('m', 'b', 'g', 'y', 'r', 'k', 'c', 'm')
    colors = ('#9966CC', '#3366CC', '#339933', '#CCCC33', '#FF6600', '#CC3333', 'c', '#666666')
    if len(visitvalues['u']) != 0:
        keynum, keybins, keypatches = pylab.hist(visitvalues[usefilter], bins=xbins, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[0], linewidth=2)
        maxy = keynum.max()
    else :
        maxy = 0
    i = 1
    for filter in filters:
        if len(visitvalues[filter]) == 0:
            continue
        if filter == usefilter:
            continue
        else:
            leg = "%s : %.0f / %.0f / %.0f" %(filter,  per25[filter], median[filter], per75[filter])
            numtemp, bintemp, patchestemp = pylab.hist(visitvalues[filter], bins=xbins, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[i], linewidth=2)
            temp = numtemp.max()
            if temp>maxy:
                maxy = temp
            i = i+1
    pylab.legend(loc=(1.05,0.45))
    pylab.ylim(0, maxy*1.1)
    pylab.xlabel("Number of Visits", fontsize=18)
    pylab.ylabel("Number of Fields", fontsize=18)
    if savefig:
        fname = figname + '.png'
        pylab.savefig(fname, format='png')
    
    # All visits
    filter = 'a'
    query = "select count(*) as t from %s where " % (opsimdb)
    for i in range(0, len(unipropids)):
        if (i == len(unipropids) - 1):
            query = query + "propID=%d" % unipropids[i]
        else:
            query = query + "propID=%d or " % unipropids[i]
    query = query + " group by fieldID order by t"
    #query = "select count(*) as t from %s where propid=%d group by fieldID order by t" %(opsimdb, unipropids)
    visitvalues[filter] = opsimQuery(cursor, query)
    visitvalues[filter] = numpy.array(visitvalues[filter])
    visitvalues[filter] = numpy.sort(visitvalues[filter])
    bmax[filter] = visitvalues[filter].max()
    bmin[filter] = visitvalues[filter].min()
    median[filter] = numpy.median(visitvalues[filter])
    mean = visitvalues[filter].mean()
    stdev = numpy.std(visitvalues[filter])
    per25[filter] = visitvalues[filter][int(len(visitvalues[filter])*.25)]
    per75[filter] = visitvalues[filter][int(len(visitvalues[filter])*.75)]
    print "In filter %s" %(filter)
    print "Maximum Visits is %f" %(bmax[filter])
    print "Minimum Visits is %f" %(bmin[filter])
    print "Median Visits is %f" %(median[filter])
    print "Visits at 25 percentile %f" %(per25[filter])
    print "Visits at 75 percentile %f" %(per75[filter])
    print "Mean Visits is %f" %(mean)
    print "Standard deviation of Visits is %f" %(stdev)
    print "Total number of Visits measurements: %d" %(len(visitvalues[filter]))
    # make the plot
    # find limits for histogram bins, compute binsize, and bin range
    #xlo = bmin[filter]
    xlo = 0
    xhi = bmax[filter]
    xbins = numpy.arange(xlo,xhi+5,5)
    print "Low= %f; High=%f" %(xlo, xhi)
    print xbins
    # set up figure
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    leg = "%s : %.0f / %.0f / %.0f" %(filter,  per25[filter], median[filter], per75[filter])
    numtemp, bintemp, patchestemp = pylab.hist(visitvalues[filter], bins=xbins, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[7], linewidth=2)
    maxy = numtemp.max()
    pylab.legend(loc=(1.05,0.45))
    pylab.ylim(0, maxy*1.1)
    pylab.xlabel("Number of Visits", fontsize=18)
    pylab.ylabel("Number of Fields", fontsize=18)
    if savefig:
        fname = figname + '_all.png'
        pylab.savefig(fname, format='png')
    return

def analyze_cvisits(opsimdb, cursor, filters, unipropids, savefig=False, figname='visits'):
    """ Test Visits distribution """
    visitvalues = {}
    median = {}
    per25 = {}
    per75 = {}
    bmax = {}
    bmin = {}

    for filter in filters:
        query = "select count(*) as t from %s where filter='%s' and (" % (opsimdb, filter)
        for i in range(0, len(unipropids)):
            if (i == len(unipropids) - 1):
                query = query + "propID=%d)" % unipropids[i]
            else:
                query = query + "propID=%d or " % unipropids[i]
        query = query + " group by fieldID order by t"
        #query = "select count(*) as t from %s where filter='%s' and propid=%d group by fieldID order by t" %(opsimdb, filter, unipropids)
        visitvalues[filter] = opsimQuery(cursor, query)
        visitvalues[filter] = numpy.array(visitvalues[filter])
        visitvalues[filter] = numpy.sort(visitvalues[filter])
        if len(visitvalues[filter]) == 0:
            per25[filter] = 0
            median[filter] = 0
            per75[filter] = 0
            bmax[filter] = 0
            bmin[filter] = 0
            continue;
        bmax[filter] = visitvalues[filter].max()
        bmin[filter] = visitvalues[filter].min()
        median[filter] = numpy.median(visitvalues[filter])
        mean = visitvalues[filter].mean()
        stdev = numpy.std(visitvalues[filter])
        per25[filter] = visitvalues[filter][int(len(visitvalues[filter])*.25)]
        per75[filter] = visitvalues[filter][int(len(visitvalues[filter])*.75)]
        print "In filter %s" %(filter)
        print "Maximum Visits is %f" %(bmax[filter])
        print "Minimum Visits is %f" %(bmin[filter])
        print "Median Visits is %f" %(median[filter])
        print "Visits at 25 percentile %f" %(per25[filter])
        print "Visits at 75 percentile %f" %(per75[filter])
        print "Mean Visits is %f" %(mean)
        print "Standard deviation of Visits is %f" %(stdev)
        print "Total number of Visits measurements: %d" %(len(visitvalues[filter]))
    # make the plot
    # find limits for histogram bins, compute binsize, and bin range
    xlo=10000
    xhi=-1
    for filter in filters:
       if  xlo>=bmin[filter]:
           xlo = bmin[filter]
       if xhi<=bmax[filter]:
           xhi = bmax[filter]
    xbins = numpy.arange(0,xhi+5,5)
    print "Low= %f; High=%f" %(xlo, xhi)
    print xbins

    #pylab.figure()
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    usefilter = 'u'
    leg = "%s : %.0f / %.0f / %.0f" %(usefilter, per25[usefilter], median[usefilter], per75[usefilter])
    #colors = ('m', 'b', 'g', 'y', 'r', 'k', 'c', 'm')
    colors = ('#9966CC', '#3366CC', '#339933', '#CCCC33', '#FF6600', '#CC3333', 'c', '#666666')
    if len(visitvalues['u']) != 0:
        keynum, keybins, keypatches = pylab.hist(visitvalues[usefilter], bins=xbins, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[0], linewidth=2, cumulative=-1)
        maxy = keynum.max()
    else :
        maxy = 0
    i = 1
    for filter in filters:
        if len(visitvalues[filter]) == 0:
            continue
        if filter == usefilter:
            continue
        else:
            leg = "%s : %.0f / %.0f / %.0f" %(filter,  per25[filter], median[filter], per75[filter])
            numtemp, bintemp, patchestemp = pylab.hist(visitvalues[filter], bins=xbins, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[i], linewidth=2, cumulative=-1)
            temp = numtemp.max()
            if temp>maxy:
                maxy = temp
            i = i+1
    pylab.legend(loc=(1.05,0.45))
    pylab.ylim(0, maxy*1.1)
    pylab.xlabel("Number of Visits", fontsize=18)
    pylab.ylabel("Number of Fields", fontsize=18)
    if savefig:
        fname = figname + '.png'
        pylab.savefig(fname, format='png')
    
    # All visits
    filter = 'a'
    query = "select count(*) as t from %s where " % (opsimdb)
    for i in range(0, len(unipropids)):
        if (i == len(unipropids) - 1):
            query = query + "propID=%d" % unipropids[i]
        else:
            query = query + "propID=%d or " % unipropids[i]
    query = query + " group by fieldID order by t"
    #query = "select count(*) as t from %s where propid=%d group by fieldID order by t" %(opsimdb, unipropids)
    visitvalues[filter] = opsimQuery(cursor, query)
    visitvalues[filter] = numpy.array(visitvalues[filter])
    visitvalues[filter] = numpy.sort(visitvalues[filter])
    bmax[filter] = visitvalues[filter].max()
    bmin[filter] = visitvalues[filter].min()
    median[filter] = numpy.median(visitvalues[filter])
    mean = visitvalues[filter].mean()
    stdev = numpy.std(visitvalues[filter])
    per25[filter] = visitvalues[filter][int(len(visitvalues[filter])*.25)]
    per75[filter] = visitvalues[filter][int(len(visitvalues[filter])*.75)]
    print "In filter %s" %(filter)
    print "Maximum Visits is %f" %(bmax[filter])
    print "Minimum Visits is %f" %(bmin[filter])
    print "Median Visits is %f" %(median[filter])
    print "Visits at 25 percentile %f" %(per25[filter])
    print "Visits at 75 percentile %f" %(per75[filter])
    print "Mean Visits is %f" %(mean)
    print "Standard deviation of Visits is %f" %(stdev)
    print "Total number of Visits measurements: %d" %(len(visitvalues[filter]))
    # make the plot
    # find limits for histogram bins, compute binsize, and bin range
    xlo = bmin[filter]
    xhi = bmax[filter]
    xbins = numpy.arange(0,xhi+5,5)
    print "Low= %f; High=%f" %(xlo, xhi)
    print xbins
    # continue
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    leg = "%s : %.2f / %.2f / %.2f" %(filter,  per25[filter], median[filter], per75[filter])
    numtemp, bintemp, patchestemp = pylab.hist(visitvalues[filter], bins=xbins, histtype='step', label=leg, facecolor='none', alpha=1, edgecolor=colors[7], linewidth=2, cumulative=-1)
    maxy = numtemp.max()
    pylab.legend(loc=(1.05,0.45))
    pylab.ylim(0, maxy*1.1)
    pylab.xlabel("Number of Visits", fontsize=18)
    pylab.ylabel("Number of Fields", fontsize=18)
    if savefig:
        fname = figname + '_all.png'
        pylab.savefig(fname, format='png')
    return

def analyze_coadded(unique_id, savefig=False, figname='coadded'):
    """ Test coadded distribution hewelhog_56_coadded_raw.dat """
    coaddedvalues = {}
    per25 = {}
    per75= {}
    median = {}
    bmin = {}
    bmax= {}

    for filter in filters:
        coaddedvalues[filter] = readCoadded(unique_id, filter)
        coaddedvalues[filter] = numpy.array(coaddedvalues[filter])
        coaddedvalues[filter] = numpy.sort(coaddedvalues[filter])
        if len(coaddedvalues[filter]) == 0:
            per25[filter] = 0
            median[filter] = 0
            per75[filter] = 0
            bmax[filter] = 0
            bmin[filter] = 0
            continue;
        bmax[filter] = coaddedvalues[filter].max()
        bmin[filter] = coaddedvalues[filter].min()
        median[filter] = numpy.median(coaddedvalues[filter])
        mean = coaddedvalues[filter].mean()
        stdev = numpy.std(coaddedvalues[filter])
        per25[filter] = coaddedvalues[filter][int(len(coaddedvalues[filter])*.25)]
        per75[filter] = coaddedvalues[filter][int(len(coaddedvalues[filter])*.75)]
        print "In filter %s" %(filter)
        print "Maximum seeing is %f" %(bmax[filter])
        print "Minimum seeing is %f" %(bmin[filter])
        print "Median seeing  is %f" %(median[filter])
        print "Seeing at 25 percentile %f" %(per25[filter])
        print "Seeing at 75 percentile %f" %(per75[filter])
        print "Mean seeing is %f" %(mean)
        print "Standard deviation of seeing is %f" %(stdev)
        print "Total number of seeing measurements: %d" %(len(coaddedvalues[filter]))
    #pylab.figure()
    # find limits for histogram bins, compute binsize, and bin range
    xlo=10000
    xhi=-1
    for filter in filters:
       if  xlo>=bmin[filter]:
           xlo = bmin[filter]
       if xhi<=bmax[filter]:
           xhi = bmax[filter]
    xlo = numpy.floor(xlo)*100/100
    xhi = numpy.ceil(xhi)*100/100
    xbins = numpy.arange(xlo,xhi+0.1,0.1)
    print "Low= %f; High=%f" %(xlo, xhi)
    print xbins
    # make figure
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    usefilter = 'u'
    leg = "%s : %.2f / %.2f / %.2f" %(usefilter, per25[usefilter], median[usefilter], per75[usefilter])
    #colors = ('m', 'b', 'g', 'y', 'r', 'k', 'c', 'm')
    colors = ('#9966CC', '#3366CC', '#339933', '#CCCC33', '#FF6600', '#CC3333', 'c', '#666666')
    if len(coaddedvalues['u']) != 0:
        keynum, keybins, keypatches = pylab.hist(coaddedvalues[usefilter], bins=xbins, label=leg, facecolor='none', edgecolor=colors[0], linewidth=2, histtype='step')
        maxy = keynum.max()
    else:
        maxy = 0
    i=1
    for filter in filters:
        if len(coaddedvalues[filter]) == 0:
            continue;
        if filter == usefilter:
            continue
        else:
            leg = "%s : %.2f / %.2f / %.2f" %(filter, per25[filter], median[filter], per75[filter])
            numtemp, bintemp, patchestemp = pylab.hist(coaddedvalues[filter], bins=xbins, label=leg, facecolor='none', edgecolor=colors[i], linewidth=2, histtype='step')
            temp = numtemp.max()
            if temp>maxy:
                maxy = temp
            i=i+1
    pylab.legend(loc=(1.05,0.45))
    pylab.ylim(0, maxy*1.1)
    pylab.xlim(23, 28)
    pylab.xlabel("Coadded Depth", fontsize=18)
    pylab.ylabel("Number of Fields", fontsize=18)
    if savefig:
        fname = figname + '.png'
        pylab.savefig(fname, format='png')
    return

def analyze_coaddedWFD(unique_id, savefig=False, figname='coadded'):
    """ Test coadded distribution hewelhog_56_coadded_wfd.dat """
    coaddedvalues = {}
    per25 = {}
    per75= {}
    median = {}
    bmin = {}
    bmax= {}

    for filter in filters:
        coaddedvalues[filter] = readCoaddedWFD(unique_id, filter)
        coaddedvalues[filter] = numpy.array(coaddedvalues[filter])
        coaddedvalues[filter] = numpy.sort(coaddedvalues[filter])
        if len(coaddedvalues[filter]) == 0:
            per25[filter] = 0
            median[filter] = 0
            per75[filter] = 0
            bmax[filter] = 0
            bmin[filter] = 0
            continue;
        bmax[filter] = coaddedvalues[filter].max()
        bmin[filter] = coaddedvalues[filter].min()
        median[filter] = numpy.median(coaddedvalues[filter])
        mean = coaddedvalues[filter].mean()
        stdev = numpy.std(coaddedvalues[filter])
        per25[filter] = coaddedvalues[filter][int(len(coaddedvalues[filter])*.25)]
        per75[filter] = coaddedvalues[filter][int(len(coaddedvalues[filter])*.75)]
        print "In filter %s" %(filter)
        print "Maximum seeing is %f" %(bmax[filter])
        print "Minimum seeing is %f" %(bmin[filter])
        print "Median seeing  is %f" %(median[filter])
        print "Seeing at 25 percentile %f" %(per25[filter])
        print "Seeing at 75 percentile %f" %(per75[filter])
        print "Mean seeing is %f" %(mean)
        print "Standard deviation of seeing is %f" %(stdev)
        print "Total number of seeing measurements: %d" %(len(coaddedvalues[filter]))
    #pylab.figure()
    # find limits for histogram bins, compute binsize, and bin range
    xlo=10000
    xhi=-1
    for filter in filters:
       if  xlo>=bmin[filter]:
           xlo = bmin[filter]
       if xhi<=bmax[filter]:
           xhi = bmax[filter]
    xlo = numpy.floor(xlo)*100/100
    xhi = numpy.ceil(xhi)*100/100
    xbins = numpy.arange(xlo,xhi+0.1,0.1)
    print "Low= %f; High=%f" %(xlo, xhi)
    print xbins
    # make figure
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    usefilter = 'u'
    leg = "%s : %.2f / %.2f / %.2f" %(usefilter, per25[usefilter], median[usefilter], per75[usefilter])
    #colors = ('m', 'b', 'g', 'y', 'r', 'k', 'c', 'm')
    colors = ('#9966CC', '#3366CC', '#339933', '#CCCC33', '#FF6600', '#CC3333', 'c', '#666666')
    if len(coaddedvalues['u']) != 0:
        keynum, keybins, keypatches = pylab.hist(coaddedvalues[usefilter], bins=xbins, label=leg, facecolor='none', edgecolor=colors[0], linewidth=2, histtype='step')
        maxy = keynum.max()
    else:
        maxy = 0
    i=1
    for filter in filters:
        if len(coaddedvalues[filter]) == 0:
            continue;
        if filter == usefilter:
            continue
        else:
            leg = "%s : %.2f / %.2f / %.2f" %(filter, per25[filter], median[filter], per75[filter])
            numtemp, bintemp, patchestemp = pylab.hist(coaddedvalues[filter], bins=xbins, label=leg, facecolor='none', edgecolor=colors[i], linewidth=2, histtype='step')
            temp = numtemp.max()
            if temp>maxy:
                maxy = temp
            i=i+1
    pylab.legend(loc=(1.05,0.45))
    pylab.ylim(0, maxy*1.1)
    pylab.xlim(23, 28)
    pylab.xlabel("Coadded Depth", fontsize=18)
    pylab.ylabel("Number of Fields", fontsize=18)
    if savefig:
        fname = figname + '.png'
        pylab.savefig(fname, format='png')
    return

def get_hostname_fromDB(sessionID):
    query = "select sessionHost from Session where sessionID=%d" % sessionID
    hostname = opsimQuery(cursor, query)
    return hostname[0][0]

def get_universal_propID(sessionID):
    query = "select propID from Proposal where Session_sessionID=%d and propConf='../conf/survey/UniversalProp.conf'" % sessionID
    uni_propID = opsimQuery(cursor, query)
    return int(uni_propID[0][0])

def get_universal_propIDs(sessionID):
    query = "select propID, propConf from Proposal where Session_sessionID=%d" % sessionID
    props_list = opsimQuery(cursor, query)
    props = []
    for i in range(0, len(props_list)):
    	#print "%d %s" % (props_list[i][0], props_list[i][1])
	index_uni = props_list[i][1].lower().find('universal')
	index_unin = props_list[i][1].lower().find('universalnorth')
	if index_uni > 0 and index_unin < 0:
            props.append(props_list[i][0])
    return props

def create_no_data_plot(figname) :
    pylab.figure(figsize=(10,6))
    #pylab.axes([0.075,0.1,0.65,0.82])
    pylab.axes([0.100,0.1,0.65,0.82])
    pylab.ylim(0, 10)
    pylab.xlim(0, 10)
    pylab.xlabel("No Data", fontsize=18)
    pylab.ylabel("No Data", fontsize=18)
    figname = figname + '.png'
    pylab.savefig(figname, format='png')
    return

if __name__ == "__main__":
    import sys

    params = {'legend.fontsize': 10}
    pylab.rcParams.update(params)

    # save figures?
    savefigures = True
    # quick tests for opsim, recorded here if need to be re-created
    do_analyze_seeing = True
    do_analyze_airmass = True
    do_analyze_skyb = True
    do_analyze_m5 = True
    do_analyze_visits = True
    do_analyze_cvisits = True
    do_analyze_coadded = True

    if len(sys.argv)>2:
	databasename = sys.argv[1]
        sessionID = sys.argv[2] 
    else:
        print "Usage ./histograms.py <databasename> <sessionID>"
        exit()

    # choose opsim and connect to db
    cursor = opsimConnect(dbname=databasename)
    hostname = get_hostname_fromDB(int(sessionID))
    unique_id = "%s_%d" % (hostname, int(sessionID))
    opsimdb = "output_%s" % unique_id

    universal_propids = get_universal_propIDs(int(sessionID))
    for i in range(0, len(universal_propids)):
	print "PropID %d" % universal_propids[i]
    #universal_propid = get_universal_propID(int(sessionID)) 
    # print "Testing %s, universal cadence propid = %d, will show all plots at the end" %(opsimdb, universal_propid)
    # COMMENT : The above 2 commented lines donot hold true anymore

    filters = ('u','g','r','i','z','y')

    # make seeing and airmass histograms for universal cadence, individual filters
    if do_analyze_seeing:
        figname = "%s_seeing_allfilters" % unique_id
	if len(universal_propids)>0 :
	    analyze_seeing(opsimdb, cursor, filters, unipropids=universal_propids, savefig=savefigures, figname=figname)
	else:
	    create_no_data_plot(figname)
    if do_analyze_airmass:
        figname = "%s_airmass_allfilters" % unique_id
    if len(universal_propids)>0 :
        analyze_airmass(opsimdb, cursor, filters, unipropids=universal_propids, savefig=savefigures, figname=figname)
    else:
	    create_no_data_plot(figname)
    if do_analyze_m5:
        figname = "%s_m5_allfilters" % unique_id
    if len(universal_propids)>0 :
        analyze_m5(opsimdb, cursor, filters, unipropids=universal_propids, savefig=savefigures, figname=figname)
    else:
	    create_no_data_plot(figname)
    if do_analyze_skyb:
        figname = "%s_skyb_allfilters" % unique_id
	if len(universal_propids)>0 :
	    analyze_skyb(opsimdb, cursor, filters, unipropids=universal_propids, savefig=savefigures, figname=figname)
	else:
	    create_no_data_plot(figname)
    if do_analyze_visits:
        figname = "%s_visits_allfilters" % unique_id
    if len(universal_propids)>0 :
        analyze_visits(opsimdb, cursor, filters, unipropids=universal_propids, savefig=savefigures, figname=figname)
    else:
	    create_no_data_plot(figname)
	    figname = figname + '_all'
	    create_no_data_plot(figname)
    if do_analyze_cvisits:
        figname = "%s_cvisits_allfilters" % unique_id
    if len(universal_propids)>0 :
        analyze_cvisits(opsimdb, cursor, filters, unipropids=universal_propids, savefig=savefigures, figname=figname)
    else:
	    create_no_data_plot(figname)
	    figname = figname + '_all'
	    create_no_data_plot(figname)
    if do_analyze_coadded:
        figname = "%s_coadded_allfilters" % unique_id
        analyze_coadded(unique_id, savefig=savefigures, figname=figname)
        figname = "%s_coadded_allfilters_wfd" % unique_id
        analyze_coaddedWFD(unique_id, savefig=savefigures, figname=figname)
    # show the plots
    cursor.close()
    # print "about to show the plots"    
    # pylab.show()
    # exit()
