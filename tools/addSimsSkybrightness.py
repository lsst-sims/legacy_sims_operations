from __future__ import print_function
import sqlite3
import numpy as np
import pandas as pd

from lsst.sims.utils import Site
import lsst.sims.skybrightness as skybrightness

from opsimUtils import calc_m5


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
                           degrees=False)
        mags = skyModel.returnMags()
        sims_skybright[j] = mags[dfi['filter']][0]
    df['sims_skybright'] = sims_skybright
    return sims_skybright

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
    # Add columns if they don't exist
    try:
        query = 'select sims_skybrightness from summary limit 1'
        cur.execute(query)
    except sqlite3.OperationalError:
        query = 'alter table summary add column "sims_skybrightness" real'
        cur.execute(query)
    try:
        query = 'select sims_m5 from summary limit 1'
        cur.execute(query)
    except sqlite3.OperationalError:
        query = 'alter table summary add column "sims_m5" real'
        cur.execute(query)
    # Populate columns.
    for i, row in df.iterrows():
        query = 'update summary set sims_skybrightness = %f, sims_m5 = %f ' \
                'where obsHistID = %d' % (row.sims_skybright, row.sims_m5, row.obsHistID)
        cur.execute(query)
    conn.close()


if __name__ == '__main__':
    dbFile = '/Users/lynnej/opsim/db/minion_1016_sqlite.db'
    print('Reading data')
    df = read_opsim(dbFile)
    print('Adding skybrightness')
    df = add_skybright(df)
    print('Adding new m5')
    df = add_m5(df)
    print('Saving to disk')
    write_opsim(df, dbFile)
