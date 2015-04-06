import unittest

import lsst.sims.operations.Database as DB
import lsst.sims.operations.Instrument as Inst
import lsst.sims.operations.utilities as utilities

class TestInstrument(unittest.TestCase):

    def setUp(self):
        """
        Setup necessary objects for creating an Instrument.
        """
        self.db = DB.Database(False)

        # Setup observatory profile
        configDict, pairs = utilities.readConfFile("conf/system/SiteCP.conf")
        simStartDay = 0.0
        obsProfile = (configDict["longitude"] * utilities.DEG2RAD,
                      configDict["latitude"] * utilities.DEG2RAD,
                      configDict["height"],
                      configDict["seeingEpoch"] + simStartDay,
                      configDict["pressure"],
                      configDict["temperature"],
                      configDict["relativeHumidity"])

        self.inst = Inst.Instrument(self.db, 1, {}, obsProfile, "conf/system/Instrument.conf", verbose=-1)

    def tearDown(self):
        self.db.closeConnection()

    def testBurstFilterChange(self):
        # No filter change
        self.assertTrue(self.inst.AllowFilterChange("r", 0))
        # Do filter change, should be allowed
        self.assertTrue(self.inst.AllowFilterChange("i", 1 * 60))
        self.inst.current_state.Filter_Pos = "i"
        self.inst.filterChangesTimeHistory.append(1 * 60)
        # Do next filter change faster, should not be allowed
        self.assertFalse(self.inst.AllowFilterChange("r", 5 * 60))
        # Do next filter change slower, should be allowed
        self.assertTrue(self.inst.AllowFilterChange("g", 21 * 60))

    def testAverageFilterChanges(self):
        # Set filter change history
        self.inst.current_state.Filter_Pos = "r"
        self.inst.filterChangesTimeHistory = [0.0, 20.0 * 60.0, 40.0 * 60.0, 60.0 * 60.0, 80.0 * 60.0]
        # Allow 5 filter changes in two hours
        self.inst.slew_params.Filter_MaxChangesAvgNumber = 5
        self.inst.slew_params.Filter_MaxChangesAvgTime = 2.0 * 60.0 * 60.0

        # This filter change should pass burst change, but fail average change
        self.assertFalse(self.inst.AllowFilterChange("i", 100.0 * 60.0))
        # This filter change should pass both burst and average change
        self.assertTrue(self.inst.AllowFilterChange("i", 120.0 * 60.0))

if __name__ == "__main__":
    unittest.main()
