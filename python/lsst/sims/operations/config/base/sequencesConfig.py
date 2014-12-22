import filters

import lsst.pex.config as pexConfig

class BaseSequenceConfig(pexConfig.Config):
    """
    This class holds the information for configuring an observation sequence.
    """
    name = pexConfig.Field('Name of sequence', str)
    numSequenceEvents = pexConfig.Field('Number of requested events for this '
                                        'sequence', int)
    numMaxMissed = pexConfig.Field('Number of missed events allowed for this '
                                   'sequence', int)
    sequenceInterval = pexConfig.Field('Valid interval in seconds', int)
    sequenceWindowStart = pexConfig.Field('Time event\'s priority starts '
                                          'rising', float)
    sequenceWindowMax = pexConfig.Field('Time event\'s priority reaches '
                                        'maximum', float)
    sequenceWindowEnd = pexConfig.Field('Time at which event is abandoned',
                                        float)

class SequenceConfig(BaseSequenceConfig):
    """
    This class is for configuring a given filter-subsequence.
    """
    sequenceFilter = pexConfig.ListField('Filter for the sequence', str)
    numSequenceExposures = pexConfig.DictField('Number of exposures per filter',
                                               str, int)

class MasterSequenceConfig(BaseSequenceConfig):
    """
    This class is for configuring a master sequence in a time-varying proposal.
    """
    subSequence = pexConfig.ConfigField('List of configs for sub-sequence',
                                        SequenceConfig, default=None)

class EventSequencingConfig(pexConfig.Config):
    """
    This class handles the configuration for event sequences.
    """

    HiatusNextNight = pexConfig.Field('Gap in nights to next observing night. '
                                      'Do we want this proposal to run every '
                                      'night? Every night = 0 and every other '
                                      'night = 1 etc. (units=nights).', int,
                                      default=0)

    # Name in Standard (static) proposals: MaxNeedAfterOverflow
    OverflowLevel = pexConfig.Field('Initial value for needed visits after '
                                    'completing the requested visits for that '
                                    'field-filter. Need starts at this value '
                                    'decaying when getting additional visits.',
                                    float, default=0.0)

    # Parameters for controlling the promotion of nearly complete field-filters.
    # The rank is basically the expression:
    # rank = scale * (partialneed/partialgoal) / (globalneed/globalgoal)
    # where partialneed = partialgoal - partialvisits for a particular
    # field-filter progress is defined as partialvisits/partialgoal.
    # When progress becomes greater than ProgressToStartBoost parameter,
    # rank receives an additional boost factor determined by:
    # MaxBoostToComplete * (progress-ProgressToStartBoost) /
    #                      (1-ProgressToStartBoost)
    # To disable this feature these are the values for both parameters.
    # ProgressToStartBoost = 1.00
    # MaxBoostToComplete   = 0.00
    ProgressToStartBoost = pexConfig.Field('Threshold of progress (decimal '
                                           'percentage) when rank receives an '
                                           'additional boost.', float,
                                           default=1.0)
    # This is actually calculated, so it really shouldn't be a parameter!
    MaxBoostToComplete = pexConfig.Field('Calculated boost value.', float,
                                         default=0.0)

    filters = pexConfig.ConfigField('Alternate specification of filter '
                                    'parameters.', filters.FiltersConfig)

class StandardEventSequencingConfig(EventSequencingConfig):
    """
    This class handles event sequencing in standard proposals.
    """

    NVisits = pexConfig.Field('Default number (count) of visits per '
                              'field/filter if specific filter not provided.',
                              float, default=30.)

class TransientEventSequencingConfig(EventSequencingConfig):
    """
    This class handles event sequencing in transient proposals.
    """

    MaxNumberActiveSequences = pexConfig.Field('Maximum number of sequences '
                                               'active simultaneously.', int,
                                               default=100)

    RestartLostSequences = pexConfig.Field('Indicates incomplete sequences '
                                           'may be restarted if terminated '
                                           'early.', bool, default=False)

    RestartCompleteSequences = pexConfig.Field('Indicates successfully '
                                               'completed sequences may be '
                                               'restarted on completion.',
                                               bool, default=False)

    masterSequences = pexConfig.ConfigDictField('The list of master sequences.',
                                                int, MasterSequenceConfig,
                                                optional=True)

    sequences = pexConfig.ConfigDictField('The list of sequences.', int,
                                          SequenceConfig)
