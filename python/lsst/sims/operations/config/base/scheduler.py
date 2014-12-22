import lsst.pex.config as pexConfig

__all__ = ["SchedulerConfig", "SchedulingDataConfig"]

class SchedulerConfig(pexConfig.Config):
    """
    This class handles the configuration for the Scheduler.
    """
    # Slew time bonus for rank observations from any proposal.
    # units are [rank*sec]
    MaxSlewTimeBonus = pexConfig.Field('Bonus to add to observations which are '
                                       'in close proximity to the current '
                                       'telescope location', float,
                                       default=5.0)

    NumSuggestedObsPerProposal = pexConfig.Field('Count of observations which '
                                                 'the proposals provide to '
                                                 'ObsScheduler for final '
                                                 'ranking and selection', int,
                                                 default=500)

    reuseRankingCount = pexConfig.Field('Count of observations to take using '
                                        'precalculated science quantities.',
                                        int, default=10)

    tooGoodSeeingLimit = pexConfig.Field('Value for which provided seeing is '
                                         '"Too Good To Be True" and is '
                                         'thereafter set/capped to '
                                         'tooGoodSeeingLimit. '
                                         '(units=arcseconds)', float,
                                         default=0.25)

    randomizeSequencesSelection = pexConfig.Field('Pick observation sequences '
                                                  'at random.', bool,
                                                  default=False)

    # Filters Swap parameters
    NewMoonPhaseThreshold = pexConfig.Field('Moon phase threshold in '
                                            'percentage for filter swapping.',
                                            float, default=20.0)

    NminFiltersToSwap = pexConfig.Field('Minimum number of filters to swap at '
                                        'start of new moon phase.', int,
                                        default=1)
    NmaxFiltersToSwap = pexConfig.Field('Maximum number of filters to swap at '
                                        'start of new moon phase.', int,
                                        default=1)

    MinDistance2Moon = pexConfig.Field('Minimum angle-distance in degrees to '
                                       'the moon allowed.', float, default=30.0)

class SchedulingDataConfig(pexConfig.Config):
    """
    This class configures parameters for intelligent (look-ahead) operations.
    """

    lookAheadNights = pexConfig.Field('The number of nights for look-ahead.',
                                      int, default=1)

    lookAheadInterval = pexConfig.Field('The number of observations in the '
                                        'queue after which to perform '
                                        'look-ahead.', int, default=400)
