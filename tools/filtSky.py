#!/usr/bin/env python
#
# Author: Michelle Miller
# Date:   May 14, 2008
#
# Script to generate filter sky brightness on runs done before this was
# a feature. Code cut from Proposal.closeObservation().

import math
import sys
import MySQLdb
import slalib
from LSSTDBInit import *
from ETC import *

extinction = 0.172
skyBrightKeys = [0, 18, 50, 80, 100]
filterOffset = { }

# Corrections for moonPhase = 0 percent (new moon)
filterOffset['u',0.] =  0.66
filterOffset['g',0.] =  0.41
filterOffset['r',0.] = -0.28
filterOffset['i',0.] = -1.36
filterOffset['z',0.] = -2.15

# Corrections for moonPhase = 18 percent
filterOffset['u',18.] =  0.28
filterOffset['g',18.] =  0.30
filterOffset['r',18.] = -0.19
filterOffset['i',18.] = -1.17
filterOffset['z',18.] = -1.99

# Corrections for moonPhase = 50 percent
filterOffset['u',50.] = -1.05
filterOffset['g',50.] =  0.03
filterOffset['r',50.] =  0.02
filterOffset['i',50.] = -0.96
filterOffset['z',50.] = -1.78

# Corrections for moonPhase = 80 percent
filterOffset['u',80.] = -1.83
filterOffset['g',80.] = -0.08
filterOffset['r',80.] =  0.10
filterOffset['i',80.] = -0.78
filterOffset['z',80.] = -1.54
 
# Corrections for moonPhase = 100 percent (full moon)
filterOffset['u',100.] = -2.50
filterOffset['g',100.] = -0.35
filterOffset['r',100.] =  0.31
filterOffset['i',100.] = -0.47
filterOffset['z',100.] = -1.16

def getFilterSkyBright (filter,moonAlt,moonPhase,skyBright):
    """
    Derive skyBrightness for filter (from Proposal.closeObservation()) 
    """
    #(sunrise, sunset) = twilightProfile
    filterSkyBright = 0.0

    # set y skybrightness for any kind of sky
    if (filter == 'y'):
        filterSkyBright = 17.3  
    else:      # g,r,i,z,u
         # If moon below horizon, use new moon offset for filter brightness
         if (math.degrees(moonAlt) <= -6.0):
             adjustBright = filterOffset[filter,0.]

         # Interpolate if needed. Note: moonPhase is a float not int
         elif (moonPhase not in skyBrightKeys):
             i = 0
             while (skyBrightKeys[i] < moonPhase):
                 i = i+1

             # find upper and lower bound
             upperMoonPhase = skyBrightKeys[i]
             lowerMoonPhase = skyBrightKeys[i-1]
             lowerAdjustBright = filterOffset[filter,lowerMoonPhase]
             upperAdjustBright = filterOffset[filter,upperMoonPhase]
             # linear interpolation
             adjustBright = lowerAdjustBright + (((moonPhase - lowerMoonPhase)*(upperAdjustBright - lowerAdjustBright))/(upperMoonPhase - lowerMoonPhase))

         else:          # moon not set and moon phase is key
             adjustBright = filterOffset[filter, moonPhase]
         filterSkyBright = skyBright + adjustBright

         # z sky brightness should never be under 17.0
         if (filter == 'z') and (filterSkyBright < 17.0):
             filterSkyBright = 17.0

         # Won't work without a way to detect twilight
         # If twilight, set brightness for z
         #if ( obs.date < sunset) or (obs.date > sunrise):
            #if (filter == 'z'):
               #filterSkyBright = 17.0

    return filterSkyBright

def getDbData(sql):
    global sessionID
    # Get a connection to the DB
    connection = openConnection ()
    cursor = connection.cursor ()
    # Fetch the data from the DB
    try:
        n = cursor.execute (sql)
    except:
        sys.stderr.write(
            'Unable to execute SQL query (%s).' % (sql) )
        sys.exit()
    try:
        ret = cursor.fetchall ()
        #print "done."
    except:
        sys.stderr.write ('No database records for Session %d' % sessionID)
        sys.exit()
    # Close the connection
    cursor.close ()
    connection.close ()
    del (cursor)
    del (connection)
    return (ret)

# Note that moonAlt as stored in cronos92 version of DB is meaningless.  Use
# moonRA and moonDec
def create_output_table(sessionID):
    print 'Creating filtSky Table ...'
    sql = 'DROP TABLE IF EXISTS filtSky_%d' % (sessionID)
    ret = getDbData(sql)
    sql = 'create table filtSky_%d (filtSkyID int unsigned AUTO_INCREMENT PRIMARY KEY, obsHistID int unsigned NOT NULL,filter varchar(8) NOT NULL,moonAlt float NOT NULL,moonPhase float NOT NULL,VskyBright float NOT NULL,expMJD double NOT NULL,airmass float NOT NULL,filtSky float NOT NULL, etcSkyBright float NOT NULL);' % (sessionID)
    ret = getDbData(sql)
    print "Create filtSky table done"
    sql = 'select obsHistID, filter, moonPhase, skyBright, expMJD, airmass, moonRA, moonDec, lst, fieldRA, fieldDec from ObsHistory where sessionID=%d' % (sessionID)
    table_data = getDbData(sql)

    sql = 'select paramValue from Config where sessionID = %d and paramName = "latitude"' % (sessionID)
    ret = getDbData(sql)
    latitude = float(ret[0][0])
    print "latitude = %f" % latitude

    print "Start processing sky brightness"
    for k in range(len(table_data)):
	obsHistID = table_data[k][0]
	filter = table_data[k][1]
	moonPhase = table_data[k][2]
	skyBright = table_data[k][3]
	expMJD = table_data[k][4]
	airmass = table_data[k][5]
        moonRA = table_data[k][6]
        moonDec = table_data[k][7]
        lst = table_data[k][8]
        fieldRA = table_data[k][9]
        fieldDec = table_data[k][10]

        # cannot use DB moonAlt here.  It is incorrect.  Use calculated value.
        moonHA_RAD = lst - moonRA
        (moonAz_RAD,d1,d2,moonAlt_RAD,d4,d5,d6,d7,d8) = slalib.sla_altaz (moonHA_RAD, moonDec, latitude)

        filtSky = getFilterSkyBright (filter, moonAlt_RAD, moonPhase, skyBright)
        etcSkyB = getETCSkyBright (filter, fieldRA, fieldDec, moonAlt_RAD, moonAz_RAD, moonPhase, lst, expMJD, latitude)

	sql = 'insert into filtSky_%d VALUES (NULL, %d, "%s", %f, %f, \
               %f, %d, %f, %f, %f)' \
             % (sessionID, obsHistID, filter, moonAlt_RAD, moonPhase, \
                skyBright, expMJD, airmass, filtSky, etcSkyB)
        (n, dummy) = executeSQL (sql)
        if n != 1:
            print "DB write failed"
    return

def getETCSkyBright (filter, fieldRA, fieldDec, moonAlt_RAD, moonAz_RAD, moonPhase, lst, expMJD, latitude):

    if filter == 'u':
        bandidx = 0
    elif filter == 'g':
        bandidx = 1
    elif filter == 'r':
        bandidx = 2
    elif filter == 'i':
        bandidx = 3
    elif filter == 'z':
        bandidx = 4
    elif filter == 'y':
        bandidx = 5
    else:
        raise ValueError, "Incorrect/missing filter"

    fieldHA_RAD = lst - fieldRA
    (az_RAD,d1,d2,alt_RAD,d4,d5,d6,d7,d8) = slalib.sla_altaz (fieldHA_RAD, fieldDec, latitude)
    alt_DEG = math.degrees (alt_RAD)
    az_DEG = math.degrees (az_RAD)

    moonAz_DEG = math.degrees(moonAz_RAD)
    moonAlt_DEG = math.degrees(moonAlt_RAD)

    #sql = 'select paramValue from Config where sessionID = %d and paramName = "longitude"' % (sessionID)
    #longitude = getDbData(sql)
    #print "longitude = %f" % (longitude)

    #(sunRA, sunDec, diam) = slalib.sla_rdplan (expMJD, 'Sun', longitude, latitude)
    #sunHA_RAD = lst - sunRA
    #(sunAz_RAD,d1,d2,sunAlt_RAD,d4,d5,d6,d7,d8) = slalib.sla_altaz (sunHA_RAD, sunDec, latitude)
    #sunAz_DEG = degrees (sunAz_RAD)
    #sunAlt_DEG = degrees (sunAlt_RAD)

    # moonPhase adjustment to phase angle (0-180)
    moonPhase = math.acos((moonPhase/50)-1)*180/math.pi

    etc = ETC()
    etcSkyB = etc.getSkyBrightnessAB (bandidx, expMJD, extinction, alt_DEG, az_DEG, moonAlt_DEG, moonAz_DEG, moonPhase, 0,0)
    #etcSkyB = etc.getSkyBrightnessAB (bandidx, expMJD, extinction, alt_DEG, az_DEG, moonAlt_DEG, moonAz_DEG, moonPhase, sunAlt_DEG, sunAz_DEG)
    return etcSkyB     

try:
    val = sys.argv[1:]
    sessionID = int (val[0])
except:
    print "\n\n..........No session parameter found!"
    print "..........Use gen_result.py <sessionID>\n\n"
    done

create_output_table(sessionID)

