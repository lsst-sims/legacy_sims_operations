import os
import numpy as np
import MySQLdb as mysqldb

def connect_db(hostname='localhost', username='www', passwdname='zxcvbnm', dbname='LSST'):
    # connect to lsst_pointings (or other) mysql db, using account that has 'alter table' privileges
    # connect to the database - this is modular to allow for easier modification from machine/machine
    db = None
    conf_file = os.path.join(os.getenv("HOME"), ".my.cnf")
    if os.path.isfile(conf_file):
        db = mysqldb.connect(read_default_file=conf_file, db=dbname)
    else:
        db = mysqldb.connect(host=hostname, user=username, passwd=passwdname, db=dbname)
    cursor = db.cursor()
    return cursor

def add_indexes(database, simname):
    ## adds some useful indexes for calculating values from opsim
    # set up a dictionary to hold the index info
    index_done = {}
    indexlist = ("fieldID", "expMJD", "filter", "fieldRA", "fieldDec", "fieldRADec", "night", "rotTelPos")
    for ind in indexlist:
        index_done[ind] = False
    # connect to the db
    cursor = connect_db(dbname=database)
    # check for existing indexes
    sqlquery = "show indexes from %s" %(simname)
    cursor.execute(sqlquery)
    results = cursor.fetchall()
    # do some testing to see if index (solely on this item) exists
    for result in results:
        if (result[3]==1):   # this is a first part of an index
            if result[4] in index_done.keys(): # is this index one of the ones we're looking for?
                index_done[result[4]] = True
        # fieldRA and dec more complicated, as secondary (both) index too
        elif (result[3]==2):
            if result[4] == "fieldDec":
                index_done["fieldRADec"] = True
    #print index_done
    for ind in indexlist:
        if (index_done[ind]):
            print "Already have an index on %s - skipping" %(ind)
        else:
            print "Adding index for %s" %(ind)
            sqlquery = "create index %s_idx on %s(%s)" %(ind, simname, ind)
            if ind == 'fieldRADec':
                sqlquery = "create index %s_idx on %s(fieldRA, fieldDec)" %(ind, simname)
            print sqlquery
            cursor.execute(sqlquery)
    # general format for index is columnname_idx
    # will create night index when add night information
    # also will add hexdith* indexes when add dither information
    print "Done adding indexes"
    cursor.close()



def remove_dither(simname, dithType, dropdatacol=False):
    """
    Remove the indices (and possibly the data) for the added columns of the specified dither type.

    Required inputs
    ---------------
    * simname
    * dithType: str: either 'hex' (for translational hex dithers) or
                            'random' (for transalational random dithers) or
                            'rot' (for random rotational dithers).
    Optional input
    --------------
    * dropdatacol: bool: set to True if want to drop the data.
                         Default: False

    """
    if (dithType=='hex'):
        newcols = ['hexDitherPerNightRA', 'hexDitherPerNightDec']
    elif (dithType=='random'):
        newcols = ['randomDitherFieldPerVisitRA', 'randomDitherFieldPerVisitDec']
    elif (dithType== 'rot'):
        newcols = ['ditheredRotTelPos']
    else:
        raise ValueError("Incorrect dithType: it should be either 'hex' or 'random' or 'rot'.")

    print "Removing existing dithering indexes and columns for %s dithers." % (dithType)
    cursor = connect_db()

    if (len(newcols)>1):   # translational dithers add two columns: RA, Dec
        for col in newcols:
            sqlquery = "drop index %s_idx on %s" % (col, simname)
            cursor.execute(sqlquery)
        sqlquery = "drop index %sDec_idx on %s" % (newcols[0], simname) #RADec_idx)
        cursor.execute(sqlquery)
        if dropdatacol:
            print "Removed indexes - now will remove columns for the dithered RA/dec."
            sqlquery = "alter table %s drop column %s, drop column %s" % (simname, newcols[0], newcols[1])
            cursor.execute(sqlquery)
    else:   # rotational dithers add only one column.
        sqlquery = "drop index %s_idx on %s" % (newcols[0], simname)
        cursor.execute(sqlquery)
        if dropdatacol:
            print "Removed indexes - now will remove columns for the dithered rotational angle."
            sqlquery = "alter table %s drop column %s" %(simname, newcols[0])
            cursor.execute(sqlquery)
    cursor.close()
    return

def offsetHex():
    """
    Returns translational hex dither offsets (217 points) in radians.

    """
    # some constants for the dithering
    fov = 3.5
    # set values associated with dithering
    dith_level = 4
    # number of rows in dither pattern
    # number of vertices in longest row is the same.
    nrows = 2**dith_level
    halfrows = int(nrows / 2)  # useful for counting from 0 at center
    # calculate size of each offset
    dith_size_x = fov  / (nrows)
    dith_size_y = np.sqrt(3) * fov / 2.0 / (nrows)  #sqrt 3 comes from hexagon
    # calculate the row identification number, going from 0 at center
    nid_row = np.arange(-halfrows, halfrows + 1, 1)
    # and calculate the number of vertices in each row
    vert_in_row = np.arange(-halfrows, halfrows+1, 1)
    total_vert = 0
    offsets = []
    for i in range(-halfrows, halfrows+1, 1):
        vert_in_row[i] = (nrows+1) - abs(nid_row[i])
        total_vert += vert_in_row[i]
    vertex_count = 0
    for i in range(0, nrows+1, 1):
        for j in range(0, vert_in_row[i], 1):
            # calculate displacement
            x_off = np.radians(dith_size_x * (j - (vert_in_row[i]-1)/2.0))
            y_off = np.radians(dith_size_y * nid_row[i])
            offsets.append([x_off, y_off])
            vertex_count += 1
    return offsets

def inHexagon(xOff, yOff, maxDither):
    """
    Identify dither offsets which fall within the inscribed hexagon.
    Parameters
    ----------
    xOff : numpy.ndarray
        The x values of the dither offsets.
    yoff : numpy.ndarray
        The y values of the dither offsets.
    maxDither : float
        The maximum dither offset.
    Returns
    -------
    numpy.ndarray
        Indexes of the offsets which are within the hexagon inscribed inside the 'maxDither' radius circle.
    """
    # Set up the hexagon limits.
    #  y = mx + b, 2h is the height.
    m = np.sqrt(3.0)
    b = m * maxDither
    h = m / 2.0 * maxDither
    # Identify offsets inside hexagon.
    inside = np.where((yOff < m * xOff + b) &
                      (yOff > m * xOff - b) &
                      (yOff < -m * xOff + b) &
                      (yOff > -m * xOff - b) &
                      (yOff < h) & (yOff > -h))[0]
    return inside


def offsetRandom(noffsets, inHex=True):
    """
    Returns translational random dither offsets in radians.

    Required input
    --------------
    * noffsets: int: number of offsets needed.

    Optional input
    --------------
    * inHex: bool: set to False if dont want to restrict the dithers to within
                   the hexagon inscribing the FOV. Default: True

    """
    # some constants for the dithering
    fov = 3.5
    maxDither= fov/2.
    # modified version of _generateRandomOffsets function private to RandomDitherFieldPerVisitStacker
    # in lsst.sims.maf.stackers.
    xOut = np.array([], float)
    yOut = np.array([], float)
    maxTries = 100
    tries = 0
    while (len(xOut) < noffsets) and (tries < maxTries):
        dithersRad = np.sqrt(np.random.rand(noffsets * 2)) * maxDither
        dithersTheta = np.random.rand(noffsets * 2) * np.pi * 2.0
        xOff = dithersRad * np.cos(dithersTheta)
        yOff = dithersRad * np.sin(dithersTheta)
        if inHex:
            # Constrain dither offsets to be within hexagon.
            idx = inHexagon(xOff, yOff, maxDither)
            xOff = xOff[idx]
            yOff = yOff[idx]
        xOut = np.concatenate([xOut, xOff])
        yOut = np.concatenate([yOut, yOff])
        tries += 1
    if len(xOut) < noffsets:
        raise ValueError('Could not find enough random points within the hexagon in %d tries. '
                         'Try another random seed?' % (maxTries))
    xOff = xOut[0:noffsets]
    yOff = yOut[0:noffsets]
    return zip(np.radians(xOff),np.radians(yOff))

def add_translationalDither(database, simname, dithType, overwrite=True):
    """
    Adds translational dither columns to the database. Two options:
        1. HexDither: Krughoff-Jones dithering pattern: dither offsets form a 217 point lattice.
                      Dithers are implemented on PerNight timescale.
                      Columns added: hexDitherPerNightRA, hexDitherPerNightDec
        2. RandomDither: random dithers within the hexagon inscribing the circular FOV.
                         Dithers are implemented on FieldPerVisit timescale.
                         Columns added: randomDitherFieldPerVisitRA, randomDitherFieldPerVisitDec

    Required inputs
    ---------------
    * database
    * simname
    * dithType: str: either 'hex' or 'random': specifies the kind of dither column to add.

    Optional input
    --------------
    * overwrite: bool: set to False if don't want to overwrite the columns if they exist.
                       Default: True

    """
    ## adds three columns (<dithType>Dither<timescale>RA, <dithType>Dither<timescale>Dec, and vertex) and indexes
    # first check to ensure correct dithType is requested.
    if (dithType=='hex'):
        dithcols = ['hexDitherPerNightRA', 'hexDitherPerNightDec']
    elif (dithType=='random'):
        dithcols = ['randomDitherFieldPerVisitRA', 'randomDitherFieldPerVisitDec']
    else:
        raise ValueError("Incorrect dithType: it should be either 'hex' or 'random'.")
    # connect to the database
    cursor =  connect_db(dbname=database)
    # check if dither columns exist
    sqlquery = "describe %s" % (simname)
    cursor.execute(sqlquery)
    sqlresults = cursor.fetchall()
    newcols = list(dithcols)
    for result in sqlresults:
        if (result[0] in newcols):
            newcols.remove(result[0])
            if overwrite:
                print '%s column already exists, but will overwrite.' %(result[0])
            else:
                print "%s column already exists - skipping adding %s dithering" %(result[0], dithType)
                return
    if len(newcols) > 0:
        print 'Adding new dither columns %s' % (dithcols)
        for n in newcols:
            # add columns for dithering
            sqlquery = 'alter table %s add %s double' % (simname, n)
            cursor.execute(sqlquery)
    # Drop the indexes, if they exist.
    for col in dithcols:
        sqlquery = "drop index %s_idx on %s" % (col, simname)
        try:
            cursor.execute(sqlquery)
        except mysqldb.OperationalError as e:
            pass
    sqlquery = "drop index %sDec_idx on %s" % (dithcols[0], simname)
    try:
        cursor.execute(sqlquery)
    except mysqldb.OperationalError as e:
        pass
    # Now add the values.
    # find the right offsets.
    if (dithType=='hex'):
        # want to change vertex on per night basis, so pull all night values from db
        sqlquery = "select distinct(night) from %s" % (simname)
        cursor.execute(sqlquery)
        sqlresults = cursor.fetchall()
        # go through each night individually
        offsets = offsetHex()
    else:   # already have checked that dithType is either 'hex' or 'random'
        # want to change vertex on per visit basis
        # get the obsHistID to track each visit.
        sqlquery = "select distinct(obsHistID) from %s" % (simname)
        cursor.execute(sqlquery)
        sqlresults = cursor.fetchall()
        offsets = offsetRandom(noffsets=len(sqlresults), inHex=True)

    for index, result in enumerate(sqlresults):
        if (dithType=='hex'):
            night = int(result[0])
            vertex = night % len(offsets) # implement hexDither on PerNight timescale.
        else: # already have checked that dithType is either 'hex' or 'random'
            obsHistID = int(result[0])
            vertex = index  # implement random dither on FieldPerNight timescale.
        x_off, y_off = offsets[vertex]
        #It doesn't make a ton of sense, but see http://bugs.mysql.com/bug.php?id=1665 for a discussion of the mysql modulus convention.
        #In the case where a mod can return a negative value (((N%M)+M)%M) will return what one would expect.
        if (dithType=='hex'):
            sqlquery = "update %s set %s = ((((fieldra+(%f/cos(fielddec)))%%(2*PI()))+(2*PI()))%%(2*PI())), " % (simname, dithcols[0], x_off)
            sqlquery += "%s = if(abs(fielddec + %f) > 90, fielddec  - %f, fielddec + %f) where night = %i" %(dithcols[1],
                                                                                                             y_off, y_off, y_off, night)
        else:
            sqlquery = "update %s set %s = ((((fieldra+(%f/cos(fielddec)))%%(2*PI()))+(2*PI()))%%(2*PI())), " % (simname, dithcols[0], x_off)
            sqlquery += "%s = if(abs(fielddec + %f) > 90, fielddec  - %f, fielddec + %f) where obsHistID = %i" %(dithcols[1], y_off,
                                                                                                                   y_off, y_off, obsHistID)
        cursor.execute(sqlquery)

    # This happens occasionally due to rounding errors, but if outside -PI/2 -- PI/2 reflect to the proper bounds.
    sqlquery = "update %s set %s = -PI()/2. - (((%s%%(-PI()/2)) + (-PI()/2.))%%(-PI()/2.)) where %s < -PI()/2" % (simname, dithcols[1],
                                                                                                                   dithcols[1], dithcols[1])
    cursor.execute(sqlquery)
    sqlquery = "update %s set %s = PI()/2. - (((%s%%(PI()/2)) + (PI()/2.))%%(PI()/2.)) where %s > PI()/2" % (simname, dithcols[1], dithcols[1],
                                                                                                             dithcols[1])
    cursor.execute(sqlquery)
    # add indexes
    print "Adding dithering indexes"
    for col in dithcols:
        sqlquery = "create INDEX %s_idx ON %s(%s)" % (col, simname, col)
        cursor.execute(sqlquery)
    sqlquery = "create INDEX %sDec_idx ON %s(%s, %s)" %(dithcols[0], simname, dithcols[0], dithcols[1])
    cursor.execute(sqlquery)
    cursor.close()

def add_rotationalDither(database, simname, overwrite=True):
    """
    Adds a rotational dither column to the database (called ditheredRotTelPos).

    Dither stategy: random offset between +/-(pi/2) radians after every filter change.

    Required inputs
    ---------------
    * database
    * simname

    Optional input
    --------------
    * overwrite: bool: set to False if don't want to overwrite the columns if they exist.
                       Default: True

    """
    # adds one column (ditheredRotTelPos) and indexes
    dithcols = ['ditheredRotTelPos']
    newcols = list(dithcols)
    # connect to the database
    cursor =  connect_db(dbname=database)
    # check if dither columns exist
    sqlquery = "describe %s" % (simname)
    cursor.execute(sqlquery)
    sqlresults = cursor.fetchall()
    for result in sqlresults:
        if (result[0] in newcols):
            newcols.remove(result[0])
            if overwrite:
                print '%s column already exists, but will overwrite.' %(result[0])
            else:
                print "%s column already exists - skipping adding dithering" %(result[0])
                return
    if len(newcols)>0:
        print 'Adding dither columns'
        for n in newcols:
            # add columns for dithering
            sqlquery = 'alter table %s add %s double' %(simname, n)
            cursor.execute(sqlquery)
    # Try to drop indexes, if they exist.
    sqlquery = "drop index %s_idx on %s" % (dithcols[0], simname)
    try:
        cursor.execute(sqlquery)
    except mysqldb.OperationalError as e:
        pass
    # want to implement rotational dither after every filter change
    # get the obsHistID to track each visit. get filter to track filter change,
    # but because the summary table contains duplicate records, need to use unique expmjd (and sort by expmjd)
    sqlquery = "select obshistid, filter from %s group by expmjd order by expMJD" % (simname)
    cursor.execute(sqlquery)
    sqlresults = cursor.fetchall()

    # Now modify the observations, adding a new offset where there was a filter change.
    filteridx = 1
    prevFilter = sqlresults[0][filteridx]
    rotOffset = 0
    for i, result in enumerate(sqlresults):
        filterBand = result[filteridx]
        if (filterBand != prevFilter):    # i.e. if there is a filter change
            rotOffset= np.random.rand() * np.pi - np.pi/2.   # calcuate a new random offset between +/-pi/2 radians
        obsHistID = int(result[0])
        sqlquery = "update %s set %s = rotTelPos + %f where obsHistID = %i" %(simname, dithcols[0], rotOffset, obsHistID)
        cursor.execute(sqlquery)
    # add indexes
    print "Adding rotational dithering indexes"
    sqlquery = "CREATE INDEX %s_idx on %s(%s)" % (dithcols[0], simname, dithcols[0])
    cursor.execute(sqlquery)
    cursor.close()

if __name__ == "__main__":
    # Give this the opsim name, then will update opsim to add useful information & indexes
    import sys

    if len(sys.argv)<3:
        print "Usage : './prep_opsim.py <realhostname> <databasename> <sessionID>'"
        sys.exit(1)
    hname = sys.argv[1]
    database = sys.argv[2]
    sessionID = sys.argv[3]
    opsimname = "summary_" + hname + "_" + sessionID
    #print "Updating %s" %(opsimname)
    add_indexes(database, opsimname)
    add_translationalDither(database, opsimname, dithType= 'hex', overwrite=False)    # SequentialHexDitherPerNight
    add_translationalDither(database, opsimname, dithType= 'random', overwrite=False)  # RandomDitherFieldPerVisit
    add_rotationalDither(database, opsimname, overwrite=False)  # random rotational dithers
