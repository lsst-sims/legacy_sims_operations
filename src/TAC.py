#!/usr/bin/env python

"""
TAC

Inherits from: Simulation.Process : object

Class Description
The TAC class generates Proposal instances. It can generate any number 
of Proposal instances at the beginning of the (simulated) year.


Method Types
Constructor/Initializers
- __init__

Activate a TAC instance
- start
"""

from utilities import *
from LSSTObject import *
from Proposal import *
from WeakLensingProp import *
#from NearEarthProp import *
#from SuperNovaProp import *
from SuperNovaSubSeqProp import *
#from KuiperBeltProp import *
from WLprop import *


#class TAC (Simulation.Process):
class TAC(object):
    def __init__(self,
		 lsstDB, 
                 nRun,
		 schedulingData,
                 sky, 
                 weather, 
                 obsScheduler, 
                 sessionID,
                 fov,
                 filters,
                 nearEarthConf=None,
                 weakLensConf=None,
                 superNovaConf=None,
                 superNovaSubSeqConf=None,
		 kuiperBeltConf=None,
                 transientObjectConf=None,
		 WLpropConf=None,
                 targetList=None, 
                 dbTableDict=None,
                 log=False, 
                 logfile='./TAC.log',
                 verbose=0):
        """
        Standard initializer.
        
	lsstDB: 	LSST DB access object        
	nRun:
        sky:            an AsronomycalSky instance.
        weather:        a Weather instance.
        obsScheduler:   a ObsScheduler instance.
        sessionID:      An integer identifying this particular run
        fov:
        filters:        a Filters instance
        nearEarthConf:  Near Earth Asteroid configuration file list
        WeakLensConf:   Weak Lensing configuration file list
        superNovaConf:  SuperNova configuration file list
        transientObjectConf:   configuration file
        targetList:     the name (with path) of the TEXT file 
                        containing the field list. It is assumed 
                        that the target list is a three column list 
                        of RA, Dec and field ID. RA and Dec are 
                        assumed to be in decimal degrees; filed ID 
                        is assumed to be an integer uniquely 
                        identifying any give field.
        dbTableDict:
        log         False if not set, else: log = logging.getLogger("...")
        logfile     Name (and path) of the desired log file.
                    Defaults "./TAC.log".
        verbose:    Log verbosity: 0=minimal, 1=wordy, >1=very verbose
                                                                                

        """
#        Simulation.Process.__init__(self)
	self.lsstDB = lsstDB    
	self.schedulingData = schedulingData    
	self.sky = sky
        self.weather = weather
        self.obsScheduler = obsScheduler
        self.targetList = targetList
        self.nRun = nRun
        self.sessionID = sessionID
        self.fov = fov
        self.filters = filters
        self.nearEarthConf = nearEarthConf
        self.weakLensConf = weakLensConf
        self.superNovaConf = superNovaConf
        self.superNovaSubSeqConf = superNovaSubSeqConf
	self.kuiperBeltConf = kuiperBeltConf
        self.transientObjectConf = transientObjectConf
	self.WLpropConf = WLpropConf
        self.dbTableDict = dbTableDict

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            print "Setting up TAC logger"
            log = logging.getLogger("TAC")
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.INFO)
                                                                                
        self.log=log
        self.logfile=logfile
        self.verbose = verbose
                                                                                

        
        self.proposals = []
        
        if ( self.log and self.verbose > 1):
            self.log.info('TAC: init()')
            #for key in self.dbTableDict:
            #     print " TAC:    Database tables: " + key,self.dbTableDict[key]

        
        return
    
    
    def start (self):
        """
        Activate the TAC instance in the simulation.
        Activate each Proposal instance (by calling its start() method) 
        and then go to sleep until the end of the year. Then start again.
        """
        if ( self.log and self.verbose > 1):
            self.log.info('TAC: start()')
        
        # Create a new Weak Lensing proposal and add it to 
        # the self.proposals array
        if ( self.weakLensConf[0] != None):
            for k in range(len(self.weakLensConf)):
                wlp = WeakLensingProp (lsstDB=self.lsstDB,
			       schedulingData=self.schedulingData,
			       sky=self.sky, 
                               weather=self.weather,
                               sessionID=self.sessionID,
                               filters=self.filters,
                               fov=self.fov,
                               weakLensConf=self.weakLensConf[k],
                               targetList=self.targetList,
                               dbTableDict=self.dbTableDict,
                               log=self.log,
                               logfile=self.logfile, 
                               verbose=self.verbose)
#                Simulation.activate (wlp, wlp.start ())
                wlp.start()
                self.proposals.append (wlp)
        
                # Notify the ObsScheduler
                self.obsScheduler.addProposal (wlp)
                if (self.log and self.verbose):
                    self.log.info ('TAC: Weak Lensing Proposal from %s'%(self.weakLensConf[k]))
        
                # now pause for a while before submitting another one.
                #yield hold, self
                
        # Create a new Super Nova proposal and add it to 
        # the self.proposals array
        if ( self.superNovaConf[0] != None):
            for k in range(len(self.superNovaConf)):
                sn = SuperNovaProp (lsstDB=self.lsstDB,
			       sky=self.sky, 
                               weather=self.weather,
                               sessionID=self.sessionID,
                               filters=self.filters,
                               superNovaConf=self.superNovaConf[k],
                               targetList=self.targetList,
                               dbTableDict=self.dbTableDict,
                               log=self.log,
                               logfile=self.logfile, 
                               verbose=self.verbose)
#                Simulation.activate (sn, sn.start ())
                sn.start()
                self.proposals.append (sn)
        
                # Notify the ObsScheduler
                self.obsScheduler.addProposal (sn)
                if (self.log and self.verbose):
                    self.log.info ('TAC: SuperNova Proposal from %s'%(self.superNovaConf[k]))
        
                # now pause for a while before submitting another one.
                #yield hold, self
                
        # Create a new Super Nova proposal and add it to 
        # the self.proposals array
        if ( self.superNovaSubSeqConf[0] != None):
            for k in range(len(self.superNovaSubSeqConf)):
                snss = SuperNovaSubSeqProp (lsstDB=self.lsstDB,
			       schedulingData=self.schedulingData,
			       sky=self.sky, 
                               weather=self.weather,
                               sessionID=self.sessionID,
                               filters=self.filters,
                               superNovaSubSeqConf=self.superNovaSubSeqConf[k],
                               targetList=self.targetList,
                               dbTableDict=self.dbTableDict,
                               log=self.log,
                               logfile=self.logfile, 
                               verbose=self.verbose)
#                Simulation.activate (snss, snss.start ())
                snss.start()
                self.proposals.append (snss)
        
                # Notify the ObsScheduler
                self.obsScheduler.addProposal (snss)
                if (self.log and self.verbose):
                    self.log.info ('TAC: SuperNovaSubSeq Proposal from %s'%(self.superNovaSubSeqConf[k]))
        
                # now pause for a while before submitting another one.
                #yield hold, self

        # Create a new NEA proposal and add it to 
        # the self.proposals array
        if ( self.nearEarthConf[0] != None):
            for k in range(len(self.nearEarthConf)):
                nea = NearEarthProp (lsstDB=self.lsstDB,
			     sky=self.sky, 
                             weather=self.weather,
                             sessionID=self.sessionID,
                             filters=self.filters,
                             targetList=self.targetList,
                             dbTableDict=self.dbTableDict,
                             log=self.log,
                             logfile=self.logfile, 
                             verbose=self.verbose,
                             nearEarthConf=self.nearEarthConf[k])
#                Simulation.activate (nea, nea.start ())
                nea.start()
                self.proposals.append (nea)
        
                # Notify the ObsScheduler
                self.obsScheduler.addProposal (nea)
                if (self.log and self.verbose):
                    self.log.info ('TAC: Near Earth Proposal from %s' %(self.nearEarthConf[k]))

                # now pause for a while before submitting another one.
                #yield hold, self

        # Create a new KBO proposal and add it to
        # the self.proposals array
        if ( self.kuiperBeltConf[0] != None):
            for k in range(len(self.kuiperBeltConf)):
                kbo = KuiperBeltProp (lsstDB=self.lsstDB,
			     sky=self.sky,
                             weather=self.weather,
                             sessionID=self.sessionID,
                             filters=self.filters,
                             targetList=self.targetList,
                             dbTableDict=self.dbTableDict,
                             log=self.log,
                             logfile=self.logfile,
                             verbose=self.verbose,
                             kuiperBeltConf=self.kuiperBeltConf[k])
#                Simulation.activate (kbo, kbo.start ())
                kbo.start()
                self.proposals.append (kbo)

                # Notify the ObsScheduler
                self.obsScheduler.addProposal (kbo)
                if (self.log and self.verbose):
                    self.log.info ('TAC: Kuiper Belt Proposal from %s' %(self.kuiperBeltConf[k]))

        # Create a new WL proposal and add it to
        # the self.proposals array
        if ( self.WLpropConf[0] != None):
            for k in range(len(self.WLpropConf)):
                wl = WLprop (lsstDB=self.lsstDB,
			     schedulingData=self.schedulingData,
			     sky=self.sky,
                             weather=self.weather,
                             sessionID=self.sessionID,
                             filters=self.filters,
                             targetList=self.targetList,
                             dbTableDict=self.dbTableDict,
                             log=self.log,
                             logfile=self.logfile,
                             verbose=self.verbose,
                             WLpropConf=self.WLpropConf[k])
#                Simulation.activate (wl, wl.start ())
                wl.start()
                self.proposals.append (wl)
                                                                                                        
                # Notify the ObsScheduler
                self.obsScheduler.addProposal (wl)
                if (self.log and self.verbose):
                    self.log.info ('TAC: Weak Lensing Transient Proposal from %s' %(self.WLpropConf[k]))
                                                                                                        
                # now pause for a while before submitting another one.
#                yield hold, self
                
        return

