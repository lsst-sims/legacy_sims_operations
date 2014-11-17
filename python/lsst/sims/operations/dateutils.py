#!/usr/bin/env python
# 
# Gregorian date to MJD converter
# 
# Formulas from http://www.fourmilab.ch/
# Converted to python by f. pierfederici
# 
# NOAO/IRAF internal use only
# 



import sys, string, math
#try:
#    import slalib
#except:
#    import pysla as slalib

import palpy as pal

# globals
TWOPI = 2 * math.pi
GREGORIAN_EPOCH = 1721425.5
MJD2JD = 2400000.5              # JD = MJD + MJD2JD

days = {'January':      31,
        'February':     28,
        'March':        31,
        'April':        30,
        'May':          31,
        'June':         30,
        'July':         31,
        'August':       31,
        'September':    30,
        'October':      31,
        'November':     30,
        'December':     31}

months = {1:  'January',
          2:  'February',
          3:  'March',
          4:  'April',
          5:  'May',
          6:  'June',
          7:  'July',
          8:  'August',
          9:  'September',
          10: 'October',
          11: 'November',
          12: 'December'}



# utility functions
def isLeap (year):
    """
    Return 1 if year is a leap year, 0 otherwise.
    """
    return (year % 4 == 0 and not (year % 100 == 0 and year % 400 != 0))


def isValid (y, m, d):
    """
    Perform a sanity check on the date is input.
    
    Return 1 is date is valid, 0 otherwise.
    """
    if (y < 1600 or m < 1 or d < 1):
        return -1
    if (isLeap (y)):
        days['February'] = 29
    try:
        t = days[months[m]] >= d
    except:
        return -1
    days['February'] = 28
    return t


def gre2mjd (date):
    """
    Convert date into MJD.
    
    date has to be in the format YYYY-MM-DDTHH:MM:SS.SSS in
    24 hour clock.
    
    Return
    MJD: Modified Julian Day (floating point number)
    
    Raise
    SyntaxError if date is not valid
    """
    # parse the date
    try:
        year = int (date[:4])
        month = int (date[5:7])
        day = int (date[8:10])
        hh = float (date[11:13])
        mm = float (date[14:16])
        ss = float (date[17:])
    except:
        msg = 'Fatal error: date has an unsupported syntax.'
        msg += '       date has to be in the format'
        msg += '       YYYY-MM-DDTHH:MM:SS.SSS'
        msg += '       in 24 hour clock'
        raise (SyntaxError, msg)
    
    # Use SLALIB to convert from (year, month, day) to MJD
    #(mjd, error) = slalib.sla_cldj (year, month, day)
    mjd = pal.cldj(year, month, day)    

    if (error):
        msg = 'Fatal error: YYYY has to be hreater or equal to 1600,'
        msg += '             MM has to be positive and less or equal to 12,'
        msg += '             DD has to be positive and less or equal to 31.'
        raise (SyntaxError, msg)
    
    # Now, handle the hh, mm and ss part
    mjd += (hh / 24.0) + (mm / 1440.) + (ss / 86400.)
    
    return (mjd);


def mjd2gre (mjd):
    # Use SLALIB to convert from MJD to (year, month, day)
    #(year, month, day, fraction, error) = slalib.sla_djcl (mjd)
    (year, month, day, fraction) = pal.djcl(mjd)

    #if (error):
    #    msg = 'Fatal error: MJD must correspond to a date later than 4701BC March 1'
    #    raise (SyntaxError, msg)
    
    # Now take care of the fraction of day
    hh = math.floor (24. * fraction)
    mm = math.floor (1440. * (fraction - hh / 24.))
    ss = 86400. * (fraction - hh / 24. - mm / 1440.)
    return ((year, month, day, int (hh), int (mm), ss))


def gre2frac (date):
    """
    Convert date to he number of fractional dayssince 2000 Jan 0.0 UT.
    
    Raise
    SyntaxError if date is not valid
    """
    # parse the date
    try:
        year = float (date[:4])
        month = float (date[5:7])
        day = float (date[8:10])
        hh = float (date[11:13])
        mm = float (date[14:16])
        ss = float (date[17:])
    except:
        msg = 'Fatal error: date has an unsupported syntax.'
        msg += '       date has to be in the format'
        msg += '       YYYY-MM-DDTHH:MM:SS.SSS'
        msg += '       in 24 hour clock'
        raise (SyntaxError, msg)
    
    ut = hh + (mm / 60.) + (ss / 3600.)
    d = 367. * year - 7. * int (year + int (month + 9.) / 12) / 4
    d += 275. * int (month) / 9 + day - 730530. + (ut / 24.)
    return (d)


def computeEclipticAngle (d):
    """
    Given a date expressed in fractional days, compute the obliquity 
    of the ecliptic.
    """
    return (23.4393 - 3.563E-7 * d)


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
    angle = float (angle)
    
    if (min == None):
        min = 0.
    if (degrees):
        if (max == None):
            max = 360.
        addit = 360.
    else:
        if (max == None):
            max = TWOPI
        addit = TWOPI

    while (angle < min):
        angle += addit
    while (angle > max):
        angle -= addit
    return (angle)


def dist (Ra1,Dec1,Ra2,Dec2):
    """
    Return the distance between two celestial locations.

    Input
        Ra1     RA for first location, in radians
        Dec1    Dec for first location, in radians
        Ra2     RA for second location, in radians
        Dec2    Dec for second location, in radians

    Output
        distance    distance between (Ra1,Dec1) and Ra2,Dec2), in radians 
    """
    dist = math.acos(math.sin(Dec1)*math.sin(Dec2) + 
           math.cos(Dec1)*math.cos(Dec2)*math.cos(Ra1 - Ra2))
    return(dist)


if (__name__ == '__main__'):
    # parse input parameters
    if (len (sys.argv) > 1):
        dates = sys.argv[1:]
    else:
        print ('usage: gre2mjd.py date')
        print ('       date has to be in the format')
        print ('       YYYY-MM-DDTHH:MM:SS.SSS')
        print ('       in 24 hour clock')
        sys.exit (1)
    
    for date in dates:
        mjd = gre2mjd (date)
        try:
            mjd = gre2mjd (date)
        except:
            mjd = 'ERROR'
        
        print ('%s -> %s' % (date, mjd))
    sys.exit (0)






