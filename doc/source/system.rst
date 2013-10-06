.. _system:

System 
==========
   
The directory /lsst/opsim/conf/system/ contains
configuration files which govern the specifications of the telescope, the details for the site, downtime parameters and details of the granularity of the sky movement, sky brightness and moon calculations.
    
DO NOT alter these parameters as many of them are under change control.

    
Instrument.conf
---------------

.. code-block:: python
    
    ######################################################################
    ########### Configuration for   Instrument   #########################
    ######################################################################
    
    # Cinematic and delay parameters for slew time computation
    
    # speed in degrees/second
    # acceleration in degrees/second**2
    DomAlt_MaxSpeed = 1.75
    DomAlt_Accel = 0.875
    DomAlt_Decel = 0.875
    
    DomAz_MaxSpeed = 1.5
    DomAz_Accel = 0.75
    DomAz_Decel = 0.75
    
    TelAlt_MaxSpeed = 3.5
    TelAlt_Accel = 3.5
    TelAlt_Decel = 3.5
    
    TelAz_MaxSpeed = 7.0
    TelAz_Accel = 7.0
    TelAz_Decel = 7.0
    
    # not used in slew calculation
    Rotator_MaxSpeed = 3.5
    Rotator_Accel = 1.0
    Rotator_Decel = 1.0
    
    # absolute position limits due to cable wrap
    # the range [0 360] must be included
    TelAz_MinPos = -270.0
    TelAz_MaxPos =  270.0
    
    Rotator_MinPos = -90.0
    Rotator_MaxPos =  90.0
    
    # Boolean flag that if True enables the movement of the rotator during
    # slews to put North-Up. If range is insufficient, then the alignment
    # is North-Down
    # If the flag is False, then the rotator does not move during the slews,
    # it is only tracking during the exposures.
    Rotator_FollowSky = False
    
    # Times in sec
    Filter_MountTime =  8*3600.0
    Filter_MoveTime  =     120.0
    
    Settle_Time  = 3.0
    
    # In azimuth only
    DomSettle_Time = 1.0
    
    Readout_Time = 2.0
    
    # Delay factor for Open Loop optics correction,
    # in units of seconds/(degrees in ALT slew)
    TelOpticsOL_Slope = 1.0/3.5
    
    # Table of delay factors for Closed Loop optics correction
    # according to the ALT slew range.
    # _AltLimit is the Altitude upper limit in degrees of a range.
    # The lower limit is the upper limit of the previous range.
    # The lower limit for the first range is 0
    # _Delay is the time delay in seconds for the corresponding range.
    TelOpticsCL_Delay    =   0.0
    TelOpticsCL_AltLimit =   9.0 # 0 delay due to CL up to 9 degrees in ALT slew
    TelOpticsCL_Delay    =  20.0
    TelOpticsCL_AltLimit =  90.0
    
    #====================================================================
    # Dependencies between the slew activities.
    # For each activity there is a list of prerequisites activities, that
    # must be previously completed.
    # The Readout corresponds to the previous observation, that's why it doesn't
    # have prerequisites and it is a prerequisite for Exposure. 
    #
    # NOTE: Each item in list of prerequisites needs to be enclosed in single
    #       quotes, not double quotes.
    prereq_DomAlt      = []
    prereq_DomAz       = []
    prereq_TelAlt      = []
    prereq_TelAz       = []
    prereq_TelOpticsOL = ['TelAlt','TelAz']
    prereq_TelOpticsCL = ['DomAlt','DomAz','Settle','Readout','TelOpticsOL','Filter','Rotator']
    prereq_Rotator     = []
    prereq_Filter      = []
    prereq_ADC         = []
    prereq_InsOptics   = []
    prereq_GuiderPos   = []
    prereq_GuiderAdq   = []
    prereq_Settle      = ['TelAlt','TelAz']
    prereq_DomSettle  = []
    prereq_Exposure    = ['TelOpticsCL']
    prereq_Readout     = []
    
    #====================================================================
    # Initial state for the mounted filters.
    # Empty positions must be filled with id="" no (filter).
    Filter_Mounted = g
    Filter_Mounted = r
    Filter_Mounted = i
    Filter_Mounted = z
    Filter_Mounted = y
    
    # Filter id currently in position. Must be one of the mounted.
    Filter_Pos = r
    
    # List of mounted filters that are removable for swapping
    Filter_Removable = y
    Filter_Removable = z
    
    # List of unmounted but available filters to swap
    Filter_Unmounted = u
    
    #====================================================================
    # Telescope altitude limits
    
    # minimum altitude from horizon (degrees)
    Telescope_AltMin = 15.0
    
    # maximum altitude for zenith avoidance (degrees)
    Telescope_AltMax = 86.5
    
    #===================================================================
    # UNUSED
    
    # List of speeds in each degree of freedom for the Telescope Optics.
    # units are nm/sec
    # Not used yet.
    TelOptics_Speed = 200.0
    TelOptics_Speed = 200.0
    TelOptics_Speed = 200.0
    TelOptics_Speed = 200.0
    TelOptics_Speed = 200.0
                                                                                 
    # List of speeds in each degree of freedom for the Instrument Optics.
    # units are nm/sec
    # Not used yet.
    InsOptics_Speed = 100.0
    InsOptics_Speed = 100.0
    InsOptics_Speed = 100.0
    InsOptics_Speed = 100.0
    InsOptics_Speed = 100.0
    
    # ADC rotation not used yet.
    ADC_Speed = 360.0/10.0
    
    
SiteCP.conf
-----------

.. code-block:: python

    ######################################################################
    ########### Configuration for   Cerro Pachon   #######################
    ######################################################################
    
    #       Jan 1 of the year seeing data was collected
    #       Units = MJD;    Format = float; Default == 1994-01-01T00:00:00.0
    seeingEpoch = 49353  # Cerro Pachon - MJD(Jan 1, 1994)
                                                                                    
    #       Telescope site's  Latitude
    #       Units = degree; Format = float, Negative implies South
    #       Default site is CTIO.
    latitude = -29.666667      # Cerro Pachon
    
    #       Telescope site's Longitude
    #       Units = degree; Format = float, Negative implies West
    #       Default site is CTIO.
    longitude = -70.59          # Cerro Pachon
    
    #       Telescope site's Elevation
    #       Units = meters above sea level; Format = float
    #       Default site is CTIO.
    height = 2737.              # Cerro Pachon
        
    #       Site's atmospheric pressure
    #       Units = millibar; Format = float  Default = 1010.
    pressure = 1010.         # Cerro Pachon
    
    #       Site's atmospheric temperature
    #       Units = degrees C; Format = float  Default = 12.
    temperature = 12.         # Cerro Pachon
    
    #       Site's relative humidity
    #       Units = percent; Format = float  Default = 0.
    relativeHumidity = 0.         # CerroPachon
        
    #       Weather data's seeing fudge factor applied to all seeing values
    #       Modifies all seeing data and to moderate "seeing too good to be true"
    #           sanity test 
    #       runSeeing = weatherSeeing * weatherSeeingFudge * telescopeEffectsFudge
    #       Units = unitless, Format = float, default = 1.0
    weatherSeeingFudge = 1.0    # Cerro Pachon
    
    #       Site Specific Database Table names
    #       Format =  string
    seeingTbl = Seeing
    #cloudTbl = CloudPachon
    #cloudTbl = Cloud2000Tololo
    #cloudTbl = Cloud3yrTololo
    cloudTbl = Cloud
    
    
AstronomicalSky.conf
--------------------

.. code-block:: python
    
    ######################################################################
    ########### Configuration for   AstronomicalSky   ####################
    ######################################################################
    
    # Wavelength of light (microns). Default = 0.5 for Claver Seeing & Cloud data
    #                               Use 0.56 for weather data prior to Claver set      
    Wavelength = 0.5
    
    #################### Optimizations: Sky Brightness ####################
    ########## Do not change unless you know what you are doing ###########
    
    # Resolution scale for dates (seconds). Default = 3600.
    SBDateScale = 3600.
    
    # Resolution scale for RA (decimal degrees). Default = 7.

    # Resolution scale for RA (decimal degrees). Default = 7.
    SBDecScale = 7.
    
    
    ####################### Optimizations: Airmass ########################
    
    # Setting scales to 1. will effectively turn off cacheing.
    
    # Resolution scale for dates (seconds). Default = 30.
    #ADateScale = 30.
    ADateScale = 1.
    
    # Resolution scale for RA (decimal degrees). Default = 5.
    #ARAScale = 5.
    ARAScale = 1.
    
    # Resolution scale for Dec (decimal degrees). Default = 5.
    #ADecScale = 5.
    ADecScale = 1.
    
    
    ######################################################################
    ###################### TWILIGHT PARAMETERS ###########################
    
    # NIGHT LIMITS
    # Altitude of the Sun in degrees that define the start end end of the night
    # for the purposes of observations
    SunAltitudeNightLimit = -12.0
    
    # TWILIGHT LIMITS
    # Altitude of the Sun in degrees that define the twilight.
    # When the sun is above this limit and below the night limit, a special
    # twilight factor is included in the sky brightness model
    SunAltitudeTwilightLimit = -18.0
    
    # TWILIGHT BRIGHTNESS
    # Sun brightness in magnitude/arcsec^2 added to the sky brightness
    # model during the twilight period defined by the parameters
    # SunAltitudeNightLimit and SunAltitudeTwilightLimit
    TwilightBrightness = 17.3
    
    
schedDown.conf
--------------

.. code-block:: python
    
    ######################################################################
    ########### Configuration for  Scheduled Downtime     ################
    ######################################################################
    
    # startNight is in days, in which simulation starts at night = 0 and 
    # duration is in days
    
    activity = general maintenance
    startNight = 68 	# March 10th in 1st year
    duration = 7
    
    activity = general maintenance
    startNight = 478 	# April 24th in 2nd year
    duration = 7
    
    activity = recoat mirror
    startNight = 856  	# May 7th in 3rd year
    duration = 14

    activity = general maintenance
    startNight = 1145 	# Feb 20th in 4th year
    duration = 7
    
    activity = recoat mirror
    startNight = 1620  	# June 10th in 5th year
    duration = 14
    
    activity = general maintenance
    startNight = 2008 	# Jul 3rd in 6th year
    duration = 7
    
    activity = recoat mirror
    startNight = 2419  	# Aug 18th in 7th year
    duration = 14
    
    activity = general maintenance
    startNight = 2832 	# Oct 5th in 8th year
    duration = 7
    
    activity = recoat mirror
    startNight = 3245  	# Nov 22nd in 9th year
    duration = 14
    
    activity = general maintenance
    startNight = 3542 	# Sep 15th in 10th year
    duration = 7
    
unschedDown.conf
----------------

.. code-block:: python

    activity = intermediate event
    startNight = 3
    duration = 3
     
    activity = minor event
    startNight = 22
    duration = 1
     
    activity = minor event
    startNight = 30
    duration = 1
     
    activity = minor event
    startNight = 44
    duration = 1
     
    activity = minor event
    startNight = 246
    duration = 1
     
    activity = intermediate event
    startNight = 296
    duration = 3
     
    activity = minor event
    startNight = 356
    duration = 1
     
    activity = minor event
    startNight = 402
    duration = 1
     
    activity = minor event
    startNight = 436
    duration = 1
     
    activity = major event
    startNight = 486
    duration = 7
     
    activity = minor event
    startNight = 507
    duration = 1
     
    activity = minor event
    startNight = 571
    duration = 1
     
    activity = intermediate event
    startNight = 710
    duration = 3
     
    activity = intermediate event
    startNight = 733
    duration = 3
     
    activity = minor event
    startNight = 757
    duration = 1
     
    activity = intermediate event
    startNight = 880
    duration = 3
     
    activity = major event
    startNight = 939
    duration = 7
     
    activity = minor event
    startNight = 958
    duration = 1
     
    activity = major event
    startNight = 1020
    duration = 7
         
    activity = intermediate event
    startNight = 1148
    duration = 3
     
    activity = minor event
    startNight = 1156
    duration = 1
     
    activity = minor event
    startNight = 1161
    duration = 1
     
    activity = intermediate event
    startNight = 1178
    duration = 3
     
    activity = minor event
    startNight = 1201
    duration = 1
     
    activity = minor event
    startNight = 1212
    duration = 1
     
    activity = minor event
    startNight = 1223
    duration = 1
     
    activity = minor event
    startNight = 1274
    duration = 1
     
    activity = intermediate event
    startNight = 1288
    duration = 3
     
    activity = minor event
    startNight = 1307
    duration = 1
     
    activity = minor event
    startNight = 1316
    duration = 1
     
    activity = intermediate event
    startNight = 1334
    duration = 3
     
    activity = minor event
    startNight = 1517
    duration = 1
     
    activity = minor event
    startNight = 1526
    duration = 1
     
    activity = catastrophic event
    startNight = 1591
    duration = 14
     
    activity = minor event
    startNight = 1637
    duration = 1
     
    activity = minor event
    startNight = 1707
    duration = 1
     
    activity = minor event
    startNight = 1738
    duration = 1
     
    activity = major event
    startNight = 1762
    duration = 7
     
    activity = minor event
    startNight = 1813
    duration = 1
     
    activity = minor event
    startNight = 1822
    duration = 1
     
    activity = major event
    startNight = 1847
    duration = 7
     
    activity = minor event
    startNight = 1883
    duration = 1
     
    activity = minor event
    startNight = 1888
    duration = 1
     
    activity = minor event
    startNight = 2065
    duration = 1
     
    activity = minor event
    startNight = 2087
    duration = 1
     
    activity = minor event
    startNight = 2119
    duration = 1
     
    activity = intermediate event
    startNight = 2158
    duration = 3
     
    activity = minor event
    startNight = 2237
    duration = 1
     
    activity = minor event
    startNight = 2269
    duration = 1
     
    activity = minor event
    startNight = 2301
    duration = 1
     
    activity = minor event
    startNight = 2315
    duration = 1
     
    activity = intermediate event
    startNight = 2356
    duration = 3
     
    activity = minor event
    startNight = 2376
    duration = 1
     
    activity = minor event
    startNight = 2378
    duration = 1
     
    activity = minor event
    startNight = 2524
    duration = 1
     
    activity = minor event
    startNight = 2527
    duration = 1
     
    activity = intermediate event
    startNight = 2583
    duration = 3
     
    activity = minor event
    startNight = 2698
    duration = 1
     
    activity = minor event
    startNight = 2702
    duration = 1
     
    activity = intermediate event
    startNight = 2724
    duration = 3
     
    activity = minor event
    startNight = 2738
    duration = 1
     
    activity = intermediate event
    startNight = 2758
    duration = 3
     
    activity = minor event
    startNight = 2799
    duration = 1
     
    activity = intermediate event
    startNight = 2812
    duration = 3
     
    activity = minor event
    startNight = 2825
    duration = 1
     
    activity = intermediate event
    startNight = 2991
    duration = 3
     
    activity = intermediate event
    startNight = 3027
    duration = 3
     
    activity = intermediate event
    startNight = 3089
    duration = 3
     
    activity = intermediate event
    startNight = 3135
    duration = 3
     
    activity = minor event
    startNight = 3218
    duration = 1
     
    activity = minor event
    startNight = 3219
    duration = 1
     
    activity = minor event
    startNight = 3307
    duration = 1
     
    activity = minor event
    startNight = 3310
    duration = 1
     
    activity = intermediate event
    startNight = 3328
    duration = 3
     
    activity = minor event
    startNight = 3354
    duration = 1
     
    activity = minor event
    startNight = 3378
    duration = 1
     
    activity = minor event
    startNight = 3381
    duration = 1
     
    activity = minor event
    startNight = 3424
    duration = 1
     
    activity = minor event
    startNight = 3440
    duration = 1
     
    activity = intermediate event
    startNight = 3644
    duration = 3
    #Total downtime = 165 over 10 years
    
    
