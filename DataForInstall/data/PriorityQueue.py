#!/usr/bin/env python
import Queue, bisect

class PriorityQueue (Queue.Queue):
    def _put (self, item):
        bisect.insort (self.queue, item)

if __name__ == "__main__":
    import time, random
    from utilities import *
    
    print ('Testing PriorityQueue...')
    queue = PriorityQueue (0)
    
    # create N observations with a random
    # distribution of priorities
    mu = AVGPRIORITY
    sigma = mu * (SIGMAPERCENT / 100.0)
    N = 14400
    
    t0 = time.time ()
    for i in range (N):
        pri = random.normalvariate (mu, sigma)
        queue.put ((pri, i))
    dt = time.time () - t0
    print ('Inserted (and sorted) %d elements in %.02fs.' % (N, dt))
    
    i = 0
    done = False
    t0 = time.time ()
    while (not done):
        try:
            (priority, value) = queue.get (block=False)
            i += 1
        except:
            done = True
    dt = time.time () - t0
    print ('Extracted %d elements in %.02fs.' % (i, dt))
    
    
    arrayQueue = []
    t0 = time.time ()
    for i in range (N):
        pri = random.normalvariate (mu, sigma)
        arrayQueue.append ((pri, i))
    arrayQueue.sort ()
    dt = time.time () - t0
    print ('Inserted (and sorted) %d elements in %.02fs.' % (N, dt))
    
    i = 0
    done = False
    t0 = time.time ()
    while (not done):
        try:
            (priority, value) = arrayQueue[i]
            i += 1
        except:
            done = True
    dt = time.time () - t0
    print ('Extracted %d elements in %.02fs.' % (i, dt))
    
    print ('Done.')





