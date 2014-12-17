from .base import lsstbaseconf as baseLsstBaseConf

import lsst.pex.config as pexConfig

from .filters import Filters30
from .sched_downtime import ScheduledDowntime
from .sites import CerroPachon
from .unsched_downtime import UnscheduledDowntime

class LsstSimConfig(baseLsstBaseConf.LsstBaseConfig):
    """
    This class handles the configuration of the LSST universe.
    """
    verbose = pexConfig.Field('The chattiness of the program.', int, default=1)

    dbWrite = pexConfig.Field('Flag to write to the simulation DB.', bool,
                              default=True)

    officialRun = pexConfig.Field('Flag to signify this is an officially '
                                  'tracked run. DO NOT SET TO TRUE UNLESS '
                                  'AUTHORIZED! THANKS!', bool, default=False)

    logFile = pexConfig.Field('File for the logging output.', str,
                              default='./lsst.log')

    import base
    siteConf = pexConfig.ConfigField('The telescope site configuration.',
                                     base.SiteConfig, default=CerroPachon())

    standard_proposals = pexConfig.ConfigDictField('The list of standard '
                                                   'proposals to run.', int,
                                                   base.StandardProposalConfig,
                                                   default={})

    transient_proposals = pexConfig.ConfigDictField('The list of transient '
                                                    'proposals to run.', int,
                                                    base.TransientProposalConfig,
                                                    default={})

    schedDown = pexConfig.ConfigField('The set of scheduled downtimes.',
                                      ScheduledDowntime,
                                      default=ScheduledDowntime())

    unschedDown = pexConfig.ConfigField('The set of unscheduled downtimes.',
                                        UnscheduledDowntime,
                                        default=UnscheduledDowntime())

    filters = pexConfig.ConfigField('The filter configuration.',
                                    base.FiltersConfig, default=Filters30())
    
    def __init__(self):
        pass
