import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import ephem
from lsst.sims.utils import galacticFromEquatorial
from lsst.sims.maf.db import OpsimDatabase
# To plot the output (for a visual check)
import lsst.sims.maf.slicers as slicers
import lsst.sims.maf.plots as plots


def queryFields(database):
    # Read the fields from the field table in the database.
    opsdb = OpsimDatabase(database)
    fields = opsdb.fetchFieldsFromFieldTable()
    # Add galactic and equatorial values to these field locations.
    gall, galb = galacticFromEquatorial(fields['fieldRA'], fields['fieldDec'])
    ecll = np.zeros(len(gall), float)
    eclb = np.zeros(len(galb), float)
    for i, (ra, dec) in enumerate(zip(fields['fieldRA'], fields['fieldDec'])):
        coord = ephem.Equatorial(ra, dec, epoch=2000)
        ecl = ephem.Ecliptic(coord)
        ecll[i] = ecl.lon
        eclb[i] = ecl.lat
    newfields = np.empty((len(gall)), dtype=[('ra', float), ('dec', float),
                                     ('galL', float), ('galB', float),
                                     ('eclL', float), ('eclB', float)])
    newfields['ra'] = fields['fieldRA']
    newfields['dec'] = fields['fieldDec']
    newfields['galL'] = gall
    newfields['galB'] = galb
    newfields['eclL'] = ecll
    newfields['eclB'] = eclb
    return newfields

def findOpsimFieldIDs(fields, region, minLon, maxLon, minLat, maxLat):
    if minLat >= maxLat:
        print "MinLat >= maxLat.. I'm going to swap them."
        print "  (sorry, this means you can only specify contiguous bands of latitude)."
        print ".. unless you do a numpy.where thing on your own! (perfectly fine)."
        tmp = minLat
        minLat = maxLat
        maxLat = tmp
        print "min/max latitudes are now %f/%f radians" % (minLat, maxLat)
    # Test specification of region.
    possible_regions = ['equatorial', 'galactic', 'ecliptic']
    if region not in possible_regions:
        raise ValueError('region can be one of %s (was passed %s)' % (possible_regions, region))
    # Identify the fields which are within "region"
    if region == 'equatorial':
        fieldsLon = fields['ra']
        fieldsLat = fields['dec']
    elif region == 'galactic':
        fieldsLon = fields['galL']
        fieldsLat = fields['galB']
    elif region == 'ecliptic':
        fieldsLon = fields['eclL']
        fieldsLat = fields['eclB']
    print np.degrees(minLon), np.degrees(maxLon), np.degrees(minLat), np.degrees(maxLat)
    fieldsLon = fieldsLon - minLon
    fieldsLon = fieldsLon % (np.pi * 2.)
    match = np.where((fieldsLon >= 0) & (fieldsLon <= (maxLon - minLon) % (np.pi*2.)) &
                     (fieldsLat >= minLat) & (fieldsLat <= maxLat))
    return match


def plotFields(fields, match):
    slicer = slicers.OpsimFieldSlicer()
    # Modify slicer so we can use it for plotting.
    slicer.slicePoints['ra'] = fields['ra']
    slicer.slicePoints['dec'] = fields['dec']
    fieldLocs = ma.MaskedArray(data=np.zeros(len(fields['ra']), float),
                               mask=np.ones(len(fields['ra']), int),
                               fill_value=-99)
    fieldLocs.data[match] = 1.0
    fieldLocs.mask[match] = 0
    skymap = plots.BaseSkyMap()
    skymap(fieldLocs, slicer, {'colorMin': 0, 'colorMax': 1, 'xlabel': 'Field Locations'})
    plt.show()


if __name__ == "__main__":

    fields = queryFields('enigma_1189_sqlite.db')

    # Edit this section to change the field selection.
    # This would select a region around the ecliptic, and ~WFD
    match = findOpsimFieldIDs(fields, 'ecliptic',
                              np.radians(0), np.radians(359.99),
                              np.radians(-12), np.radians(12))
    match2 = findOpsimFieldIDs(fields, 'equatorial',
                               np.radians(0), np.radians(359.99),
                               np.radians(-62.1), np.radians(2.7))
    # Join together any multiple selections made above
    match = np.concatenate([match[0], match2[0]])
    match = np.unique(match)
    # Check their locations on a plot.
    plotFields(fields, match)

    # Or - another example - just pull out the fields you want here.
    # This will select band around ecliptic, and ranging down to top of WFD.
    match = np.where((fields['eclB'] <= np.radians(15)) &
                     ((fields['eclB'] >= np.radians(-15)) |
                      (fields['dec'] >= np.radians(2.7))))
    plotFields(fields, match)

    # Potentially, add an offset to each user region.
    offset = 0.00
    # And write them to the screen.
    for f in fields[match]:
        print 'userRegion = %.2f,%.2f,%.2f' % (np.degrees(f['ra']),
                                               np.degrees(f['dec'])+offset, 0.03)
