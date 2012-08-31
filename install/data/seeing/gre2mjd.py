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
def is_leap (y):
    return (y % 4 == 0 and not (y % 100 == 0 and y % 400 != 0))

def is_valid (y, m, d):
    if (y < 1600 or m < 1 or d < 1):
        return -1
    if (is_leap (y)):
        days['February'] = 29
    try:
        t = days[months[m]] >= d
    except:
        return -1
    days['February'] = 28
    return t


# main routine
def gre2mjd (dateString):
    """
    Convert a date in the Gregorian calendar to Modified Julian Days
    (MJD).
    
    dateString as to be in the format YYYY-MM-DDTHH:MM:SS.SSS (24 hour
    clock).
    """
    # parse the input parameters
    date = dateString
    
    # parse the date
    try:
        year = int (date[:4])
        month = int (date[5:7])
        day = int (date[8:10])
        hh = int (date[11:13])
        mm = int (date[14:16])
        ss = float (date[17:])
    except:
        msg = 'dateString as to be in the format '
        msg += 'YYYY-MM-DDTHH:MM:SS.SSS (24 hour clock).'
        raise SyntaxError, msg
    
    # is the date reasonable?
    if (is_valid (year, month, day) == 0):
        msg = 'Fatal error: ' + months[month] + ' ' + str(year) 
        msg +=' has only ' + str (days[months[month]]) + ' days.'
        raise ValueError, msg
    elif (is_valid (year, month, day) == -1):
        msg = 'Fatal error: YYYY has to be hreater or equal to 1600,'
        msg += '             MM has to be positive and less or equal to 12,'
        msg += '             DD has to be positive and less or equal to 31.'
        raise ValueError, msg
    
    
    # compute the MJD
    yy = year - 1
    leap = is_leap (year)
    leap_factor = 0
    if (month > 2 and leap == 1):
        leap_factor = -1
    elif (month > 2 and leap == 0):
        leap_factor = -2
    
    # this is the integer part
    jd =  GREGORIAN_EPOCH - 1
    jd += 365 * yy
    jd += int (float (yy) / 4.0)
    jd += - int (float (yy) / 100.0)
    jd += int (float (yy) / 400)
    jd += int (float (367 * month - 362) / 12.0)
    jd += leap_factor + day
    
    # add the fraction of the day
    fraction = (float (hh) / 24.0)
    fraction += (float (mm) / 1440.0)
    fraction += (ss / 86400.0)
    
    jd += fraction
    
    mjd = jd - JMJD
    
    return (mjd)










