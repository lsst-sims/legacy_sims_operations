#!/usr/bin/env python

import sys, time, string

def loadTargetList (fileName):
    # loads a target list (RA Dec ID)
    # from fileName (is non null) or initializes one.
    t = []
    list = file (fileName).readlines ()
    for line in list:
        line = string.strip (line)
        
        # skip comments (identified by a #)
        if (line[0] == '#'):
            continue
        
        # try and parse the line, skip the line 
        # in case of error (silently)
        try:
            (ra, dec, id) = string.split (line)
        except:
            continue
        
        t.append ((ra, dec, id))
    return (t)


if __name__ == "__main__":
    t0 = time.time ()
    try:
        targets = loadTargetList (sys.argv[1])
    except:
        sys.stderr.write ('usage: reader.py filename\n')
        sys.exit (1)
    dt = dt = time.time () - t0
    print ('reading took %.02fs' % (dt))
    
    sys.exit (0)