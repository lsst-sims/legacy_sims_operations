#!/usr/bin/env python

"""
Distribution

Inherits from: LSSTObject : object

Class Description
Distribution describes the way a given event (e.g. performing a 
sequence of observations) is repeated over time. A Distribution is 
characterized by a function and a method that, using that function, 
predicts when the next event should take place.


Method Types
Constructor/Initializers
- __init__

Next Event
- eventTime

Internal Use
- computeNumEvents

"""



from utilities import *
from LSSTObject import *




class Distribution (LSSTObject):
    """
    Base class for the Distribution hiarchy.
    """
    def __init__ (self, 
                  date, 
                  duration,
                  log=False, 
                  logfile='./Distribution.log',
                  verbose=-1):
        """
        Standard initializer.
        
        date:       date, in seconds from January 1st (start of the 
                    simulated year).
        duration:   number of simulated seconds the distribution is
                    valid.
        log:        False if not set, else: log = logging.getLogger("...")
        logfile:    name (and path) of the desired log file (defaults
                    to './Distribution.log'.
        verbose:    Log verbosity:-1=none, 0=minimal, 1=wordy, >1=verbose
        """
        self.date = date
        self.duration = duration
        
        # The total number of events to distribute. It depends on the 
        # particular subclass and on its duration in time.
        self.computeNumEvents ()
        
        # The number of event in an atomic sequence
        self.numAtomic = None
        
        self.log = log
        self.logfile = logfile
        self.verbose = verbose
        return
    
    
    def computeNumEvents (self):
        """
        Compute the total number of events given the distribution type
        and its duration.
        
        Subclasses should override this method. The default 
        implementation returns self.numEvents
        """
        self.numEvents = None
        return
        
    
    
    def eventTime (self, i):
        """
        Compute time at which the i-th event should occur. The current
        implementation simply does a sanity check. Each Distribution 
        subclass should override this method.
        
        Input
        i:      event number. Numbering starts from 0.
        
        Return
        None
        """
        if (i > self.numEvents):
            raise (IndexError, 'i > self.numEvents')
        elif (i < 0):
            raise (IndexError, 'i < 0')
        return (None)




class LinearDistribution (Distribution):
    """
    Linear distribution: the self.numEvents are evenly distributed 
    over self.duration seconds starting from self.date.
    """
    def __init__ (self, 
                  date, 
                  duration, 
                  interval,
                  log=False,
                  logfile='./Distribution.log',
                  verbose=-1):
        """
        Custom initializer: we need the frequency of the distribution.
        
        date:       date, in seconds from January 1st (start of the 
                    simulated year).
        duration:   number of simulated seconds the distribution is
                    valid.
        interval:   number of seconds between observations. Must be
                    > 0.
        log:        False if not set, else: log = logging.getLogger("...")
        logfile:    name (and path) of the desired log file (defaults
                    to './Distribution.log')
        verbose:    Log verbosity:-1=none, 0=minimal, 1=wordy, >1=verbose
        """
        if (interval <= 0):
            raise (ValueError, 'interval must be > 0')
        self.interval = interval
        self.log=log
        self.logfile=logfile
        self.verbose=verbose
        
        # Run the superclass init 
        super (LinearDistribution, self).__init__ (date, 
                                                   duration, 
                                                   self.log,
                                                   self.logfile, 
                                                   verbose)
        self.numAtomic = 1
        return
        
        
    def computeNumEvents (self):
        """
        Compute the total number of events for a linear distribution.
        """
        self.numEvents = int (self.duration / self.interval)
        return
    
    
    
    def eventTime (self, i):
        """
        Compute time at which the i-th event should occur.
        
        Input
        i:      event number. Numbering starts from 0.
        
        Return
        The time for the i-th event, rounded to the next integer 
        (seconds).
        """
        super (LinearDistribution, self).eventTime (i)
        
        t = self.date + i * (self.duration / self.numEvents)
        return (int (round (t)))



class LogDistribution (Distribution):
    """
    Log distribution: the self.numEvents are distributed over 
    self.duration seconds starting from self.date using a log
    function.
    """
    def __init__ (self, 
                  date, 
                  duration, 
                  interval,
                  log=False, 
                  logfile='./Distribution.log',
                  verbose=-1):
        """
        Custom initializer: we need the frequency of the distribution.
        
        date:       date, in seconds from January 1st (start of the 
                    simulated year).
        duration:   number of simulated seconds the distribution is
                    valid.
        interval:   log (seconds) between observations. Must be > 0.
        log:        False if not set, else: log = logging.getLogger("...")
        logfile:    name (and path) of the desired log file (defaults
                    to './Distribution.log'
        verbose:    Log verbosity:-1=none, 0=minimal, 1=wordy, >1=verbose
        """
        if (interval <= 0):
            raise (ValueError, 'interval must be > 0')
        self.interval = interval
        self.log = log
        self.logfile=logfile
        self.verbose=verbose
        
        # Run the superclass init 
        super (LogDistribution, self).__init__ (date, 
                                                duration, 
                                                log, 
                                                logfile,
                                                verbose)
        self.numAtomic = 1
        return
    
    
    
    def computeNumEvents (self):
        """
        Compute the total number of events for a log distribution.
        """
        self.numEvents = int (math.log (self.duration) / self.interval)
        return
    
    
    def eventTime (self, i):
        """
        Compute time at which the i-th event should occur.
        
        Input
        i:      event number. Numbering starts from 0.
        
        Return
        The time for the i-th event, rounded to the next integer 
        (seconds).
        """
        super (LogDistribution, self).eventTime (i)
        
        t = self.date + 10. ** (i * self.interval)
        return (int (round (t)))



class IvezicDistribution (Distribution):
    """
    Ivezic distribution: the self.numEvents are distributed over 
    self.duration seconds starting from self.date. The first event 
    happens at self.date, the second one after SHORT_STEP seconds from
    the first one. The third and fourth are separated by SHORT_STEP 
    one from the other and by MEDIUM_STEP from the second. Fourth and
    fifth, SHORT_STEP and LONG_STEP.
    
    The whole sequence is truncated or extended if needed (and 
    depending on self.duration and self.numEvents). If the sequence is
    repeated, we do so after NEXT_STEP seconds.
    """
    # Class variables
    SHORT = 900
    MEDIUM = 86400 * 2
    LONG = 86400 * 6
    NEXT = 86400 * 5
    
    def __init__ (self, 
                  date=0, 
                  duration=0.0,
                  intervals=[],
                  repeats=1,
                  repeatdelay=0.0,
                  log=False, 
                  logfile='./Distribution.log',
                  verbose=-1):
        """
        Standard initializer.
        
        What we do differently is computing the delay times at 
        different stages in the sequence.
        
        date:       date, in seconds from January 1st (start of the 
                    simulated year).
        duration:   number of simulated seconds the distribution is
                    valid.
        log:        False if not set, else: log = logging.getLogger("...")
        logfile:    name (and path) of the desired log file (defaults
                    to './Distribution.log'
        verbose:    Log verbosity:-1=none, 0=minimal, 1=wordy, >1=verbose
        """

        self.log = log
        self.logfile=logfile
        self.verbose = verbose

        # Delays
        if intervals == []:
            self.delay = [self.SHORT,
                          self.MEDIUM,
                          self.SHORT,
                          self.LONG,
                          self.SHORT]
        else:
            self.delay = intervals

        if repeatdelay == 0.0:
            self.delayNext = self.NEXT
        else:
            self.delayNext = repeatdelay
            
        
        self.seqDelay = 0.0
        for t in self.delay:
            self.seqDelay += t
            # length of an atomic sequence
        
        # Number of full atomic sequences
        if duration > 0.0:
            self.nSequences = int(float(duration)/float(self.seqDelay+self.delayNext))
            if duration-(self.nSequences*(self.seqDelay+self.delayNext)) >= (self.seqDelay):
                 self.nSequences += 1
        else:
            self.nSequences=max(repeats,1)
            duration = self.nSequences*self.seqDelay+(self.nSequences-1)*self.delayNext

        super (IvezicDistribution, self).__init__ (date, 
                                                   duration, 
                                                   self.log, 
                                                   self.logfile,
                                                   verbose)
        self.numAtomic = len(self.delay)+1

        return
        
        
    def computeNumEvents (self):
        """
        Compute the total number of events for a linear distribution.
        """
        self.numEvents = 0
        
        # We have 6 events in an atomic sequence. This, times the 
        # number of atomic sequences should give us numEvents (more or
        # less)
        #if (self.nSequences):
        #    t = self.duration - (self.delayNext * self.nSequences)
        #else:
        #    t = self.duration
        
        #for i in range (5):
        #    t -= self.delay[i]
        #    if (t <= 0):
        #        break
        #self.numEvents = i
        #if (self.nSequences):
        #    self.numEvents += self.nSequences * 6

        self.numAtomic = len(self.delay)+1
        self.numEvents = self.nSequences*self.numAtomic
        
        return
    
    
    def eventTime (self, i):
        """
        Compute time at which the i-th event should occur.
        
        Input
        i:      event number. Numbering starts from 0.
        
        Return
        The time for the i-th event, rounded to the next integer 
        (seconds).
        """
        super (IvezicDistribution, self).eventTime (i)
        
        # The atomic sequence has only six events. If i >= 6 then we 
        # are repeating the sequence. If i < 6, then we still are in 
        # the atomic sequence.
        #j = i
        #t = self.date
        #if (j > 5):
        #    n = int (j / self.numAtomic)
        #    j = j % self.numAtomic
            
        #    t += self.seqDelay * n
        #    t += self.delayNext * n
        
        # Since self.delay lists the delay between consecutive 
        # events starting from event 1 vrt event 0, we need to 
        # decrement j
        #j -= 1
        
        # Now j refers to an index in the atomic sequence
        #k = 0
        #while (k <= j):
        #    t += self.delay[k]
        #    k += 1

        fullseqs = int(i / self.numAtomic)
        remains  =     i % self.numAtomic

        t = self.date + fullseqs*self.seqDelay
        for j in range(remains):
            t += self.delay[j]

        return (t)
    
    
    
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
        linearInterval = 86400 * 2
        logInterval = math.log (43200)
        
        linearKnownValues = (((0, 0),
                              (1, 172800),
                              (2, 345600), 
                              (3, 518400),
                              (4, 691200), 
                              (5, 864000), 
                              (6, 1036800), 
                              (7, 1209600),
                              (8, 1382400), 
                              (9, 1555200),
                              (10, 1728000),
                              (11, 1900800),
                              (12, 2073600),
                              (13, 2246400),
                              (14, 2419200)))
        logKnownValues = ()
        ivezicKnownValues = ((0, 0),               # start
                             (1, 900),             # +15m
                             (2, 173700),          # +2d
                             (3, 174600),          # +15m
                             (4, 693000),          # +6d
                             (5, 693900),          # +15m
                             (6, 1125900),         # +5d
                             (7, 1126800),         # +15m
                             (8, 1299600),         # +2d
                             (9, 1300500),         # +15m
                             (10, 1818900),        # 6d
                             (11, 1819800),        # +15m
                             (12, 2251800),        # 5d
                             (13, 2252700),        # +15m
                             (14, 2425500))        # 2d
        
        def testLinearNextEvent (self):
            d = LinearDistribution (date=0,
                                    duration=self.duration,
                                    interval=self.linearInterval)
            
            for (input, expectedResult) in self.linearKnownValues:
                result = d.eventTime (input)
                self.assertEqual (result, expectedResult)
            return
        
        def testLogNextEvent (self):
            # TBD
            return
        
        def testIvezicNextEvent (self):
            d = IvezicDistribution (date=0,
                                    duration=self.duration)
            
            for (input, expectedResult) in self.ivezicKnownValues:
                result = d.eventTime (input)
                self.assertEqual (result, expectedResult)
            return
    
    # Run the tests
    unittest.main ()





















 
