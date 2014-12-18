import lsst.pex.config as pexConfig

class FilterConfig(pexConfig.Config):
    """
    This class holds the primary configuration for a given filter. The
    values contained in here are based off two 15 second exposures for the
    visits.
    """
    name = pexConfig.Field('Name of filter', str)
    minBright = pexConfig.Field('Minimum V band sky brightness', float)
    maxBright = pexConfig.Field('Maximum V band sky brightness', float)
    wavelength = pexConfig.Field('The wavelength (microns) center of the '
                                 'filter band.', float)
    maxSeeing = pexConfig.Field('The maximum allowed seeing for the filter.',
                                float, optional=True)
    numVisits = pexConfig.Field('The number of requested visits for this '
                                'filter.', int, optional=True)
    # Multiplicative factor for the visit time
    # VisitTime = Nexp*(ShutterTravelTime + EffectiveExpTime) +
    #             (Nexp-1)*ReadoutTime
    # In this version of the code:
    #                      Nexp=2 hardcoded
    #                      ShutterTravelTime = 1[sec] hardcoded
    #                      ReadoutTime = 2[sec] parameter in Instrument.conf
    #                      VisitTime = 34[sec] parameter in science programs
    # 30 seconds effective exposure instead of 15 seconds
    # Filter_ExpFactor = (2*(30+1)+2)/(2*(15+1)+2) = 64 / 34 = 1.88235
    expFactor = pexConfig.Field('A scale factor that can adjust the visit '
                                'exposure time from the standard of 34 seconds '
                                'which is based on 2 15 second exposures plus '
                                'readout and shutter time.', float,
                                default=1.0)

class FiltersConfig(pexConfig.Config):
    """
    This class is for the collection of all necessary filters for observations.
    """
    filters = pexConfig.ConfigDictField('Collection of all observation '
                                        'filters.', str, FilterConfig)

    def setDefaults(self):
        """
        This function sets the information for the standard LSST observation
        filters based on the 2x 15 second exposure case.
        """
        uFilter = FilterConfig()
        uFilter.name = 'u'
        uFilter.minBright = 21.4
        uFilter.maxBright = 30.0
        uFilter.wavelength = 0.34
        uFilter.expFactor = 1.0

        gFilter = FilterConfig()
        gFilter.name = 'g'
        gFilter.minBright = 21.0
        gFilter.maxBright = 30.0
        gFilter.wavelength = 0.52
        gFilter.expFactor = 1.0

        rFilter = FilterConfig()
        rFilter.name = 'r'
        rFilter.minBright = 20.5
        rFilter.maxBright = 30.0
        rFilter.wavelength = 0.67
        rFilter.expFactor = 1.0

        iFilter = FilterConfig()
        iFilter.name = 'i'
        iFilter.minBright = 20.25
        iFilter.maxBright = 30.0
        iFilter.wavelength = 0.79
        iFilter.expFactor = 1.0

        zFilter = FilterConfig()
        zFilter.name = 'z'
        zFilter.minBright = 17.5
        zFilter.maxBright = 21.0
        zFilter.wavelength = 0.91
        zFilter.expFactor = 1.0

        yFilter = FilterConfig()
        yFilter.name = 'y'
        yFilter.minBright = 17.5
        yFilter.maxBright = 21.0
        yFilter.wavelength = 1.04
        yFilter.expFactor = 1.0

        self.filters = {'u': uFilter, 'g': gFilter, 'r': rFilter, 'i': iFilter,
                        'z': zFilter, 'y': yFilter}
