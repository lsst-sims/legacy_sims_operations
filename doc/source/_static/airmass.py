####################################################################
#  Srinivasan Chandrasekharan, Lynne Jones
#  Quick plots from opsim airmass
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

def createLimitSQL(opsimdb, sessionID, topic):
    query = "select %s from %s where Session_sessionID=%d" % (topic, opsimdb, sessionID)
    return query

def createTopicSQL(opsimdb, filter, sessionID, topic):
    query = "select %s from %s where filter='%s' and Session_sessionID=%d" % (topic, opsimdb, filter, sessionID)
    return query

def analyze_airmass(opsimdb, cursor, filters, sessionID, savefig=False, figname='airmass'):
    """ Test airmass distribution """
    airmassvalues = {}
    median = {}
    per25 = {}
    per75 = {}

    # find limits for histogram bins, compute binsize, and bin range
    query = createLimitSQL(opsimdb, sessionID, 'airmass')
    airmasslim =  opsimQuery(cursor, query)
    airmasslim =  numpy.array(airmasslim)
    lo = numpy.floor(numpy.min(airmasslim)*1000)/1000
    hi = numpy.ceil(numpy.max(airmasslim)*1000)/1000
    hi = 1.8
    b = numpy.arange(lo,hi,0.01)

    #airmasslimits = (1, 2.2) # a bit random, change if necessary
    for filter in filters:
        query = createTopicSQL(opsimdb, filter, sessionID, 'airmass')
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

def get_hostname_fromDB(sessionID):
    query = "select sessionHost from Session where sessionID=%d" % sessionID
    hostname = opsimQuery(cursor, query)
    return hostname[0][0]

if __name__ == "__main__":
    import sys

    params = {'legend.fontsize': 10}
    pylab.rcParams.update(params)

    if len(sys.argv)>2:
	databasename = sys.argv[1]
        sessionID = sys.argv[2] 
    else:
        print "Usage python airmass.py <databasename> <sessionID>"
        exit()

    # choose opsim and connect to db
    cursor = opsimConnect(dbname=databasename)
    hostname = get_hostname_fromDB(int(sessionID))
    unique_id = "%s_%d" % (hostname, int(sessionID))
    opsimdb = "ObsHistory"

    filters = ('u','g','r','i','z','y')

    figname = "%s_airmass_allfilters" % unique_id
    analyze_airmass(opsimdb, cursor, filters, sessionID=int(sessionID), savefig=True, figname=figname)
    cursor.close()

