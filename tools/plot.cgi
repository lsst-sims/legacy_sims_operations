#!/data1/simulator/sw/python/bin/python -Ou
#!/usr/bin/python -Ou
# 
# Plot.cgi
# 
# Utility script to parse proposalX.log files and build a data file
# for the lsst SM macro.
# 
# F. Pierfederici
# 

import sys, os, tempfile, time
import cgi, MySQLdb
import cgitb; cgitb.enable(logdir='/tmp')


# General constants
FOV = 3.5
REFRESH = 10          # seconds
EXEC = '/data1/simulator/sw/sm/bin/sm'
PS2PNG = './ps2png.sh'
TEMPLATE = \
"""
device postencap %s
macro read lsst.sm
lsst "%s"
"""

# Database specific stuff
DBHOST          = ''
DBPORT          = None
DBDB            = 'LSST'
DBUSER          = 'www'
DBPASSWD        = 'zxcvbnm'
OBSHIST = 'ObsHistory'
SEQHIST = 'SeqHistory'
FIELD = 'Field'

# HTML related
HEADER = 'Content-Type: text/html\n\n<html>\n'
TITLE_STANDARD = '<head><title>LSST Simulator</title></head>'
TITLE_REFRESH = '<head><title>LSST Simulator</title>\n'
TITLE_REFRESH += '<META HTTP-EQUIV="Refresh" '
TITLE_REFRESH += 'CONTENT="%d"></head>'
CONTENT = '<body><p>'
FOOTER = '</p></body></html>'
CGI = 'plot.cgi'
FORMSTART = '<form method=GET action="%s' % (CGI)
FORMEND = '</form>'
IMGDIR = 'images'




def main ():
    """
    Main routine: this is where all the action starts.
    
    The GET parameter 'action' determines the flow of the program.
    action = index      create the index page
    action = sessionID  create the page for sessionID
    """
    form = cgi.FieldStorage ()
    
    try:
        action = form['action'].value
    except:
        action = 'index'
    
    try:
        SID = int (form['sessionID'].value)
    except:
        SID = None
        action = 'index'
    
    try:
        image = form['image'].value
    except:
        image = None
    
    try:
        fov = float (form['fov'].value)
    except:
        fov = FOV
    
    try:
        refresh = int (form['refresh'].value)
    except:
        refresh = REFRESH
    
    if (action == 'index'):
        createIndexPage ()
    else:
        createDatasetPage (sessionID=SID, 
                           image=image, 
                           fov=fov, 
                           refresh=refresh)
    return



def createIndexPage ():
    """
    Create the main index page.
    """
    # Build the index page HTML
    html = '<center><h1>LSST Observation Simulator</h1><br />\n'
    
    load = getLoad ()
    html += 'Machine load: <b>%s</b><br /><br />\n' % (load)
    
    now = time.strftime ('%a, %d %b %Y %H:%M:%S', time.localtime ())
    html += 'It is %s<br />\n' % (now)
    
    html += '<br /><br />\n'
    
    html += '<pre>'
    html += 'SessionID: <input type="text" name="sessionID" size="5" /><br />\n'
    html += 'FoV: <input type="text" name="fov" value="%.01f" size="5" /><br />\n' % (FOV)
    html += 'Refresh (s): <input type="text" name="refresh" value="%d" size="3" /><br />\n' % (REFRESH)
    html += '<br /><input type="reset"><input type="submit" /><br />'
    html += '</pre></center><br />'
    
    printPage (html, refresh=False, action='display')
    return



def createDatasetPage (sessionID, image=None, 
                                  fov=FOV, 
                                  refresh=REFRESH):
    if (image):
        try:
            os.remove (image)
        except:
            sys.stderr.write ('Failed removing %s.' % (image))
    
    # Get a connection to the DB
    connection = openConnection ()
    cursor = connection.cursor ()
    
    # Remember that the ObsHistory records the same observation up tp N times
    # where N is the number of active proposals (serendipitous obs!). In 
    # particular, some proposals accept any serendipitous observation, other
    # don't. We need to figure out the max spatial coverage.
    # Fetch all the data for this Session ID, if any
    sql = 'SELECT f.fieldRA, f.fieldDec, f.fieldID, '
    sql += 'o.filter, o.expDate '
    sql += 'FROM %s f, %s o WHERE ' % (FIELD, OBSHIST)
    sql += 'o.sessionID = %d AND ' % (sessionID)
    sql += 'f.fieldFov = %s AND ' % (fov)
    sql += 'o.fieldID = f.fieldID '
    sql += 'GROUP BY o.expDate'
    
    # Fetch the data from the DB
    sys.stderr.write ('Fetching data from the DB...\n')
    try:
        n = cursor.execute (sql)
    except:
        fatalError ('Unable to execute SQL query (%s).' % (sql))
    
    try:
        resObs = cursor.fetchall ()
    except:
        resObs = None
    
    if (not resObs):
        outFileName = None
        sys.stderr.write ('No data for Session %d.\nTrying again later...\n' \
            % (sessionID))
    else:
        # Fetch all the data for this Session ID, if any
        sql = 'SELECT f.fieldRA, f.fieldDec, s.fieldID '
        sql += 'FROM %s f, %s s WHERE ' % (FIELD, SEQHIST)
        sql += 's.sessionID = %d AND ' % (sessionID)
        sql += 'f.fieldFov = %s AND ' % (fov)
        sql += 's.completion >= 1 AND '
        sql += 's.fieldID = f.fieldID '
        
        # Fetch the data from the DB
        sys.stderr.write ('Fetching data from the DB...\n')
        n = cursor.execute (sql)
        
        try:
            resSeq = cursor.fetchall ()
        except:
            resSeq = None
        
        # Create three temp files, one for the data, one for EXEC
        # and one for the image
        (dataFile, dataFileName) = tempfile.mkstemp (dir='/tmp')
        (execFile, execFileName) = tempfile.mkstemp (dir='/tmp')
        (outFile, outFileName) = tempfile.mkstemp (dir=os.path.abspath (IMGDIR))
        os.close (outFile)
        
        # Summarize the results
        (targets, r, g, y, i, z, nea) = summary (resObs, resSeq)
        
        # Now print out the summary
        for fieldID in targets.keys ():
            ra = targets[fieldID][0]
            dec = targets[fieldID][1]
            rt = r[fieldID]
            gt = g[fieldID]
            yt = y[fieldID]
            it = i[fieldID]
            zt = z[fieldID]
            try:
                neat = nea[fieldID]
            except:
                neat = 0
            
            n = os.write (dataFile, 
                '%.04f  %.04f  %.01f  %.01f  %.01f  %.01f  %.01f  %d\n' \
                % (ra, dec, rt, gt, yt, it, zt, neat))
        os.close (dataFile)
        
        # Write the commands to startup EXEC and produce the plot
        os.remove (outFileName)
        data = TEMPLATE % (outFileName + '.ps', dataFileName)
        n = os.write (execFile, data)
        os.close (execFile)
        
        # Create the PS
        sys.stderr.write ('Plotting...\n')
        n = os.system ('cat %s | %s >& /dev/null' % (execFileName, 
                                                     EXEC))
        
        # Turn the PS into PNG
        n = os.system ('%s %s %s >& /dev/null' % (PS2PNG, 
                                                  outFileName + '.ps',
                                                  outFileName + '.png'))
        
        # Remove intermediate files
        try:
            os.remove (dataFileName)
            os.remove (execFileName)
            os.remove (outFileName + '.ps')
        except:
            pass
    
    # Display the PNG and build the page HTML
    html = '<center><h1>LSST Observation Simulator</h1><br />\n'
    html += '<b>Simulation Parameters</b><br />\n'
    html += 'Session ID: %d <br />\n' % (sessionID)
    html += 'FoV: %.02f deg<br /><br />\n' % (fov)
    
    load = getLoad ()
    html += 'Machine load: <b>%s</b><br /><br />\n' % (load)
    
    now = time.strftime ('%a, %d %b %Y %H:%M:%S', time.localtime ())
    html += 'It is %s<br />\n' % (now)
    
    html += '<i>page automatically updated every %d sec</i>' % (refresh)
    html += '<br /><br />\n'
    
    if (outFileName):
        html += '<img src="%s/%s" border="0" /><br />\n' % (IMGDIR,
            os.path.basename (outFileName + '.png'))
        html += '<input type="hidden" name="image" value="%s" /><br />\n' \
            % (outFileName + '.png')
    else:
        html += 'No data yet.'
    
    html += '<input type="hidden" name="fov" value="%s" /><br />\n' % (fov)
    html += '<input type="hidden" name="refresh" value="%d" /><br />\n' % (refresh)
    html += '</center>\n'
    
    printPage (html, refresh=refresh, action='display')
    return



def printPage (message, refresh=False, action='index'):
    print (HEADER)
    
    if (refresh):
        print (TITLE_REFRESH % (refresh))
    else:
        print (TITLE_STANDARD)
    
    print (CONTENT)
    
    print ('%s">' % (FORMSTART))
    print ('<input type="hidden" name="action" value="%s" /><br />' % (action))
    
    print (message)
    
    print (FORMEND)
    print (FOOTER)
    return


def getLoad ():
    try:
        load = file ('/proc/loadavg').readlines()[0]
    except:
        load = None
    
    # Extract the 1 min average load
    if (load):
        avgLoad = load.split ()[0]
        return (avgLoad)
    else:
        return ('N/A')
    return


def summary (resObs, resSeq):
    # Cumulative number of visits per fieldID
    r = {}
    g = {}
    y = {}
    i = {}
    z = {}
    nea = {}
    
    # Utility dictionary {fieldID: (ra, dec)}
    targets = {}
    
    # Start with the NEA sequences
    # Each row has the format
    # (ra, dec, fieldID)
    # We want RA in decimal hours...
    for row in resSeq:
        ra = float (row[0]) / 15.
        dec = float (row[1])
        fieldID = int (row[2])
        
        if (not targets.has_key (fieldID)):
            targets[fieldID] = (ra, dec)
        
        if (not nea.has_key (fieldID)):
            nea[fieldID] = 1
        else:
            nea[fieldID] += 1
    
    
    # Now the observations!
    # Each row has the format
    # (ra, dec, fieldID, filter, expDate)
    # and it is grouped by observation date.
    for row in resObs:
        # We want RA in decimal hours...
        ra = float (row[0]) / 15.
        dec = float (row[1])
        fieldID = int (row[2])
        filter = row[3].lower ()
        date = row[4]
        
        if (not targets.has_key (fieldID)):
            targets[fieldID] = (ra, dec)
        
        if (filter == 'r'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 1
            else:
                r[fieldID] += 1
            if (not g.has_key (fieldID)):
                g[fieldID] = 0
            if (not y.has_key (fieldID)):
                y[fieldID] = 0
            if (not i.has_key (fieldID)):
                i[fieldID] = 0
            if (not z.has_key (fieldID)):
                z[fieldID] = 0
        elif (filter == 'g'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 0
            if (not g.has_key (fieldID)):
                g[fieldID] = 1
            else:
                g[fieldID] += 1
            if (not y.has_key (fieldID)):
                y[fieldID] = 0
            if (not i.has_key (fieldID)):
                i[fieldID] = 0
            if (not z.has_key (fieldID)):
                z[fieldID] = 0
        elif (filter == 'y'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 0
            if (not g.has_key (fieldID)):
                g[fieldID] = 0
            if (not y.has_key (fieldID)):
                y[fieldID] = 1
            else:
                y[fieldID] += 1
            if (not i.has_key (fieldID)):
                i[fieldID] = 0
            if (not z.has_key (fieldID)):
                z[fieldID] = 0
        elif (filter == 'i'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 0
            if (not g.has_key (fieldID)):
                g[fieldID] = 0
            if (not y.has_key (fieldID)):
                y[fieldID] = 0
            if (not i.has_key (fieldID)):
                i[fieldID] = 1
            else:
                i[fieldID] += 1
            if (not z.has_key (fieldID)):
                z[fieldID] = 0
        elif (filter == 'z'):
            if (not r.has_key (fieldID)):
                r[fieldID] = 0
            if (not g.has_key (fieldID)):
                g[fieldID] = 0
            if (not y.has_key (fieldID)):
                y[fieldID] = 0
            if (not i.has_key (fieldID)):
                i[fieldID] = 0
            if (not z.has_key (fieldID)):
                z[fieldID] = 1
            else:
                z[fieldID] += 1
    return (targets, r, g, y, i, z, nea)



def openConnection ():
    """
    Open a connection to DBDB running on DBHOST:DBPORT as user DBUSER
    and return the connection.
    
    Raise exception in case of error.
    """
    if (DBPORT):
        connection = MySQLdb.connect (user=DBUSER, 
                                      passwd=DBPASSWD, 
                                      db=DBDB, 
                                      host=DBHOST, 
                                      port=DBPORT)
    else:
        connection = MySQLdb.connect (user=DBUSER, 
                                      passwd=DBPASSWD, 
                                      db=DBDB, 
                                      host=DBHOST)
    return (connection)



if (__name__ == '__main__'):
    main ()
    
        
        

























