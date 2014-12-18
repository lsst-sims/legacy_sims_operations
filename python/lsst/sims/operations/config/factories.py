import lsst.pex.config as pexConfig

import base
import utils

standardPropReg = pexConfig.makeRegistry('A registry for standard proposal '
                                         'types.', base.StandardProposalConfig)

transientPropReg = pexConfig.makeRegistry('A registry for transient proposal '
                                          'types.',
                                          base.TransientProposalConfig)

def load_proposals(proposal_str):
    """
    Get a list of proposal instances based off a comma-separated string of
    proposal class names. The module name is set in the function.

    @param proposal_str: A comma-separates string of proposal names
    """
    proposals = []
    module_name = "lsst.sims.operations.config.proposals."
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

    @return: A dictionary listing the proposals for the two main classes.
    """
    import importlib
    STANDARD = "Standard"
    TRANSIENT = "Transient"

    prop_dict = {STANDARD: [], TRANSIENT: []}
    module_name = "lsst.sims.operations.config.proposals"
    module = importlib.import_module(module_name)
    names = dir(module)
    for name in names:
        cls = utils.load_class(module_name + "." + name)
        try:
            key = None
            if issubclass(cls, base.StandardProposalConfig):
                key = STANDARD
            if issubclass(cls, base.TransientProposalConfig):
                key = TRANSIENT
            if key is not None:
                prop_dict[key].append(cls.__name__)
        except TypeError:
            # Don't care about things that aren't classes.
            pass
    return prop_dict
