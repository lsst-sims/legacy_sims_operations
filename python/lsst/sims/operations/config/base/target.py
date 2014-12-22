import lsst.pex.config as pexConfig

__all__ = ["TargetRankingConfig", "TargetSelectionConfig", "TransientTargetRankingConfig"]

class TargetSelectionConfig(pexConfig.Config):
    """
    This class handles the configuration for the target selection criteria.
    """

    MaxAirmass = pexConfig.Field('Maximum accepted airmass (units=unitless)',
                                 float, default=1.6)

    MaxSeeing = pexConfig.Field('Default max airmass adjusted seeing if '
                                'specific filter not provided '
                                '(units=arcseconds)', float, default=1.5)

    minTransparency = pexConfig.Field('Minimum cloud transparency of allowable '
                                      'observations (decimal percentage)',
                                      float, default=0.7)

    # 2 15-secs. exposures, 1 2-secs. readout, 2-secs. shutter time
    ExposureTime = pexConfig.Field('Exposure time in seconds per visit. NOTE: '
                                   'This takes into account readout and '
                                   'shutter time.', float, default=34.0)

    # MM - NOT YET IMPLEMENTED  11/03/05
    #  Hard-coded in AstronomicalSky.py to -18.0 degrees
    TwilightBoundary = pexConfig.Field('Boundary when twilight observing '
                                       'begins/ends (units=degrees)', float,
                                       default=-12.0)

class TargetRankingConfig(pexConfig.Config):
    """
    This class handles the configuration for the target ranking criteria.
    """

    RelativeProposalPriority = pexConfig.Field('Relative priority parameter '
                                               'for the proposal. This factor '
                                               'is applied in the final rank '
                                               'for all the observations '
                                               'proposed by this proposal.',
                                               float, default=1.2)

    MaxProximityBonus = pexConfig.Field('Proximity bonus factor that is added '
                                        'internally in the proposal to select '
                                        'the observations to propose promoting '
                                        'the closest to the current telescope '
                                        'position. However, the scheduler then '
                                        'replaces this bonus by the more '
                                        'accurate slew time prediction.',
                                        float, default=0.5)

    RankScale = pexConfig.Field('Scale factor for ranking (i.e. value of the '
                                'average rank)', float, default=0.1)

    AcceptSerendipity = pexConfig.Field('Accept observations with low ranking '
                                        'in this proposal that have been '
                                        'observed for other proposals?', bool,
                                        default=True)

    AcceptConsecutiveObs = pexConfig.Field('Accept consecutive observations '
                                           'for the same field', bool,
                                           default=True)

    # Set these parameters if proposal should not run for the entire simulation
    StartTime = pexConfig.Field('Start time (seconds since start of '
                                'simulation) for proposal.', int,
                                optional=True)
    StopTime = pexConfig.Field('Stop time (seconds since start of simulation) '
                               'for proposal.', int, optional=True)

class TransientTargetRankingConfig(TargetRankingConfig):
    """
    This class adds extra parameters to deal with transient proposals.
    """

    RankTimeMax = pexConfig.Field('Maximum rank scale for the time window.',
                                  float, default=1.0)

    RankLossRiskMax = pexConfig.Field('Maximum rank bonus for sequence that '
                                      'has exhausted allowable misses.',
                                      float, default=0.0)

    RankIdleSeq = pexConfig.Field('Rank for an idle sequence (not started '
                                  'yet).', float, default=0.10)

    # Disabled values, formula still on development.
    RankDaysLeftMax = pexConfig.Field('', float, default=0.0)
    DaysLeftToStartBoost = pexConfig.Field('', int, default=0)
