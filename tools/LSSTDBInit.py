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


# Database specific stuff
try:
    DBHOST  = os.environ['DBHOST']
except:
    DBHOST = ''

try:
    DBPORT   = os.environ['DBPORT']
    if DBPORT == 'None':
        DBPORT = None
except:
    DBPORT   = None

try:
    DBDB     = os.environ['DBDB']
except:
    DBDB     = 'OpsimDB'

try:
    DBUSER   = os.environ['DBUSER']
except:
    DBUSER   = 'www'

try:
    DBPASSWD = os.environ['DBPASSWD']
except:
    DBPASSWD = 'zxcvbnm'

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
    
    
def getCursor (connection):
    """
    If connection is still valid, return a cursor. Otherwise
    open a new connection and return a cursor from it.
    
    Return a two element array with the connection and the
    cursor
    """
    try:
        cursor = connection.cursor ()
    except:
        try:
            connection = openConnection ()
            cursor = connection.cursor ()
        except:
            raise (IOException, 'Connection to the DB failed.')
    return ((connection, cursor))


def executeSQL (query, timeout=10):
    """
    Execute any given query and return both the number of rows that 
    were affected and the results of the query. If the connection 
    to the DB fails, the code tries to reconect for a specified number
    of seconds (timeout).
    
    Input
    query       A string containing the SQL query to be sent to the
                database.
    timeout     timeout in seconds for re-trying to send the query.
    
    Return
    A two element array of the form [n, res] where:
    n       number of affected rows
    res     result array: [[col1, col2, ..], [col1, col2, ...], ...]
            If the query returns no data, res is empty.
    
    Raise
    Exception if either the connection to the DB failed or the 
    execution of the query failed.
    """
    done = False
    
    t0 = time.time ()
    while (not done):
        try:
            connection = openConnection ()
            done = True
        except:
            if (time.time () - t0 > timeout):
                raise (IOError, 'Connection to the database failed.')
            else:
                continue
    # <- end of while loop
    
    cursor = connection.cursor ()
    n = cursor.execute (query)
    try:
        res = cursor.fetchall ()
    except:
        res = []
    
    # Close the connection
    cursor.close ()
    connection.close ()
    del (cursor)
    del (connection)
    
    # print ('utilities.executeSQL(): %.01f' % (time.time () - t0))
    
    # Return the results
    return (n, res)
