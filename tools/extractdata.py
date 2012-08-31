#!/data1/simulator/sw/python-2.3.4/bin/python

#  Phil Pinto 18 Oct 2004
#   based on lsst:plot.cgi of Francesco Pierfederici

import math
from Numeric import *
from pyx import *
from pyx.graph import axis
import TableIO 
from matplotlib.matlab import *
import sys, re
import MySQLdb
import socket
from optparse import OptionParser

# General constants
FOV = 3.5

# Database specific stuff
from LSSTDBInit import *

OBSHIST = 'ObsHistory'
SEQHIST = 'SeqHistory'
FIELD = 'Field'

# Color redefinitions to get brighter colors
BLACK = "#000000"
BLUE = "#0055ff"
CYAN = "#00ffff"
GREEN = "#00ff00"
YELLOW = "#ffff00"
RED = "#ff0000"
MAGENTA = "#ff00ff"
WHITE = "#ffffff"

# only two fonts used
bigfont = {'fontname'   : 'Courier',
            'color'      : 'r',
            'fontweight' : 'bold',
            'fontsize'   : 11}

smallfont = {'fontname'   : 'Courier',
            'color'      : 'r',
            'fontweight' : 'bold',
            'fontsize'   : 8}


def project(ra, dec):
    """
    do the Aitoff projection
    (compromise between shape and scale distortion)
    """

    a = ra*math.pi/180.0
    d = dec*math.pi/180.0
    z = sqrt((1+cos(d)*cos(a/2.0))*0.5)+0.00001
    x = 2.0*cos(d)*sin(a/2.0)/z
    y = sin(d)/z

    return x, y


def meridian(ra):
    """
    create a meridian line at given ra
    """

    phi = arrayrange(-90,90)
    lam = zeros(len(phi)) + ra

    return lam, phi


def parallel(dec):
    """
    create a longitude line at given dec
    """

    lam = arrayrange(-180,180)
    phi = zeros(len(lam)) + dec

    return lam, phi


def plotPanel(RA, Dec, nvisits, label, colvals, colnam):
    """
    Plot a panel of visit data
    """
    
    circlesize = 2
    r = RA[:]
    d = Dec[:]
    n = nvisits[:]
    r = r*15.0
    # sort arrays
    ind = argsort(n)
    r = take(r,ind)
    d = take(d,ind)
    n = take(n,ind)
    r = where(r>180.0,r-360.0,r)

    axis("off")

    if label == "nea":
        aitoff_e()
    else:
        aitoff()
        
    cols = setcolors(n, colvals, colnam)
    docir(r, d, circlesize, n, cols)

    if label == "nea":
        label = "NEA Sequences"
    else:
        label = "WL Fields: "+ label

    text(0, 1.51, label, bigfont, horizontalalignment='center')
    axis([-3,3,-1.5,1.5])

    return


def leglab(title, word, colvals, colnam):
    """
    make labels for the colormaps
    """

    axis("off")
    
    x0 = -2.7
    dx = 2.9
    xw = 0.7
    xo = 0.8
    y0 = -1.74
    dy = -0.1
    yw = 0.1
    yo = 0.02
    
    i = -1
    
    for ix in range(2):
        for iy in range(3):
            i=i+1
            ll = [x0+ix*dx, y0+iy*dy]
            ur = [x0+ix*dx+xw, y0+iy*dy+yw]
            legbox(ll, ur, colnam[i+1])
            if i<len(colvals)-1:
                string = " " + str(colvals[i]+1) + "-" + str(colvals[i+1]) + " " + word
            else:
                string = " >" + str(colvals[i]) + " " + word
            text(ll[0]+xo,ll[1]+yo, string, smallfont, horizontalalignment='left', color=colnam[i+1])

    text(0.0,-1.6,title, bigfont, horizontalalignment='center', color=WHITE)
    
    axis([-3,3,-2.1,-1.55])
    
    return
    

def legbox(ll, ur, color):
    """
    make a box of the given color between
    lower left (ll) and upper right (ur) coordinates
    """
    
    x = [ll[0],ur[0],ur[0],ll[0]]
    y = [ll[1],ll[1],ur[1],ur[1]]
    a = fill(x,y,color,linewidth=0)

    return

  
def infoWrite(sessionID, numfields, nums):
    """
    add various information to the bottom of the plot
    """
    
    axis("off")
#    text(1.0,-0.6,socket.gethostname(),bigfont,horizontalalignment='right', color=WHITE)
    
    [nnights, nlun, nobs, ncompl, nlost, nlunlost, neventlost] = logFileParse(sessionID)


    string = "%d nights" % nnights
    text(0.0,0.,string,bigfont,horizontalalignment='left', color=WHITE)
    string = "%d lunations" % nlun
    text(0.6,0.,string,bigfont,horizontalalignment='left', color=WHITE)

    string = "%d NEA sequences completed" % ncompl
    text(0.6,-0.15,string,bigfont,horizontalalignment='left', color=WHITE)

    string = "%d fields observed" % numfields
    text(0.0,-0.15,string,bigfont,horizontalalignment='left', color=WHITE)

    string = "%d r observations" % nums[0]
    text(0.0,-0.3,string,smallfont,horizontalalignment='left', color=WHITE)
    string = "%d g observations" % nums[1]
    text(0.0,-0.45,string,smallfont,horizontalalignment='left', color=WHITE)
    string = "%d i observations" % nums[2]
    text(0.0,-0.6,string,smallfont,horizontalalignment='left', color=WHITE)
    string = "%d z observations" % nums[3]
    text(0.3,-0.3,string,smallfont,horizontalalignment='left', color=WHITE)
    string = "%d y observations" % nums[4]
    text(0.3,-0.45,string,smallfont,horizontalalignment='left', color=WHITE)

    string = "%d sequences lost to lunation" % nlunlost
    text(0.6,-0.3,string,smallfont,horizontalalignment='left', color=WHITE)
    string = "%d sequences lost to event" % neventlost
    text(0.6,-0.45,string,smallfont,horizontalalignment='left', color=WHITE)

    axis([0,1,0,1])

    return


def extractLsst(sessionID, extractFile):
    """
    extract all ObsHistory data and write to specified file
    """
    # write out all data to named file
    resObs = extractDataset(sessionID)
    try:
            f=open(extractFile,'w')
    except:
            sys.stderr.write('Unable to open EXTRACT file: %s .' % (extractFile) )
            return
    f.write ("#ra,dec,fieldId,obshistID,sessionId,exptime,filter,maxseeing,seeing,expdata,propid,fieldId,seqnNum,slewtime,airmass,skybright,moonphase\n")
    for s in resObs:
            f.write( "%f %f %d %d %d %f %s %f %f %d %d %d %f %f %f %f\n" % (s[0],s[1],s[2],s[3],s[4],s[5],s[6],s[7],s[8],s[9],s[10],s[12],s[13],s[14],s[15],s[16]))


def lsst(SessionID):
    """
    main workhorse of the plotting package
    """

    [ra, dec, rnum, gnum, ynum, inum, znum, neanum] = createDataset(SessionID)

    figure(num=1, figsize=(9,9), facecolor='k', edgecolor='k')

    # define colors for regular plots
    colvals = array([0, 20, 40, 60, 80, 100])
    colnam = [BLACK,BLUE,CYAN,GREEN,YELLOW,RED,MAGENTA]

    subplot(4,2,1)
    plotPanel(ra,dec,rnum,"r",colvals, colnam)
    subplot(4,2,2)
    plotPanel(ra,dec,gnum,"g",colvals, colnam)
    subplot(4,2,3)
    plotPanel(ra,dec,inum,"i",colvals, colnam)
    subplot(4,2,4)
    plotPanel(ra,dec,ynum,"y",colvals, colnam)
    subplot(4,2,5)
    plotPanel(ra,dec,znum,"z",colvals, colnam)

    subplot(4,2,7)
    leglab("WL Fields", "epochs", colvals, colnam)

    # redefine colors for nea plots
    colvals = array([0,6,12,18,24,30])
    colnam = [BLACK,BLUE,CYAN,GREEN,YELLOW,RED,MAGENTA]
    subplot(4,2,6)
    plotPanel(ra,dec,neanum,"nea",colvals, colnam)

    subplot(4,2,8)
    leglab("NEA Sequences", "sequences", colvals, colnam)

    subplot(4,1,4)
    nums = [sum(rnum),sum(gnum),sum(inum),sum(znum),sum(ynum)]

    numfields = len(ra)
    infoWrite(SessionID, numfields, nums)

    return 


def aitoff():
    """
    make aitoff projection grid
    """
    
    xlim(-3,3)
    ylim(1,1)

    d = arrayrange(-90.0,91.0,30.0)
    for dd in d:
        [lam, phi] = parallel(dd)
        [x, y] = project(lam, phi)
        plot(x,y,color='w')
        
    r = arrayrange(-180.0,181.0,30.0)
    for rr in r:
        [lam, phi] = meridian(rr)
        [x, y] = project(lam, phi)
        plot(x,y,color='w')

    return


def aitoff_e():
    """
    make aitoff grid with ecliptic
    """

    aitoff()
    
    r = arrayrange(-180.0,181.0,30.0)
    d = arctan(sin(r*math.pi/180.0)*tan(23.43333*math.pi/180.0))*180.0/math.pi
    [x, y] = project(r, d)
    plot(x, y, linewidth=3, color='w')

    return


def setcolors(y, colval, colnam):
    """
    return an array with the entries of colnam such that
    values less than colval[0] are colnum[0]
    colval[i-1] < values <= colval[i] are colnam[i]
    values greater than colval[-1] are colnam[len(colval)+1]
    """

    z = zeros(len(y),Int)
    for i in range(len(colval)):
        z = add(z,(i)*logical_and(less_equal(y,colval[i]), greater(y,colval[i-1])))
    z = add(z,len(colval)*greater(y,colval[-1]))
    q = []
    for i in z:
        q.append(colnam[i])

    return q


def docir(ra, dec, size, cnt, color):
    """
    plot a shaded circle (on the sky) at
    the given ra and dec
    """
    
    phi = arrayrange(0.0,361.0,30.0)
    for i in range(len(ra)):
        db = dec[i] + size*cos(phi*math.pi/180.0)
        rb = ra[i] - size*sin(phi*math.pi/180.0)/cos(db*math.pi/180.0)
        [x, y] = project(rb, db)
        fill(x, y, color[i], linewidth=0)

    return


def openConnection ():
    """
    Open a connection to DBDB running on DBHOST:DBPORT as user DBUSER
    and return the connection.
    
    Raise exception in case of error.
    """
    if (DBPORT ):
        connection = MySQLdb.connect (user=DBUSER, 
                                      passwd=DBPASSWD, 
                                      db=DBDB, 
                                      host=DBHOST, 
                                      port=DBPORT)
    else:
        connection = MySQLdb.connect (user=DBUSER, 
                                      passwd=DBPASSWD, 
                                      db=DBDB, 
                                      host=DBHOST)
    return (connection)


def summary (resObs, resSeq):
    # Cumulative number of visits per fieldID
    r = {}
    g = {}
    y = {}
    i = {}
    z = {}
    nea = {}
    
    # Utility dictionary {fieldID: (ra, dec)}
    targets = {}
    
    # Start with the NEA sequences
    # Each row has the format
    # (ra, dec, fieldID)
    # We want RA in decimal hours...
    for row in resSeq:
        ra = float (row[0]) / 15.
        dec = float (row[1])
        fieldID = int (row[2])
        
        if (not targets.has_key (fieldID)):
            targets[fieldID] = (ra, dec)
        
        if (not nea.has_key (fieldID)):
            nea[fieldID] = 1
        else:
            nea[fieldID] += 1
    
    
    # Now the observations!
    # Each row has the format
    # (ra, dec, fieldID, filter, expDate)
    # and it is grouped by observation date.
    for row in resObs:
        # We want RA in decimal hours...
        ra = float (row[0]) / 15.
        dec = float (row[1])
        fieldID = int (row[2])
        filter = row[3].lower ()
        date = row[4]
        
        if (not targets.has_key (fieldID)):
            targets[fieldID] = (ra, dec)
        
        if (filter == 'r'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 1
            else:
                r[fieldID] += 1
            if (not g.has_key (fieldID)):
                g[fieldID] = 0
            if (not y.has_key (fieldID)):
                y[fieldID] = 0
            if (not i.has_key (fieldID)):
                i[fieldID] = 0
            if (not z.has_key (fieldID)):
                z[fieldID] = 0
        elif (filter == 'g'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 0
            if (not g.has_key (fieldID)):
                g[fieldID] = 1
            else:
                g[fieldID] += 1
            if (not y.has_key (fieldID)):
                y[fieldID] = 0
            if (not i.has_key (fieldID)):
                i[fieldID] = 0
            if (not z.has_key (fieldID)):
                z[fieldID] = 0
        elif (filter == 'y'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 0
            if (not g.has_key (fieldID)):
                g[fieldID] = 0
            if (not y.has_key (fieldID)):
                y[fieldID] = 1
            else:
                y[fieldID] += 1
            if (not i.has_key (fieldID)):
                i[fieldID] = 0
            if (not z.has_key (fieldID)):
                z[fieldID] = 0
        elif (filter == 'i'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 0
            if (not g.has_key (fieldID)):
                g[fieldID] = 0
            if (not y.has_key (fieldID)):
                y[fieldID] = 0
            if (not i.has_key (fieldID)):
                i[fieldID] = 1
            else:
                i[fieldID] += 1
            if (not z.has_key (fieldID)):
                z[fieldID] = 0
        elif (filter == 'z'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 0
            if (not g.has_key (fieldID)):
                g[fieldID] = 0
            if (not y.has_key (fieldID)):
                y[fieldID] = 0
            if (not i.has_key (fieldID)):
                i[fieldID] = 0
            if (not z.has_key (fieldID)):
                z[fieldID] = 1
            else:
                z[fieldID] += 1

    return (targets, r, g, y, i, z, nea)


def extractDataset(sessionID, fov=FOV):
    # Get a connection to the DB
    connection = openConnection ()
    cursor = connection.cursor ()

    # Remember that the ObsHistory records the same observation up tp N times
    # where N is the number of active proposals (serendipitous obs!). In 
    # particular, some proposals accept any serendipitous observation, other
    # don't. We need to figure out the max spatial coverage.
    # Fetch all the data for this Session ID, if any
    sql = 'SELECT f.fieldRA, f.fieldDec, f.fieldID, '
    sql += 'o.* '
    sql += 'FROM %s f, %s o WHERE ' % (FIELD, OBSHIST)
    sql += 'o.sessionID = %d AND ' % (sessionID)
    sql += 'f.fieldFov = %s AND ' % (fov)
    sql += 'o.fieldID = f.fieldID '
    sql += 'GROUP BY o.expDate'
    
    # Fetch the data from the DB
    sys.stderr.write ('Fetching data from the DB...\n')
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write('Unable to execute SQL query (%s).' % (sql) )

    try:
        resObs = cursor.fetchall ()
    except:
        resObs = None

    return (resObs)
    
def createDataset(sessionID, fov=FOV):
    # Get a connection to the DB
    connection = openConnection ()
    cursor = connection.cursor ()

    # Remember that the ObsHistory records the same observation up tp N times
    # where N is the number of active proposals (serendipitous obs!). In 
    # particular, some proposals accept any serendipitous observation, other
    # don't. We need to figure out the max spatial coverage.
    # Fetch all the data for this Session ID, if any
    sql = 'SELECT f.fieldRA, f.fieldDec, f.fieldID, '
    sql += 'o.filter, o.expDate '
    sql += 'FROM %s f, %s o WHERE ' % (FIELD, OBSHIST)
    sql += 'o.sessionID = %d AND ' % (sessionID)
    sql += 'f.fieldFov = %s AND ' % (fov)
    sql += 'o.fieldID = f.fieldID '
    sql += 'GROUP BY o.expDate'
    
    # Fetch the data from the DB
    sys.stderr.write ('Fetching data from the DB...\n')
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write('Unable to execute SQL query (%s).' % (sql) )

    try:
        resObs = cursor.fetchall ()
    except:
        resObs = None
    
    if (not resObs):
        outFileName = None
        sys.stderr.write ('No data for Session %d' \
            % (sessionID))
    else:
        # Fetch all the data for this Session ID, if any
        sql = 'SELECT f.fieldRA, f.fieldDec, s.fieldID '
        sql += 'FROM %s f, %s s WHERE ' % (FIELD, SEQHIST)
        sql += 's.sessionID = %d AND ' % (sessionID)
        sql += 'f.fieldFov = %s AND ' % (fov)
        sql += 's.completion >= 1 AND '
        sql += 's.fieldID = f.fieldID '
        
        # Fetch the data from the DB
        sys.stderr.write ('Fetching data from the DB...\n')
        n = cursor.execute (sql)
        
        try:
            resSeq = cursor.fetchall ()
        except:
            resSeq = None
        
        # Summarize the results
        (targets, r, g, y, i, z, nea) = summary (resObs, resSeq)

        ra = array([targets[fieldID][0] for fieldID in targets.keys()])
        dec = array([targets[fieldID][1] for fieldID in targets.keys()])
        rt = array([r[fieldID] for fieldID in targets.keys()])
        gt = array([g[fieldID] for fieldID in targets.keys()])
        yt = array([y[fieldID] for fieldID in targets.keys()])
        it = array([i[fieldID] for fieldID in targets.keys()])
        zt = array([z[fieldID] for fieldID in targets.keys()])

        def neafilt(x,id):
            if x.has_key(id):
                return x[id]
            else:
                return 0

        neat = array([neafilt(nea,fieldID) for fieldID in targets.keys()])

        return (ra, dec, rt, gt, yt, it, zt, neat)


def logFileParse(sessionID):

    nnights = 0
    nlun = 0
    nobs = 0
    ncompl = 0
    nlost = 0
    nlunlost = 0
    neventlost = 0

    filename = '/home/lsst/lsst/simulator/src/lsst.log_' + str(sessionID)
    try:
        input = open(filename,'r')
        print 'opening ', filename
    except:
        sys.stderr.write("cannot find file %s\n" % (filename) )

    nnightstr = re.compile(r"cheduler:startNight")
    nlunstr = re.compile(r"FinishLunation")
    nobsstr = re.compile(r"Prop[\w\W]*closeObservation")
    complstr = re.compile("COMPLETE")
    loststr = re.compile("sequence[\s]*LOST[\w\W]")
    lostlunstr = re.compile("sequence[\s]*LOST[\w\W]*lunation")
    losteventstr = re.compile("sequence[\s]*LOST[\w\W]*event")
    
    for line in input.readlines():
        if nnightstr.search(line):
            nnights = nnights+1
        elif nlunstr.search(line):
            nlun = nlun + 1
        elif nobsstr.search(line):
            nobs = nobs + 1
            if complstr.search(line):
                ncompl = ncompl + 1
        elif loststr.search(line):
            nlost = nlost + 1
            if lostlunstr.search(line):
                nlunlost = nlunlost + 1
            elif losteventstr.search(line):
                neventlost = neventlost + 1

    return (nnights, nlun, nobs, ncompl, nlost, nlunlost, neventlost)


def main():

    usage = "usage: %prog sessionID"

    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--filename",
                      action="store", type="string", dest="filename",
                      help="plot to file FILENAME")
    parser.add_option("-r", "--resolution",
                      action="store", type="string", dest="res", default=120,
                      help="set resolution of output file to RES")
    parser.add_option("-e", "--extract",
                      action="store", type="string", dest="extfile",
                      help="extract data to file EXTRACT")

    (options, args) = parser.parse_args()

    if(len(args)!=1):
        parser.error("wrong number of arguments")

    sessionID = args[0]

    if options.extfile != None:
        extractLsst(int(sessionID), options.extfile)
        return

    print "sessionID = ", sessionID
    lsst(int(sessionID))

    if options.filename == None:
        show()
    else:
        savefig(options.filename, dpi=options.res, facecolor='k',
                edgecolor='k',orientation='portrait')

if __name__ == "__main__":
    main()
