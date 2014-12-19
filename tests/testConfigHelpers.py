import unittest

import lsst.sims.operations.config.helpers as configHelpers

class TestConfigHelpers(unittest.TestCase):

    def testListProposals(self):
        proposals = configHelpers.listProposals()
        self.assertEquals(len(proposals.keys()), 2)
        self.assertEquals(len(proposals.items()), 2)

    def testLoadProposals(self):
        proposals = configHelpers.loadProposals("SouthCelestialPole")
        self.assertEquals(proposals[0].name, "SouthCelestialPole-18-0824")
        self.assertEquals(proposals[0].eventSequence.NVisits, 3)

    def testStandardProposalRegistry(self):
        props = configHelpers.standardPropReg
        self.assertEquals(len(props.items()), 1)

    def testTransientProposalRegistry(self):
        props = configHelpers.transientPropReg
        self.assertEquals(len(props.items()), 1)

if __name__ == "__main__":
    unittest.main()
