import sys, re, time, socket
import numpy as np
import MySQLdb as mysqldb
import os
from socket import gethostname


def connect_db(hostname='localhost', username='www', passwdname='zxcvbnm', dbname='OpsimDB'):
    # connect to lsst_pointings (or other) mysql db, using account that has 'alter table' privileges
    # connect to the database - this is modular to allow for easier modification from machine/machine
    db = None
    conf_file = os.path.join(os.getenv("HOME"), ".my.cnf")
    if os.path.isfile(conf_file):
        print 'Using connection information from %s' %(conf_file)
        db = mysqldb.connect(read_default_file=conf_file, db=dbname)
    else:
        db = mysqldb.connect(host=hostname, user=username, passwd=passwdname, db=dbname)
    cursor = db.cursor()
    db.autocommit(True)
    return db, cursor

def getDbData(cursor, sql):
    cursor.execute(sql)
    ret = cursor.fetchall()
    return ret

def insertDbData(cursor, sql):
    cursor.execute(sql)

def calc_m5(visitFilter, filtsky, FWHMeff, expTime, airmass, tauCloud=0):
    # Set up expected extinction (kAtm) and m5 normalization values (Cm) for each filter.
    # The Cm values must be changed when telescope and site parameters are updated.
    Cm = {'u':22.32,
          'g':24.01,
          'r':24.13,
          'i':24.08,
          'z':23.97,
          'y':23.55}
    dCm_infinity = {'u':0.56,
                    'g':0.12,
                    'r':0.06,
                    'i':0.05,
                    'z':0.03,
                    'y':0.02}
    kAtm = {'u':0.52,
            'g':0.19,
            'r':0.10,
            'i':0.07,
            'z':0.05,
            'y':0.17}
    # Calculate adjustment if readnoise is significant for exposure time
    # (see overview paper, equation 7)
    T = expTime / 30.0
    dCm = dCm_infinity[visitFilter] - 1.25*np.log10(1 + (10**(0.8*dCm_infinity[visitFilter]) - 1)/T)
    # Calculate fiducial m5
    m5 = (Cm[visitFilter] + dCm + 0.50*(filtsky-21.0) + 2.5*np.log10(0.7/FWHMeff) +
          1.25*np.log10(expTime/30.0) - kAtm[visitFilter]*(airmass-1.2) + 1.1*tauCloud)
    return m5

def create_output_table(cursor, database, hname, sessionID):
    """
    Create summary table.
    """
    # Expected summary table name is -
    summarytable = 'summary_%s_%d' %(hname, sessionID)
    # First check if summary table with expected name exists.
    #  Note that by using the connect_db method above, we are already using the correct database (OpsimDB).
    sql = "show tables like '%s'" %(summarytable)
    results = getDbData(cursor, sql)
    if len(results) > 0:
        # Summary table exists. Stop and ask user to handle this.
        message = []
        message.append("The summary table %s already exists in the MySQL %s database." % (summarytable, database))
        message.append("Please remove the table if you wish to rerun gen_output.py")
        print os.linesep.join(message)
        sys.exit(255)

    # Otherwise, table does not exist and we're good to go.
    print 'Creating summary table %s' %(summarytable)
    sql = 'create table %s (obsHistID int(10) unsigned not null, sessionID int(10) unsigned not null, ' %(summarytable)
    sql += 'propID int(10), fieldID int(10) unsigned not null, fieldRA double, fieldDec double, '
    sql += 'filter varchar(8), expDate int(10) unsigned, expMJD double, night int(10) unsigned, '
    sql += 'visitTime double, visitExpTime double, finRank double, FWHMeff double,  FWHMgeom double, transparency double, '
    sql += 'airmass double, vSkyBright double, filtSkyBrightness double, rotSkyPos double, rotTelPos double, lst double, '
    sql += 'altitude double, azimuth double, dist2Moon double, solarElong double, moonRA double, moonDec double, '
    sql += 'moonAlt double, moonAZ double, moonPhase double, sunAlt double, sunAz double, phaseAngle double, '
    sql += 'rScatter double, mieScatter double, moonIllum double, moonBright double, darkBright double, '
    sql += 'rawSeeing double, wind double, humidity double, slewDist double, slewTime double, fiveSigmaDepth double);'
    ret = getDbData(cursor, sql)

    # Select data from ObsHistory table.
    sql = 'select obsHistID, Session_sessionID as sessionID, Field_fieldID as fieldID, filter, expDate, expMJD, '
    sql += 'night, visitTime, visitExpTime, finRank, finSeeing, transparency, airmass, vSkyBright, '
    sql += 'filtSkyBright as filtSkyBrightness, rotSkyPos, lst, alt as altitude, az as azimuth, dist2Moon, '
    sql += 'solarElong, moonRA, moonDec, moonAlt, moonAZ, moonPhase, sunAlt, sunAz, phaseAngle, rScatter, mieScatter, '
    sql += 'moonIllum, moonBright, darkBright, rawSeeing, wind, humidity from ObsHistory '
    sql += 'where Session_sessionID = %d;' %(sessionID)
    ret = getDbData(cursor, sql)

#    ctioHeight = 2215.;
#    ctioLat = -30.16527778;
#    ctioLon = 70.815;
#    extC = .172;
#    DEG2RAD = 0.0174532925;
#    RAD2DEG = 57.2957795;

    # For each observation, add the relevant additional information from other tables.
    # Note that the summary table is not one-to-one with the ObsHistory table (observations used for multiple proposals
    #  are recorded multiple times into the summary table).
    for k in range(len(ret)):
        obsHistID = ret[k][0]
        fieldID = ret[k][2]
        sql = 'select fieldRA, fieldDec from Field where fieldID = %d' % fieldID
        fld = getDbData(cursor, sql)
        sql = 'select slewTime, slewDist, slewID from SlewHistory where ObsHistory_Session_sessionID = %d and ObsHistory_obsHistID = %d' % (sessionID, obsHistID)
        slw = getDbData(cursor, sql)
        sql = 'select Proposal_propID as propID from ObsHistory_Proposal where ObsHistory_Session_sessionID = %d and ObsHistory_obsHistID = %d' % (sessionID, obsHistID)
        prp = getDbData(cursor, sql)
        sql = 'select rotTelPos from SlewState where SlewHistory_slewID = %d' % slw[0][2]
        rtp = getDbData(cursor, sql)

        for i in range(len(prp)):
            MJD = float(ret[k][5]);
            alt_RAD = float(ret[k][17]);
            az_RAD = float(ret[k][18]);

            moonRA_RAD = float(ret[k][21]);
            moonDec_RAD = float(ret[k][22]);
            lst_RAD = float(ret[k][16]);
            moonha_RAD = lst_RAD - moonRA_RAD;
            malt_RAD = float(ret[k][23]);
            mphase = float(ret[k][25]);
            saz = float(ret[k][27]);
            salt = float(ret[k][26]);
            mphase = np.arccos((mphase/50)-1)*180/np.pi;
            # 5 sigma calculations
            visitFilter = ret[k][3];
            FWHMeff = float(ret[k][10]);
            FWHMgeom = 0.822*FWHMeff + 0.52;
            airmass = float(ret[k][12]);
            filtsky = float(ret[k][14]);
            expTime = float(ret[k][8]);
            tauCloud = 0
            m5 = calc_m5(visitFilter, filtsky, FWHMeff, expTime, airmass, tauCloud)
            sql = 'insert into %s (obsHistID, sessionID, propID, fieldID, fieldRA, fieldDec, filter, ' %(summarytable)
            sql += 'expDate, expMJD, night, visitTime, visitExpTime, finRank, FWHMeff, FWHMgeom, transparency, airmass, vSkyBright, '
            sql += 'filtSkyBrightness, rotSkyPos, rotTelPos, lst, altitude, azimuth, dist2Moon, solarElong, moonRA, moonDec, '
            sql += 'moonAlt, moonAZ, moonPhase, sunAlt, sunAz, phaseAngle, rScatter, mieScatter, moonIllum, '
            sql += 'moonBright, darkBright, rawSeeing, wind, humidity, slewDist, slewTime, fiveSigmaDepth) values '
            sql += '(%d, %d, %d, %d, %f, %f, "%s", %d, %f, %d, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f)' % (ret[k][0], ret[k][1], prp[i][0], ret[k][2], np.radians(fld[0][0]), np.radians(fld[0][1]), ret[k][3], ret[k][4], ret[k][5], ret[k][6], ret[k][7], ret[k][8], ret[k][9], FWHMeff, FWHMgeom, ret[k][11], ret[k][12], ret[k][13], ret[k][14], ret[k][15], rtp[1][0], ret[k][16], ret[k][17], ret[k][18], ret[k][19], ret[k][20], ret[k][21], ret[k][22], ret[k][23], ret[k][24], ret[k][25], ret[k][26], ret[k][27], ret[k][28], ret[k][29], ret[k][30], ret[k][31], ret[k][32], ret[k][33], ret[k][34], ret[k][35], ret[k][36], slw[0][1], slw[0][0], m5)
            insertDbData(cursor, sql)

if __name__ == "__main__":
    import sys
    if len(sys.argv)<4:
        print "Usage : './gen_output.py <realhostname> <databasename> <sessionID>'"
        sys.exit(1)
    hname = sys.argv[1]
    database = sys.argv[2]
    sessionID = sys.argv[3]
    db, cursor = connect_db(dbname=database)
    create_output_table(cursor, database, hname, int(sessionID));
    db.close()
