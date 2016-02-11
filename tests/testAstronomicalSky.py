import math
import unittest

import lsst.sims.operations.Database as DB
import lsst.sims.operations.AstronomicalSky as AS
import lsst.sims.operations.utilities as utilities

class TestAstronomicalSky(unittest.TestCase):

    def setUp(self):
        """
        Setup necessary objects for creating an AstronomicalSky instance.
        """
        self.db = DB.Database(False, dbConnect=False)

        # Setup observatory profile
        configDict, pairs = utilities.readConfFile("example_conf/system/SiteCP.conf")
        simStartDay = 0.0
        obsProfile = (configDict["longitude"] * utilities.DEG2RAD,
                      configDict["latitude"] * utilities.DEG2RAD,
                      configDict["height"],
                      configDict["seeingEpoch"] + simStartDay,
                      configDict["pressure"],
                      configDict["temperature"],
                      configDict["relativeHumidity"])

        self.sky = AS.AstronomicalSky(self.db, obsProfile, 0., 1, {},
                                      configFile="example_conf/system/AstronomicalSky.conf")

        # Field position in degrees
        self.ra = 96.055377
        self.dec = -62.021153
        self.alt = 43.098286
        self.az = 148.697731

    def tearDown(self):
        self.db.closeConnection()

    def testLsstVSkyBrightness(self):
        date = 2922.8256
        dp = self.sky.computeDateProfile(date)
        mp = self.sky.computeMoonProfile(date)

        (sb, moon_dist, moon_alt) = self.sky.getLsstVSkyBrightness(self.ra, self.dec, self.alt, self.az,
                                                                   dp, mp)
        self.assertEquals(sb, 19.52104094298906)
        self.assertAlmostEqual(moon_dist, 1.621921, delta=1e-6)
        self.assertAlmostEqual(moon_alt, -0.493971, delta=1e-6)

    def testSkyBrightnessForFilter(self):
        ofilter = 'y'
        mjd = 59580.033829
        sb = self.sky.getSkyBrightnessForFilter(self.ra, self.dec, self.alt, self.az, ofilter, mjd)
        self.assertAlmostEqual(sb, 16.463820733240276, delta=1e-7)

    def testNanLsstVSkyBrightness(self):
        date = 23482.0
        dp = self.sky.computeDateProfile(date)
        mp = self.sky.computeMoonProfile(date)
        ra = 29.6710624694824
        dec = -63.7820816040039
        alt = math.degrees(0.407980)
        az = math.degrees(3.637970)
        (sb, moon_dist, moon_alt) = self.sky.getLsstVSkyBrightness(ra, dec, alt, az, dp, mp)
        self.assertEquals(sb, -999.0)

if __name__ == "__main__":
    unittest.main()
