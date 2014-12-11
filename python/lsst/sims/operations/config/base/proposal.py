import lsst.pex.config as pexConfig

class ProposalConfig(pexConfig.Config):
    """
    This is the base class for the proposal variants.
    """
    name = pexConfig.Field('Unique identifier for the proposal.', str)

    WLType = pexConfig.Field('Identified the proposal as standard (False) or '
                             'transient (True).', bool, default=False)

    # WFD: Wide, Fast, Deep
    # DD: Deep Drilling
    ScienceType = pexConfig.ListField('Description of science type. This can '
                                      'have more than one value. Possible '
                                      'values are: WFD, Rolling, DD', str,
                                      default=["WFD"])

    targetSelect = pexConfig.ConfigField('Set of target selection parameters.',
                                         TargetSelectionConfig)

class StandardProposalConfig(ProposalConfig):
    """
    This class handles parameters for standard (non transient) proposals.
    """

    eventSequence = pexConfig.ConfigField('Set of event sequencing parameters.',
                                          StandardEventSequencingConfig)

    fieldSelect = pexConfig.ConfigField('Set of field selection parameters.',
                                        FieldSelectionConfig)

    targetRanking = pexConfig.ConfigField('Set of target ranking parameters.',
                                          TargetRankingConfig)

class TransientProposalConfig(ProposalConfig):
    """
    This class handles parameters for transient (time-varying) proposals.
    """

    eventSequence = pexConfig.ConfigField('Set of event sequencing parameters.',
                                          TransientEventSequencingConfig)

    fieldSelect = pexConfig.ConfigField('Set of field selection parameters.',
                                        TransientFieldSelectionConfig)

    targetRanking = pexConfig.ConfigField('Set of target ranking parameters.',
                                          TransientTargetRankingConfig)
