import lsst.pex.config as pexConfig

import base
import factories
from .sched_downtime import ScheduledDowntime
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

    standardProposals = pexConfig.ConfigDictField('The list of standard '
                                                  'proposals to run.', int,
                                                  base.StandardProposalConfig)

    transientProposals = pexConfig.ConfigDictField('The list of transient '
                                                   'proposals to run.', int,
                                                   base.TransientProposalConfig)

    schedDown = pexConfig.ConfigField('The set of scheduled downtimes.',
                                      ScheduledDowntime)

    unschedDown = pexConfig.ConfigField('The set of unscheduled downtimes.',
                                        UnscheduledDowntime)

    def setDefaults(self):
        """
        Set default objects here.
        """
        base.LsstBaseConfig.setDefaults(self)

        self.schedDown = ScheduledDowntime()
        self.unschedDown = UnscheduledDowntime()
