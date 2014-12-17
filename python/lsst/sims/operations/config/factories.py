import lsst.pex.config as pexConfig

import base
import utils

def load_proposals(proposal_str):
    """
    Get a list of proposal instances based off a comma-separated string of
    proposal class names. The module name is set in the function.

    @param proposal_str: A comma-separates string of proposal names
    """
    proposals = []
    module_name = "lsst.sims.operations.config."
    for proposal_class in proposal_str.split(','):
        try:
            cls = utils.load_class(module_name + proposal_class)
            proposals.append(cls())
        except AttributeError:
            print("WARNING: %s proposal not found!" % proposal_class)
    return proposals

def list_proposals():
    """
    This function parses through the config module and find all of the proposal
    class names and prints them.
    """
    import importlib
    prop_list = []
    module_name = "lsst.sims.operations.config"
    module = importlib.import_module(module_name)
    names = dir(module)
    for name in names:
        cls = utils.load_class(module_name + "." + name)
        try:
            spc = issubclass(cls, base.StandardProposalConfig)
            tpc = issubclass(cls, base.TransientProposalConfig)
            if spc or tpc:
                prop_list.append(cls.__name__)
        except TypeError:
            # Don't care about things that aren't classes.
            pass
    return prop_list

siteRegistry = pexConfig.makeRegistry('Registry for observing site '
                                      'configurations.', base.SiteConfig)

filtersRegistry = pexConfig.makeRegistry('Registry for observation filter '
                                         'sets.', base.FiltersConfig)
