#!/usr/bin/env python
"""
patch_database.py

Script to modify the seeing data in the database according to the 
information in the cloud coverage data.


Usage
patch_database.py db_table cloud_data_file


Assumptions

1. db_table is in the format
date
flux
fwhm
fwhmx
fwhmy
secz

date is in seconds from YYYY-01-01T00:00:00.00 where YYYY is the year of
the weather data. 

2. It is assumed that the year of the weather data in the database 
(YYYY) is the same as the year the cloud data refers to.

3. cloud_data_file is a text (ASCII) file with data organized in 
tab-separated columns. The format of the file is
"%s %d - %d\t%d\t%d\t%d\t%d\t%s" \
  % (Month, StartDay, EndDay, Clouds1, Clouds2, Clouds3, Clouds4, Notes)
Where
 Month is the name of the month.
 StartDay is the day of the start of the night.
 EndDay is the day at the end of the night.
 CloudsN is the cloud factor for the N-th quarter of the night.
 
 The cliud factor is an integer in the range [0; 8], 0 mean not cloudy, 
 8 completely cloudy. For our purposes, a cloud factor of 4 or higer
 means that the sky is too cloudy to observe.
"""

import sys, time, re
from utilities import *


# GLOBALS
dbUser = 'www'
dbPasswd = 'zxcvbnm'
dbDB = 'LSST'

PATTERN = '^(\S+)\s+(\S{,2})\s+-\s+(\S{,2})\s+(\S)\s+(\S)\s+(\S)\s+(\S)\s+(.+)\s*$'

QUART = 2.5     # Duration in hours of each quarter pf the night

QUERY = 'UPDATE %s SET w_fwhm = 10 WHERE w_date BETWEEN %d AND %d'

CONFIG = 'LSST.conf'

MONTH = {'January': 1,
         'February': 2,
         'March': 3,
         'April': 4,
         'May': 5,
         'June': 6,
         'July': 7,
         'August': 8,
         'September': 9,
         'October': 10,
         'November': 11,
         'December': 12}




# Utility routines
def error (msg):
    """
    Simple utility routine: print msg to STDERR and quit with a status 
    code of 1.
    """
    sys.stderr.write ('ERROR: %s\n' % (msg))
    sys.exit (1)

def usage ():
    """
    Print usage strung and exit with a status code of 1.
    """
    USAGE = 'patch_database.py db_table cloud_data_file'
    sys.stderr.write ('%s\n' % (USAGE))
    sys.exit (1)



def getNightQuartBoundaries (year, month, startDay, epoch):
    """
    Compute the start and end times for the 4 quarters of the night of 
    year/month/startDay-endDay (at LATITUDE, LONGITUDE).
    
    We assume that each quarter lasts 2.5 hours.
    
    Return the (MJD-epoch) values for the beginning and end of the 4
    quarters.
    """
    deltaMJD = QUART / 24.
    
    # Compute MJD at midnight
    date = '%04d-%02d-%02dT24:00:00.0' % (year, month, startDay)
    midnightMJD = gre2mjd (date)
    
    # Night quarters
    quarts = []
    
    # First quarter
    start = ((midnightMJD - 2. * deltaMJD) - epoch) * DAY
    end = ((midnightMJD - deltaMJD) - epoch ) * DAY
    quarts.append ((start, end))
    # Second quarter
    start = ((midnightMJD - deltaMJD) - epoch) * DAY
    end = (midnightMJD - epoch ) * DAY
    quarts.append ((start, end))
    # Third quarter
    start = (midnightMJD - epoch) * DAY
    end = ((midnightMJD + deltaMJD) - epoch ) * DAY
    quarts.append ((start, end))
    # Fourth quarter
    start = ((midnightMJD + deltaMJD) - epoch) * DAY
    end = ((midnightMJD + 2. * deltaMJD) - epoch ) * DAY
    quarts.append ((start, end))
    return (quarts)







if (__name__ == '__main__'):
    # Parse the input params
    try:
        dbTable = sys.argv[1]
    except:
        usage ()
    try:
        data = file (sys.argv[2]).readlines ()
    except:
        usage ()
    
    
    # Parse the config file
    conf = readConfFile (CONFIG)
    try:
        lat = conf['latitude']
        lon = conf['longitude']
    except:
        error ('"latitude" and/or "longitude" keywords not in %s' \
            % (CONFIG))
    try:
        epoch = conf['simEpoch']
    except:
        error ('"simEpoch" keyword not in %s' % (CONFIG))
    
    # Get the year from the epoch
    (year, m, d, hh, mm, ss) = mjd2gre (epoch)
    
    # Compute the new epoch
    epoch = gre2mjd ('%04d-01-01T00:00:00.0' % (year))
    
    # Compile the RegEx pattern
    pat = re.compile (PATTERN)
    
    # Now, split each line and convert the dates in seconds from
    # January 1st using the RegEx pattern pat.
    ignored = 0
    total = len (data)
    for line in data:
        correct = False
        try:
            fields = res = pat.match (line).groups ()
        except:
            fields = ()
        if (len (fields) < 5):
            ignored += 1
            print ('Ignoring "%s"' % (line))
            continue
        
        # Determine the start and end time of the quarters of the night.
        quarts = getNightQuartBoundaries (year=year,
                                          month=MONTH[fields[0]], 
                                          startDay=int(fields[1]), 
                                          epoch=epoch)
        
        # Fetch the cloud factors
        clouds = fields[3:7]
        
        # Now, update the db
        for i in range (4):
            (start, end) = quarts[i]
            cloud = int (clouds[i])
            if (cloud > 4):
                query = QUERY % (dbTable, int (start), int (end))
                # print (query)
                (n, dummy) = executeSQL (query)
        # <-- end for loop
    # <-- end for loop
    
    # Exit
    if (ignored > 0):
        print ('Skipped %d lines out of %d' % (ignored, total))
    else:
        print ('Fully processed %d lines' % (total))
    
    
    



























