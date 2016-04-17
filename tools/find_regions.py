import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import ephem
from lsst.sims.utils import galacticFromEquatorial, haversine
from lsst.sims.maf.db import OpsimDatabase
# To plot the output (for a visual check -- not needed after testing).
import lsst.sims.maf.slicers as slicers
import lsst.sims.maf.plots as plots


def queryFields(database):
    # Read the fields from the field table in the database.
    opsdb = OpsimDatabase(database)
    fields = opsdb.fetchFieldsFromFieldTable()
    return fields

def findOpsimFieldIDs(fields, region, minLon, maxLon, minLat, maxLat):
    if minLat >= maxLat:
        print "MinLat >= maxLat.. I'm going to swap them. (sorry, this means you can only specify contiguous bands of latitude)."
        tmp = minLat
        minLat = maxLat
        maxLat = tmp
        print "min/max latitudes are now %f/%f radians" %(minLat, maxLat)
    # Test specification of region.
    possible_regions = ['equatorial', 'galactic', 'ecliptic']
    if region not in possible_regions:
        raise ValueError('region can be one of %s (was passed %s)' %(possible_regions, region))
    # 'region' is specified by a min/max parameter for longitude/ra latitude/dec.
    # Convert the field ra/dec values into galactic and ecliptic coordinates.
    gall, galb = galacticFromEquatorial(fields['fieldRA'], fields['fieldDec'])
    ecll = np.zeros(len(gall), float)
    eclb = np.zeros(len(galb), float)
    for i, (ra, dec) in enumerate(zip(fields['fieldRA'], fields['fieldDec'])):
        coord = ephem.Equatorial(ra, dec, epoch=2000)
        ecl = ephem.Ecliptic(coord)
        ecll[i] = ecl.lon
        eclb[i] = ecl.lat
    # Identify the fields which are within "region"
    if region == 'equatorial':
        fieldsLon = fields['fieldRA']
        fieldsLat = fields['fieldDec']
    elif region == 'galactic':
        fieldsLon = gall
        fieldsLat = galb
    elif region == 'ecliptic':
        fieldsLon = ecll
        fieldsLat = eclb
    print np.degrees(minLon), np.degrees(maxLon), np.degrees(minLat), np.degrees(maxLat)
    fieldsLon = fieldsLon - minLon
    fieldsLon = fieldsLon % (np.pi*2.)
    match = np.where((fieldsLon >= 0) & (fieldsLon <= (maxLon - minLon) % (np.pi*2.)) & (fieldsLat >= minLat) & (fieldsLat <= maxLat))

    return match


def plotFields(fields, match):
    slicer = slicers.OpsimFieldSlicer()
    # Modify slicer so we can use it for plotting.
    slicer.slicePoints['ra'] = fields['fieldRA']
    slicer.slicePoints['dec'] = fields['fieldDec']
    fieldLocs = ma.MaskedArray(data = np.zeros(len(fields['fieldRA']), float),
                               mask = np.ones(len(fields['fieldRA']), int),
                               fill_value=-99)
    fieldLocs.data[match] = 1.0
    fieldLocs.mask[match] = 0
    skymap = plots.BaseSkyMap()
    fignum = skymap(fieldLocs, slicer,
                    {'colorMin':0, 'colorMax':1, 'xlabel':'Field Locations'})
    plt.show()


if __name__ == "__main__":

    fields = queryFields('enigma_1189_sqlite.db')
    # Edit this section to change the field selection.
    match = findOpsimFieldIDs(fields, 'ecliptic',
                              np.radians(0), np.radians(359.99),
                              np.radians(-30), np.radians(12))
    match2 = findOpsimFieldIDs(fields, 'equatorial',
                               np.radians(0), np.radians(359.99),
                               np.radians(-90), 0)
    # Join together any multiple selections made above
    match = np.concatenate([match[0], match2[0]])
    match = np.unique(match)

    # Check their locations on a plot.
    plotFields(fields, match)

    # Add an offset to each reported user region so that opsim doesn't crash.
    offset = 0.01
    # And write them to the screen.
    for f in fields[match]:
        print 'userRegion = %.2f,%.2f,%.2f' %(np.degrees(f['fieldRA']), np.degrees(f['fieldDec'])+offset, 0.03)
    for f in fields[match2]:
        print 'userRegion = %.2f,%.2f,%.2f' %(np.degrees(f['fieldRA']), np.degrees(f['fieldDec'])+offset, 0.03)
