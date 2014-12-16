from .base import lsstconf as baseLsstconf
import factories
import filters
from .sched_downtime import ScheduledDowntime
import sites
from .unsched_downtime import UnscheduledDowntime

class OpSimConfig(object):
    """
    This class is for storing simulation level configuration information that
    does not need to be stored.
    """
    verbose = 0

    def __init__(self):
        pass

class LsstSim(object):

    def __init__(self, proposal_list, obs_site="CerroPachon"):
        self.lsst = baseLsstconf.LsstConfig()
        self.obs_site = sites.CerroPachon()
        self.filters = filters.Filters30()
        self.sched_down = ScheduledDowntime()
        self.unsched_down = UnscheduledDowntime()
        self.proposals = factories.load_proposals(proposal_list)

    def save(self, file_head, save_dir=None, hidden=False):
        if save_dir is None:
            import os
            save_dir = os.path.abspath(os.getcwd())

    def load(self, pargs):
        """
        This function takes an args parameter to gather all of the override
        config files.

        @param pargs: An argument object containing possible config files.
        """
        pass
