from __future__ import print_function
import sqlite3
import numpy as np
import pandas as pd

import argparse

from lsst.sims.utils import Site
import lsst.sims.skybrightness as skybrightness

from opsimUtils import calc_m5

import time
def dtime(time_prev):
    return (time.time() - time_prev, time.time())



def convert_ecliptic(ra, dec):
    ecinc = np.radians(23.439291)
    x = np.cos(ra) * np.cos(dec)
    y = np.sin(ra) * np.cos(dec)
    z = np.sin(dec)
    xp = x
    yp = np.cos(ecinc) * y + np.sin(ecinc) * z
    zp = -np.sin(ecinc) * y + np.cos(ecinc) * z
    ecLat = np.arcsin(zp)
    ecLon = np.arctan2(yp, xp)
    ecLon = ecLon % (2 * np.pi)
    return ecLat, ecLon


def read_opsim(dbFileName):
    conn = sqlite3.connect(dbFileName)
    # Opsim angles are in radians.
    query = "select obsHistID, fieldRA, fieldDec, altitude, azimuth, expMJD, filter, "
    query += "visitExpTime, FWHMeff, airmass, moonPhase, moonAlt, moonAz, sunAlt, "
    query += "sunAz from summary"
    df = pd.read_sql_query(query, conn)
    conn.close()
    eclipLat, eclipLon = convert_ecliptic(df.fieldRA, df.fieldDec)
    df['eclipLat'] = eclipLat
    df['eclipLon'] = eclipLon
    # Grab LSST longitude/latitude for ra/dec to alt/az conversion.
    telescope = Site('LSST')
    sunEclipLon = np.zeros(len(df))
    for i, row in df.iterrows():
        sunRA, sunDec = skybrightness.stupidFast_altAz2RaDec([row['sunAlt']], [row['sunAz']],
                                                             telescope.latitude_rad,
                                                             telescope.longitude_rad, row['expMJD'])
        sunEclLat, sunEclipLon[i] = convert_ecliptic(sunRA[0], sunDec[0])
    df['sunEclipLon'] = sunEclipLon
    return df


def add_skybright(df):
    skyModel = skybrightness.SkyModel(mags=True)
    sims_skybright = np.zeros(len(df), float)
    t = time.time()
    for i, dfi in df.iterrows():
        airmass = dfi.airmass
        alts = dfi.altitude
        # Fake the airmass if we're over the limit.
        if airmass > skyModel.airmassLimit:
            airmass = skyModel.airmassLimit - 0.1
            alts = np.pi/2.-np.arccos(1./airmass)
        skyModel.setParams(airmass=np.array([airmass]), azs=np.array([dfi.azimuth]),
                           alts=np.array([alts]),
                           moonPhase=dfi.moonPhase, moonAlt=dfi.moonAlt,
                           moonAz=dfi.moonAZ, sunAlt=dfi.sunAlt, sunAz=dfi.sunAz,
                           sunEclipLon=dfi.sunEclipLon, eclipLon=np.array([dfi.eclipLon]),
                           eclipLat=np.array([dfi.eclipLat]),
                           degrees=False, filterNames=[dfi['filter']])
        mags = skyModel.returnMags()
        sims_skybright[i] = mags[dfi['filter']][0]
    dt, t = dtime(t)
    print('%f seconds to calculate %d skybrightnesses' % (dt, i))
    df['sims_skybright'] = sims_skybright
    return df


def add_m5(df):
    m5 = np.zeros(len(df))
    for f in df['filter'].unique():
        match = np.where(df['filter'] == f)
        m5[match] = calc_m5(f, df.sims_skybright.as_matrix()[match], df.FWHMeff.as_matrix()[match],
                            df.visitExpTime.as_matrix()[match], df.airmass.as_matrix()[match])
    df['sims_m5'] = m5
    return df


def write_opsim(df, dbFileName):
    # Could have written data back to sqlite using pandas, to_sql, but it's not clear if that would
    # let me insert just the additional columns.
    conn = sqlite3.connect(dbFileName)
    cur = conn.cursor()
    # Add index on obsHistID
    query = 'create index obsHistID_idx on summary(obsHistID)'
    cur.execute(query)
    conn.commit()
    # Replace filtSkyBrightness and fiveSigmaDepth values with new values.
    # First set columns to NULL so we know if we failed at some point.
    query = "update summary set filtSkyBrightness='NULL', fiveSigmaDepth='NULL'"
    cur.execute(query)
    # Populate columns with new values.
    for i, row in df.iterrows():
        query = 'update summary set filtSkyBrightness = %f, fiveSigmaDepth = %f ' \
                'where obsHistID = %d' % (row.sims_skybright, row.sims_m5, row.obsHistID)
        cur.execute(query)
    conn.commit()
    # Find the session id, then add a comment about updating the sky brightness.
    query = 'select sessionID from Session'
    cur.execute(query)
    res = cur.fetchall()
    sessionID = int(res[0])
    query = "insert into Config (moduleName, paramIndex, paramName, paramValue, comment, Session_sessionID, nonPropID) values"
    query += "('Comment', 1, 'SkyBrightness', 'sims_skybrightness', '', sessionID, '0');"
    cur.execute(query)
    conn.commit()
    conn.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Replace filtSkyBrightness and fiveSigmaDepth with values based on sims_skybrightness')
    parser.add_argument('dbFile', type=str, default=None, help='full file path to the opsim sqlite file')
    parser.set_defaults()
    args = parser.parse_args()

    print('Reading data')
    df = read_opsim(args.dbFile)
    print('Adding skybrightness - this could take a while')
    df = add_skybright(df)
    print('Adding new m5')
    df = add_m5(df)
    print('Saving to disk')
    write_opsim(df, args.dbFile)
