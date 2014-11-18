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

SEQ_IDLE     = 0
SEQ_ACTIVE   = 1
SEQ_COMPLETE = 2
SEQ_LOST     = 3

class SubSequence (LSSTObject):
    """
    Base class for the Sequence hiarchy.
    """
    def __init__ (self, 
                  propID,
                  field,
		  WLtype,
		  subName,
		  subNested,
                  subFilters, 
		  subExposures,
                  subEvents,
                  subMaxMissed,
                  subInterval,
                  subWindowStart,
                  subWindowMax,
                  subWindowEnd):

        self.propID         = propID
        self.field          = field
	self.WLtype	    = WLtype
	self.subName	    = subName
	self.subNested      = subNested
        self.subEvents      = int(subEvents)
        self.subMaxMissed   = int(subMaxMissed)
        self.subInterval    = subInterval
        self.subWindowStart = subWindowStart
        self.subWindowMax   = subWindowMax
        self.subWindowEnd   = subWindowEnd

	self.nestedSubSequence = None

#	print subFilters
#	print subExposures

	self.subFilters = []
	self.subExposures = [1]
	if subNested == None:
	    for filter in subFilters.split(','):
		if filter != '':
		    self.subFilters.append(filter)
	    self.subExposures = []
	    for exposures in str(subExposures).split(','):
	        if exposures != '':
        	    self.subExposures.append(int(eval(exposures)))
	self.Nsubevents = len(self.subFilters)
	    
#	print self.subFilters
#	print self.subExposures

        visitIntervals = []
        for i in range(self.subEvents-1):
            visitIntervals.append(eval(str(self.subInterval)))

        self.distribution = IvezicDistribution(date=0,
                                               duration   =0.0,
                                               intervals  =visitIntervals,
                                               repeats    =1,
                                               repeatdelay=0.0)

        self.Restart()
        
        return

    def attachNestedSubSequence(self, subseq):

	self.nestedSubSequence = subseq

	self.Restart()

	return

    def Restart(self):

        if self.nestedSubSequence != None:
            self.nestedSubSequence.Restart()
	    self.exposuresLeft = 1
	else:
	    self.exposuresLeft = self.subExposures[0]

	self.date = 0

        self.allHistory = []
        self.obsHistory = []
        self.misHistory = []
	self.obsHistID  = []
	self.misHistID  = []

	self.subeventIndex = 0

        self.aborted = False
        self.pairNum = 0

        self.UpdateState()

        return

    def UpdateState(self):

	if self.nestedSubSequence != None:
	    self.nestedSubSequence.UpdateState()

        self.nAllEvents = len(self.allHistory)
        self.nObsEvents = len(self.obsHistory)
        self.nMisEvents = len(self.misHistory)
        
        if (self.aborted == True) or ((self.nMisEvents > self.subMaxMissed) and not self.WLtype):
            self.state = SEQ_LOST
            
        elif ((self.nAllEvents >= self.subEvents) and not self.WLtype) or ((self.nObsEvents >= self.subEvents) and self.WLtype):
            self.state = SEQ_COMPLETE

        elif ((self.nAllEvents == 0) and not self.IsEventInProgress()):
            self.state = SEQ_IDLE

        else:
            self.state = SEQ_ACTIVE

	if (self.exposuresLeft == 1) and (self.subeventIndex == self.Nsubevents-1):
	    self.exclusiveBlockNeeded = False
	else:
	    self.exclusiveBlockNeeded = True

        if self.CollectPairs():
            self.pairNum = self.nAllEvents/2 + 1
            
        return self.state

    def IsIdle(self):

        if (self.state == SEQ_IDLE):
            return True
        else:
            return False

    def IsActive(self):

        if self.state == SEQ_ACTIVE:
            return True
        else:
            return False
    
    def IsComplete(self):

        if self.state == SEQ_COMPLETE:
            return True
        else:
            return False

    def IsLost(self):

        if self.state == SEQ_LOST:
            return True
        else:
            return False
    
    def GetFilterList(self):

	if self.nestedSubSequence != None:
	    return self.nestedSubSequence.GetFilterList()
	return list(self.subFilters)

    def GetNextFilter(self):

	if self.nestedSubSequence != None:
	    return self.nestedSubSequence.GetNextFilter()
	return self.subFilters[self.subeventIndex]

    def GetExclusiveBlockNeed(self):

	if self.nestedSubSequence != None:
	    return self.nestedSubSequence.GetExclusiveBlockNeed()
	return self.exclusiveBlockNeeded

    def GetNextDate(self):

	if self.WLtype:
	    history=self.obsHistory
	else:
	    history=self.allHistory

	i = len(history)

        if i > 0:
            delta = self.distribution.eventTime(i) - self.distribution.eventTime(i-1)
            nextdate = history[i-1] + delta
        else:
            nextdate = self.date + self.GetNextInterval()

        return (nextdate)

    def GetNextInterval(self):
        
        if self.WLtype:
            i = len(self.obsHistory)
        else:
            i = len(self.allHistory)
        
        if i>0:
            interval = self.distribution.eventTime(i) - self.distribution.eventTime(i-1)
        else:
            interval = self.distribution.eventTime(i+1) - self.distribution.eventTime(i)

        return (interval)

    def GetListObsID(self):

	return self.obsHistID

    def GetListMisID(self):

	return self.misHistID

    def HasTimeWindow(self):

	if not self.WLtype:
	    return True
	elif self.subInterval == 0:
	    return False
	elif (len(self.allHistory) % 2) == 0:
	    return False
	else:
	    return True

    def CollectPairs(self):

        if self.WLtype and self.subInterval != 0:
            return True
        else:
            return False

    def RankTimeWindow(self, date):
        """
        Evaluates the priority of an event according to the proximity to the
        event time.

        Input
        deltat: the proximity in seconds to the event (current T - event T)
        scale:  the time scale for the window. Default 5 minutes.
        """

	# if this subsequence has a nested subsequence, and if this nested subsequence
	# is in progress, then the time window has to be taken from the subsequence
	# otherwise the nested subsequence is IDLE and the time window is taken from
	# this subsequence (parent)
	if self.nestedSubSequence != None:
	    if self.nestedSubSequence.IsIdle() == False:
		return self.nestedSubSequence.RankTimeWindow(date)

        scale    = self.GetNextInterval()
        deltat   = date - self.GetNextDate()
        
        w_start  = self.subWindowStart*scale
        w_inflex = self.subWindowMax  *scale
        w_end    = self.subWindowEnd  *scale

        if deltat <= w_start-DAY:
            rank = -0.1
        elif deltat <= w_start:
            rank = 0.0
        elif deltat <= w_inflex:
            rank = (deltat-w_start)/(w_inflex-w_start)
        elif deltat <= w_end:
            rank = 1.0
        else:
            rank = -1.0
            # event missed
            
        return rank

    def ObserveEvent(self, date, obsHistID):

	if self.nestedSubSequence != None:
	    self.nestedSubSequence.ObserveEvent(date, obsHistID)
	    if self.nestedSubSequence.IsComplete() == False:
		return False
	    else:
		self.nestedSubSequence.Restart()
 
	self.exposuresLeft -= 1
	#print "exposures left = " + str(self.exposuresLeft)
	if self.exposuresLeft > 0:
	    self.UpdateState()
	    return False

	self.subeventIndex += 1
	#print "subevent index = " + str(self.subeventIndex)
	#print "Nsubevents = " + str(self.Nsubevents)
	if self.subeventIndex < self.Nsubevents:
	    self.exposuresLeft = self.subExposures[self.subeventIndex]
	    #print "left = " + str(self.exposuresLeft)
	    #print 'subeventIndex<Nsubevents '+str(self.subeventIndex)+'<'+str(self.Nsubevents)
	    self.UpdateState()
	    return False

	self.subeventIndex = 0
	self.exposuresLeft = self.subExposures[0]

        self.allHistory.append(date)
	self.obsHistID.append(obsHistID)
	#print ("subseq=%s history=%s" % (self.subName, str(self.allHistory)))
        self.obsHistory.append(date)

        if len(self.allHistory) == 1:
            self.distribution.date = date
	    self.date = date
            
        self.UpdateState()
	#print self.state
        return True

    def MissEvent(self, date, misHistID):

	if self.nestedSubSequence != None:
	    self.nestedSubSequence.MissEvent(date, misHistID)
	    if self.nestedSubSequence.IsLost() == False:
		return

	d = self.GetNextDate()

	if ((self.nMisEvents < self.subMaxMissed) or self.WLtype):
	    self.allHistory.append(d)
	    self.misHistID.append(misHistID)
        self.misHistory.append(d)

        self.subeventIndex = 0
        self.exposuresLeft = self.subExposures[0]

        self.UpdateState()

        return

    def Abort(self):

	if self.nestedSubSequence != None:
	    self.nestedSubSequence.Abort()

        self.aborted = True

        self.updateState()

        return

    def GetProgress(self):

        if self.subEvents == 0:
           return 1.0

	if self.WLtype:
	    return float(self.nObsEvents)/float(self.subEvents)
	else:
            return float(self.nAllEvents)/float(self.subEvents)

    def IsEventInProgress(self):

	if self.nestedSubSequence != None:
	    return self.nestedSubSequence.IsEventInProgress()

	if self.subeventIndex > 0:
	    return True

	if (self.exposuresLeft < self.subExposures[0]):
	    return True

	return False

    def GetRemainingAllowedMisses(self):

	if self.WLtype:
	    return self.subEvents
	else:
	    return self.subMaxMissed - self.nMisEvents

class SuperSequence (LSSTObject):
    """
    Base class for the Sequence hiarchy.
    """
    def __init__ (self, 
                  propID,
                  field,
		  seqNum,
		  WLtype,
		  masterSubSequence,
		  subSeqName,
		  subSeqNested,
                  subSeqFilters,
		  subSeqExposures,
                  subSeqEvents,
                  subSeqMaxMissed,
                  subSeqInterval,
                  subSeqWindowStart,
                  subSeqWindowMax,
                  subSeqWindowEnd,
		  overflowLevel=0.0,
		  progressToStartBoost=1.0,
		  maxBoostToComplete=0.0,
                  log=None, 
                  logfile='./SuperSequence.log',
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

        self.propID		= propID
        self.field		= field
	self.WLtype		= WLtype
	self.masterSubSequence	= masterSubSequence
	self.subSeqName		= list(subSeqName)
	self.subSeqNested       = list(subSeqNested)
        self.subSeqFilters	= list(subSeqFilters)
	self.subSeqExposures	= list(subSeqExposures)
        self.subSeqEvents	= list(subSeqEvents)
        self.subSeqMaxMissed	= list(subSeqMaxMissed)
        self.subSeqInterval	= list(subSeqInterval)
        self.subSeqWindowStart	= list(subSeqWindowStart)
        self.subSeqWindowMax	= list(subSeqWindowMax)
        self.subSeqWindowEnd	= list(subSeqWindowEnd)
	self.overflowLevel      = overflowLevel
	self.progressToStartBoost = progressToStartBoost
	self.maxBoostToComplete = maxBoostToComplete

        self.subSequence = {}

	#first create all the subsequences
	for n in range(len(self.subSeqName)):
            name   = self.subSeqName[n]
	    nested = self.subSeqNested[n]
	    if nested == ".":
		nested = None
            self.subSequence[name] = SubSequence(self.propID,
       	                                        self.field,
               	                                WLtype,
                       	                        name,
						nested,
                                                self.subSeqFilters[n],
       	                                        self.subSeqExposures[n],
               	                                self.subSeqEvents[n],
                       	                        self.subSeqMaxMissed[n],
                               	                self.subSeqInterval[n],
                                       	        self.subSeqWindowStart[n],
                                               	self.subSeqWindowMax[n],
                                                self.subSeqWindowEnd[n])

	#second find the nested subsequences and attaches them
	nestedlist = []
#	for subseq in self.subSequence.keys():
        for subseq in sorted(self.subSequence.iterkeys()):
	    nested = self.subSequence[subseq].subNested
	    if nested != None:
		nestedsubseq = self.subSequence[nested]
		self.subSequence[subseq].attachNestedSubSequence(nestedsubseq)
		nestedlist.append(nested)
	#third leaves only the first level subsequences in the dictionary
	for nested in nestedlist:
	    del self.subSequence[nested]
	    self.subSeqName.remove(nested)

	if not self.masterSubSequence in self.subSeqName:
	    self.masterSubSequence = None

        self.Restart(seqNum)

        self.nTargetEvents = self.ComputeNumEvents()
        
        return
    
    def Restart(self, seqNum):

	self.seqNum = seqNum

        for name in self.subSeqName:
            self.subSequence[name].Restart()

	self.date = 0

        self.allHistory = []
        self.obsHistory = []
	self.misHistory = []

        self.aborted = False

        self.UpdateState()

        return

    def UpdateState(self):

        self.nAllEvents = len(self.allHistory)
        self.nObsEvents = len(self.obsHistory)
        self.nMisEvents = len(self.misHistory)

        if self.aborted == True:
            self.state = SEQ_LOST
        else:
            anylost     = False
            allcomplete = True
            allidle     = True
            for name in self.subSeqName:
                substate = self.subSequence[name].state
                if substate == SEQ_LOST:
                    anylost = True
		if substate != SEQ_COMPLETE:
                    allcomplete = False
                if substate != SEQ_IDLE:
                    allidle = False

            if anylost == True:
                self.state = SEQ_LOST
            elif allcomplete == True:
                self.state = SEQ_COMPLETE
            elif allidle == True:
                self.state = SEQ_IDLE
            else:
                self.state = SEQ_ACTIVE

        return self.state

    def GetPairNum(self, name):
        return self.subSequence[name].pairNum

    def IsIdle(self, name=None):

        if name == None:
            if self.state == SEQ_IDLE:
                return True
            else:
                return False
        elif self.masterSubSequence == None:
            return self.subSequence[name].IsIdle()
	elif name == self.masterSubSequence:
	    return self.subSequence[self.masterSubSequence].IsIdle()
	else:
	    return False
        
    def IsActive(self, name=None):

        if name == None:
            if self.state == SEQ_ACTIVE:
                return True
            else:
                return False
	elif self.masterSubSequence == None:
            return self.subSequence[name].IsActive()
	elif self.subSequence[name].IsIdle() and not self.subSequence[self.masterSubSequence].IsIdle():
	    return True
	else:
            return self.subSequence[name].IsActive()
        
    def IsComplete(self, name=None):

        if name == None:
            if self.state == SEQ_COMPLETE:
                return True
            else:
                return False
        else:
            return self.subSequence[name].IsComplete()

    def IsLost(self, name=None):

        if name == None:
            if self.state == SEQ_LOST:
                return True
            else:
                return False
        else:
            return self.subSequence[name].IsLost()
       
    def IsEventInProgress(self, subseq):

	return self.subSequence[subseq].IsEventInProgress()
 
    def GetFilterListForSubseq(self, subseq):

	return self.subSequence[subseq].GetFilterList()

    def ComputeNumEvents (self):
        """
        Return the total number of events in the sequence given its
        duration and distribution.
        
        Subclasses should override this method. The default 
        implementation does nothing.
        """
        N = 0
        for name in self.subSeqName:
            N += self.subSequence[name].subEvents
            
        return N

    def GetNumTargetEvents(self):

        return self.nTargetEvents

    def GetNumActualEvents(self):

	return self.nObsEvents

    def GetNumMissedEvents (self):

        return self.nMisEvents

    def GetExclusiveBlockNeed(self, subseq):

	return self.subSequence[subseq].GetExclusiveBlockNeed()

    def GetNextFilter(self, subseq):

	return self.subSequence[subseq].GetNextFilter()

    def GetNextDate (self, name):
        """
        Return the dates of the next event in the sequence.
        """

        return self.subSequence[name].GetNextDate()
   
    def GetListObsID(self):

	listObsID = []
	for subseq in self.subSeqName:
	    listObsID = listObsID + self.subSequence[subseq].GetListObsID()
	return listObsID
 
    def GetListMisID(self):

        listMisID = []
        for subseq in self.subSeqName:
            listMisID = listMisID + self.subSequence[subseq].GetListMisID()
        return listMisID

    def HasEventsTonight(self, date):

	if self.state == SEQ_IDLE:
	    return True
	elif self.state == SEQ_LOST or self.state == SEQ_COMPLETE:
	    return False
	else:
	    has = False
	    for name in self.subSeqName:
		if has == False:
		    if self.subSequence[name].GetNextDate() - date < DAY:
			has = True
	    return has

    def ObserveEvent (self, date, name, obsHistID):
        """
        Simply register the fact that one of our observations has been
        carried out and uodate self.obsHistory
        """

        if self.subSequence[name].ObserveEvent(date, obsHistID) == True:

	    self.allHistory.append((date, name))
            self.obsHistory.append((date, name))

            if len(self.allHistory) == 1:
                self.date = date
	        if self.masterSubSequence != None:
	            for name in self.subSeqName:
		        if name != self.masterSubSequence:
	                    self.subSequence[name].date = date
	
        self.UpdateState()
        
        return

    def MissEvent (self, date, name, obsHistID):
	"""
	Event missed. allHistory will store the event as if it were observed,
	and misHistory will register the miss.
	"""

        self.subSequence[name].MissEvent(date, obsHistID)

        self.allHistory.append((date, name))
        self.misHistory.append((date, name))
        
        self.UpdateState()
	if self.state == SEQ_LOST:
	    del self.allHistory[-1]
	    self.nAllEvents = len(self.allHistory)
        
	return

    def Abort(self):

        for name in self.subSeqName:
            self.subSequence[name].Abort()

        self.aborted = True

        self.UpdateState()

	return

    def GetProgress(self, name=None):
        """
        Returns the progress of the full sequence.

        0.0 = no observations done
        1.0 = complete
        """
        if self.nTargetEvents == 0:
           return 1.0

	if name == None:
	    if self.WLtype:
		return float(self.nObsEvents)/float(self.nTargetEvents)
	    else:
                return float(self.nAllEvents)/float(self.nTargetEvents)
	else:
	    return self.subSequence[name].GetProgress()

    def RankTimeWindow(self, name, date):

	if not self.subSequence[name].HasTimeWindow():
	    timeWindow = False
	    progress = {}
	    avgprogress = 0.0
	    for ss in self.subSeqName:
		progress[ss] = self.subSequence[ss].GetProgress()
		avgprogress += min(progress[ss],1.0)
	    avgprogress /= len(progress)
	    seqneed = 1.0 - avgprogress
	    if self.progressToStartBoost < avgprogress < 1.0:
		seqneed += self.maxBoostToComplete*(avgprogress-self.progressToStartBoost)/(1.0-self.progressToStartBoost)
	    if avgprogress < 1.0:
		if progress[name] < 1.0:
		    rank = 0.5*(seqneed + (1.0-progress[name]))
		else:
		    # subsequence complete and no need for overflow (sequence incomplete)
		    rank = -0.1
	    else:
		rank = self.overflowLevel / progress[name]
	else:
	    timeWindow = True
	    progress_ss = self.subSequence[name].GetProgress()
	    if progress_ss < 1.0:
		rank = self.subSequence[name].RankTimeWindow(date)
	    else:
		# subsequence complete, overflow not considered yet
		rank = -0.1

	return (rank, timeWindow)

    def GetRemainingAllowedMisses(self, name):

	return self.subSequence[name].GetRemainingAllowedMisses()

