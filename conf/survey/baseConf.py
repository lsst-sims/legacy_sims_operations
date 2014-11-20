import lsst.pex.config as pexConfig

class BaseConfig(pexConfig.Config):
######################################################################
#  A thorough description of the KBO configuration file and target
#       selection algorithm is at the end of this configuration file.
# -----------------------------------------------------------------------
#                   Event Sequencing Parameters
# -----------------------------------------------------------------------
#   Gap in nights to next observing night. Do we want this proposal to run
#   every night?  Every night = 0 and every other night = 1.
#       Units = nights.  Default = 0.
    HiatusNextNight = pexConfig.Field('', int, default=0)

    MaxNumberActiveSequences = pexConfig.Field('', int, default=100)

    RestartLostSequences = pexConfig.Field('', bool, default=False)

    RestartCompleteSequences = pexConfig.Field('', bool, default=False)

#   Limits in degrees for the range of the sky to build
#       the list of new targets every night.
#       Default = 0.0 for both
    newFieldsLimitEast_afterLSTatSunset   = pexConfig.Field('', float, default=0.0)
    newFieldsLimitWest_beforeLSTatSunrise = pexConfig.Field('', float, default=0.0)

#   During night potentially visible fields are bracketted by region:
#       [LST@sunSet-deltaLST:LST@sunRise+deltaLST],
#                          [Dec-arccos(1/MaxAirmass: Dec+arccos(1/MaxAirmass]
#       Units = degree; Format = float; Default is 60.0
    deltaLST = pexConfig.Field('', float, default=60.0)

#   Galactic plane exclusion zone
#       During a night, the EXCLUDED fields are bracketted by
#       region: +/- peakL deg in latitude at 0 longitude   going to
#               +/- taperL deg in latitude at taperB longitude.
#       defaults: +/- 25. deg in latitude at 0 deg longitude going to
#               +/- 5. deg in latitude at 180. deg longitude.
#       Units = degree; Format = float; Default: taperL=5, taperB=180 peakL=25
    taperL = pexConfig.Field('', float, default=2.)
    taperB = pexConfig.Field('', float, default=180.)
    peakL = pexConfig.Field('', float, default=20.)

#   Min/Max Declination of allowable observations
#       Units = degree; Format = float; Default is 80.
    maxReach = pexConfig.Field('', float, default=90.0)

#   Ecliptic inclusion zone
#       During a night the potentially visible fields are bracketted by
#       region: [*],[-EB : +EB]
#       Units = Ecliptic degree; Format = float; Default is 10.
    EB = pexConfig.Field('', float, default=10.)

# --------------------------------------------------------------------
#               Target Selection Parameters
# --------------------------------------------------------------------
#   Maximum accepted airmass
#       Units: unitless Format: float   Default: 2.0
    MaxAirmass   = pexConfig.Field('', float, default=2.0)

#   Maximum accepted seeing (not adjusted for airmass)
#       Units: arcseconds Format: float   Default: 2.0
    MaxSeeing    = pexConfig.Field('', float, default=2.0)

#   Minimum Cloud Transparency of allowable observations
#       Units = range 0:1; Format = float; Default is .9; Hardcoded limit=.9
    minTransparency = pexConfig.Field('', float, default=.7)

#   Exposure time in seconds per visit
#       Units: seconds   Format: float   Default: 30.0
    ExposureTime = pexConfig.Field('', float, default=34.0)      # 2 15-secs. exposures, 1 2-secs. readout, 2-secs. shutter time

# MM - NOT YET IMPLEMENTED  11/03/05
#  Hard-coded in AstronomicalSky.py to -18.0 degrees
#   Boundary when TwilightObserving begins/ends
#       Units = degrees Format = float; Default is -12. 
    TwilightBoundary = pexConfig.Field('', float, default=-12.)
                                                                                    
# -----------------------------------------------------------------------
#                   Target Ranking Parameters
# -----------------------------------------------------------------------
#   Relative priority parameter for the proposal.
#       Factor applied in final rank for all obs proposed by this proposal.
#       Default = 1.0
    RelativeProposalPriority = pexConfig.Field('', float, 5.0)

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
    MaxProximityBonus = pexConfig.Field('', float, 0.5)

#   Ranking values
#
#   Maximum rank scale for the time window
#       No default.
    RankTimeMax = pexConfig.Field('', float, 1.00)

#   Maximum rank bonus for sequence that has exhausted allowable misses.
#       No default.
    RankLossRiskMax = pexConfig.Field('', float, default=10.0)

#   Rank for an idle sequence (not started yet).
#       No default.
    RankIdleSeq = pexConfig.Field('', float, default=0.10)

# Accept observations with low ranking in this proposal
# that have been observed for other proposals?
    AcceptSerendipity = pexConfig.Field('', bool, default=False)

# Accept consecutive observations for the same field
    AcceptConsecutiveObs = pexConfig.Field('', bool, default=True)
