#!/usr/bin/env python
# 
# Gregorian date to MJD converter
# 
# Formulas from http://www.fourmilab.ch/
# Converted to python by f. pierfederici
# 
# NOAO/IRAF internal use only
# 



import sys, string


# globals
GREGORIAN_EPOCH = 1721425.5
JMJD = 2400000.5
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
    
    
    # is the date reasonable?
    if (isValid (year, month, day) == 0):
        msg = 'Fatal error: ' + months[month] + ' ' + str(year) + ' has only ' + str (days[months[month]]) + ' days.'
        raise (SyntaxError, msg)
    elif (isValid (year, month, day) == -1):
        msg = 'Fatal error: YYYY has to be hreater or equal to 1600,'
        msg += '             MM has to be positive and less or equal to 12,'
        msg += '             DD has to be positive and less or equal to 31.'
        raise (SyntaxError, msg)
    
    
    # compute the MJD
    yy = year - 1.
    leap = isLeap (year)
    leap_factor = 0.
    if (month > 2. and leap == 1.):
        leap_factor = -1.
    elif (month > 2. and leap == 0.):
        leap_factor = -2.
    
    jd =  GREGORIAN_EPOCH - 1
    jd += 365. * yy
    jd += int (float (yy) / 4.)
    jd += - int (float (yy) / 100.)
    jd += int (float (yy) / 400.)
    jd += int (float (367. * month - 362.) / 12.)
    jd += leap_factor + day
    jd += leap_factor + (hh / 24.)
    jd += leap_factor + (mm / 1440.)
    jd += leap_factor + (ss / 86400.)
    
    mjd = jd - JMJD
    
    return (mjd)


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
        try:
            mjd = gre2mjd (date)
        except:
            mjd = 'ERROR'
        
        print ('%s -> %s' % (date, mjd))
    sys.exit (0)









