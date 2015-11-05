import unittest

import lsst.sims.operations.Database as DB
import lsst.sims.operations.Filters as F

class TestFilters(unittest.TestCase):
    def setUp(self):
        """
        Setup necessary objects for creating an Instrument.
        """
        self.db = DB.Database(False, dbConnect=False)

        # Parameters for seeing adjustments
        telescope_seeing = 0.25
        optical_design_seeing = 0.08
        camera_seeing = 0.3
        scale_to_neff = 1.16
        atm_neff_factor = 1.04

        self.filters = F.Filters(self.db, "conf/system/Filters.conf", 1, {},
                                 telescope_seeing, optical_design_seeing, camera_seeing,
                                 scale_to_neff, atm_neff_factor, verbose=-1)

    def tearDown(self):
        self.db.closeConnection()

    def testInitialCreation(self):
        self.assertEqual(self.filters.seeing_fwhm_sys_zenith, 0.39862262855989494)
        # g filter wavelength correction
        self.assertEqual(self.filters.filterNamesSorted[1], 'g')
        self.assertEqual(self.filters.basefilterWavelenSorted[1], 1.0107454756446859)

    def testSeeingComputationInGBand(self):
        seeing = 0.7
        airmass = 1.1
        filterList = {}
        import math
        airmassCorrection = math.pow(airmass, 0.6)
        self.filters.computeFwhmEffSeeing(filterList, 1, seeing, airmassCorrection)
        self.assertEquals(filterList['g'], 1.0124922970058186)

if __name__ == "__main__":
    unittest.main()
