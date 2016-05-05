import os
import argparse
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
# To plot the output
import lsst.sims.maf.slicers as slicers
import lsst.sims.maf.plots as plots
import lsst.sims.utils as simsUtils

def readUserRegions(confFile, useExclusions=True):
    fieldRA = []
    fieldDec = []
    peakL = 25.
    taperL = 5
    taperB = 180.
    maxReach = 80.
    maxAirmass = 10.
    with open(confFile, 'r') as f:
        for line in f:
            vals = line.split()
            if len(vals) > 0:
                if vals[0] == 'userRegion':
                    ra, dec, _ = vals[2].split(',')
                    fieldRA.append(ra)
                    fieldDec.append(dec)
                elif vals[0] == 'taperL':
                    taperL = float(vals[2])
                elif vals[0] == 'taperB':
                    taperB = float(vals[2])
                elif vals[0] == 'peakL':
                    peakL = float(vals[2])
                elif vals[0] == 'maxReach':
                    maxReach = float(vals[2])
                elif vals[0] == 'MaxAirmass':
                    maxAirmass = float(vals[2])
    #print confFile, taperL, taperB, peakL, maxReach, maxAirmass
    fieldRA = np.array(fieldRA, dtype=float)
    fieldDec = np.array(fieldDec, dtype=float)
    if useExclusions:
        # Remove fields that would be excluded based on declimit from 'maxReach' and 'maxAirmass'.
        latLimit = np.degrees(np.arccos(1. / maxAirmass))
        site = simsUtils.Site(name='LSST')
        latSite = site.latitude
        minDec = np.max([latSite - latLimit, -1 * np.abs(maxReach)])
        maxDec = np.min([latSite + latLimit, np.abs(maxReach)])
        condition = np.where((minDec < fieldDec) & (fieldDec < maxDec))
        print confFile, minDec, maxDec
        fieldRA = fieldRA[condition]
        fieldDec = fieldDec[condition]
        # Remove fields that would be excluded by galactic exclusion zone.
        # (there are other limits that could come in due to airmass, but we won't deal with them here .. for now).
        galL, galB = simsUtils.galacticFromEquatorial(fieldRA, fieldDec)
        band = peakL - taperL
        if taperL != 0 and taperB != 0:
            condition = np.where((galL < 180.) & (np.abs(galB) > (peakL - (band * np.abs(galL) / taperB))))
            condition2 = np.where((galL > 180.) & (np.abs(galB) > (peakL - (band * np.abs(galL - 360.) / taperB))))
            fieldRA = np.concatenate([fieldRA[condition], fieldRA[condition2]])
            fieldDec = np.concatenate([fieldDec[condition], fieldDec[condition2]])
    return fieldRA, fieldDec


def plotFields(fieldRA, fieldDec):
    slicer = slicers.OpsimFieldSlicer()
    fignum = None
    colorlist = [[1, 0, 0], [1, 1, 0], [0, 1, 0], [0, .25, .5],
                 [.5, 0, .5], [0, 0, 0], [.5, .5, 1]]
    ci = 0
    colors = {}
    for prop in fieldRA:
        # Modify slicer so we can use it for plotting.
        slicer.slicePoints['ra'] = np.radians(fieldRA[prop])
        slicer.slicePoints['dec'] = np.radians(fieldDec[prop])
        fieldLocs = ma.MaskedArray(data=np.empty(len(fieldRA[prop]), object),
                                   mask=np.zeros(len(fieldRA[prop]), bool),
                                   fill_value=-99)
        colors[prop] = [colorlist[ci][0], colorlist[ci][1], colorlist[ci][2], 0.4]
        ci += 1
        if ci == len(colorlist):
            ci = 0
        for i in xrange(len(fieldRA[prop])):
            fieldLocs.data[i] = colors[prop]
        skymap = plots.BaseSkyMap()
        fignum = skymap(fieldLocs, slicer,
                        {'metricIsColor': True, 'bgcolor': 'lightgray', 'raCen': 0},
                        fignum=fignum)
    plt.figure(fignum)
    labelcolors = []
    labeltext = []
    for prop in fieldRA:
        el = Ellipse((0, 0), 0.03, 0.03,
                     fc=(colors[prop][0], colors[prop][1], colors[prop][2]),
                     alpha=colors[prop][3])
        labelcolors.append(el)
        labeltext.append(prop.rstrip('.conf'))
    plt.legend(labelcolors, labeltext, loc=(0.85, 0.9), fontsize='smaller')
    plt.show()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Python script to plot the expected footprint of a survey, based on the configuration files."
                                     " Uses the userRegions in each configuration file, combined with the expected exclusions due to"
                                     " galactic exclusions (taperL, taperB, peakL) and airmass constraints (MaxAirmass) or dec hard limits"
                                     " (MaxReach). \n"
                                     "This doesn't fetch the field tesselation from the Field table, so essentially is assuming that "
                                     "the user regions are already coming from this tesselation (that there is a field at or near the "
                                     "userRegion location.")
    parser.add_argument('--confFile', type=str, default=None, help='Plot the expected footprint for this single configuration file.'
                        ' If None (default), then plots footprints for all configuration files in the directory.')
    parser.add_argument('--skipExclusions', dest='skipExclusions', action='store_true', default=False,
                        help="Don't add the exclusions based on MaxReach, MaxAirmass, or the galactic exclusion zones.")
    parser.set_defaults()
    args = parser.parse_args()

    if args.confFile is None:
        # Find the proposal configuration files in the current directory.
        tmp = os.listdir('.')
        propConfs = []
        for t in tmp:
            if t.endswith('.conf'):
                propConfs.append(t)

        print "Found configuration files %s - will check for user regions and limit parameters." % propConfs

    else:
        propConfs = [args.confFile]
        print "Will read configuration file %s." % propConfs

    fieldRA = {}
    fieldDec = {}
    for prop in propConfs:
        ra, dec = readUserRegions(prop, args.skipExclusions)
        if len(ra) > 0:
            fieldRA[prop] = ra
            fieldDec[prop] = dec

    # Check their locations on a plot.
    plotFields(fieldRA, fieldDec)
