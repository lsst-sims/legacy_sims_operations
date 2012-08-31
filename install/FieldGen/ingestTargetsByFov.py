#!/usr/bin/env python

import sys, MySQLdb
from utilities import *

STEP            = 10

# Database specific
from LSSTDBInit import *
DBTABLE         = 'Field'

USAGE_STR = '[--fov=4.0] [--fields=./fields_4.0]'


# Parse the command line args
try:
    args = parseArgs (sys.argv[1:])
except:
    usage (USAGE_STR)
    sys.stderr.write ('Syntax error\n')
    sys.exit (1)
    
# FOV?
if (args.has_key ('fov')): 
    fov = float(args['fov'])
else:
    usage (USAGE_STR)
    sys.stderr.write ('Syntax error\n')
    sys.exit (1)
    
# Filename?
if (args.has_key ('fields')): 
    fields = args['fields']
else:
    usage (USAGE_STR)
    sys.stderr.write ('Syntax error\n')
    sys.exit (1)
    
print (" FOV: %f  fields: %s" % (fov, fields))

try:
    data = file (fields).readlines ()
except:
    sys.stderr.write ('usage: ingestTargetByFov.py --fov=field_of_view --fields=input_file\n')
    sys.exit (1)

try:
    dbc = MySQLdb.connect (user=DBUSER, 
                           passwd=DBPASSWD, 
                           db=DBDB, 
                           host=DBHOST).cursor ()
except:
    sys.stderr.write ('Connection to the DB failed.\n')
    sys.exit (1)

i = 0
for line in data:
    i += 1
    try:
        (ra, dec, gl, gb, el,eb ) = line.split ()
        ra = float (ra)
        dec = float (dec)
        gl = float(gl)
        gb = float(gb)
        el = float(el)
        eb = float(eb)
    except:
        sys.stderr.write ('skipped line %d\n' % (i))
        continue
    sql = 'INSERT INTO %s VALUES ' % (DBTABLE)
    sql += '(NULL, %f, %f, %f, %f,%f,%f,%f) ' % (fov, ra, dec, gl, gb, el, eb)

    try:
        res = dbc.execute (sql)
    except:
        sys.stderr.write ('SQL error in the query (%s)\n' % (sql))
        sys.exit (1)

sys.exit (0)
