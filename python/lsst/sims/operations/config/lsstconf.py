import lsst.pex.config as pexConfig

import base
from .filters import Filters30
from .sched_downtime import ScheduledDowntime
from .sites import CerroPachon
from .unsched_downtime import UnscheduledDowntime

class LsstConfig(base.LsstBaseConfig):
    """
    This class handles the configuration of the LSST universe that's not
    handled in the base class.
    """
    verbose = pexConfig.Field('The chattiness of the program.', int, default=1)

    dbWrite = pexConfig.Field('Flag to write to the simulation DB.', bool,
                              default=True)

    officialRun = pexConfig.Field('Flag to signify this is an officially '
                                  'tracked run. DO NOT SET TO TRUE UNLESS '
                                  'AUTHORIZED! THANKS!', bool, default=False)

    logFile = pexConfig.Field('File for the logging output.', str,
                              default='./lsst.log')


    siteConf = pexConfig.ConfigField('The telescope site configuration.',
                                     base.SiteConfig)
    
    standard_proposals = pexConfig.ConfigDictField('The list of standard '
                                                   'proposals to run.', int,
                                                   base.StandardProposalConfig)

    transient_proposals = pexConfig.ConfigDictField('The list of transient '
                                                    'proposals to run.', int,
                                                    base.TransientProposalConfig)

    schedDown = pexConfig.ConfigField('The set of scheduled downtimes.',
                                      ScheduledDowntime)

    unschedDown = pexConfig.ConfigField('The set of unscheduled downtimes.',
                                        UnscheduledDowntime)
    
    filters = pexConfig.ConfigField('The filter configuration.',
                                    base.FiltersConfig)

    def __init__(self):
        """
        Class constructor. Set some default objects here.
        """
        self.siteConf = CerroPachon()
        self.filters = Filters30()
        self.schedDown = ScheduledDowntime()
        self.unschedDown = UnscheduledDowntime()
        

