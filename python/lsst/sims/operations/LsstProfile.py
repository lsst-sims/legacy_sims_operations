#!/usr/bin/env python

# Demo python script to generate a profiling report of the 30 leading time consumers.

# The Lsst Simulator loads the profiling data into file: ProfileData .
# This script leads the profiling data, counts the hits (which is time consuming)
#   and then reports


#  To generate a profiling report:
#   cronos% ./main.py --profile=yes
#   cronos% ./LsstProfile.py



import hotshot, hotshot.stats
stats = hotshot.stats.load("ProfileData")
stats.strip_dirs()
stats.sort_stats('time','calls')
stats.print_stats(1000)
stats.sort_stats('calls','time')
stats.print_stats(1000)

