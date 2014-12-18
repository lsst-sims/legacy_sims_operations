import unittest

import lsst.sims.operations.config.helpers as helpers

class TestConfigHelpers(unittest.TestCase):

    def testListProposals(self):
        proposals = helpers.listProposals()
        self.assertEquals(len(proposals.keys()), 2)
        self.assertEquals(len(proposals.items()), 2)

    def testLoadProposals(self):
        proposals = helpers.loadProposals("SouthCelestialPole")
        self.assertEquals(proposals[0].name, "SouthCelestialPole-18-0824")
        self.assertEquals(proposals[0].eventSequence.NVisits, 3)

if __name__ == "__main__":
    unittest.main()
