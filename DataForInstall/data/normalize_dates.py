#!/usr/bin/env python
# 
# F. Pierfederici
# 

import sys
import string
import numarray

import dateutils



if (__name__ == '__main__'):
    try:
        data = file (sys.argv[1]).readlines ()
    except:
        sys.stderr.write ('usage: normalize_dates.py data_file\n')
        sys.exit (1)
    
    N = len (data)
    
    # Create placeholder arrays
    text = []
    SEC = numarray.zeros (shape=(N))
    
    for i in range (N):
        (date, time, rest) = string.split (data[i], None, 2)
        ut = '%sT%s' % (date, time)
        
        mjd = float (dateutils.gre2mjd (ut))
        SEC[i] = int (mjd * 86400.)
        text.append (rest)
    
    # Find out the zero point
    zero = SEC.min ()
    
    # Normalize
    SEC = SEC - zero
    
    # Now, substitute date and time with the corresponding 
    # normalized MJD
    out = ''
    for i in range (N):
        # Remember: text[i] is already terminated with a '\n'
        out += '%d  %s' % (SEC[i], text[i])
    
    print (out)
    sys.exit (0)
    
    
