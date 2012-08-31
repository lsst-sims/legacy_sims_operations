#!/usr/bin/env python

"""
Filters

Inherits from: Simulation.Process : object

Class Description
The Filters class generates filter instances. 


Method Types
Constructor/Initializers
- __init__

Destructor
- __del__


Accessors
- getFiltersForSky
"""

from utilities import *
from LSSTObject import *


#class Filters (Simulation.Process):
class Filters (object):
    def __init__ (self,
		  lsstDB, 
                  filtersConf,
                  sessionID,
                  dbTableDict,
                  telSeeing,
                  opticalDesSeeing,
                  cameraSeeing,
                  log=False,
                  logfile='./Filters.log', 
                  verbose=0):
        """
        Standard initializer.
        
	lsstDB:      LSST DB access object        
	dbTableDict: dictionary containing all DB tables defined for simulation 
        telSeeing: fudge to account for telescope systematics
        filtersConf: Filters configuration file
        log         False if not set, else: log = logging.getLogger("...")
        logfile     Name (and path) of the desired log file.
                    Defaults "./Instrument.log".
        verbose:    Log verbosity: 0=minimal, 1=wordy, >1=very verbose
        """
        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up Filters logger"
            log = logging.getLogger("Filters")
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.INFO)
                                                                                
	self.lsstDB=lsstDB        
	self.log=log
        self.logfile=logfile
        self.verbose = verbose
        self.telSeeing = telSeeing
        self.opticalDesSeeing = opticalDesSeeing
        self.cameraSeeing = cameraSeeing
   
        if ( self.log and self.verbose > 1 ):
           self.log.info('Filters: init()')

        # read the configuration file, if specified
        filters_dict, pairs = readConfFile(filtersConf)
        self.filterNames   = filters_dict["Filter_Defined"]
        self.filterMinBrig = filters_dict["Filter_MinBrig"]
        self.filterMaxBrig = filters_dict["Filter_MaxBrig"]
        self.filterWavelen = filters_dict["Filter_Wavelen"]
	self.filterExpFactor = filters_dict["Filter_ExpFactor"]

        # save config values to DB
        for line in pairs:
            storeParam (self.lsstDB, sessionID, 0, 'filters', line['index'], line['key'], line['val'])

        self.filterMinBrigSorted = self.filterMinBrig[:]
        self.filterMinBrigSorted.sort()
        self.filterMinBrigSorted.reverse()

        self.filterNamesSorted   = []
        self.filterMaxBrigSorted = []
        self.filterWavelenSorted = []
	self.filterExpFactorSorted = []

        temp_filterNames   = self.filterNames[:]
        temp_filterMinBrig = self.filterMinBrig[:]
        temp_filterMaxBrig = self.filterMaxBrig[:]
        temp_filterWavelen = self.filterWavelen[:]
	temp_filterExpFactor = self.filterExpFactor[:]

        for minb in self.filterMinBrigSorted:
            ix = temp_filterMinBrig.index(minb)
            self.filterMaxBrigSorted.append(temp_filterMaxBrig[ix])
            self.filterNamesSorted.append(temp_filterNames[ix])
            self.filterWavelenSorted.append(temp_filterWavelen[ix])
	    self.filterExpFactorSorted.append(temp_filterExpFactor[ix])
            del temp_filterMinBrig[ix]
            del temp_filterMaxBrig[ix]
            del temp_filterNames[ix]
            del temp_filterWavelen[ix]
	    del temp_filterExpFactor[ix]

        self.filterRank = self.filterMinBrigSorted[:]
        self.filterRank[-1] = 1.0
        numFilters = len(self.filterMinBrigSorted)
        for ix in range(numFilters-1):
            if self.filterMinBrigSorted[-ix-2] > self.filterMinBrigSorted[-ix-1]:
                self.filterRank[-ix-2]=self.filterRank[-ix-1] + 1.0
            else:
                self.filterRank[-ix-2]=self.filterRank[-ix-1]

        self.relativeRankForFilter = {}
        self.basefilterWavelenSorted = {}
	self.ExposureFactor = {}
        for ix in range(numFilters):
            self.relativeRankForFilter[self.filterNamesSorted[ix]] = self.filterRank[ix]/self.filterRank[0]
            self.basefilterWavelenSorted[ix] = math.pow((0.50 / float(self.filterWavelenSorted[ix])),0.2)
	    self.ExposureFactor[self.filterNamesSorted[ix]] = self.filterExpFactorSorted[ix]
        return
    
    
    def __del__ (self):
        """
        Destructor: close the log file.
        """
        try:
            self.log.close ()
        except:
            pass
        return

    def computeFiltersForSky(self, brightness,seeing,airmass):
        """
        Computes a list of adequate filters according to the sky brightness
        """
        # NOTE Require sky brightness to be precomputed and passed as parameter

        filterList = {}
        air_3_5 = math.pow(airmass,0.6)
        for ix in range(len(self.filterNamesSorted)):
            #print "%d" % (ix)
            if self.filterMinBrigSorted[ix] < brightness < self.filterMaxBrigSorted[ix]:
                # Layer on adjustments to seeing:
                # entered with: raw -> tooGood 
                # adding on: wavelength -> airmass -> telescopeSystematics
                wvSee = seeing * self.basefilterWavelenSorted[ix]
                adjustSee = math.sqrt (math.pow (wvSee*air_3_5, 2) + \
                                   math.pow(self.telSeeing*air_3_5, 2) + \
                                   math.pow (self.opticalDesSeeing, 2) + \
                                   math.pow (self.cameraSeeing, 2))
                filterList[self.filterNamesSorted[ix]] = adjustSee

        return filterList

    def computeFilterSeeing(self, seeing, airmass):
        filterList = {}
        air_3_5 = math.pow(airmass,0.6)
        for ix in range(len(self.filterNamesSorted)):
            # Layer on adjustments to seeing:
            # entered with: raw -> tooGood
            # adding on: wavelength -> airmass -> telescopeSystematics
            wvSee = seeing * self.basefilterWavelenSorted[ix]
            adjustSee = math.sqrt (math.pow (wvSee*air_3_5, 2) + \
                                   math.pow(self.telSeeing*air_3_5, 2) + \
                                   math.pow (self.opticalDesSeeing, 2) + \
                                   math.pow (self.cameraSeeing, 2))
            filterList[self.filterNamesSorted[ix]] = adjustSee

        return filterList

