#!/usr/bin/env python

import sys, MySQLdb

STEP            = 10

# DB specifics
from LSSTDBInit import *


try:
    data = file (sys.argv[1]).readlines ()
except:
    sys.stderr.write ('usage: ingest_target_list.py input_file\n')
    sys.exit (1)

sql = 'INSERT INTO %s VALUES ' % (DBTABLE)
i = 0
for line in data:
    i += 1
    try:
        (ra, dec, fieldID) = line.split ()
        ra = float (ra)
        dec = float (dec)
    except:
        sys.stderr.write ('skipped line %d\n' % (i))
        continue
    sql += '(NULL, %f, %f), ' % (ra, dec)
sql = sql[:-2]

try:
    dbc = MySQLdb.connect (user=DBUSER, 
                           passwd=DBPASSWD, 
                           db=DBDB, 
                           host=DBHOST).cursor ()
except:
    sys.stderr.write ('Connection to the DB failed.\n')
    sys.exit (1)

try:
    res = dbc.execute (sql)
except:
    sys.stderr.write ('SQL error in the query (%s)\n' % (sql))
    sys.exit (1)

sys.exit (0)
