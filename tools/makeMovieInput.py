#!/usr/bin/env python

# command syntax:  ./makeMovieInput.py <#SimDays>
 
#Output file format:
    #days 1 1.5
    #plot
    #save Mov_1.5.png
    #days 1 2
    #plot
    #save Mov_2.png
    #days 1 2.5
    #plot
    #save Mov_2.5.png
    #days 1 3
    #plot
    #save Mov_3.png
    #quit

# See $LSSTROOT/simulator/doc/Movies   for movie making procedure.

import sys

i = len(sys.argv)
numDays = int(sys.argv[1])
if i == 3:
   interval = float(sys.argv[2])
elif i ==2:
   interval = 0.5
else:
   print "\n\n..........No count of simulation days to process!"
   print "..........Use makeMovieInput.py <#SimDays>\n\n"
   sys.exit()

if interval < 1:
   incr = 1 + interval
else:
   incr = interval

seq = 1
while incr <= numDays :
   print "days 1 %.1f" % (incr)
   print "reread"
   print "plot"
   print "save Mov_%03d.png" % (seq)
   incr += interval
   seq += 1

# snapshot of entire simulation
print "days 1 %.1f" % (numDays)
print "reread"
print "plot"
print "save Mov_%03d.png" % (seq)
print "quit"
