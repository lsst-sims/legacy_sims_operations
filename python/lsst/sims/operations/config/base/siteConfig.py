import lsst.pex.config as pexConfig

class SiteConfig(pexConfig.Config):
    """
    This is the base configuration class for Telescope site information.
    """
    name = pexConfig.Field('Telescope site name.', str)
    seeingEpoch = pexConfig.Field('Jan 1 of the year seeing data was collected '
                                  '(units=MJD)', int)
    latitude = pexConfig.Field('Telescope site\'s Latitude (units=degrees), '
                               'negative implies South.', float)
    longitude = pexConfig.Field('Telescope site\'s Longitude (units=degrees), '
                                'negative implies West', float)
    height = pexConfig.Field('Telescope site\'s Elevation (units=meters above '
                             'sea level)', float)
    pressure = pexConfig.Field('Telescope site\'s atmospheric pressure '
                               '(units=millibars)', float)
    temperature = pexConfig.Field('Telescope site\'s atmospheric temperature '
                                  '(units=degrees C)', float)
    relativeHumidity = pexConfig.Field('Telescope site\'s relative humidity '
                                       '(units=precent)', float)
    weatherSeeingFudge = pexConfig.Field('Weather data\'s seeing fudge factor '
                                         'applied to all seeing values. '
                                         'Modifies all seeing data and to '
                                         'moderate "seeing too good to be true"'
                                         'sanity test runSeeing = '
                                         'weatherSeeing * weatherSeeingFudge * '
                                         'telescopeEffectsFudge '
                                         '(units=unitless)', float)
    seeingTbl = pexConfig.Field('Telescope site specific seeing Database '
                                'table.', str)
    cloudTbl = pexConfig.Field('Telescope site specific cloud Database table.',
                               str)

    def setDefaults(self):
        """
        This function sets the defaults to the Cerro Pachon observing site.
        """
        self.name = "Cerro Pachon"
        self.seeingEpoch = 49353
        self.latitude = -29.666667
        self.longitude = -70.59
        self.height = 2737.0
        self.pressure = 1010.0
        self.temperature = 12.0
        self.relativeHumidity = 0.0
        self.weatherSeeingFudge = 1.0
        self.seeingTbl = "Seeing"
        self.cloudTbl = "Cloud"
