import os

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
    indexlist = ("fieldID", "expMJD", "filter", "fieldRA", "fieldDec", "fieldRADec", "night")
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
    print index_done
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

def remove_dither(simname, dropdatacol = False):
    print "Removing existing dithering indexes and columns."
    cursor = connect_db()
    sqlquery = "drop index ditheredRA_idx on %s" %(simname)
    cursor.execute(sqlquery)
    sqlquery = "drop index ditheredDec_idx on %s" %(simname)
    cursor.execute(sqlquery)
    sqlquery = "drop index ditheredRADec_idx on %s" %(simname)
    cursor.execute(sqlquery)
    if dropdatacol:
        print "Removed indexes - now will remove columns ditheredRA/dec."
        sqlquery = "alter table %s drop column ditheredRA, drop column ditheredDec" %(simname)
        cursor.execute(sqlquery)
    cursor.close()
    return

def offsetHex():
    """ 
    Returns translational hex dither offsets (217 points) in radians.
               
    """
    import numpy
    # some constants for the dithering
    fov = 3.5
    # set values associated with dithering
    dith_level = 4
    # number of rows in dither pattern
    # number of vertices in longest row is the same.
    nrows = 2**dith_level
    halfrows = int(nrows/2)  # useful for counting from 0 at center
    # calculate size of each offset
    dith_size_x = fov  / (nrows)
    dith_size_y = numpy.sqrt(3) * fov/2.0/(nrows)  #sqrt 3 comes from hexagon
    # calculate the row identification number, going from 0 at center
    nid_row = numpy.arange(-halfrows, halfrows+1, 1)
    # and calculate the number of vertices in each row
    vert_in_row = numpy.arange(-halfrows, halfrows+1, 1)
    total_vert = 0
    offsets = []
    for i in range(-halfrows, halfrows+1, 1):
        vert_in_row[i] = (nrows+1) - abs(nid_row[i])
        total_vert += vert_in_row[i]
    vertex_count = 0
    for i in range(0, nrows+1, 1):
        for j in range(0, vert_in_row[i], 1):
            # calculate displacement
            x_off = numpy.radians(dith_size_x * (j - (vert_in_row[i]-1)/2.0))
            y_off = numpy.radians(dith_size_y * nid_row[i])
            offsets.append([x_off, y_off])
            vertex_count += 1
    return offsets

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
    import numpy as np
    from lsst.sims.maf.stackers import inHexagon
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
    * overwrite: bool: Default: True
                  
    """
    ## adds three columns (<dithType>Dither<timescale>RA, <dithType>Dither<timescale>Dec, and vertex) and indexes
    # first check to ensure correct dithType is requested.
    if (dithType=='hex'):
        newcols = ['hexDitherPerNightRA', 'hexDitherPerNightDec']
    elif (dithType=='random'):
        newcols = ['randomDitherFieldPerVisitRA', 'randomDitherFieldPerVisitDec']
    else:
        print "Incorrect dithType: it should be either 'hex' or 'random'."
        return
    # connect to the database
    cursor =  connect_db(dbname=database)
    # check if dither columns exist
    sqlquery = "describe %s"%(simname)
    cursor.execute(sqlquery)
    sqlresults = cursor.fetchall()
    for result in sqlresults:
        if (result[0] in newcols):
            newcols.remove(result[0])
            if overwrite:
                print '%s column already exists, but will overwrite.' %(result[0])
            else:
                print "%s column already exists - skipping adding dithering" %(result[0])
                break
    if len(newcols)>0:
        print 'Adding dither columns'
        for n in newcols:
            # add columns for dithering
            sqlquery = 'alter table %s add %s double' %(simname, n)
            cursor.execute(sqlquery)
              
    # find the right offsets.
    if (dithType=='hex'):
        # want to change vertex on night/night basis, so pull all night values from db
        sqlquery = "select distinct(night) from %s"%(simname)
        #print sqlquery
        cursor.execute(sqlquery)
        sqlresults = cursor.fetchall()
        # go through each night individually
        offsets = offsetHex()
    else:   # already have checked that dithType is either 'hex' or 'random'
        # want to change vertex on per visit basis
        offsets = offsetRandom(noffsets=len(fieldRA), inHex=True)
        # get the obsHistID to track each visit.
        sqlquery = "select distinct(obsHistID) from %s"%(simname)
        cursor.execute(sqlquery)
        sqlresults = cursor.fetchall()

    for index, result in enumerate(sqlresults):
        if (dithType=='hex'):
            night = int(result[0])
            vertex = night%len(offsets) # implement hexDither on PerNight timescale.
        else: # already have checked that dithType is either 'hex' or 'random'
            obsHistID = int(result[0])
            vertex= index  # implement random dither on FieldPerNight timescale.
        x_off, y_off = offsets[vertex]
        #It doesn't make a ton of sense, but see http://bugs.mysql.com/bug.php?id=1665 for a discussion of the mysql modulus convention.
        #In the case where a mod can return a negative value (((N%M)+M)%M) will return what one would expect.
        if (dithType=='hex'):
            sqlquery = "update %s set "+ newcols[0] +" = ((((fieldra+(%f/cos(fielddec)))%%(2*PI()))+(2*PI()))%%(2*PI())), "+ newcols[1] +" = if(abs(fielddec + %f) > 90, fielddec  - %f, fielddec + %f) where night = %i"%(simname, x_off, y_off, y_off, y_off, night)
        else:
            sqlquery = "update %s set "+ newcols[0] +" = ((((fieldra+(%f/cos(fielddec)))%%(2*PI()))+(2*PI()))%%(2*PI())), "+ newcols[1] +" = if(abs(fielddec + %f) > 90, fielddec  - %f, fielddec + %f) where obsHistID = %i"%(simname, x_off, y_off, y_off, y_off, obsHistID)
        #Sometimes when the offset is 0 the above may still produce dec centers < -90 deg because fielddec can be < -pi/2. because of rounding issues.
        #it would make for a very complicated query string.
        cursor.execute(sqlquery)
        #print "Night %d done ....:" % (night)
    #This shouldn't really happen, but if outside -PI/2 -- PI/2 reflect to the proper bounds.  This does happen sometimes due to rounding issues.
    sqlquery = "update %s set "+ newcols[1] +" = -PI()/2. - ((("+ newcols[1] +"%%(-PI()/2)) + (-PI()/2.))%%(-PI()/2.)) where "+ newcols[1] +" < -PI()/2;"%(simname)
    cursor.execute(sqlquery)
    sqlquery = "update %s set "+ newcols[1] +" = PI()/2. - ((("+ newcols[1] +"%%(PI()/2)) + (PI()/2.))%%(PI()/2.)) where "+ newcols[1] +" > PI()/2;"%(simname)
    cursor.execute(sqlquery)
    # add indexes
    print "Adding dithering indexes"
    sqlquery = "create index "+ newcols[0] +"_idx on %s("+ newcols[0] +")" %(simname)
    cursor.execute(sqlquery)
    sqlquery = "create index "+ newcols[1] +"_idx on %s("+ newcols[1] +")" %(simname)
    cursor.execute(sqlquery)
    sqlquery = "create index "+ newcols[0] +"Dec_idx on %s("+ newcols[0] +", "+ newcols[1] +")" %(simname)
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
    * overwrite: bool: Default: True

    """
    # adds one column (ditheredRotTelPos) and indexes
    newcols = ['ditheredRotTelPos']
    
    # connect to the database
    cursor =  connect_db(dbname=database)
    # check if dither columns exist
    sqlquery = "describe %s"%(simname)
    cursor.execute(sqlquery)
    sqlresults = cursor.fetchall()
    for result in sqlresults:
        if (result[0] in newcols):
            newcols.remove(result[0])
            if overwrite:
                print '%s column already exists, but will overwrite.' %(result[0])
            else:
                print "%s column already exists - skipping adding dithering" %(result[0])
                break
    if len(newcols)>0:
        print 'Adding dither columns'
        for n in newcols:
            # add columns for dithering
            sqlquery = 'alter table %s add %s double' %(simname, n)
            cursor.execute(sqlquery)
            
    # want to implement rotational dither after every filter changed
    # get the obsHistID to track each visit. get filter to track filter change.
    sqlquery = "select distinct obsHistID, filter from %s"%(simname)
    cursor.execute(sqlquery)
    sqlresults = cursor.fetchall()

    for index, result in enumerate(sqlresults):
        if (index>0): # no data for previous filter for index=0, so ignore it.
            filterBand= results[1]
            if (filterBand[index-1]!=filterBand[index]):    # i.e. if there is a filter change
                rotOffset= np.random.rand()*np.pi-np.pi/2.   # random offset between +/-pi/2 radians
                obsHistID = int(result[0])
                sqlquery= "update %s set "+ newcols[0] +" = rotTelPos + %f, where obsHistID = %i"%(simname, rotOffset, obsHistID)
                cursor.execute(sqlquery)
    # add indexes
    print "Adding rotational dithering indexes"
    sqlquery = "create index "+ newcols[0] +"_idx on %s("+ newcols[0] +")" %(simname)
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
    add_rotationalDither(database, opsimname, overwrite=False)  # random rotational dithers.
