#!/usr/bin/env python

import sys, MySQLdb,os

STEP            = 10
DBHOST          = ''
DBDB            = os.environ['DBDB']
DBUSER          = os.environ['DBUSER']
DBPASSWD        = os.environ['DBPASSWD']
DBTABLE         = 'Field'


sql = 'INSERT INTO %s VALUES ' % (DBTABLE)
for dec in range (0, 360, STEP):
    for ra in range (0, 360, STEP):
        sql += '(NULL, %d, %d), ' % (ra, dec)
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
