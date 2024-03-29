import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from lsst.sims.utils import m5_flat_sed

# Convert at least some older run sqlite outputs into new format sqlite outputs (for MAF)


def calc_night(expMJD, minexpMJD):
    local_midnight = 0.16
    const = minexpMJD + local_midnight - 0.5
    night = np.floor(expMJD - const)
    return night

def read_data(filename):
    data = pd.read_table(filename)
    return data

def convert_cols(data):
    cols_need = ['obsHistID', 'sessionID', 'propID', 'fieldID', 'fieldRA', 'fieldDec', 'filter',
                 'expDate', 'expMJD', 'night', 'visitTime', 'visitExpTime', 'finRank', 'finSeeing',
                 'transparency', 'airmass', 'vSkyBright', 'filtSkyBrightness', 'rotSkyPos', 'rotTelPos',
                 'lst', 'altitude', 'azimuth', 'dist2Moon', 'solarElong',
                 'moonRA', 'moonDec', 'moonAlt', 'moonAZ', 'moonPhase', 'sunAlt', 'sunAz', 'phaseAngle',
                 'rScatter', 'mieScatter', 'moonIllum', 'moonBright', 'darkBright', 'rawSeeing', 'wind',
                 'humidity', 'slewDist', 'slewTime', 'fiveSigmaDepth', 'ditheredRA', 'ditheredDec']
    cols_have = []
    for k in data:
        cols_have.append(k)
    cols_map = {'ditheredRA':'hexdithra', 'ditheredDec':'hexdithdec', 'visitTime':'expTime',
                'vSkyBright':'VskyBright', 'filtSkyBrightness':'filtSky', 'finSeeing':'seeing',
                'transparency':'xparency' }
    cols_map_backup = {'ditheredRA':-99, 'ditheredDec':-99}
    cols_default = {'visitExpTime':30.0, 'solarElong':-99, 'wind':-99, 'humidity':-99, 'moonAZ':-99}
    cols_calc = {'fiveSigmaDepth':m5_flat_sed, 'night':calc_night}

    print "Needed but not present or translated."
    for c in cols_need:
        if c not in cols_have and c not in cols_default and c not in cols_calc:
            if c in cols_map:
                if cols_map[c] not in cols_have:
                    if c not in cols_map_backup:
                        print c
            else:
                print c
    print "Present, but not in needed list. "
    for k in cols_have:
        if k not in cols_need:
            print k

    nvisits = len(data)
    data2 = {}
    for c in cols_need:
        if c in cols_have:
            data2[c] = data[c]
        elif c in cols_map:
            if cols_map[c] not in data and c in cols_map_backup:
                data2[c] = np.ones(nvisits,float) * cols_map_backup[c]
            else:
                data2[c] = data[cols_map[c]]
        elif c in cols_default:
            data2[c] = np.ones(nvisits, float) * cols_default[c]
        elif c in cols_calc:
            if c == 'fiveSigmaDepth':
                data2[c] = np.zeros(nvisits, float)
                for index, v in data.iterrows():
                    data2[c][index] = m5_flat_sed(v['filter'], v['filtSky'], v['seeing'],
                                               v['expTime']-4.0, v['airmass'])
            elif c == 'night':
                data2[c] = calc_night(data['expMJD'], int(data['expMJD'].min()))
    data2 = pd.DataFrame(data2)
    return data2


if __name__ == '__main__':
    #data = read_data('opsim3_61_output.dat')
    data = read_data('opsim2_168_output.dat')
    data2 = convert_cols(data)
    print data2.keys()
    #engine = create_engine('sqlite:///opsim3_61_sqlite.db')
    engine = create_engine('sqlite:///opsim2_168_sqlite.db')
    data2.to_sql('summary', engine, index=False)
    
