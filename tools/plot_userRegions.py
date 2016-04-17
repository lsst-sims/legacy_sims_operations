import os
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
# To plot the output
import lsst.sims.maf.slicers as slicers
import lsst.sims.maf.plots as plots


def readUserRegions(confFile):
    fieldRA = []
    fieldDec = []
    with open(confFile, 'r') as f:
        for line in f:
            vals = line.split()
            if len(vals) > 0:
                if vals[0] == 'userRegion':
                    ra, dec, _ = vals[2].split(',')
                    fieldRA.append(ra)
                    fieldDec.append(dec)
    fieldRA = np.array(fieldRA, dtype=float)
    fieldDec = np.array(fieldDec, dtype=float)
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
    # Find the proposal configuration files in the current directory.
    tmp = os.listdir('.')
    propConfs = []
    for t in tmp:
        if t.endswith('.conf'):
            propConfs.append(t)

    print "Found configuration files %s - will check for user regions." % propConfs

    fieldRA = {}
    fieldDec = {}
    for prop in propConfs:
        ra, dec = readUserRegions(prop)
        if len(ra) > 0:
            fieldRA[prop] = ra
            fieldDec[prop] = dec

    # Check their locations on a plot.
    plotFields(fieldRA, fieldDec)
