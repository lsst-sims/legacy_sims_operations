#!/usr/bin/env python

# Philip A. Pinto 22 October 2004

import pygtk
pygtk.require('2.0')
import gtk

import math
from Numeric import *
from matplotlib.mlab import *
import sys, re, time, socket
import MySQLdb
from optparse import OptionParser
import ephem
from slalib import *

from pylab import *

DAY = 86400.0
MJDEpoch = 2400000.5
DEG2RAD = math.pi/180.0
RAD2DEG = 1.0/DEG2RAD

# Database specific stuff
from LSSTDBInit import *
OBSHIST = 'ObsHistory'
SEQHIST = 'SeqHistory'
FIELD = 'Field'
LSSTCONF = 'LsstConf'


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
            'fontsize'   : 9}

def getLsstConf():
    global FOV, longitude, latitude, simEpoch
                                                                               
    # Get a connection to the DB
    connection = openConnection ()
    cursor = connection.cursor ()
                                                                               
    sql = 'SELECT fov,latitude,longitude,seeingEpoch,simStartDay from %s where sessionID = %d ' % (LSSTCONF, sessionID)
                                                                               
    # Fetch the data from the DB
    print "Fetching Simulation globals from the LSSTCONF DB...",
                                                                               
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write(
            'Unable to execute LsstConf SQL query (%s).' % (sql) )
        sys.exit()
                                                                               
    try:
        dbTxt = cursor.fetchall ()
        print "dbtxt: ",dbTxt
        print "done."
    except:
        sys.stderr.write ('No Simulation global data for Session %d' \
            % (sessionID))
        sys.exit()
                                                                               
    for n in dbTxt:
        (FOV, latitude, longitude,seeingEpoch,simStartDay) = (float(n[0]),float(n[1]),float(n[2]),float(n[3]),int(n[4]))
        simEpoch = seeingEpoch + simStartDay
    print "FOV:%f  LAT:%f LON:%f Epoch:%f" % (FOV,latitude, longitude,simEpoch)
                                                                               

def get_refcounts():
    d = {}
    sys.modules
    # collect all classes
    for m in sys.modules.values():
        for sym in dir(m):
            o = getattr (m, sym)
            if type(o) is types.ClassType:
                d[o] = sys.getrefcount (o)
    # sort by refcount
    pairs = map (lambda x: (x[1],x[0]), d.items())
    pairs.sort()
    pairs.reverse()
    return pairs

def print_top(len):
    for n, c in get_refcounts()[:len]:
        print '%10d %s' % (n, c.__name__)
    return


# here begins the data munging
def timeAsString(t):
    # t here is in radians
    (sign,time) = sla_cr2tf(2,t)
    str = "%s%2d:%2.2d:%2.2d.%2.2d" % \
              (sign, time[0], time[1], time[2], int(100.0*time[3]))
    return str


def angleAsString(d):
    # d here is in radians
    (sign,angle) = sla_cr2af(2,d)
    str = "%s%2d:%2.2d:%2.2d.%2.2d" % \
              (sign, angle[0], angle[1], angle[2], int(100.0*angle[3]))
    return str


def mjdAsDateString(mjd):
    (year, month, day, frac, ok) =  sla_djcl(mjd)
    (sign,time) = sla_cd2tf(2,frac)
    str = "%4d/%2.2d/%2.2d %2d:%2.2d:%2.2d.%2.2d" % \
          (year, month, day, \
           time[0], time[1], time[2], int(100.0*time[3]))
    return str

def meanJulianDate(date, epoch):
    mjd = (float (date) / float (DAY)) + epoch
    return (mjd)

def localSiderealTime (mjd, longitude):
    """
    Given a date in MJD and a longitude on the Earth, compute the
    local sidereal time at that meridian.
    
    Input
    mjd         Modified Julias Day in days and fractions of a day.
    longitude   longitude North in decimal degrees.
    
    Output
    The local Sidereal Time (float) in decimal degrees.
    """
    # Convert the longitude to radians.
    longitude *= DEG2RAD
    
    # Compute the Greenwich mean sidereal time (radians)
    gst = sla_gmst (mjd)
    
    # Local Sidereal time (radians)
    # LSST convention is W is negative, East is positive
    lst  = gst + longitude
    
    # Convert the local Sidereal time to decimal degrees
    lst *= RAD2DEG
    #print "LST: longitude: %f mjd: %f gst: %f lst: %f" % (longitude,mjd,gst,lst)
    return (lst)


def hourAngle(ra,lst):
    ha = normalize (lst - ra, min=-180., max=180., degrees=True)
    return (ha)


def convertRaToHa(date, ra):
    global FOV, longitude, latitude, simEpoch
    mjd = meanJulianDate(date, simEpoch)
    lst = localSiderealTime(mjd, longitude)
    ha = hourAngle(ra, lst)
    return (ha)

def normalize (angle, min=0., max=None, degrees=True):
    """
    Given an angle, make sure that its value is within the range
    [min, max].
     
    If degrees=True the ammount to add/subtract is 360.
    If degrees=False the ammount to add/subtract is 2*pi
     
    If min/max is not specified, it reverts to its default value
    (which depends on the value of degrees):
    min = 0
    max = 360./2*pi
     
    Return the normalized angle in its original units
    """
    twoPI = 2 * math.pi
     
    angle = float (angle)
     
    if (min == None):
        min = 0.
    if (max == None and degrees):
        max = 360.
    elif (max == None and not degrees):
        max = twoPI
     
    if (degrees):
        while (angle < min):
            angle += 360.
        while (angle > max):
            angle -= 360.
    else:
        while (angle < min):
            angle += twoPI
        while (angle > max):
            angle -= twoPI
    return (angle)

def moon(mjd):
    """
    returns moon ra, dec, phase
    """
    global FOV, longitude, latitude, simEpoch

    (ra1, dec1, diam) = sla_rdplan(mjd, 3, longitude*DEG2RAD, latitude*DEG2RAD)

    v6moon = sla_dmoon(mjd)

    Rmatrix = sla_prenut(2000.0, mjd)

    xyzMoon2000 = sla_dmxv(Rmatrix, v6moon)

    (moonra, moondec)  = sla_dcc2s(xyzMoon2000)

    moonra = sla_dranrm(2.0*math.pi + moonra)

    sun12 = sla_evp(mjd, 2000.0)

    #sun3heliocentric = (-sun12[3])
    sun3heliocentric = sun12[3]
    for i in range(3) :
        sun3heliocentric[i] *= -1
    
    (sunra, sundec) = sla_dcc2s(sun3heliocentric)
    sunra = sla_dranrm(2.0*math.pi + sunra)

    moonsunsep = sla_dsep(sunra, sundec, moonra, moondec)

    phase = (1.0 - math.cos(moonsunsep))/2.0

    return (moonra, moondec, phase)


def leglab(cmin, cmax, a):
    """
    make labels for and draw the colormaps
    """
                                                                                
    x0 = -2.9
    dx = 5.7
    y0 = -1.74
    dy = 0.1
                                                                                
    i = -1
    n = 100
    bright = arrayrange(cmin,cmax,(cmax-cmin)/float(n))
    bright = (-bright+cmin)/(cmin-cmax)
    color = cm.jet(bright)
    
    n = len(bright)
    delx = dx/float(n)
    for ix in xrange(n):
        cx = ix / float(n)
        xpos = cx*dx + x0
        rgb = (color[ix][0], color[ix][1], color[ix][2])
        ccc = matplotlib.colors.rgb2hex(rgb)
        x = [xpos,xpos+delx,xpos+delx,xpos]
        y = [y0, y0, y0+dy, y0+dy]
        fill(x,y,ccc,edgecolor=color[ix],linewidth=0)
                                                                                
    str = "%4.1f" % cmin
    a.text(x0,y0-dy,str, smallfont, horizontalalignment='center', color=WHITE)
    str = "%4.1f" % ((cmax+cmin)/2.0)
    a.text(x0+dx/2.0,y0-dy,str, smallfont, horizontalalignment='center', color=WHITE)
    str = "%4.1f" % cmax
    a.text(x0+dx,y0-dy,str, smallfont, horizontalalignment='center', color=WHITE)
    title = "sky brightness"
    a.text(0.0,-2.0,title, bigfont, horizontalalignment='center', color=WHITE)
                                                                                
    a.set_axis_off()
    a.set_xlim([-3,3])
    a.set_ylim([-2.1,-1.55])
                                                                                
    return

def getBrightness(tmin, tmax):
    global sessionID
    global FOV, longitude, latitude, simEpoch
    
    # Get a connection to the DB
    connection = openConnection ()
    cursor = connection.cursor ()

    pnum ={}
    pnum['g'] = 421
    pnum['r'] = 422
    pnum['i'] = 423
    pnum['z'] = 424
    pnum['y'] = 425
    ax = {}
    axt = subplot(427)
    axc = subplot(426)
    cmax = 15.0
    cmin = 22.0
    leglab(cmin,cmax,axc)
   
    t0 = tmin*86400.0
    t1 = (tmax+1.0)*86400.0

    mjd = meanJulianDate(t0,simEpoch)
    print "starting date: ", mjdAsDateString(mjd)
    mjd = meanJulianDate(t1,simEpoch)
    print "ending date: ", mjdAsDateString(mjd)

    sql = 'select f.fieldRA, f.fieldDec, f.fieldID, '
    sql += 'o.skyBright, o.expDate, o.filter '
    sql += 'FROM %s f, %s o ' % (FIELD, OBSHIST)
    sql += 'WHERE f.fieldFov = %s AND ' % (FOV)
    sql += 'o.sessionID = %d AND ' % (sessionID)
    sql += 'o.expDate >= %f AND o.expDate < %f AND ' % (t0, t1)
    sql += 'o.fieldID=f.fieldID group by o.expDate'
    #sql += 'o.fieldID=f.fieldID'
       
    # Fetch the data from the DB
    print "Fetching data from the ObsHist DB...",sql
    
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write(
            'Unable to execute ObsHistory SQL query (%s).' % (sql) )
        sys.exit()
            
    try:
        resBri = cursor.fetchall ()
        print "done."
    except:
        sys.stderr.write ('No data for Session %d' \
                          % (sessionID))
        sys.exit()

    lenresBri = len(resBri)
    #print "RAA: len(resBri):%d startDay:%f EndDay:%f expDate:min:%f expDate:max:%f" %(lenresBri,tmin,tmax,t0,t1)
    for x in arrayrange(tmin*86400.0,tmax*86400.0,86400.0/12.0):

        t0 = x
        t1 = x + 86400.0/12.0
        mjd = meanJulianDate(t0, simEpoch)

        targets = dict([(row[2],(row[0]/15.0, row[1], row[3], row[4], row[5])) for row in resBri \
                        if row[4] >= t0 and row[4] < t1])

        #print "RAA startInt:%f endInt:%f len(targets):%d" %(t0,t1,len(targets))

        # the sky panels
        axt.cla()
        for k in ax.keys():
            ax[k].cla()

        countstr = ""

        # If there is no data, don't repaint black. Potentially, loss of 
        #	ancillary info regarding missed Obs opportunities. Mostly: sun.
        if len(targets) <= 0:
            continue
        else: 
        #if len(targets) > 0:

            for k in pnum.keys():
                ax[k] = subplot(pnum[k])

#                ra = array([targets[fieldID][0] for fieldID in targets.keys() if targets[fieldID][4]==k])
                dec = array([targets[fieldID][1] for fieldID in targets.keys() if targets[fieldID][4]==k ])
                bright = array([targets[fieldID][2] for fieldID in targets.keys() if targets[fieldID][4]==k ])
                ha = array([convertRaToHa(targets[fieldID][3],targets[fieldID][0]*15.0) \
                            for fieldID in targets.keys() if targets[fieldID][4]==k])
        
                countstr += "%s %4d  " % (k, len(dec))
                    
                if(len(dec) > 0):
                    bright = (-bright+cmin)/(cmin-cmax)
                    color = cm.jet(bright)

#                    ra = ra * 15.0
#                    ra = where(ra>180.0,ra-360.0,ra)
            
                    db = []
                    rb = []
                    x = []
                    y = []
                    
                    size = FOV/2.0
                    phi = arrayrange(0.0,361.0,30.0)*math.pi/180.0
                    
                    for i in xrange(len(dec)):
                        db = dec[i] + size*cos(phi)
                        rb = ha[i] - size*sin(phi)/cos(db*math.pi/180.0)
                        [x, y] = project(rb, db)
                        xy = zip(x,y)
                        p = Polygon(xy,facecolor=color[i],edgecolor=color[i])
                        ax[k].add_patch(p)
                
        # where can these labels go????
        #label = "Filter: " + k
        #ax[k].label(0,1.51,label,bigfont,horizontalalignment='center')

        mjd = meanJulianDate((t0+t1)/2.0, simEpoch)
        (mra, mdec, phase) = moon(mjd)
        #print "moon: ", mjd, mjdAsDateString(mjd), timeAsString(mra), angleAsString(mdec), phase
        
        mra = mra * RAD2DEG
        mdec = mdec * RAD2DEG
        size = phase*10.0
        mha = convertRaToHa(t0, mra)
        mha = mra
        if mha > 180.0: mha = mha - 360.0
            
        for k in ax.keys():
            for dd in xrange(-90,91,30):
                [lam, phi] = parallel(dd)
                [x, y] = project(lam, phi)
                ax[k].plot(x,y,color=WHITE)
                
            for rr in xrange(-180,181,30):
                [lam, phi] = meridian(rr)
                [x, y] = project(lam, phi)
                ax[k].plot(x,y,color=WHITE)
                
            phi = arrayrange(0.0,361.0,30.0)*math.pi/180.0
            db = mdec + size*cos(phi)
            rb = mha - size*sin(phi)/cos(db*math.pi/180.0)
            [x, y] = project(rb, db)
            ax[k].fill(x,y,facecolor='w')
            
            ax[k].set_xlim([-3,3])
            ax[k].set_ylim([-1.5,1.5])
            ax[k].set_axis_off()
            
            axt.text(-3.1,0.0, countstr, bigfont, \
                     horizontalalignment='left', color = 'w')

                
        str = "moon: %4.2f" % (phase)
        axt.text(3.0,-1.8,str, bigfont, \
                 horizontalalignment='left', color = 'w')
        str = "date: " +  mjdAsDateString(mjd)
        axt.text(-3.1,-1.8,str, bigfont, \
                 horizontalalignment='left', color = 'w')

        
        lst = localSiderealTime (mjd, longitude)
        str = "lst: " +  timeAsString(lst*DEG2RAD)
        axt.text(-3.1,-2.1,str, bigfont, \
                 horizontalalignment='left', color = 'w')
        
        axt.set_xlim([-3,3])
        axt.set_ylim([-1.5,1.5])
        axt.set_axis_off()
                
        manager.canvas.draw()
    
    return
    
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
    del a, d, z
                                                                               
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

 
#def aitoff():
#    """
#    plot the ra/dec grid on all plots
#    with the ecliptic on the nea plot
#    """
#    
#    global ax
#
#    for dd in xrange(-90,91,30):
#        [lam, phi] = parallel(dd)
#        [x, y] = project(lam, phi)
#        for k in ax.keys():
#            ax[k].plot(x,y,color=WHITE)
#         
#    for rr in xrange(-180,181,30):
#        [lam, phi] = meridian(rr)
#        [x, y] = project(lam, phi)
#        for k in ax.keys():
#            ax[k].plot(x,y,color=WHITE)
#
#    del d, r, lam, phi, x, y
#    return


def updatefig(*args):
    """
    called by gtk
    """
    global tstart, tend
    
    getBrightness(tstart, tend)
    sys.exit()

    manager.canvas.draw()
 
    return gtk.TRUE
 

fig = figure(num=1, figsize=(9,11), facecolor='k', edgecolor='k')

try:
    val = sys.argv[1:]
    sessionID = int (val[0])
except:
    print "..........No session parameter found!"
    print "..........Use newbri.py <sessionID>"
    sessionID = 23

print "Session ID: %d" % (sessionID)

#tstart  = 0.001
tstart  = 0
tend = 100

# load the simulation global parameters: FOV, longitude, latitude, simEpoch
getLsstConf()

try:
    manager = get_current_fig_manager()
 
    gtk.timeout_add(10, updatefig)
    show()
except:
    pass
