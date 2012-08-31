#!/usr/bin/env python
#
# Author: Michelle Miller
# Date:   Oct. 7, 2010
#
# Calculate random downtime using following probabilities:
#	minor event (remainder of night and next day) = 5/365 days
#		e.g. power supply failure
#       intermediate (3 nights) = 2/365 days
#		e.g. repair filter mechanism, rotator, hexapod, or shutter
#	major event (7 nights) = 1/2*365 days
#	catastrophic event (14 nights) = 1/3650 days
#		e.g. replace a raft
#
#  USAGE: ./randomDown.py > <filename>   
#       To emit a configuration file for random downtime in OpSim, I usually
#       take the median of 10 random runs.

import random

i = downtime = 0
while i < 3650:
   c = random.random()
   if c < 0.000274:
      print " "
      print "activity = catastrophic event"
      print "startNight = %d" % i
      print "duration = 14"
      i += 14
      downtime += 14
      i += 1
      continue
   else:
      c = random.random()
      if c < 0.00137:
         print " "
         print "activity = major event"
         print "startNight = %d" % i
         print "duration = 7"
         i += 7
         downtime += 7
         i += 1
         continue
      else:
         c = random.random()
         if c < 0.00548:
            print " "
            print "activity = intermediate event"
            print "startNight = %d" % i
            print "duration = 3"
            i += 3
            downtime += 3
            i += 1
            continue
         else:
            c = random.random()
            if c < 0.0137:
               print " "
               print "activity = minor event"
               print "startNight = %d" % i
               print "duration = 1"
               downtime += 1
   i += 1
print "# Total downtime = %d over 10 years" % (downtime)
