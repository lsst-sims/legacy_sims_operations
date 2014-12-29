#!/usr/bin/env python

import remoteD, time, sys, string


def child_function (Shared, id, max):
    i = 0
    while (i < max):
        i += 1
    
    Shared[id] = "Hello World"
    return



if (__name__ == '__main__'):
    t0 = time.time ()
    
    numProcesses = 0
    maxCount = 0
    for arg in sys.argv[1:]:
        try:
            (par, val) = string.split (arg, '=', 1)
        except:
            continue
        if (par == '--processes'):
            try:
                numProcesses = int (val)
            except:
                continue
        elif (par == '--count'):
            try:
                maxCount = int (val)
            except:
                continue
        else:
            continue
    
    if (not maxCount or not numProcesses):
        print ('usage: multiprocess.py --processes=N --count=M')
        print ('       N = number of processes to start (N > 0)')
        print ('       M = how much each process should count for (M > 0)')
        sys.exit (1)
    
    t1 = time.time ()
    dt1 = t1 - t0
    
    SharedD = remoteD.initShare (sType=remoteD.UNIXSOCK)
    
    i = 0
    while (i < numProcesses):
        SharedD.newProc (child_function, [i, maxCount])
        i += 1
    
    t2 = time.time ()
    dt2 = t2 - t1
    
    n = 0
    while (n < numProcesses):
        n = len (SharedD.keys ())
        time.sleep (0.2)
    
    t3 = time.time ()
    dt3 = t3 - t2
    dt0 = t3 - t0
    
    print ('ARGV parsing:       %.02fs' % (dt1))
    print ('Starting processes: %.02fs' % (dt2))
    print ('Collecting results: %.02fs' % (dt3))
    print ('Total time:         %.02fs' % (dt0))





