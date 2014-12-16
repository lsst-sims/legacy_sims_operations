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
