#!/usr/bin/env python

# System modules
import os
import math
import random
import re
import socket
import string
import sys
import tempfile
import time
import logging
#import MySQLdb

# SimPy includes
#from SimPy import Simulation
#from SimPy.Simulation import hold, request, release, now, PriorityQ, FIFO
# from SimPy.Monitor import Monitor

# Third-party includes
#try:
#    import slalib
#except:
#    import pysla as slalib
import palpy as pal

import Sun

try:
    from lsstUtil import distance
    #print('Using a FAST implementation of distance().')
except:
    #print('Warning: a slower version of distance() is being used.')
    def distance(field0, fields):
        """
        Compute the distance (on a sphere) between field0 and each one of fields.
        
        Input
        field0:   a two dimensional list of floats/doubles (x, y)
        fields:   a list of two dimensional list of floats/doubles ((x, y), ...)
        
        Output
        A list of N+1 distances, where N=len(fields). Each distance is the angular
        distance between pairs of coordinates.
        
        Note
        1. x and y are assumed to be in radians.
        2. x and y are assumed to be spherical coordinates.
        3. This is a fallback solution in case an optimized version of this 
           routine does not exist.
        """
        #return([slalib.sla_dsep(field0[0], field0[1], field[0], field[1]) for field in fields])
        return([pal.dsep(field0[0], field0[1], field[0], field[1]) for field in fields])

# Simulator specific includes
from dateutils import *
from exceptions import *



# Simulation parameters
STARTMJD        = 50000.        # MJD of the first day of simulation
HOUR            = 3600.         # seconds in one hour (approximate)
DAY             = 86400.        # seconds in one day (approximate)
WEEK            = 604800.       # seconds in one week (approximate)
MONTH           = 262800.       # seconds in one month (approximate)
YEAR            = 31536000.     # seconds in one year (approximate)
TWOPI 		= 2 * math.pi

# Default Configuration Files
DefaultLSSTConfigFile = 'conf/survey/LSST.conf'
DefaultInstrumentConfigFile = 'conf/system/Instrument.conf'

DefaultGeneralPropConfigFile = './GeneralProp.conf'
DefaultNEAConfigFile = './NearEarthProp.conf'
DefaultSNConfigFile = './SuperNovaProp.conf'
DefaultSNSSConfigFile = './SuperNovaSubSeqProp.conf'
DefaultWLConfigFile = './WeakLensProp.conf'
DefaultWLSConfigFile = './WeakLensShearProp.conf'
DefaultKBOConfigFile = './KuiperBeltProp.conf'
DefaultWLTSSConfigFile = './WLprop.conf'

DefaultASConfigFile = 'conf/system/AstronomicalSky.conf'
DefaultFiltersConfigFile = 'conf/survey/Filters.conf'
DefaultSchedulerConfigFile = 'conf/scheduler/Scheduler.conf'

# Observation Types for events in sequences
OBSTYPE_VISIT = 0
OBSTYPE_MISSED = 1

# SeqHistory Sequence completion status
SUCCESS = 0
MAX_MISSED_EVENTS = 1
CYCLE_END = 2
SIMULATION_END =3

# TimeHistory Events
START_NIGHT = 0
MOON_WANING = 1         # New lunation, too
MOON_WAXING = 2
NEW_YEAR = 3
END_DUSK    = 4
START_DAWN  = 5
END_NIGHT   = 6

# Telescope parameters
DOWNTIME        = 10.           # Yearly mean down time (percent)

# For testing only
AVGPRIORITY     = 1.0           # The mean Observation priority.
SIGMAPERCENT    = 10.           # Sigma (percent of the mean).
AVGDELTAPRI     = 0.1           # The mean delta in priority.

# Routines and non user-specific globals
DEG2RAD = math.pi / 180.    # radians = degrees * DEG2RAD
RAD2DEG = 180. / math.pi    # degrees = radians * RAD2DEG

# RE to match a key/value specifier and optional comment - LD (MM modification)
_config_line_re = re.compile(r'^\s*(\w+\[*\w*\]*\s*=\s*[^#]+)(.*)')

# RE to extract key and value - LD (MM modification)
_config_item_re = re.compile(r'^\s*(\w+\[*\w*\]*)\s*=\s*(\S+)')

def warning (msg):
    """
    Print a warning (i.e. a non fatal error) to STDOUT.
    
    msg is the warning text to be printed.
    """
    sys.stderr.write ('Warning: ' + msg + '\n')
    return


def parseArgs (args):
    """
    Do a quick command line argument parsing. 
    
    The expected syntax is --var=val. No check on the semantic is 
    performed (it is left to the colling code).
    
    Return a dictionary of var=val entries. If args is None, an empty
    dictionary is returned.
    
    Raise an exception of type SyntaxError in case of syntax errors 
    in the command line args.
    """
    result = {}
    
    for arg in args:
        try:
            (var, val) = string.split (arg, '=', 1)
        except:
            raise (SyntaxError, '%s is in the wrond format' % (arg))
        
        if (var[:2] != '--'):
            raise (SyntaxError, 'variable names must start with a ' +
                                'double dash (%s)' % (var))
        
        result[var[2:]] = val
    return (result)


def usage (usageString):
    """
    Print the usageString to STDERR.
    
    If usageString is null, print a generic message saying that some
    of the command line arguments had syntax errors in them.
    """
    command = os.path.basename (sys.argv[0])
    if (usageString):
        sys.stderr.write ('usage: %s %s\n' % (command, usageString))
    else:
        sys.stderr.write ('Error in parsing command line arguments.\n')
    return


def fatalError (errorMessage, exitCode=1):
    """
    Print the errorMessage to STDERR and exit with an exit code equal
    to exitCode (default 1).
    
    If errorMessage is null, print a generic message saying that 
    something went wrong.
    """
    if (errorMessage):
        sys.stderr.write ('Fatal Error: ' + errorMessage + '\n')
    else:
        sys.stderr.write ('Fatal Error: something went wrong.\n')
    sys.exit (exitCode)
    return

def sex2deg(sex, sep=':'):
    """
    Convert angles in sexagesimal format (sex) to decimal format.
    
    Input
    sex     value in sexagesimal format (string)
    sep     separator for degrees, minutes and seconds (char). 
            Defaults to ':'
    
    Return
    Decimal value corresponding to sex (float)
    """
    try:
        (dd, mm, ss) = string.split(string.strip(sex), sep)
    except:
        (dd, mm) = string.split(string.strip(sex), sep)
        ss = '0'
    if(float(dd) >= 0):
        return(float(dd) + float(mm) / 60.0 + float(ss) / 3600.0)
    else:
        return(float(dd) - float(mm) / 60.0 - float(ss) / 3600.0)


def deg2sex (deg, sep=':'):
    """
    Convert angles in decimal format (deg) to sexagesimal format.
    
    Input
    deg     value in decimal format (float)
    sep     separator for degrees, minutes and seconds for output
            formatting (char). Defaults to ':'
    
    Return
    Sexagesimal value corresponding to deg (string)
    """
    try:
        deg = float (deg)
    except:
        return ('')
    
    degrees = int (deg)
    if(degrees >= 0):
        temp = (deg - degrees) * 60
        minutes = int (temp)
        seconds = int ((temp - minutes) * 60)
    else:
        temp = - (deg - degrees) * 60
        minutes = int (temp)
        seconds = int ((temp - minutes) * 60)
    
    sex = "%02d%c%02d%c%05.2f" % (degrees, sep, minutes, sep, seconds)
    return (sex)


def readConfFile (fileName):
    """
    Parse the configuration file (fileName) and return a dictionary of
    the content of the file.
    
    fileName must be an ASCII file containing a list of key = value
    pairs, one pair per line. Comments are identified by a '#' and can
    be anywhere in the file. Everything following a '#' (up to the 
    carriage return/new line) is considered to be a comment and 
    ignored.
    
    The dictionary has the form {key: value} where value is a simple 
    number if and only if key appears only one time in fileName. 
    Otherwise, value is an array.
    
    Value can have '=' sign in it: each non-comment line is split 
    using the '=' character as delimiter, only once and starting from 
    the left. Extra white spaces and '\n' characters are stripped from
    both key and value.
    
    An attempt is made to convert value into a float. If that fails, 
    value is assumed to be a string.
    
    
    Input
    fileName:   the name (with path) of the configuration file.
    
    Return
    A dictionary of key = value elements.
    A 2d array of key, value pairs.
    
    Raise
    IOError if fileName cannot be opened for reading.
    """
    conf = {}
    pairs = []
    index = 0

    # Try and read the file fileName (raise IOError if something bad 
    # happens).
    lines = file (fileName).readlines ()
    
    for line in lines:
        line = line.strip()
        if not line:			# skip blank line
            continue
        if line[0]=='#': 		# skip comment line
            continue

        comment = ""
        m = re.search (_config_line_re, line)
        if m:
            good, comment = m.group(1), m.group(2)

        m = re.search (_config_item_re, good)
        if m:
            key, val = m.group(1), m.group(2)

            # store "key = value" string
            pairs.append({
                    'key' : key,
                    'val' : val,
                    'index' : index,
            })
            index += 1

            # Try and convert val to a float
            try:
                val = float (val)
            except:
                # Ops, must be a string, then
                pass
            
            if not conf.has_key (key):
                conf[key] = val
            elif (isinstance (conf[key], list)):
                conf[key].append (val)
            else:
                conf[key] = [conf[key], val]
    return conf, pairs


def storeParam (lsstDB, sessionID, propID, moduleName, paramIndex, paramName,
                    paramValue, comment=""):

#    sql = 'insert into Config values (NULL, '
#    sql += '"%d", ' % (sessionID)
#    sql += '"%d", ' % (propID)
#    sql += '"%s", ' % (moduleName)
#    sql += '"%d", ' % (paramIndex)
#    sql += '"%s", ' % (paramName)
#    sql += '"%s", ' % (MySQLdb.escape_string(paramValue))
#    sql += '"%s") ' % (comment)
#
#    (n, dummy) = lsstDB.executeSQL(sql)
    lsstDB.addConfig(sessionID, propID, moduleName, paramIndex, paramName, paramValue, comment)

#def computeDateProfile (obsProfile, date):
    """
    Convert Simulator seconds to an MJD and LST for observatory location
    and epoch.
        Input
            obsProfile	longitude, latitude, elevation, epoch of observatory
            date    	elapsed simulation time in seconds

        Output
            dateProfile     an array containing
                date
                mjd
                lst_RAD
    """
#    (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = obsProfile
#    mjd = (float (date) / float (DAY)) + float(epoch_MJD)
##    lst_RAD = slalib.sla_gmst(mjd)  + lon_RAD
#    lst_RAD = pal.gmst(mjd) + lon_RAD
#    if lst_RAD < 0:
#        lst_RAD += TWOPI
#    return (date, mjd, lst_RAD)

_secmap = {
    's' : 1,
    'm' : 60,
    'min' : 60,
    'h' : 3600,
    'd' : 86400,
    'w' : 86400 * 7,
    'mon' : 86400 * 30,
    'y' : 86400 * 365
}


_timeStr_re = re.compile(r'([-+]?[\d]*\.?[\d]+)\s*([a-z]*)', re.IGNORECASE)

def timeStr2Sec(time_str):
    """
    Convert a time interval specification to seconds.  Allow
    any number of concatenated strings of the form:

      3d
      0.5y
      1h30m
      6mon

    etc.

    """

    if type(time_str) is float:
        return time_str                 # we were passed a float

    all_matches = re.findall(_timeStr_re, time_str)
    sec = 0
    if not all_matches:
        raise Exception("strange timeStr: " + str(time_str));

    for s, u in all_matches:
        if u:
            sec += _secmap.get(u, 1) * float(s)         # got a unit specifier
        else:
            sec += float(s)                             # no unit suffix; assume sec
    return sec

def compareWinners (a, b):
    # Sort top proposal targets by lowest airmass, then darkest sky brightness,
    # then fieldID.  Should parameterize to allow user to choose criteria.
    if a.airmass < b.airmass:
        return -1
    elif a.airmass > b.airmass:
        return 1
    elif a.skyBrightness > b.skyBrightness:  # airmass equal
        return -1
    elif a.skyBrightness < b.skyBrightness:
        return 1
    elif a.fieldID < b.fieldID:     # airmass & sky brightness equal
        return -1
    elif a.fieldID > b.fieldID:
        return 1
    else:
        return 0


# Memory usage debug routines from  Active State Programmer Network
#           http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/286222
# Compliments of 
#           Submitter: Jean Brouwers (other recipes)
#           Last Updated: 2004/07/11
#           Version no: 1.0
#           Category: System
#           Description:
#
#       This recipe provides a number of functions to get the memory usage 
#       of a Python application on Linux.
#
#   Use:    m0 = memory(); r0 = resident(); s0 = stacksize()
#           ....
#           m1 = memory(m1); r1 = resident(r0); s1 = stacksize(s0)
import os

_proc_status = '/proc/%d/status' % os.getpid()

_scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
          'KB': 1024.0, 'MB': 1024.0*1024.0}

def _VmB(VmKey):
    '''
    Private.
    '''
    global _proc_status, _scale
    # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
    # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
    # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]


def memory(since=0.0):
    '''
    Return memory usage in bytes.
    '''
    return _VmB('VmSize:') - since


def resident(since=0.0):
    '''
    Return resident memory usage in bytes.
    '''
    return _VmB('VmRSS:') - since

def stacksize(since=0.0):
    '''
    Return stack size in bytes.
    '''
    return _VmB('VmStk:') - since


if __name__ == '__main__':
    import unittest
    class TestTimeStr2Sec (unittest.TestCase):
        """Test various time string conversions to seconds"""
        _testvals = {
                "0" : 0,
                "30" : 30,
                "30s" : 30,
                "1d" : 86400,
                "1w" : 86400 * 7,
                "0.5y" : 86400 * 365 / 2,
                "20m" : 60 * 20,
                "20min" : 60 * 20,
                "1h20m" : 3600 + 60 * 20,
                "3mon" : 86400 * 30 * 3,
        }
        def testStuff (self):
            for k, v in self._testvals.items():
                self.assertEqual (timeStr2Sec(k), v)
        
    unittest.main()
