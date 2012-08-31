#!/usr/bin/env python

# System modules
import os
import socket
import sys
import time
import logging

# Third-party includes
import MySQLdb
from exceptions import *

class LSSTDatabase :

    def openConnection (self):
	"""
	Open a connection to DBDB running on DBHOST:DBPORT as user DBUSER
	and return the connection.

	Raise exception in case of error.
	"""
        if (self.DBPORT):
	    self.conn = MySQLdb.connect (user=self.DBUSER, passwd=self.DBPASSWD, db=self.DBDB, host=self.DBHOST, port=self.DBPORT) 
	else:
	    self.conn = MySQLdb.connect (user=self.DBUSER, passwd=self.DBPASSWD, db=self.DBDB, host=self.DBHOST)
	self.getCursor()   
 
    def getCursor (self):
	"""
	If connection is still valid, return a cursor. Otherwise
	open a new connection and return a cursor from it.

	Return a two element array with the connection and the
	cursor
	"""
	try:
	    self.cur = self.conn.cursor ()
	except:
	    try:
	        self.conn = self.openConnection ()
	        self.cur = self.conn.cursor ()
	    except:
	        raise (IOException, 'Connection to the DB failed.')

    def executeSQL (self, query):
	"""
	Execute any given query and return both the number of rows that 
	were affected and the results of the query. 

	Input
	query       A string containing the SQL query to be sent to the
		database.

	Return
	A two element array of the form [n, res] where:
	n       number of affected rows
	res     result array: [[col1, col2, ..], [col1, col2, ...], ...]
	    If the query returns no data, res is empty.

	Raise
	Exception if either the connection to the DB failed or the 
	execution of the query failed.
	"""

	n = self.cur.execute (query)
	try:
	    res = self.cur.fetchall ()
	except:
	    res = []

	# Return the results
	return (n, res)

    def closeConnection(self) :
	# Close the cursor
	self.cur.close()
	del (self.cur)
	self.conn.close()
	del (self.conn)

    def __init__(self):
	# Database specific stuff
        try:
	    self.DBHOST  = os.environ['DBHOST']
	except:
	    self.DBHOST = 'localhost'

	try:
	    self.DBPORT   = os.environ['DBPORT']
	    if self.DBPORT == 'None':
		self.DBPORT = None
	except:
	    self.DBPORT   = None

	try:
	    self.DBDB     = os.environ['DBDB']
	except:
	    self.DBDB     = 'LSST'

	try:
	    self.DBUSER   = os.environ['DBUSER']
	except:
	    self.DBUSER   = 'www'

	try:
	    self.DBPASSWD = os.environ['DBPASSWD']
	except:
	    self.DBPASSWD = 'zxcvbnm'

	done = False
	t0 = time.time ()
	timeout=10
	print "We are going to connect to DB"
	#self.openConnection()	
	while (not done):
	    try:
	        self.connection = self.openConnection ()
	        done = True
	    except:
	        if (time.time () - t0 > timeout):
		    raise (IOError, 'Connection to the database failed.')
	        else:
		    continue

