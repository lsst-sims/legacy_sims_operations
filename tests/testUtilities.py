import unittest

import lsst.sims.operations.utilities as utilities

class TestUtilities(unittest.TestCase):

    def testTimeStr2Sec(self):
        """
        Test various time string conversions to seconds
        """
        _testvals = {"0": 0,
                     "30": 30,
                     "30s": 30,
                     "1d": 86400,
                     "1w": 86400 * 7,
                     "0.5y": 86400 * 365 / 2,
                     "20m": 60 * 20,
                     "20min": 60 * 20,
                     "1h20m": 3600 + 60 * 20,
                     "3mon": 86400 * 30 * 3}

        for k, v in _testvals.items():
            self.assertEqual(utilities.timeStr2Sec(k), v)

if __name__ == "__main__":
    unittest.main()
