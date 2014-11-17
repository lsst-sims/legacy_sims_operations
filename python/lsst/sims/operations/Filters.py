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

skyBrightKeys = [0, 18, 50, 80, 100]
filterOffset = { }

# Corrections for moonPhase = 0 percent (new moon)
filterOffset['u',0.] =  0.66
filterOffset['g',0.] =  0.41
filterOffset['r',0.] = -0.28
filterOffset['i',0.] = -1.36
filterOffset['z',0.] = -2.15

# Corrections for moonPhase = 18 percent
filterOffset['u',18.] =  0.28
filterOffset['g',18.] =  0.30
filterOffset['r',18.] = -0.19
filterOffset['i',18.] = -1.17
filterOffset['z',18.] = -1.99

# Corrections for moonPhase = 50 percent
filterOffset['u',50.] = -1.05
filterOffset['g',50.] =  0.03
filterOffset['r',50.] =  0.02
filterOffset['i',50.] = -0.96
filterOffset['z',50.] = -1.78

# Corrections for moonPhase = 80 percent
filterOffset['u',80.] = -1.83
filterOffset['g',80.] = -0.08
filterOffset['r',80.] =  0.10
filterOffset['i',80.] = -0.78
filterOffset['z',80.] = -1.54

# Corrections for moonPhase = 100 percent (full moon)
filterOffset['u',100.] = -2.50
filterOffset['g',100.] = -0.35
filterOffset['r',100.] =  0.31
filterOffset['i',100.] = -0.47
filterOffset['z',100.] = -1.16


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


    def computeSkyBrightnessForFilter(self, filter, skyBrightness, date, twilightProfile, moonProfileAltAz):

	(sunriseTwil, sunsetTwil) = twilightProfile
	(moonRA_RAD, moonDec_RAD, moonPhase_PERCENT, moonAlt_RAD, moonAz_RAD) = moonProfileAltAz

        # set y skybrightness for any kind of sky
        if (filter == 'y'):
	    filterSkyBright = 17.3
        else:      # g,r,i,z,u
	    # If moon below horizon, use new moon offset for filter
            # brightness - MM
            if (math.degrees(moonAlt_RAD) <= -6.0):
		adjustBright = filterOffset[filter,0.]

            # Interpolate if needed. Note: moonPhase is a float not int
            elif (moonPhase_PERCENT not in skyBrightKeys):
		i = 0
		while (skyBrightKeys[i] < moonPhase_PERCENT):
		    i = i+1

                # find upper and lower bound
                upperMoonPhase = skyBrightKeys[i]
                lowerMoonPhase = skyBrightKeys[i-1]
                lowerAdjustBright = filterOffset[filter,lowerMoonPhase]
                upperAdjustBright = filterOffset[filter,upperMoonPhase]
                # linear interpolation
                adjustBright = lowerAdjustBright + (((moonPhase_PERCENT - lowerMoonPhase)*(upperAdjustBright - lowerAdjustBright))/(upperMoonPhase - lowerMoonPhase))

	    else:          # moon not set and moon phase is key
		adjustBright = filterOffset[filter, moonPhase_PERCENT]
            filterSkyBright = skyBrightness + adjustBright

            # z sky brightness should never be under 17.0
            if (filter == 'z') and (filterSkyBright < 17.0):
		filterSkyBright = 17.0

        # If twilight, set brightness for z and y
	if ( date < sunsetTwil) or (date > sunriseTwil):
	    if (filter == 'z') or (filter == 'y'):
		filterSkyBright = 17.0

	return filterSkyBright


