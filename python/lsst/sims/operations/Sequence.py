#!/usr/bin/env python

"""
Sequence

Inherits from: LSSTObject : object

Class Description
We only support two sequence types, at the moment. Each type is a 
subclass of the Sequence root class:
1. Observe the same field using the same filter and one of the 
   supported Distributions (linear, log, Ivezic).
2. Observe the same filed using two filters in a fixed alternation (
   e.g. V-R--V-B--V-R). Use one of the supported Distributions.


Method Types
Constructor/Initializers
- __init__

Filter
- chooseFilter

Position in the sequence
- getPosition
"""



from utilities import *
from LSSTObject import *
from Distribution import *




class Sequence (LSSTObject):
    """
    Base class for the Sequence hiarchy.
    """
    def __init__ (self, 
                  propID,
                  field, 
                  filters, 
                  distribution,
                  date, 
                  duration,
                  log=None, 
                  logfile='./Sequence.log',
                  verbose=0):
        """
        Standard initializer.
        
        propID      ID of the parent Proposal instance
        field:      ID of the field (i.e. position on the sky) this
                    Sequence instance applies to.
        filters:    array of filterID.
        distribution:  the Distribution object to use for this 
                    Sequence instance.
        date:       date, in seconds from January 1st (start of the 
                    simulated year).
        duration:   number of simulated seconds the distribution is
                    valid.
        log         False if not set, else: log = logging.getLogger("...")
        logfile     Name (and path) of the desired log file.
                    Defaults "./Sequence.log".
        verbose:    Log verbosity: 0=minimal, 1=wordy, >1=very verbose
                                                                                

        """
        self.field = field
        self.distribution = distribution
        self.filters = filters
        
        self.propID = propID
        self.date = date
        
        ## Setup logging
        #if (verbose < 0):
        #    logfile = "/dev/null"
        #elif ( not log ):
        #    print "Setting up Sequence logger"
        #    log = logging.getLogger("Sequence")
        #    hdlr = logging.FileHandler(logfile)
        #    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        #    hdlr.setFormatter(formatter)
        #    log.addHandler(hdlr)
        #    log.setLevel(logging.INFO)
        #                                                                        
        #self.log=log
        #self.logfile=logfile
        #self.verbose = verbose

        return
    
    
    def getField (self):
        """
        Getter method: return the field ID.
        """
        return (self.field)
    
    
    def getFilters (self):
        """
        Getter method: return the filter ID array
        """
        return (self.filters)
    
    
    def getDistribution (self):
        """
        Getter method: return the Distribution object in use.
        """
        return (self.distribution)
    
    
    def nextFilters (self):
        """
        Return the array of allowed filters for the next event.
        
        Subclasses should override this method. The default 
        implementation does nothing.
        """
        return (None)
    
    
    def nextDate (self):
        """
        Return the dates of the next event in the sequence.
        
        Subclasses should override this method. The default 
        implementation does nothing.
        """
        return (None)

    def nextPeriod (self):
        """
        Returns the time interval between the next event
        and the previous event.
        """
        return (None)
    
    def nextDateFilter (self):
        """
        Return a two-element array (date, filters) by invoking 
        self.nextDate () and self.nextFilters ().
        """
        date = self.nextDate ()
        filters = self.nextFilters ()
        return ((date, filters))
        
    def closeEvent (self, date, filter):
        """
        Simply register the fact that one of our observations has been
        carried out.
        
        Subclasses should override this method. The default 
        implementation does nothing.
        """
        return
    


class OneFilterLogSequence (Sequence):
    """
    Implement a simple (but not trivial) observing strategy: one field
    one filter and a logarithmic cadence.
    """
    pass



class IvezicSequence (Sequence):
    """
    Implement the standard Ivezic sequence using two filters. One 
    filter is the primary filter and will be used for every first
    exposure in each pair.
    """
    def __init__ (self, 
                  propID, 
                  field,
		  seqNum, 
                  filters, 
                  distribution,
                  date, 
                  duration,
		  maxmissed,
                  log=None, 
                  logfile='./Sequence.log',
                  verbose=0):
        """
        Standard initializer.
        
        propID      ID of the parent Proposal instance
        field:      ID of the field (i.e. position on the sky) this
                    Sequence instance applies to.
        filters:    array of filterID.
        distribution:  the Distribution object to use for this 
                    Sequence instance.
        date:       date, in seconds from January 1st (start of the 
                    simulated year).
        duration:   number of simulated seconds the distribution is
                    valid.
        log:        True if logfile should be generated
        logfile:    name (and path) of the desired log file (defaults
                    to './Sequence.log')
        verbose:    integer specifying the verbosity level (defaults 
                    to 0 meaning quite).
        """
        super (IvezicSequence, self).__init__ (propID,
                                               field, 
                                               filters, 
                                               distribution,
                                               date, 
                                               duration,
                                               log, 
                                               logfile,
                                               verbose)
        
        # self.distribution needs to be a IvezicDistribution
        if (not isinstance (distribution, IvezicDistribution)):
            raise (TypeError, 'distribution needs to be a ' +
                              'IvezicDistribution.')
        
        # self.fields needs to be a non empty array
        if (not isinstance (self.filters, list) and
            not isinstance (self.filters, tuple)):
            raise (TypeError, 'filters needs to be a list.')
        if (not len (self.filters)):
            raise (ConfigError, 'filters needs to be non empty.')

	self.maxMissedEvents = maxmissed
        
        # Setup primary and secondary filters
        self.primaryFilter = self.filters[0]
        try:
            self.secondaryFilters = self.filters[1:]
        except:
            self.secondaryFilters = [self.primaryFilter]
        
        # the self.obsHistory array lists date and filter for 
        # each event. Its index is the observation number.
        self.obsHistory = []
	self.misHistory = []
        
        # Number of events in the atomic sequence
        self.numAtomic = self.distribution.numAtomic

        self.lost = False

	self.lastFilters = []

	self.seqNum = seqNum

        return
   
    def GetDuration(self):

	return self.distribution.duration 
    
    def GetNumTargetEvents(self):
        """
        Return the total number of events in the sequence given its
        duration and distribution.
        
        Subclasses should override this method. The default 
        implementation does nothing.
        """
        return (self.distribution.numEvents)
    
    
    def nextFilters (self):
        """
        Return the array of allowed filters for the next event.
        
        Subclasses should override this method. The default 
        implementation does nothing.
        """
        i = len (self.obsHistory)

        # if this is the second of a pair, then the filter
        # should be the same than the first of this pair
        if i%2==1:
            filters = [self.obsHistory[i-1][1]]
        else:
            filters = self.filters

        return filters

    def GetLastFilters(self):

	return self.lastFilters
    
    def nextDate (self):
        """
        Return the dates of the next event in the sequence.
        """
        i = len (self.obsHistory)
        
        date = self.distribution.eventTime (i)

        if i>0:
            delta = date - self.distribution.eventTime(i-1)
            date = self.obsHistory[i-1][0] + delta
            
        return (date)
    
    def nextPeriod(self):
        
        i = len (self.obsHistory)
        
        date = self.distribution.eventTime (i)
        if i>0:
            period = date - self.distribution.eventTime(i-1)
        else:
            period = self.distribution.eventTime(i+1) - date

        return (period)
    
    def GetProgress(self, type='full'):
        """
        Return the current sequence completition percentage given the
        type of sequence (either "atomic" or "full").
        
        Subclasses should override this method. The default 
        implementation does nothing.
        """
        n = len (self.obsHistory)
        
        if (type == 'atomic'):
            if (self.numAtomic == 0):
               return 1.0

            # We are at the n-th event. We know that there are only
            # self.numAtomic in each atomic sequence.
            if (n > self.numAtomic):
                n = n % self.numAtomic
                if (n == 0):
                    n = self.numAtomic
            
            # Now we have "normalized" n to the atomic sequence index
            percent = float(n) / float(self.numAtomic)
        elif (type == 'full'):
            numEvents = self.GetNumTargetEvents ()
            if (numEvents == 0):
               return 1.0
            percent = float(n) / float(numEvents)
        else:
            raise (InputParamError, 'type="atomic"|"full".')
        return (percent)
    
    
    def closeEvent (self, date, filter):
        """
        Simply register the fact that one of our observations has been
        carried out and uodate self.obsHistory
        """
        # if this is the first observation for the sequence
        # sets its start date to the actual observation date.
        if not self.IsActive():
            self.date = date
            self.distribution.date = date

        self.obsHistory.append ((date, filter))

	if filter in self.lastFilters:
	    ix=self.lastFilters.index(filter)
            del self.lastFilters[ix]
	self.lastFilters.insert(0,filter)

        return

    def missEvent (self, date, filter=None):
	"""
	Event missed. obsHistory will store the event as if it were observed,
	and misHistory will register the miss.
	"""

        if len(self.misHistory) >= self.maxMissedEvents:
            self.SetLost()
	    return

	ix = len(self.obsHistory)

	if ((filter==None) and (ix>0)):
	    fil = self.obsHistory[ix-1][1]
	else:
	    fil = filter

	dat = self.nextDate()

	self.closeEvent(dat, fil)

	self.misHistory.append((dat, ix))

	return

    def GetMissedEvents (self):

	return len(self.misHistory)

    def GetNumActualEvents(self):

	return len(self.obsHistory) - len(self.misHistory)

    def GetRemainingAllowedMisses(self):

	return self.maxMissedEvents - len(self.misHistory)

    def IsComplete(self):

	if self.lost:
	    return False

        if len(self.obsHistory) ==  self.GetNumTargetEvents():
            return True
        else:
            return False
        
    def IsActive(self):

        if self.obsHistory == []:
            return False
        else:
            return True

    def IsIdle(self):

	if self.obsHistory == [] and not self.lost:
	    return True
	else:
	    return False

    def IsProgressing(self):

        if self.obsHistory == []:
            return False
        elif self.lost:
            return False
        elif self.IsComplete():
            return False
        else:
            return True

    def SetLost(self):

        self.lost = True
        
    def IsLost(self):

        return self.lost
    
    def Restart(self, seqNum):

        self.obsHistory = []
	self.misHistory = []
        self.date = 0.0
        self.distribution.date = 0.0
        self.lost = False
	self.lastFilters = []

	self.seqNum = seqNum
        
        return
    
# 
# UNIT TESTS
# 
if (__name__ == '__main__'):
    import unittest
    
    class KnownValues (unittest.TestCase):
        """
        Make sure that we get what we expect.
        """
        duration = 86400 * 30
        field = 0
        
        ivezicKnownValues = ((0, 'V'),                  # start
                             (900, ('B','R')),          # +15m
                             (173700, 'V'),             # +2d
                             (174600, ('B','R')),       # +15m
                             (693000, 'V'),             # +6d
                             (693900, ('B','R')),       # +15m
                             (1125900, 'V'),            # +5d
                             (1126800, ('B','R')),      # +15m
                             (1299600, 'V'),            # +2d
                             (1300500, ('B','R')),      # +15m
                             (1818900, 'V'),            # 6d
                             (1819800, ('B','R')),      # +15m
                             (2251800, 'V'),            # 5d
                             (2252700, ('B','R')),      # +15m
                             (2425500, 'V'))            # 2d
        
        def testNextDateFilter (self):
            d = IvezicDistribution (date=0,
                                    duration=self.duration)
            s = IvezicSequence (propID=0,
                                date=0,
                                duration=self.duration,
                                field=self.field,
                                filters=('V', 'B', 'R'),
                                distribution=d)
            for expectedResult in self.ivezicKnownValues:
                result = s.nextDateFilter ()
                self.assertEqual (result, expectedResult)
                # Notify the Sequence object that we observed one of
                # its fields.
                date = result[0]
                filter = result[1]
                if (isinstance (filter, list) or
                    isinstance (filter, tuple)):
                    filter = filter[0]
                s.closeEvent (date, filter)
    
    
    
    # Run the tests
    unittest.main ()





















 
