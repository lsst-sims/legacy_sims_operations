from .downtime import DowntimeConfig
from .filters import FiltersConfig
from .instrument import InstrumentConfig
from lsst.sims.operations.config.base.proposalconf import ProposalConfig
from .scheduler import SchedulerConfig
from .scheduler import SchedulingDataConfig
from lsst.sims.operations.config.base.siteconf import SiteConfig

import lsst.pex.config as pexConfig

class LsstConfig(pexConfig.Config):
    """
    This class handles the configuration of the LSST universe.
    """

    nRun = pexConfig.Field('The length (years) of the simulation.', float,
                           default=1.0)

    simStartDay = pexConfig.Field('Days (MJD) relative to seeingEpoch from '
                                  'which simulation commences. Zero starts '
                                  'the simulation with the first year of '
                                  'weather data.', float,
                                  default=0.0)

    # Field of View
    # When using bundled fov, reset Scheduler:reuseRankCount to 1
    # Prepackaged FOV are in range: [3.0 : 4.0] in steps of .1
    # Additional FOV are easily installed on request.
    #       Units = degree; Format = float; Default = 3.5
    fov = pexConfig.Field('Telescope field of view (units=degrees)', float,
                          default=3.5)

    # Telescope Effects factor degrades seeing with zenith distance
    # Optical Design and Camera factor degrades seeing a fixed amount
    # adjust = sqrt ((seeing * filter_wavelength * airmass^0.6)^2 +
    #                (telSeeing * airmass^0.6)^2 + opticalDesSeeing^2 +
    #               cameraSeeing^2)
    telSeeing = pexConfig.Field('Size of seeing degradation due to the '
                                'telescope\'s distance from zenith.', float,
                                default=0.241)
    opticalDesSeeing = pexConfig.Field('Size of seeing degradation due to the '
                                       'optical design.', float, default=0.097)
    cameraSeeing = pexConfig.Field('Size of seeing degradation due to camera.',
                                   float, default=0.280)

    idleDelay = pexConfig.Field('Time (seconds) to delay when no target is '
                                'available for observation.', int, default=300)

    maxCloud = pexConfig.Field('Maximum cloudiness for observing, regardless '
                               'of proposal needs in decimal percentage.',
                               float, default=0.7)

    siteConf = pexConfig.ConfigField('The telescope site configuration.',
                                     SiteConfig)

    proposals = pexConfig.ConfigDictField('The list of proposals to run.', int,
                                          ProposalConfig, default={})

    instrument = pexConfig.ConfigField('The instrument configuration.',
                                       InstrumentConfig)

    #schedDown = pexConfig.ConfigurableField('The set of scheduled downtimes.',
    #                                        ConfigClass=DowntimeConfig)

    unschedDown = pexConfig.ConfigField('The set of unscheduled downtimes.',
                                        DowntimeConfig)

    filters = pexConfig.ConfigField('The filter configuration.', FiltersConfig)

    scheduler = pexConfig.ConfigField('The scheduler configuration.',
                                      SchedulerConfig)

    schedulingData = pexConfig.ConfigField('The scheduling data configuration.',
                                           SchedulingDataConfig)

    table_names = {"obsHistTbl": "ObsHistory",
                   "timeHistTbl": "TimeHistory",
                   "proposalTbl": "Proposal",
                   "sessionTbl": "Session",
                   "seqHistoryTbl": "SeqHistory",
                   "fieldTbl": "Field",
                   "downHistTbl": "DownHist"}

    opsimdbTables = pexConfig.DictField('The dictionary of table names for the '
                                        'OpsimDB.', str, str,
                                        default=table_names)
