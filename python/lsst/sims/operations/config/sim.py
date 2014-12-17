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
        """
        The class constructor.
        
        @param proposal_list: Comma-separated string of proposal names.
        @param obs_site: The class name of the observing site.
        """
        self.lsst = baseLsstconf.LsstConfig()
        self.obs_site = sites.CerroPachon()
        self.filters = filters.Filters30()
        self.sched_down = ScheduledDowntime()
        self.unsched_down = UnscheduledDowntime()
        self.proposals = factories.load_proposals(proposal_list)

    def save(self, file_head="opsim", save_dir=None, hidden=False):
        """
        This function writes out the configuration objects to separate files.
        
        @param file_head: A file part to add at the start of the filename.
        @param save_dir: Directory to save the configuration files to.
        @param hidden: Flag to write out config for things most users 
                       shouldn't touch.
        """
        import os
        if save_dir is None:
            save_dir = os.path.abspath(os.getcwd())
            
        self.lsst.save(os.path.join(save_dir, file_head + "_lsst.py"))
        self.obs_site.save(os.path.join(save_dir, file_head + "_obssite.py"))
        self.filters.save(os.path.join(save_dir, file_head + "_filters.py"))
        for i, prop in enumerate(self.proposals):
            prop.save(os.path.join(save_dir, 
                                   file_head + "_proposal%02d.py" % i))
        if hidden:
            self.sched_down.save(os.path.join(save_dir,
                                              file_head + "_scheddown.py"))
            self.unsched_down.save(os.path.join(save_dir,
                                                file_head + "_unscheddown.py"))

    def load(self, pargs):
        """
        This function takes an args parameter to gather all of the override
        config files.

        @param pargs: An argument object containing possible config files.
        """
        pass
