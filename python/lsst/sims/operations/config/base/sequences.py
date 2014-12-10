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
