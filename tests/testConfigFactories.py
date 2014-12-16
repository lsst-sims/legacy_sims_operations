import unittest

import lsst.sims.operations.config.factories as factories

class TestConfigFactories(unittest.TestCase):

    def testListProposals(self):
        proposals = factories.list_proposals()
        self.assertEquals(len(proposals), 2)

    def testLoadProposals(self):
        proposals = factories.load_proposals("SouthCelestialPole")
        self.assertEquals(proposals[0].name, "SouthCelestialPole-18-0824")
        self.assertEquals(proposals[0].eventSequence.NVisits, 3)

if __name__ == "__main__":
    unittest.main()
