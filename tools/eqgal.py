#!/usr/bin/env python

import math
from Numeric import *
from matplotlib.mlab import *

from pylab import *

def eqgal(l,b):
    # convert (l,b) to (ra,dec)
    l = l*math.pi/180.0
    b = b*math.pi/180.0
    sind = sin(b)*cos(1.0926)
    sind += cos(b)*sin(l-0.5760)*sin(1.0926)
    sind = where(sind>1.0, 1.0, sind)
    sind = where(sind<-1.0, -1.0, sind)
    dec = arcsin(sind)
    sinra = (cos(b)*sin(l - 0.5760)*cos(1.0926) - \
                    sin(b)*sin(1.0926))/cos(dec)
    cosra = cos(b)*cos(l - 0.5760)/cos(dec)
    cosra = where(cosra>1.0, 1.0, cosra)
    cosra = where(cosra<-1.0, -1.0, cosra)
    ra = arccos(cosra)
    ra = where(sinra>0, ra, 2.0*math.pi -ra)
    dec = dec*180.0/math.pi
    ra = ra*180.0/math.pi + 282.25
    ra = where(ra>360.0,ra - 360.0, ra)
    ra = ra / 15.0

    return (ra, dec)


def project(ra, dec):
    """
    do the Aitoff projection
    (compromise between shape and scale distortion)
    """

    # expects ra on (-180,180), dec, on (-90,90)
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

    # dec goes from -90 to 90
    phi = arrayrange(-90,90)
    lam = zeros(len(phi)) + ra
 
    return lam, phi

 
def parallel(dec):
    """
    create a longitude line at given dec
    """

    # ra goes from 0 to 360 (but we subtract 180 to get zero at center)
    lam = arrayrange(-180,180)
    phi = zeros(len(lam)) + dec
 
    return lam, phi

 
def aitoff():
    """
    plot the ra/dec grid on all plots
    with the ecliptic on the nea plot
    """
    
    global ax

    d = arrayrange(-90.0,91.0,30.0)
    for dd in d:
        [lam, phi] = parallel(dd)
        [x, y] = project(lam, phi)
        if dd == 0:
            plot(x,y,color='r')
        elif dd == -30:
            plot(x,y,color='r')
        else:
            plot(x,y,color='k')
         
    r = arrayrange(-180.0, 181.0, 30.0)
    for rr in r:
        ra = rr/15.0
        if ra < 0: ra += 24.0
        [lam, phi] = meridian(rr)
        [x, y] = project(lam, phi)
        if ra == 0:
            plot(x,y,color='r')
        elif abs(ra - 18.0) < 0.1:
            plot(x,y,color='r')
        else:
            plot(x,y,color='k')
        
    del d, r, lam ,phi, x, y
    return

def excludePlot():
    global ax, galaxyExclusion

    pL = galaxyExclusion['peakL']
    tL = galaxyExclusion['taperL']
    tB = galaxyExclusion['taperB']
    band = pL - tL
 
    galL = arrayrange(-180.0, 181.0, 1.0)
    xb = zeros(2*len(galL))
    xl = zeros(2*len(galL))

    i =-1
    for l in galL:
        i+=1
        xb[i] = pL - band*abs(l)/tB
        xl[i] = l

    galL = arrayrange(181.0, -180.0, -1.0)
    for l in galL:
        i+=1
        xb[i] = -(pL - band*abs(l)/tB)
        xl[i] = l

    (Ra, Dec) = eqgal(xl, xb)

    Ra = Ra * 15.0
    Ra = where(Ra>180.0, Ra-360.0, Ra)
    [x, y] = project(Ra, Dec)

    plot(x,y,'w.')
    axis("off")
    
    del galL, Ra, Dec, x, y, xb, xl
    return

def excludePlot1():
    global ax, galaxyExclusion

    pL = galaxyExclusion['peakL']
    tL = galaxyExclusion['taperL']
    tB = galaxyExclusion['taperB']
    band = pL - tL
 
    galL = arrayrange(0, 361.0, 1)
    xb = zeros(2*len(galL))
    xl = zeros(2*len(galL))

    i =-1
    for l in galL:
        i+=1
        xb[i] = pL - band*abs(l)/tB
        xl[i] = l

    (Ra, Dec) = eqgal(xl, xb)

    Ra = Ra * 15.0
    Ra = where(Ra>180.0, Ra-360.0, Ra)

    [x, y] = project(Ra, Dec)
    pm = scatter(x,y,c='r',s=1)
    set(pm, edgecolor='r',linewidth=0)
    
    galL = arrayrange(361.0, 0.0, -1)
    for l in galL:
        i+=1
        xb[i] = -(pL - band*abs(l)/tB)
        xl[i] = l

    (Ra, Dec) = eqgal(xl, xb)

    Ra = Ra * 15.0
    Ra = where(Ra>180.0, Ra-360.0, Ra)
    [x, y] = project(Ra, Dec)


    pm = scatter(x,y,c='r',s=1)
    set(pm, edgecolor='r',linewidth=0)
    axis("off")

    del galL, Ra, Dec, x, y, xb, xl
    return


def putpoint(Ra, Dec):
    """
    plot a shaded circle (on the sky) at
    the given ra and dec in hours, degrees
    """

    rRa = Ra * 15.0
    if rRa > 0: rRa = 180.0 - rRa
    size = 2
    phi = arrayrange(0.0, 361.0, 5.0)
    dec = Dec + size*cos(phi*math.pi/180.0)
    ra = rRa - size*sin(phi*math.pi/180.0)/cos(dec*math.pi/180.0)
    [x,y] = project(ra,dec)
    fill(x,y,'g')

    Ra = rRa/15.0
    if Ra < 0: Ra += 24.0
    str = '%3d' % int(Ra)
    (r,d) = project(rRa,Dec)
    text(r,d,str)

    return

def docir(ra, dec):
    """
    plot a shaded circle (on the sky) at
    the given ra and dec in (-180,180), (-90,90)
    """
 
    global ax

    size = 3.5/2.0

    ora = ra
    odec = dec
 
    phi = arrayrange(0.0,361.0,30.0)
    db = dec + size*cos(phi*math.pi/180.0)
    rb = ra - size*sin(phi*math.pi/180.0)/cos(db*math.pi/180.0)
    [x, y] = project(rb, db)
    fill(x, y, '#eef294', linewidth=0)

    (r,d) = project(ra,dec)

    ra = ra/15.0
    if ra < 0: ra += 24.0
    str = '%3d,%3d' % (int(ra), int(dec))
    text(r,d,str,verticalalignment='top',color='k')
    str = '%3d,%3d' % (int(ora), int(odec))
    text(r,d,str,verticalalignment='bottom',color='r')
 
    del phi, db, rb, x, y
 
    return
 
def shiftra(ra):
    ra = ra*15.0
    if ra>180: ra = ra-360
    return ra

galaxyExclusion = {'peakL':10.0, 'taperL':10.0, 'taperB':180.0}

fig = figure(1)
subplot(1,1,1)
aitoff()

ra = shiftra(2.0)
dec = -45
docir(ra,dec)
ra = shiftra(18.0)
dec = -45
docir(ra,dec)

galL = arrayrange(0,361,20)
for l in galL:
    (ra,dec) = eqgal(l,0.0)
#    print ra, dec
    ra = shiftra(ra)
    docir(ra,dec)

excludePlot()
#putpoint(0,0)
#(ra, dec) = eqgal(0.0,0.0)
#print "0,0 -> ", ra, dec
#putpoint(ra,dec)


#for ra in range(0.0,25.0,2.0):
#    putpoint(ra,0.0)
#    putpoint(ra,-30.0)
#    putpoint(ra,30.0)

show()
