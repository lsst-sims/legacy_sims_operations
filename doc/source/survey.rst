.. _survey:

Survey  
==========

The directory /lsst/opsim/conf/survey/ contains configuration files which govern the survey programs and master control of the survey. The only parameters you should change in LSST.conf are the run length and what observing modes/proposals are going to be used in the simulation.

LSST.conf
---------

LSST.conf is the primary setup file which specifies the observing modes to be used in this simulation. It also sets parameters such as the length of the run, the site specific configuation file, and specifies all other configuration file names and database table names.   In general, the only parameters you should change in LSST.conf are the run length and what observing modes/proposals are going to be used in the simulation.  There are short descriptions of the parameters within the configuration file.  The simulator will generate a log file describing what it is doing and why. The verbosity parameter sets how detailed the logging is.  Verbose :math:`\ge 2` will generate HUGE log files and should only be used for VERY short runs.

Observations will be taken when the cloud value in the cloud table is less than the parameter maxCloud.  This is the fraction of the sky judged cloudy by the CTIO night assistant, four times per night, over the 10 year database used for the simulation.  The cloudiness was recorded as clear eighths of the sky, so with the default (maxCloud < .7), observations will be taken when :math:`\frac{5}{8}\rm ths`  or more of the sky is clear.


There are two classes of observing mode - weakLensConf (or WLProp), and WLpropConf (or WLTSS). Only observing programs specified in the following way are included.  WLprop observing modes only consider how many field/filter combinations are requested versus how many have been accumulated.  WLpropConf observing modes can have complex cadence requirements in addition to field/filter observations requirements.  A typical simulation with design area requirement and design visit requirement and 3.61-type auxilary proposals uses the following proposals::

    weakLensConf = ../conf/survey/GalacticPlaneProp.conf
    weakLensConf = ../conf/survey/SouthCelestialPole-18.conf
    weakLensConf = ../conf/survey/Standby.conf

    WLpropConf = ../conf/survey/Universal-18-0824.conf
    WLpropConf = ../conf/survey/NorthEclipticSpur-18.conf
    WLpropConf = ../conf/survey/SuperNovaSubSeqdeep.conf

The following configuration files should not be modified without great caution::

    instrumentConf = ../conf/system/Instrument.conf
    schedDownConf = ../conf/system/schedDown.confi
    unschedDownConf = ../conf/system/unschedDown.conf
    filtersConf = ../conf/survey/Filters.conf

The configuration files in ``../conf/scheduler/`` can be used to fine tune simulations, but should only be modified with care.  The default values have been derived over years and hundreds of simulations.

.. code-block:: python
     
    ######################################################################
    ########### Configuration for   LSST   ############################
    ######################################################################
    #
    #       Number of years to simulate. 
    #       Units = year; Format = float; Default = 1 year
    #nRun = 0.009    # about 3 days
    #nRun = 0.0794   # 1 lunation
    #nRun = 0.16     # 2 lunations
    #nRun = 1.0      # 1 year
    #nRun = 3.0      # 3 years
    nRun = 10.0     # 10 years
    #nRun = 1.3      # 1+ years
      
    #       Days relative to seeingEpoch from which simulation commences
    #       Units = MJD;    Format = float; Default == 0.0
    simStartDay = 0.0       # start simulation with first year of Weather data
    #simStartDay = 365.0    # start simulation with second year of Weather data
     
    #       Field of View 
    #           Prepackaged FOV are in range: [3.0 : 4.0] in steps of .1
    #           Additional FOV are easily installed on request.
    #       Units = degree; Format = float; Default = 3.5
    fov=3.5
    #       When using bundled fov, reset Scheduler:reuseRankCount to 1
    #fov = 13.0      # large hexagon simulating 19 hexagons for fov=3.0
    #fov = 15.25     # large hexagon simulating 19 hexagons for fov=3.5                
     
    #       Telescope Effects factor degrades seeing with zenith distance
    #       Optical Design and Camera factor degrades seeing a fixed amount
    #	adjust = sqrt ((seeing * filter_wavelngth * airmass^0.6)^2 + 
    #                      (telSeeing * airmass^0.6)^2 + opticalDesSeeing^2 +
    #                      cameraSeeing^2)
    #       Units = unitless, Format = float, no default 
    telSeeing = 0.241 	  # design goal
    opticalDesSeeing = 0.097
    cameraSeeing = 0.280
     
    #----------------------------------------------------------------------------
    #       Paths to Auxiliary Configuration files
    #       Units = unitless; 
    #       Format = Unix pathname; may be relative to current working directory
    #       Defaults are in current working directory:
    #           {WeakLensProp.conf,NearEarthProp.conf,Instrument.conf}
    #----------------------------------------------------------------------------
    #       Site Specific configuration file
    #           SiteCP=Cerro Pachon; SiteCT=Cerro Tololo; 
    #           SiteSPM=San Pedro Martir; SiteLC=Las Companas
    #siteConf = ./SiteSPM.conf
    siteConf = ../conf/system/SiteCP.conf
     
    #       Weak Lensing Proposal configuration file
    #       If missing, then do not process Weak Lensing proposal
    #weakLensConf = ./WeakLensProp.conf    
    weakLensConf = ../conf/survey/GalacticPlaneProp.conf
    weakLensConf = ../conf/survey/SouthCelestialPole-18.conf
    weakLensConf = ../conf/survey/Standby.conf
     
    #       New Weak Lensing as Transient with subsequences for each filter.
    #WLpropConf = ./WLprop.conf    
    WLpropConf = ../conf/survey/Universal-18-0824.conf
    WLpropConf = ../conf/survey/NorthEclipticSpur-18.conf
     
    #       Near Earth Asteroid Proposal configuration file
    #       If missing, then do not process Near Earth Asteroid proposal
    #nearEarthConf = ./NEOSweet60-80.conf  
    #nearEarthConf = ./NEOSweet80-90.conf  
     
    #       SuperNova Proposal configuration file  ---mostly depricated
    #       If missing, then do not process (a simple) SuperNova proposal
    #superNovaConf = ./SuperNovaProp.conf
    #superNovaConf = ./ShortTimeDomainProp.conf
     
    #       SuperNova with SubSequences Proposal configuration file
    #       If missing, then do not process SuperNovaSubSeq proposal
    #superNovaSubSeqConf = ./SuperNovaSubSeqProp.conf
    #superNovaSubSeqConf = ./SuperNovaSubSeqPropwide.conf
    WLpropConf = ../conf/survey/SuperNovaSubSeqdeep.conf
        
    #	     Kuiper Belt Object proposal configuration file
    #	     If missing, then do not process KuiperBelt proposal
    #kuiperBeltConf = ./KuiperBeltProp.conf
     
    #       Instrument configuration file
    instrumentConf = ../conf/system/Instrument.conf    
     
    #       Downtime configuration files
    schedDownConf = ../conf/system/schedDown.conf                  
    unschedDownConf = ../conf/system/unschedDown.conf
     
    #       Filters configuration file
    filtersConf = ../conf/survey/Filters.conf
     
    #       Observation Scheduler configuration file
    schedulerConf = ../conf/scheduler/Scheduler.conf
     
    schedulingDataConf = ../conf/scheduler/SchedulingData.conf
     
    #------------------------------------------------------------------------------
    #       Database Table names  
    #       Format =  string
    obsHistTbl     = ObsHistory
    timeHistTbl    = TimeHistory
    proposalTbl    = Proposal
    sessionTbl     = Session
    seqHistoryTbl  = SeqHistory
    fieldTbl       = Field
    downHistTbl    = DownHist
     
    #------------------------------------------------------------------------------
    #       Time to delay when no target is available for observation
    #       Units = seconds,  Format = integer, default = 30
    idleDelay = 300
     
    #       Verbosity of Logging 
    #       Units = -1=none, 0=min, 1=wordy, >1=verbose >2=output precalculation 
    #            tables every timestep (shouldrestrict nRun=1day); Format = integer
    #       Default is Wordy
    verbose = 1
     
    #       Pathname of Logging  Filename
    #       Units = unitless; Format = Unix pathname; may be relative to CWD
    #       Default is "./lsst.log_<sessionID>" 
    #               where <sessionid> is automatically determined during the run
    #                                 and is always printed on startup.
    #       Include filename *only* if you want to change the default.
    #logfile = ./lsst.log        
     
    #	     Variable for Code Testing 
    # 	code_test = 1 (default) which means that the run is a code-test run
    #	code_test = 0 means that the run is a production run
    code_test = 0
     
    #       Maximum cloudiness for observing, regardless of proposal needs
    maxCloud = 0.7
     

Filters.conf
------------

This configuration file is likely to be significantly changed in the future.  It provides default filter usage rules with respect to sky brightness, but these rules have been moved to each proposal for better control.  It also defines filter wavelengths and relative exposure time (for all proposals), and these parameters will eventually be moved to Instrument.conf.  It is possible you may want to change relative exposure times for a simulation and that is about all you should change here.

.. code-block:: python
     
    ######################################################################
    ########### Configuration for   Filters   ############################
    ######################################################################
    # Filters defined in the system.
    # After each definition the brightness limits and the wavelength *must* follow.
    
    # Filter         Units: label     Format: character
    # MinBrightness  Units:           Format: float; relative to v-band brightness 
    #                                                             and extinction
    # MaxBrightness  Units:           Format: float; relative to v-band brightness 
    #                                                             and extinction
    # Wavelength     Units: microns   Format: float
    #
    # If a proposal does not define its particular set of brightness limits
    # then the values in this file are taken as default.
    
    Filter_Defined = u
    Filter_MinBrig = 21.40
    Filter_MaxBrig = 30.00
    Filter_Wavelen = 0.35
    Filter_ExpFactor = 1.0
    #Filter_ExpFactor = 1.88235
    #Multiplicative factor for the visit time
    # VisitTime = Nexp*( ShutterTravelTime + EffectiveExpTime ) + (Nexp-1)*ReadoutTime
    # In this version of the code:
    #                              Nexp=2 hardcoded
    #                              ShutterTravelTime = 1[sec] hardcoded
    #                              ReadoutTime = 2[sec] parameter in Instrument.conf
    #                              VisitTime = 34[sec] parameter in science programs
    # 30 seconds effective exposure instead of 15 seconds
    # Filter_ExpFactor = (2*(30+1)+2)/(2*(15+1)+2) = 64 / 34 = 1.88235 
    #
    Filter_Defined = g
    Filter_MinBrig = 21.00
    Filter_MaxBrig = 30.00
    Filter_Wavelen = 0.52
    Filter_ExpFactor = 1.0
    
    Filter_Defined = r
    Filter_MinBrig = 20.50
    Filter_MaxBrig = 30.00
    Filter_Wavelen = 0.67
    Filter_ExpFactor = 1.0                                                       
    
    Filter_Defined = i
    Filter_MinBrig = 20.25
    Filter_MaxBrig = 30.00
    Filter_Wavelen = 0.79
    Filter_ExpFactor = 1.0                                                       
    
    Filter_Defined = z
    Filter_MinBrig = 17.50
    Filter_MaxBrig = 21.00
    Filter_Wavelen = 0.91
    Filter_ExpFactor = 1.0                                                       
    
    Filter_Defined = y
    Filter_MinBrig = 17.50
    Filter_MaxBrig = 21.00
    Filter_Wavelen = 1.04
    Filter_ExpFactor = 1.0                                                       
    

Universal-18-0824.conf
----------------------

This proposal is the primary way the WFD observing program has been simulated.  It currently cannot use look ahead.  The ``WLtype = True`` statement makes the proposal collect field/filter visits in pairs (with the separation set by the window parameters), but otherwise does not consider cadence.  Advice from early LSST NEO people was that u and y were not useful for NEOs, so we have been running those filters without collecting in pairs (note the window parameters).  There are a few important parameters which you may want to play with.  ``reuseRankingCount`` determines how often a complete reranking of all available field/filters is done.  Large values for ``reuseRankingCount`` may result in sky conditions changing enough that field/filter combinations are taken which probably shouldn't be.  Small values for ``reuseRankingCount`` slows down the simulation due to the constant reevaluation of the field/filters ranking.  We have found a value of 10 works well. This means that all possible field/filter combinations are ranked based on the internal proposal logic, the relative importance of each proposal and the slew time to reach them.  The top 10 are chosen; number 1 is observed.

Embedded comments explain most of the parameters well, but a few comments might be helpful.  

- **MaxNumberActiveSequences** is set to a ridiculously high number and is irrelevant.  

- **RestartLostSequences** is more relevant to WLpropConf proposals without ``WLtype = True``.  ``RestarLostSequences`` will restart a sequence which is lost due to its missing too many observations.  It is set to False here, because it is not critical that field/filter visits be collected in pairs, just useful.  If set to True, it would probably result in collecting too many visits per unit time for some fields as the proposal continues to try and get the appropriately spaced pair.

- **OverflowLevel, ProgressToStartBoost** and **MaxBoostToComplete** are parameters which were developed to help deliver the maximum number of fields which have the SRD required number of visits in each filter.  ``OverflowLevel`` sets the amount of field/filter visits allowed beyond the number requested.  ``ProgressToStartBoost`` and ``MaxBoostToComplete`` are well explained in the embedded comments.  They were inserted to make sure that at least some fields collected the requested number of visits in each filter.  These are parameters which need to be more fully explored, but will likely become irrelevant when look ahead is implemented in WLpropConf proposals.

Selection of the fields to be observed can be done in two ways: 1) define limits on the sky or 2) explicitly define the fields from the field table to be used.  The simulator currently will only observe at defined field centers chosen to tile the sky with no gaps (kind of hexagonal close packing for the inscribed hexagon of the circular FOV).  Dithering is currently added in a postprocessing step.  The ``userRegions`` found in the default configuration files have been chosen to deliver the appropriate area for each of the proposals with no gaps.

The conditions which allow observations to be taken are set by airmass limits, seeing limits and sky brightness limits.  Seeing is calculated from 500nm zenith seeing values corrected for airmass and wavelength.  Sky brightness is calculated using the Krisciunus and Schafer algoritm for V band brightness and corrected to LSST bands.  A single value for z and y sky brightness is used for twilight observations.  In a postprocessing step, the LSST ETC sky brightness is calculated and added to the output table and used for all calculations in the SSTAR output.  Clearly, this is inconsistent and we are working to fix this.
 
.. code-block:: python
    
    WLtype = True
    
    # -----------------------------------------------------------------------
    #                   Event Sequencing Parameters
    # -----------------------------------------------------------------------
    #   Gap in nights to next observing night. Do we want this proposal to run
    #   every night?  Every night = 0 and every other night = 1.
    #       Units = nights.  Default = 0.
    HiatusNextNight = 0
    
    #   Count of observations to take with one set of ranking.  How often rerank?
    reuseRankingCount = 10
    
    #   Maximum number of sequences active simultaneously
    #       No Default
    MaxNumberActiveSequences = 10000
    #MinNumberActiveSequences =  1500
                                                                                         
    #   Indicates incomplete sequences may be restarted if terminated early.
    #       Default = False
    RestartLostSequences = False
                                                                                         
    #   Indicates successfully completed sequences may be restarted on completion.
    #       Default = False
    RestartCompleteSequences = False
                                                                                         
    # Configuration for each filter-subsequence
    #MasterSubSequence = 
                                                                                         
    #   SubSeqName       = name of subsequence
    #                      Default = value defined for SubSeqFilters
    #   SubSeqFilters    = ordered list of filters.   No default.
    #   SubSeqExposures  = filter-ordered list of exposure counts
    #                      Default = 1 for missing values
    #   SubSeqEvents     = Requested Number Events per Completed Sequence.
    #                      No default.
    #   SubSeqMaxMissed  = Maximum number of events the proposal allowed to miss
    #                      in a sequence without declaring it as lost.   No default.#   SubSeqInterval   = Time interval (sec) between events in a Sequence.
    #                      No default.
    #   SubSeqInterval   = time interval between events.
    #                      if WLtype=True and SubSeqInterval>0, that interval applies to the second of each pair of events.
    #   SubSeqWindowStart= Time at which event's priority starts rising. No default
    #   SubSeqWindowMax  = Time at which event's priority reaches max.  No default.
    #   SubSeqWindowEnd  = Time at which event is abandoned. No default.
    
    # Visits requirements for a 1, 3 and 10 year survey are provided. Adjust proportionally to the right survey length.
    
    SubSeqName      = u
    SubSeqFilters   = u
    SubSeqExposures = 1
    #SubSeqEvents    = 7
    #SubSeqEvents    = 21
    #SubSeqEvents    = 70
    SubSeqEvents    = 56
    SubSeqMaxMissed = 0
    SubSeqInterval  = 0
    SubSeqWindowStart       = 0
    SubSeqWindowMax         = 0
    SubSeqWindowEnd         = 0
                                                                                                              
    SubSeqName      = g
    SubSeqFilters   = g
    SubSeqExposures = 1
    #SubSeqEvents    = 10
    #SubSeqEvents    = 30
    #SubSeqEvents    = 100
    SubSeqEvents    = 80
    SubSeqMaxMissed = 0
    SubSeqInterval  = 30*60
    SubSeqWindowStart       = -0.5
    SubSeqWindowMax         =  0.5
    SubSeqWindowEnd         =  1.0
    
    SubSeqName      = r
    SubSeqFilters   = r
    SubSeqExposures = 1
    #SubSeqEvents    = 23
    #SubSeqEvents    = 69
    #SubSeqEvents    = 230
    SubSeqEvents    = 184
    SubSeqMaxMissed = 0
    SubSeqInterval  = 30*60
    SubSeqWindowStart       = -0.5
    SubSeqWindowMax         =  0.5
    SubSeqWindowEnd         =  1.0
    
    SubSeqName      = i
    SubSeqFilters   = i
    SubSeqExposures = 1
    #SubSeqEvents    = 23
    #SubSeqEvents    = 69
    #SubSeqEvents    = 230
    SubSeqEvents    = 184
    SubSeqMaxMissed = 0
    SubSeqInterval  = 30*60
    SubSeqWindowStart       = -0.5
    SubSeqWindowMax         =  0.5
    SubSeqWindowEnd         =  1.0
                                                                                                     
    SubSeqName      = z
    SubSeqFilters   = z
    SubSeqExposures = 1
    #SubSeqEvents    = 20
    #SubSeqEvents    = 60
    #SubSeqEvents    = 200
    SubSeqEvents    = 160
    SubSeqMaxMissed = 0
    SubSeqInterval  = 30*60
    SubSeqWindowStart       = -0.5
    SubSeqWindowMax         =  0.5
    SubSeqWindowEnd         =  1.0
    
    SubSeqName      = y
    SubSeqFilters   = y
    SubSeqExposures = 1
    #SubSeqEvents    = 20
    #SubSeqEvents    = 60
    #SubSeqEvents    = 200
    SubSeqEvents    = 160
    SubSeqMaxMissed = 0
    SubSeqInterval  = 0
    SubSeqWindowStart       = 0
    SubSeqWindowMax         = 0
    SubSeqWindowEnd         = 0
    
    
    #   Initial value for needed visits after completing the requested visits
    #       for that field-filter. Need starts at this value decaying when
    #       getting additional visits.
    OverflowLevel = 0.0
                                                                                            
    # Parameters for controlling the promotion of nearly complete field-filters.
    # The rank is basically the expression:
    # rank = scale * (partialneed/partialgoal) / (globalneed/globalgoal)
    # where partialneed = partialgoal - partialvisits for a particular field-filter
    # progress is defined as partialvisits/partialgoal.
    # When progress becomes greater than ProgressToStartBoost parameter,
    # rank receives an additional boost factor determined by:
    # MaxBoostToComplete * (progress-ProgressToStartBoost) / (1-ProgressToStartBoost)
    # To disable this feature these are the values for both parameters.
    # ProgressToStartBoost = 1.00
    # MaxBoostToComplete   = 0.00
    ProgressToStartBoost = 0.90 # after 70% progress
    MaxBoostToComplete   = 10.00 # double rank near the end compared to a
                           # non-observed field-filter
                                                                                            
    # ----------------------------------------------------------------------
    #                       Field Selection Parameters
    #-----------------------------------------------------------------------
    #   User Region Definitions
    #       list of (ra,dec,width)  containing center point around which a cone of
    #                            diameter width is centered.
    #       Units: deg,deg,deg Format: float, float, float
    #       Default: none; do not include
    
    # fields/userRegions_design.txt - design fields - 18,000 sq deg
    userRegion = 240.05,-62.02,0.03
    userRegion = 119.94,-62.02,0.03
    userRegion = 335.95,-62.02,0.03
    userRegion = 24.06,-62.02,0.03
    userRegion = 312.05,-62.02,0.03
    userRegion = 47.94,-62.02,0.03
    continued......
    
    # Galactic plane exclusion zone
    #       During a night, the EXCLUDED fields are bracketted by
    #       region: +/- peakL deg in latitude at 0 longitude   going to
    #               +/- taperL deg in latitude at taperB longitude.
    #       defaults: +/- 25. deg in latitude at 0 deg longitude going to
    #               +/- 5. deg in latitude at 180. deg longitude.
    #       Units = degree; Format = float; Default: taperL=5, taperB=180 peakL=25
    #taperL = 0.1
    #taperB = 90.
    #peakL = 10.
    taperL = 0.0
    taperB = 0.0
    peakL = 0.0
                                                                                            
    #   During night potentially visible fields are bracketted by region:
    #       [LST@sunSet-deltaLST:LST@sunRise+deltaLST],
    #                          [Dec-arccos(1/MaxAirmass: Dec+arccos(1/MaxAirmass]
    #       Units = degree; Format = float; Default is 60.0
    deltaLST = 60.0
                                                                                            
    #   Min/Max Declination of allowable observations
    #       Units = degree; Format = float; Default is 80.
    maxReach = 90.0
                                                                                            
                                                                                         
    #   Limits in degrees for the range of the sky to build
    #       the list of new targets every night.
    #       Default = 0.0 for both
    newFieldsLimitEast_afterLSTatSunset   = 0.0
    newFieldsLimitWest_beforeLSTatSunrise = 0.0
                                                                                         
    #   Ecliptic inclusion zone
    #       During a night the potentially visible fields are bracketted by
    #       region: [*],[-EB : +EB]
    #       Units = Ecliptic degree; Format = float; Default is 10; Don't use=0.
    EB = 0
    
    # --------------------------------------------------------------------
    #               Target Selection Parameters
    # --------------------------------------------------------------------
    #   Maximum accepted airmass
    #       Units: unitless Format: float   Default: 2.0
    MaxAirmass   = 1.5
                                                                                            
    #   Max acceptable airmass-adjusted-seeing per filter
    #       Units: arcseconds   Format: float   Default: MaxSeeing
    # Filter         Units: label     Format: character
    # MinBrightness  Units:           Format: float; relative to v-band brightness
    #                                                             and extinction
    # MaxBrightness  Units:           Format: float; relative to v-band brightness
    #                                                             and extinction
    Filter = u
    Filter_MinBrig = 21.30
    Filter_MaxBrig = 30.00
    Filter_MaxSeeing= 1.5
                                                                                                              
    Filter = g
    Filter_MinBrig = 21.00
    Filter_MaxBrig = 30.00
    Filter_MaxSeeing= 1.5
    
    Filter = r
    Filter_MinBrig = 20.25
    Filter_MaxBrig = 30.00
    Filter_MaxSeeing= 1.5
    
    Filter = i
    Filter_MinBrig = 19.50
    Filter_MaxBrig = 30.00
    Filter_MaxSeeing= 1.5
    
    Filter = z
    Filter_MinBrig = 17.00
    Filter_MaxBrig = 21.00
    Filter_MaxSeeing= 1.5
    
    Filter = y
    Filter_MinBrig = 16.50
    Filter_MaxBrig = 21.00
    Filter_MaxSeeing= 1.5
    
    #   Default max airmass adjusted seeing if specific filter not provided
    #       Units: arcseconds  Format: float   Default: none
    MaxSeeing    = 1.5
                                                                                                 
    #   Minimum Cloud Transparency of allowable observations
    #       Units = range 0:1; Format = float; Default is .9, Hardcoded limit =.9
    minTransparency = .7
                                                                                                 
    #   Exposure time in seconds per visit
    #       Default  = 30.
    ExposureTime = 34.0      # 2 15-secs. exposures, 1 2-secs. readout, 2-secs. shutter time
    #ExposureTime = 570.     # composite region for 19 fov hexagons
                                                                                            
    #   Boundary when TwilightObserving begins/ends
    #       Units = degrees Format = float; Default is -12. = nautical
    TwilightBoundary = -12.
                                                                                            
    # -----------------------------------------------------------------------
    #                   Target Ranking Parameters
    # -----------------------------------------------------------------------
    #   Relative priority parameter for the proposal.
    #       This factor is applied in the final rank for all the observations
    #       proposed by this proposal. Default = 1.0
    RelativeProposalPriority = 1.1
                                                                                                 
    #   Proximity bonus factor that is added internally in the proposal
    #       to select the observations to propose promoting the closest to the
    #       current telescope position.
    #       However, the scheduler then replaces this bonus by the more accurate
    #       slew time prediction.
    MaxProximityBonus = 0.1
                                                                                            
    #   Ranking values
    #
    #   Maximum rank scale for the time window
    #       No default.
    RankTimeMax = 5.00
                                                                                         
    #   Rank for an idle sequence (not started yet)
    #   or average rank for no timewindow (distribution WLtype)
    #       No default.
    RankIdleSeq = 0.10
    
    #   Maximum rank bonus for sequence that has exhausted allowable misses.
    #       No default.
    RankLossRiskMax = 0.0
                                                                                         
    # Disabled values, formula still on development.
    RankDaysLeftMax = 0.0
    DaysLeftToStartBoost = 0                                                    
    
    # Accept observations with low ranking in this proposal
    # that have been observed for other proposals?
    AcceptSerendipity = True
    
    # Accept consecutive observations for the same field
    AcceptConsecutiveObs = False
    
    # Set start and stop time if proposal should not run for the entire simulation
    # duration (secs since start of simulation).
    #StartTime =
    #StopTime =


NorthEclipticSpur-18.conf
-------------------------

This proposal collects pairs of observations north of the limits for the WFD observing area and along the ecliptic north of the WFD area primarily for the purpose of detecting NEOs.  As such, it does not collect u or y data.  It is a variant of the Universal proposal.  Note the necessity to allow observations at higher airmass and larger seeing.

.. code-block:: python
     
    WLtype = True
    
    # -----------------------------------------------------------------------
    #                   Event Sequencing Parameters
    # -----------------------------------------------------------------------
    #   Gap in nights to next observing night. Do we want this proposal to run
    #   every night?  Every night = 0 and every other night = 1.
    #       Units = nights.  Default = 0.
    HiatusNextNight = 0
    
    #   Count of observations to take with one set of ranking.  How often rerank?
    reuseRankingCount = 10
    
    #   Maximum number of sequences active simultaneously
    #       No Default
    MaxNumberActiveSequences = 10000
    #MinNumberActiveSequences =  1500
                                                                                              
    #   Indicates incomplete sequences may be restarted if terminated early.
    #       Default = False
    RestartLostSequences = False
                                                                                              
    #   Indicates successfully completed sequences may be restarted on completion.
    #       Default = False
    RestartCompleteSequences = False
                                                                                              
    # Configuration for each filter-subsequence
    #MasterSubSequence = r
                                                                                              
    #   SubSeqName       = name of subsequence
    #                      Default = value defined for SubSeqFilters
    #   SubSeqFilters    = ordered list of filters.   No default.
    #   SubSeqExposures  = filter-ordered list of exposure counts
    #                      Default = 1 for missing values
    #   SubSeqEvents     = Requested Number Events per Completed Sequence.
    #                      No default.
    #   SubSeqMaxMissed  = Maximum number of events the proposal allowed to miss
    #                      in a sequence without declaring it as lost.   No default.#   SubSeqInterval   = Time interval (sec) between events in a Sequence.
    #                      No default.
    #   SubSeqInterval   = time interval between events.
    #                      if WLtype=True and SubSeqInterval>0, that interval applies to the second of each pair of events.
    #   SubSeqWindowStart= Time at which event's priority starts rising. No default
    #   SubSeqWindowMax  = Time at which event's priority reaches max.  No default.
    #   SubSeqWindowEnd  = Time at which event is abandoned. No default.
    
    # Visits requirements for a 1 year survey. Adjust proportionally to the right survey length.
    
    #SubSeqName      = u
    #SubSeqFilters   = u
    #SubSeqExposures = 1
    #SubSeqEvents    = 7
    #SubSeqEvents    = 21
    #SubSeqEvents    = 70
    #SubSeqMaxMissed = 0
    #SubSeqInterval  = 0
    #SubSeqWindowStart       = 0
    #SubSeqWindowMax         = 0
    #SubSeqWindowEnd         = 0
                                                                                                              
    SubSeqName      = g
    SubSeqFilters   = g
    SubSeqExposures = 1
    #SubSeqEvents    = 10
    #SubSeqEvents    = 30
    SubSeqEvents    = 100
    SubSeqMaxMissed = 0
    SubSeqInterval  = 30*60
    SubSeqWindowStart       = -0.5
    SubSeqWindowMax         =  0.5
    SubSeqWindowEnd         =  1.0
    
    SubSeqName      = r
    SubSeqFilters   = r
    SubSeqExposures = 1
    #SubSeqEvents    = 23
    #SubSeqEvents    = 69
    SubSeqEvents    = 230
    SubSeqMaxMissed = 0
    SubSeqInterval  = 30*60
    SubSeqWindowStart       = -0.5
    SubSeqWindowMax         =  0.5
    SubSeqWindowEnd         =  1.0
    
    SubSeqName      = i
    SubSeqFilters   = i
    SubSeqExposures = 1
    #SubSeqEvents    = 23
    #SubSeqEvents    = 69
    SubSeqEvents    = 230
    SubSeqMaxMissed = 0
    SubSeqInterval  = 30*60
    SubSeqWindowStart       = -0.5
    SubSeqWindowMax         =  0.5
    SubSeqWindowEnd         =  1.0
                                                                                                          
    SubSeqName      = z
    SubSeqFilters   = z
    SubSeqExposures = 1
    #SubSeqEvents    = 20
    #SubSeqEvents    = 60
    SubSeqEvents    = 200
    SubSeqMaxMissed = 0
    SubSeqInterval  = 30*60
    SubSeqWindowStart       = -0.5
    SubSeqWindowMax         =  0.5
    SubSeqWindowEnd         =  1.0
    
    #SubSeqName      = y
    #SubSeqFilters   = y
    #SubSeqExposures = 1
    #SubSeqEvents    = 20
    #SubSeqEvents    = 60
    #SubSeqEvents    = 200
    #SubSeqMaxMissed = 0
    #SubSeqInterval  = 0
    #SubSeqWindowStart       = 0
    #SubSeqWindowMax         = 0
    #SubSeqWindowEnd         = 0
    
    #   Initial value for needed visits after completing the requested visits
    #       for that field-filter. Need starts at this value decaying when
    #       getting additional visits.
    OverflowLevel = 0.0
                                                                                                 
    # Parameters for controlling the promotion of nearly complete field-filters.
    # The rank is basically the expression:
    # rank = scale * (partialneed/partialgoal) / (globalneed/globalgoal)
    # where partialneed = partialgoal - partialvisits for a particular field-filter
    # progress is defined as partialvisits/partialgoal.
    # When progress becomes greater than ProgressToStartBoost parameter,
    # rank receives an additional boost factor determined by:
    # MaxBoostToComplete * (progress-ProgressToStartBoost) / (1-ProgressToStartBoost)
    # To disable this feature these are the values for both parameters.
    # ProgressToStartBoost = 1.00
    # MaxBoostToComplete   = 0.00
    ProgressToStartBoost = 0.90 # after 70% progress
    MaxBoostToComplete   = 10.00 # double rank near the end compared to a
                                # non-observed field-filter
                                                                                                 
    # ----------------------------------------------------------------------
    #                       Field Selection Parameters
    #-----------------------------------------------------------------------
    #   User Region Definitions
    #       list of (ra,dec,width)  containing center point around which a cone of
    #                            diameter width is centered.
    #       Units: deg,deg,deg Format: float, float, float
    #       Default: none; do not include
    
    
    
    userRegion = 137.64,2.84,0.03
    userRegion = 78.36,2.84,0.03
    userRegion = 65.64,2.84,0.03
    userRegion = 353.64,2.84,0.03
    userRegion = 6.36,2.84,0.03
    userRegion = 150.36,2.84,0.03
    userRegion = 350.48,3.06,0.03
    continued....
                                                                                                  - 
    
    # Galactic plane exclusion zone
    #       During a night, the EXCLUDED fields are bracketted by
    #       region: +/- peakL deg in latitude at 0 longitude   going to
    #               +/- taperL deg in latitude at taperB longitude.
    #       defaults: +/- 25. deg in latitude at 0 deg longitude going to
    #               +/- 5. deg in latitude at 180. deg longitude.
    #       Units = degree; Format = float; Default: taperL=5, taperB=180 peakL=25
    taperL = 0.1
    taperB = 90.
    peakL = 10.
                                                                                                 
    #   During night potentially visible fields are bracketted by region:
    #       [LST@sunSet-deltaLST:LST@sunRise+deltaLST],
    #                          [Dec-arccos(1/MaxAirmass: Dec+arccos(1/MaxAirmass]
    #       Units = degree; Format = float; Default is 60.0
    deltaLST = 60.0
                                                                                                 
    #   Min/Max Declination of allowable observations
    #       Units = degree; Format = float; Default is 80.
    maxReach = 90.0
                                                                                                 
                                                                                              
    #   Limits in degrees for the range of the sky to build
    #       the list of new targets every night.
    #       Default = 0.0 for both
    newFieldsLimitEast_afterLSTatSunset   = 0.0
    newFieldsLimitWest_beforeLSTatSunrise = 0.0
                                                                                              
    #   Ecliptic inclusion zone
    #       During a night the potentially visible fields are bracketted by
    #       region: [*],[-EB : +EB]
    #       Units = Ecliptic degree; Format = float; Default is 10; Don't use=0.
    EB = 0
    
    # --------------------------------------------------------------------
    #               Target Selection Parameters
    # --------------------------------------------------------------------
    #   Maximum accepted airmass
    #       Units: unitless Format: float   Default: 2.0
    MaxAirmass   = 2.5
                                                                                                 
    #   Max acceptable airmass-adjusted-seeing per filter
    #       Units: arcseconds   Format: float   Default: MaxSeeing
    # Filter         Units: label     Format: character
    # MinBrightness  Units:           Format: float; relative to v-band brightness
    #                                                             and extinction
    # MaxBrightness  Units:           Format: float; relative to v-band brightness
    #                                                             and extinction
    Filter = u
    Filter_MinBrig = 21.30
    Filter_MaxBrig = 30.00
    Filter_MaxSeeing = 2.0
                                                                                                              
    Filter = g
    Filter_MinBrig = 21.00
    Filter_MaxBrig = 30.00
    Filter_MaxSeeing= 2.0
    
    Filter = r
    Filter_MinBrig = 20.25
    Filter_MaxBrig = 30.00
    Filter_MaxSeeing= 2.0
    
    Filter = i
    Filter_MinBrig = 19.50
    Filter_MaxBrig = 30.00
    Filter_MaxSeeing= 2.0
    
    Filter = z
    Filter_MinBrig = 17.00
    Filter_MaxBrig = 21.00
    Filter_MaxSeeing= 2.0
    
    Filter = y
    Filter_MinBrig = 16.50
    Filter_MaxBrig = 21.00
    Filter_MaxSeeing= 1.5
    
    #   Default max airmass adjusted seeing if specific filter not provided
    #       Units: arcseconds  Format: float   Default: none
    MaxSeeing    = 1.5
                                                                                                 
    #   Minimum Cloud Transparency of allowable observations
    #       Units = range 0:1; Format = float; Default is .9, Hardcoded limit =.9
    minTransparency = .7
                                                                                                 
    #   Exposure time in seconds per visit
    #       Default  = 30.
    ExposureTime = 34.0      # 2 15-secs. exposures, 1 2-secs. readout, 2-secs. shutter time
    #ExposureTime = 570.     # composite region for 19 fov hexagons
                                                                                                 
    #   Boundary when TwilightObserving begins/ends
    #       Units = degrees Format = float; Default is -12. = nautical
    TwilightBoundary = -12.
                                                                                                 
    # -----------------------------------------------------------------------
    #                   Target Ranking Parameters
    # -----------------------------------------------------------------------
    #   Relative priority parameter for the proposal.
    #       This factor is applied in the final rank for all the observations
    #       proposed by this proposal. Default = 1.0
    RelativeProposalPriority = 0.8
                                                                                                 
    #   Proximity bonus factor that is added internally in the proposal
    #       to select the observations to propose promoting the closest to the
    #       current telescope position.
    #       However, the scheduler then replaces this bonus by the more accurate
    #       slew time prediction.
    MaxProximityBonus = 0.1
                                                                                                 
    #   Ranking values
    #
    #   Maximum rank scale for the time window
    #       No default.
    RankTimeMax = 5.00
                                                                                              
    #   Rank for an idle sequence (not started yet)
    #   or average rank for no timewindow (distribution WLtype)
    #       No default.
    RankIdleSeq = 0.10
    
    #   Maximum rank bonus for sequence that has exhausted allowable misses.
    #       No default.
    RankLossRiskMax = 0.0
                                                                                              
    # Disabled values, formula still on development.
    RankDaysLeftMax = 0.0
    DaysLeftToStartBoost = 0                                                    
    
    # Accept observations with low ranking in this proposal
    # that have been observed for other proposals?
    AcceptSerendipity = True
    
    # Accept consecutive observations for the same field
    AcceptConsecutiveObs = False
    
    # Set start and stop time if proposal should not run for the entire simulation
    # duration (secs since start of simulation).
    #StartTime =
    #StopTime =

     
GalacticPlaneProp.conf
----------------------

.. code-block:: python

    ######################################################################
    ########### Configuration for Galactic Plane Survey  #################
    ######################################################################
    # -----------------------------------------------------------------------
    #                   Event Sequencing Parameters
    # -----------------------------------------------------------------------
    #   Desired number of visits per individual field/filter.
    #       Used to get uniform coverage in all accessible fields to requied depth.
    #       Cover as many fields as possible to these depths
    #  NOTE: These numbers are for one year.
    #
    # Filter         Units: label     Format: character
    # MinBrightness  Units:           Format: float; relative to v-band brightness
    #                                                             and extinction
    # MaxBrightness  Units:           Format: float; relative to v-band brightness
    #                                                             and extinction
    #   Max acceptable airmass-adjusted-seeing per filter
    #       Units: arcseconds   Format: float   Default: MaxSeeing
    Filter = g
    Filter_Visits  = 30
    Filter_MaxSeeing = 3.0
    Filter_MinBrig = 21.15
    Filter_MaxBrig = 30.00
                                                                                                                                   
    Filter = r
    Filter_Visits  = 30
    Filter_MaxSeeing = 2.0
    Filter_MinBrig = 20.00
    Filter_MaxBrig = 30.00
                                                                                                                                   
    Filter = i
    Filter_Visits  = 30
    Filter_MaxSeeing = 2.0
    Filter_MinBrig = 19.50
    Filter_MaxBrig = 30.00
                                                                                                                                   
    Filter = z
    Filter_Visits  = 30
    Filter_MaxSeeing = 2.0
    Filter_MinBrig = 17.50
    Filter_MaxBrig = 21.40
                                                                                                                                   
    Filter = y
    Filter_Visits  = 30
    Filter_MaxSeeing = 3.0
    Filter_MinBrig = 16.00
    Filter_MaxBrig = 21.40
                                                                                                                                   
    Filter = u
    Filter_Visits  = 30
    Filter_MaxSeeing = 2.0
    Filter_MinBrig = 21.20
    Filter_MaxBrig = 30.00
    
    #   Gap in nights to next observing night. Do we want this proposal to run
    #   every night?  Every night = 0 and every other night = 1.
    #       Units = nights.  Default = 0.
    HiatusNextNight = 0
    
    #   Count of observations to take with one set of ranking.  How often rerank?
    reuseRankingCount = 10
    
    #   Default number of visits per field/filter if specific filter not provided
    #       Units: count  Format: float   Default: 30
    NVisits = 3.
    
    #   Initial value for needed visits after completing the requested visits
    #       for that field-filter. Need starts at this value decaying when
    #       getting additional visits.
    MaxNeedAfterOverflow = 0.0
    
    # Parameters for controlling the promotion of nearly complete field-filters.
    # The rank is basically the expression:
    # rank = scale * (partialneed/partialgoal) / (globalneed/globalgoal)
    # where partialneed = partialgoal - partialvisits for a particular field-filter
    # progress is defined as partialvisits/partialgoal.
    # When progress becomes greater than ProgressToStartBoost parameter,
    # rank receives an additional boost factor determined by:
    # MaxBoostToComplete * (progress-ProgressToStartBoost) / (1-ProgressToStartBoost)
    # To disable this feature these are the values for both parameters.
    # ProgressToStartBoost = 1.00
    # MaxBoostToComplete   = 0.00
    ProgressToStartBoost = 1.00 # after 70% progress
    MaxBoostToComplete   = 0.00 # double rank near the end compared to a 
                                # non-observed field-filter
    
    # ----------------------------------------------------------------------
    #                       Field Selection Parameters
    #-----------------------------------------------------------------------
    #   User Region =  Definitions
    #       list of (ra,dec,width)  containing center point around which a cone of
    #                            diameter width is centered.
    #       Units: deg,deg,deg Format: float, float, float
    #       Default: none; do not include
    
    
    
    userRegion = 208.17,-65.93,0.03
    userRegion = 200.52,-65.50,0.03
    userRegion = 180.00,-65.32,0.03
    userRegion = 193.20,-64.78,0.03
    userRegion = 186.33,-63.78,0.03
    userRegion = 173.67,-63.78,0.03
    userRegion = 212.44,-63.58,0.03
    userRegion = 219.56,-63.58,0.03
    continued...
    
    # Galactic plane exclusion zone
    #       During a night, the EXCLUDED fields are bracketted by
    #       region: +/- peakL deg in latitude at 0 longitude   going to
    #               +/- taperL deg in latitude at taperB longitude.
    #       defaults: +/- 25. deg in latitude at 0 deg longitude going to
    #               +/- 5. deg in latitude at 180. deg longitude.
    #       Units = degree; Format = float; Default: taperL=5, taperB=180 peakL=25 
    taperL = 0.
    taperB = 0.
    peakL = 0.
    
    #   During night potentially visible fields are bracketted by region:
    #       [LST@sunSet-deltaLST:LST@sunRise+deltaLST],
    #                          [Dec-arccos(1/MaxAirmass: Dec+arccos(1/MaxAirmass]
    #       Units = degree; Format = float; Default is 60.0
    deltaLST = 60.0
    
    #   Min/Max Declination of allowable observations
    #       Units = degree; Format = float; Default is 80.
    maxReach = 90.0
    
    # --------------------------------------------------------------------
    #               Target Selection Parameters
    # --------------------------------------------------------------------
    #   Maximum accepted airmass
    #       Units: unitless Format: float   Default: 2.0
    MaxAirmass   = 2.5
    
    #   Default max airmass adjusted seeing if specific filter not provided
    #       Units: arcseconds  Format: float   Default: none
    MaxSeeing    = 2.
                                                                                    
    #   Minimum Cloud Transparency of allowable observations
    #       Units = range 0:1; Format = float; Default is .9, Hardcoded limit =.9
    minTransparency = 0.7
    
    #   Exposure time in seconds per visit
    #       Default  = 30.
    ExposureTime = 34.0      # 2 15-secs. exposures, 1 2-secs. readout, 2-secs. shutter time
    #ExposureTime = 570.     # composite region for 19 fov hexagons
    
    #   Boundary when TwilightObserving begins/ends
    #       Units = degrees Format = float; Default is -12. = nautical
    TwilightBoundary = -12.
    
    
    # -----------------------------------------------------------------------
    #                   Target Ranking Parameters
    # -----------------------------------------------------------------------
    #   Relative priority parameter for the proposal.
    #       This factor is applied in the final rank for all the observations
    #       proposed by this proposal. Default = 1.0
    RelativeProposalPriority = 1.0
    
    #   Proximity bonus factor that is added internally in the proposal
    #       to select the observations to propose promoting the closest to the
    #       current telescope position.
    #       However, the scheduler then replaces this bonus by the more accurate
    #       slew time prediction.
    MaxProximityBonus = 0.5
    
    #   Scale factor for ranking (i.e. value of the average rank)
    #       Units:   Format: float   Default: 0.1
    RankScale = 0.1
    
    # Accept observations with low ranking in this proposal
    # that have been observed for other proposals?
    AcceptSerendipity = True
    
    # Accept consecutive observations for the same field
    AcceptConsecutiveObs = True
    
    # Set start and stop time if proposal should not run for the entire simulation
    # duration (secs since start of simulation).
    #StartTime =
    #StopTime = 
    
    #====================================================================
    #   Priority Ranking Scheme across all Proposals
    #
    #   All proposals use the same ranking scale of values [0.0 : 1.0] .
    #       Rank 0.0  indicates that, in the current context of the proposal,
    #           a Field should not be observed.
    #       Rank 0.1 is a 'stand-by' rank indicating that the Field is ready to
    #           be observed (butthere is no urgency).
    #       Rank 0.5 indicates increasing urgency to observe the Field due to
    #           the Proposal's scheduling requirements. Few Fields at any moment
    #           should have such a high priority.
    #       Rank 1.0 indicates urgent need to observe the Field.  Failure to
    #           observe immediately will cause the current sequence to abort.
    #====================================================================
    
    
SuperNovaSubSeqdeep.conf
------------------------
    
.. code-block:: python

    ######################################################################
    ########### Configuration for Proposals with SubSequences   #################
    ######################################################################
    #  A thorough description of the KBO configuration file and target
    #       selection algorithm is at the end of this configuration file.
    # -----------------------------------------------------------------------
    #                   Event Sequencing Parameters
    # -----------------------------------------------------------------------
    #   Gap in nights to next observing night. Do we want this proposal to run
    #   every night?  Every night = 0 and every other night = 1.
    #       Units = nights.  Default = 0.
    HiatusNextNight = 0
    
    #   Count of observations to take with one set of ranking.  How often rerank?
    reuseRankingCount = 10
    
    #   Maximum number of sequences active simultaneously
    #       No Default
    MaxNumberActiveSequences = 100
    
    #   Indicates incomplete sequences may be restarted if terminated early.
    #       Default = False
    RestartLostSequences = True
    
    #   Indicates successfully completed sequences may be restarted on completion.
    #       Default = False
    RestartCompleteSequences = True
    
    # Configuration for each filter-subsequence
    MasterSubSequence = main
    
    #   SubSeqName	     = name of subsequence
    #                      Default = value defined for SubSeqFilters
    #   SubSeqFilters    = ordered list of filters.   No default.
    #   SubSeqExposures  = filter-ordered list of exposure counts 
    #                      Default = 1 for missing values
    #   SubSeqEvents     = Requested Number Events per Completed Sequence. 
    #                      No default.
    #   SubSeqMaxMissed  = Maximum number of events the proposal allowed to miss
    #                      in a sequence without declaring it as lost.   No default.
    #   SubSeqInterval   = Time interval (sec) between events in a Sequence.
    #                      No default.
    #   SubSeqWindowStart= Time at which event's priority starts rising. No default
    #   SubSeqWindowMax  = Time at which event's priority reaches max.  No default.
    #   SubSeqWindowEnd  = Time at which event is abandoned. No default.
    SubSeqName     		= main
    SubSeqFilters		= r,g,i,z,y 
    SubSeqExposures		= 20,10,20,20,20
    SubSeqEvents    	= 20
    SubSeqMaxMissed		= 3
    SubSeqInterval		= 5*24*60*60
    SubSeqWindowStart	=-0.30
    SubSeqWindowMax		= 0.30
    SubSeqWindowEnd		= 0.50
    
    #SubSeqName              = color
    #SubSeqFilters           = i z y
    #SubSeqExposures         = 20 20 20
    #SubSeqEvents            = 20
    #SubSeqMaxMissed         = 3
    #SubSeqInterval          = 5*24*60*60
    #SubSeqWindowStart       =-0.30
    #SubSeqWindowMax         = 0.30
    #SubSeqWindowEnd         = 0.50
    #
    #SubSeqName              = last
    #SubSeqFilters           = g
    #SubSeqExposures         = 10
    #SubSeqEvents            = 20
    #SubSeqMaxMissed         = 3
    #SubSeqInterval          = 5*24*60*60
    #SubSeqWindowStart       =-0.30
    #SubSeqWindowMax         = 0.30
    #SubSeqWindowEnd         = 0.30
    
    # Filter         Units: label     Format: character
    # MinBrightness  Units:           Format: float; relative to v-band brightness
    #                                                             and extinction
    # MaxBrightness  Units:           Format: float; relative to v-band brightness
    #                                                             and extinction
    Filter = g
    Filter_MinBrig = 19.00
    Filter_MaxBrig = 30.00
    
    Filter = r
    Filter_MinBrig = 19.00
    Filter_MaxBrig = 30.00
    
    Filter = i
    Filter_MinBrig = 19.00
    Filter_MaxBrig = 30.00
    
    Filter = z
    Filter_MinBrig = 17.50
    Filter_MaxBrig = 30.00
    
    Filter = y
    Filter_MinBrig = 17.50
    Filter_MaxBrig = 30.00
    
    # ----------------------------------------------------------------------
    #                       Field Selection Parameters
    #-----------------------------------------------------------------------
    #   User Region Definitions
    #       list of (ra,dec,width)  containing center point around which a cone of
    #                            diameter width is centered.
    #       Units: deg,deg,deg Format: float, float, float
    #       Default: none; do not include
    ########################################################################
    # NOTE: DO NOT use spaces between these values or you will break config!
    ########################################################################
    #userRegion = 0.0,-34.0, 4.0
    userRegion = 185.712,-2.625,0.01
    userRegion = 355.453,-2.625,0.01
    userRegion = 240.272,-18.375,0.01
    userRegion = 60.00,-34.0,0.01
    userRegion = 300.0,-75.0,0.01
    userRegion = 120.0,-75.0,0.01
    #userRegion = 60.0,-34.0, 4.0
    #userRegion = 90.0,-39.0,0.01
    #userRegion = 120.0,-34.0, 4.0
    #userRegion = 150.0,-39.0,0.01
    #userRegion = 180.0,-34.0, 4.0
    #userRegion = 210.0,-39.0,0.01
    #userRegion = 240.0,-34.0, 4.0
    #userRegion = 270.0,-39.0,0.01
    #userRegion = 300.0,-34.0, 4.0
    #userRegion = 330.0,-39.0,0.01
    
    #   Limits in degrees for the range of the sky to build
    #       the list of new targets every night.
    #       Default = 0.0 for both
    newFieldsLimitEast_afterLSTatSunset   = -60.0
    newFieldsLimitWest_beforeLSTatSunrise = -60.0
    
    #   During night potentially visible fields are bracketted by region:
    #       [LST@sunSet-deltaLST:LST@sunRise+deltaLST],
    #                          [Dec-arccos(1/MaxAirmass: Dec+arccos(1/MaxAirmass]
    #       Units = degree; Format = float; Default is 60.0
    deltaLST = 60.0
    
    #   Galactic plane exclusion zone
    #       During a night, the EXCLUDED fields are bracketted by
    #       region: +/- peakL deg in latitude at 0 longitude   going to
    #               +/- taperL deg in latitude at taperB longitude.
    #       defaults: +/- 25. deg in latitude at 0 deg longitude going to
    #               +/- 5. deg in latitude at 180. deg longitude.
    #       Units = degree; Format = float; Default: taperL=5, taperB=180 peakL=25
    taperL = 2.
    taperB = 180.
    peakL = 20.
    
    #   Min/Max Declination of allowable observations
    #       Units = degree; Format = float; Default is 80.
    maxReach = 90.0
    
    #   Ecliptic inclusion zone
    #       During a night the potentially visible fields are bracketted by
    #       region: [*],[-EB : +EB]
    #       Units = Ecliptic degree; Format = float; Default is 10.
    EB = 10.
    
    # --------------------------------------------------------------------
    #               Target Selection Parameters
    # --------------------------------------------------------------------
    #   Maximum accepted airmass
    #       Units: unitless Format: float   Default: 2.0
    MaxAirmass   = 2.0
                                                                                    
    #   Maximum accepted seeing (not adjusted for airmass)
    #       Units: arcseconds Format: float   Default: 2.0
    MaxSeeing    = 2.0
    
    #   Minimum Cloud Transparency of allowable observations
    #       Units = range 0:1; Format = float; Default is .9; Hardcoded limit=.9
    minTransparency = .7
    
    #   Exposure time in seconds per visit
    #       Units: seconds   Format: float   Default: 30.0
    ExposureTime = 34.0      # 2 15-secs. exposures, 1 2-secs. readout, 2-secs. shutter time
    #ExposureTime = 570.     # composite region for 19 fov hexagons
    
    # MM - NOT YET IMPLEMENTED  11/03/05
    #  Hard-coded in AstronomicalSky.py to -18.0 degrees
    #   Boundary when TwilightObserving begins/ends
    #       Units = degrees Format = float; Default is -12. 
    TwilightBoundary = -12.
                                                                                        
    # -----------------------------------------------------------------------
    #                   Target Ranking Parameters
    # -----------------------------------------------------------------------
    #   Relative priority parameter for the proposal.
    #       Factor applied in final rank for all obs proposed by this proposal.
    #       Default = 1.0
    RelativeProposalPriority = 5.0
    
    #   Time window for priority ranking of an observing visit
    #       Normalized time used is:
    #       normalizedT = (currentTime-nextEventTime)/(nextEventTime-lastEventTime)
    #
    #       Priority rank of an event starts rising at WindowStart, reaches a 
    #       maximum value at WindowMAx, and is abandoned at WindowEnd
    
    #       Proximity bonus factor added internally within proposal in order to 
    #       promote rank of targets closest to the current telescope position.
    #       However, the scheduler then replaces this bonus by more accurate
    #       slew time prediction.
    #       Default = 1.0
    MaxProximityBonus = 0.5
    
    #   Ranking values
    #
    #   Maximum rank scale for the time window
    #       No default.
    RankTimeMax = 1.00
    
    #   Maximum rank bonus for sequence that has exhausted allowable misses.
    #       No default.
    RankLossRiskMax = 10.0
    
    #   Rank for an idle sequence (not started yet).
    #       No default.
    RankIdleSeq = 0.10
    
    # Accept observations with low ranking in this proposal
    # that have been observed for other proposals?
    AcceptSerendipity = False
    
    # Accept consecutive observations for the same field
    AcceptConsecutiveObs = True
    
    # Set start and stop time if proposal should not run for the entire simulation
    # duration (secs since start of simulation).
    #StartTime =
    #StopTime =
    
    #==========================================================================
    #             KBO Sample Sequence setup and description:
    # ============================================================
    # MasterSubSequence = main
    #                    
    # SubSeqName              = main
    # SubSeqFilters           = r i
    # SubSeqExposures         = 3 4
    # SubSeqEvents            = 4
    # SubSeqMaxMissed         = 1
    # SubSeqInterval          = 1*24*60*60
    # SubSeqWindowStart       =-0.5
    # SubSeqWindowMax         = 0.35
    # SubSeqWindowEnd         = 0.50
    #                   
    # SubSeqName              = extra
    # SubSeqFilters           = g
    # SubSeqExposures         = 10
    # SubSeqEvents            = 3
    # SubSeqMaxMissed         = 1
    # SubSeqInterval          = 2*24*60*60
    # SubSeqWindowStart       =-0.30
    # SubSeqWindowMax         = 0.30
    # SubSeqWindowEnd         = 0.50
    #                  
    # SubSeqName              = last
    # SubSeqFilters           = r  i y
    # SubSeqExposures         = 10 3 2
    # SubSeqEvents            = 2
    # SubSeqMaxMissed         = 0
    # SubSeqInterval          = 4*24*60*60
    # SubSeqWindowStart       =-0.50
    # SubSeqWindowMax         = 0.30
    # SubSeqWindowEnd         = 0.50
    # 
    # 1-Several subsequences can be defined with no limits.
    #                                                                              
    # 2-Each subsequence needs a name, any single-word-string or number.
    #                                                                             
    # 3-The SubSeqFilters keyword describes the series of filters to use in a
    # single event (or complex event).
    #                                                                            
    # 4-The SubSeqExposures keyword describes the number of repeated exposures for
    # each one of the respective filters in SubSeqFilters. All these exposures will
    # be taken in a single observation block, one after the other, changing the
    # filter as indicated. There is no limit in the number of filters to use in
    # this "microsequence". Other proposals cannot interrupt the completion of
    # this complex event, but will analyze the exposures for serendipity. The
    # complex-event can be interrupted by downtime like clouds, end of night, etc.
    # In case of interruption, the event is missed.
    #                                                                           
    # 5-The event is proposed only if all the required filters are available from
    # sky brightness criteria.
    #                                                                          
    #                                                                         
    # 6-All the other parameters have exactly the same meaning as in SNSS proposal.
    #                                                                        
    # The example above says that the master subsequence is "main", the whole
    # sequence must start with that one. The "main" subsequence needs 4 events
    # with an interval of 1 day; each interval is composed of 3 r consecutive
    # exposures followed by 4 i exposures. Only 1 event can be missed without
    # loosing the whole sequence.
    # The subsequence "extra" has 3 events, each one composed of 10 consecutive g
    # exposures.
    # The subsequence "last" has 2 events, none can be missed, each one composed
    # of 10 r exposures, followed by 3 i and finally 2 y.
    #                                                   
    # 7-The ObsScheduler was modified to support this complex-events. It works the
    # same way as before, computing 20 (parameter) observations in a block to save
    # cpu. If one observation from KBO is taken, then this proposal gains the
    # exclusive attention from the scheduler while the complex-event is observed.
    # Each exposure is sent with a special flag to all the other proposals to
    # check for serendipity. Once the complex-event is finished, the scheduler
    # returns to its normal block of 20 mode.
    #                                                
    #==========================================================================
    #==========================================================================
    #   Priority Ranking Scheme across all Proposals
    #
    #   All proposals use the same ranking scale of values [0.0 : 1.0] .
    #       Rank 0.0  indicates that, in the current context of the proposal, 
    #           a Field should not be observed.
    #       Rank 0.1 is a 'stand-by' rank indicating that the Field is ready to
    #           be observed (but there is no urgency).
    #       Rank 0.5 indicates increasing urgency to observe the Field due to 
    #           the Proposal's scheduling requirements. Few Fields at any moment
    #           should have such a high priority.
    #       Rank 1.0 indicates urgent need to observe the Field.  Failure to 
    #           observe immediately will cause the current subsequence to abort.
    #====================================================================
    #   Priority Ranking within a Sequenced-Events Proposal
    #
    #   A Sequenced-event proposal uses the closeness between the current 
    #       Simulation Time and the Next Event time as the primary ranking 
    #       criteria for a Field.
    #
    #       A timing window is constructed from the time interval between 
    #       the next Visit and the previous Visit. From that interval an urgency 
    #       scale is created to the precision required.
    #
    #   The normalized time scale used is as follows:
    #       normalizedT = (currentTime-nextVisitTime)/(nextVisitTime-lastVisitTime)
    #
    #   The priority ranking of an observing visit starts rising at "WindowStart";
    #       it reaches a maximum value at "WindowMax"; and it is
    #       abandoned at "WindowEnd" if it still hasn't been observed.
    #   
    #   Using defaults: WindowStart=-0.20, WindowMax=0.20; WindowEnd=4.0,
    #       The priority begins rising at (0.2 * normalizedT) before the Visit time;
    #       it reaches the maximum priority at (0.2 * normalizedT) after the event 
    #       time; and returns to lowest prioirty at (0.4 * normalizedT) after 
    #       the Visit time.  
    #       Note: negative indicates *before* Visit time, positive is *after* Visit.
    
