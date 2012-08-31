#!/usr/bin/python -Ou
# 
# extract_fwhm.py
# 
# Author: F. Pierfederici <fpierfed@noao.edu>
# 

"""
Given an ASCII table of ambient data, extract the DIMM seeing FWHM 
values.


Description:

The input file has to be in text (ASCII) format. Values have to be 
organized in columns, separated by blanks. Since the specific tabular
content is allowed to vary, the user has to specify which columns to 
extract data from.


Usage:

    extract_fwhm.py --file=data_file --date=i --seeing=j [--hour=k]
    e.g. extract_fwhm.py --file=data.txt --date=1 --seeing=-12 --hour=2


Options:

    --file=data_file    extract data from the specified file
    --date=i            specify the column number for date values
    --seeing=j          specify the column number for seeing values
    --hour=k            specify the column number for hour values
    --skip=h            specify the number of lines to skip


A note on column numbering:

Columns are numbered from left to right, starting from 0. Columns are 
separated by blanks. This means that the number of columns in a given 
file might not be the same for every line (especially true if one or 
more fields are strings with spaces).

To get around this problem, negative values can be specified. In this 
case, columns are numbered from right to left, staring from -1 (0 is 
already taken).

e.g. Suppose the data.txt contains the following data
2003-01-11 00:31:57	1336	A Ret	1.21
2003-01-10 00:30:31	1336	A Ret	1.21
2003-01-10 00:32:02	1336	ARet	1.21
2003-01-10 00:33:17	1336	ARet	1.21
2003-01-10 00:34:34	1336	ARet	1.21

The first two lines have 6 columns, lines three to five only have 5 
columns. What we could do is 

extract_fwhm.py --file=data.txt --date=0 --seeing=-1 --hour=1

"""

import os
import sys
import string
import calendar

import gre2mjd

# GLOBALS
USAGE_STR = '--file=data_file --date=i --seeing=j [--hour=k] [--skip=h]'
LINE_NO = 0


def warning (msg):
    """
    Print a warning (i.e. a non fatal error) to STDOUT.
    
    msg is the warning text to be printed.
    """
    sys.stderr.write ('Warning: ' + msg + '\n')
    return


def parseArgs (args):
    """
    Do a quick command line argument parsing. 
    
    The expected syntax is --var=val. No check on the semantic is 
    performed (it is left to the colling code).
    
    Return a dictionary of var=val entries. If args is None, an empty
    dictionary is returned.
    
    Raise an exception of type SyntaxError in case of syntax errors 
    in the command line args.
    """
    result = {}
    
    for arg in args:
        try:
            (var, val) = string.split (arg, '=', 1)
        except:
            raise (SyntaxError, '%s is in the wrond format' % (arg))
        
        if (var[:2] != '--'):
            raise (SyntaxError, 'variable names must start with a ' +
                                'double dash (%s)' % (var))
        
        result[var[2:]] = val
    return (result)


def usage (usageString):
    """
    Print the usageString to STDERR.
    
    If usageString is null, print a generic message saying that some
    of the command line arguments had syntax errors in them.
    """
    command = os.path.basename (sys.argv[0])
    if (usageString):
        sys.stderr.write ('usage: %s %s\n' % (command, usageString))
    else:
        sys.stderr.write ('Error in parsing command line arguments.\n')
    return


def fatalError (errorMessage, exitCode=1):
    """
    Print the errorMessage to STDERR and exit with an exit code equal
    to exitCode (default 1).
    
    If errorMessage is null, print a generic message saying that 
    something went wrong.
    """
    if (errorMessage):
        sys.stderr.write ('Fatal Error: ' + errorMessage + '\n')
    else:
        sys.stderr.write ('Fatal Error: something went wrong.\n')
    sys.exit (exitCode)
    return


def checkArgs (argDictionary):
    """
    Perform sanity check on the command line parameters.
    
    Input:
    argDictionary   a dictionary of keyword=value pairs as produced 
                    by parseArgs.
    
    Output:
    (data, dateCol, seeingCol, hourCol)
    data            an array of strings. each string is a line in the
                    input data file.
    dateCol         non null integer specifying the column number for 
                    date values.
    seeingCol       non null integer specifying the column number for 
                    seeing values.
    hourCol         integer specifying the column number for hour 
                    values. It can be None.
    
    Raise:
    SynyavError exception in case something goes wrong. The 
    accompaining text message explains the cause of the exception.
    
    Notes:
    It is NOT a generic routine: it is customized for this particular 
    application.
    """
    global LINE_NO
    
    # Make sure that we have a data file
    try:
        dataFile = argDictionary['file']
    except:
        raise SyntaxError, USAGE_STR
    try:
        data = file (dataFile).readlines ()
    except:
        raise SyntaxError, '%s cannot be opened for reading.' % (dataFile)
    if (not len (data)):
        raise SyntaxError, '%s is empty.' % (dataFile)
    
    
    # Make sure that we know where to get the date from
    try:
        dateCol = int (argDictionary['date'])
    except:
        raise SyntaxError, USAGE_STR
    
    # Make sure that we know where to get the seeing from
    try:
        seeingCol = int (argDictionary['seeing'])
    except:
        raise SyntaxError, USAGE_STR
    
    # Where do we get the hour from? This is optional.
    try:
        hourCol = int (argDictionary['hour'])
    except:
        hourCol = None
    
    # Is there a header to skip? This is optional.
    try:
        skip = int (argDictionary['skip'])
    except:
        skip = 0
    data = data[skip:]
    LINE_NO += skip
    
    # Perform a simple sanity check
    test = data[0].split ()
    try:
        date = test[dateCol]
    except:
        raise SyntaxError, '%s cannot be parsed. Invalid date column specification?' % (dataFile)
    try:
        seeing = float (test[seeingCol])
    except:
        raise SyntaxError, '%s cannot be parsed. Invalid seeing column specification?' % (dataFile)
    try:
        hour = test[hourCol]
    except:
        hourCol = None
    return ((data, dateCol, seeingCol, hourCol))




if (__name__ == '__main__'):
    
    # Parse the command line arguments
    try:
        args = parseArgs (sys.argv[1:])
    except:
        usage (USAGE_STR)
        sys.exit (1)
    
    # Make sure that args makes sense
    try:
        (data, dateCol, seeingCol, hourCol) = checkArgs (args)
    except SyntaxError, msg:
        msg = str (msg)
        if (msg == USAGE_STR):
            usage (USAGE_STR)
            sys.exit (1)
        else:
            fatalError (msg)
    
    # Get ready to extract the data
    if (hourCol != None):
        # Three column extraction
        results = [[], [], []]
        for line in data:
            el = line.split ()
            try:
                # date
                date = el[dateCol]
                # hour
                hour = el[hourCol]
                # seeing
                fwhm = float (el[seeingCol])
            except:
                warning ('skipping line %d' % (LINE_NO))
                LINE_NO += 1
                continue
            
            mjd = gre2mjd.gre2mjd ('%sT%s' % (date, hour))
            print ('%.02f\t%.02f' % (mjd, fwhm))
            
            LINE_NO += 1
    else:
        # Two column extraction
        results = [[], []]
        for line in data:
            el = line.split ()
            hour = '12:00:00.0'
            try:
                # date
                date = el[dateCol]
                # seeing
                fwhm = float (el[seeingCol])
            except:
                warning ('skipping line %d' % (LINE_NO))
                LINE_NO += 1
                continue
            
            mjd = gre2mjd.gre2mjd ('%sT%s' % (date, hour))
            print ('%.02f\t%.02f' % (mjd, fwhm))
            
            LINE_NO += 1
    # <-- end of the if...else block
    
    # Exit gracefuly
    sys.exit (0)












