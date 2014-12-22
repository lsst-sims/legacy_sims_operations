import lsst.pex.config as pexConfig

__all__ = ["AstronomicalSkyConfig"]

class AstronomicalSkyConfig(pexConfig.Config):
    """
    This class holds the parameters for defining aspects of the astronomical
    sky.
    """
    # Use 0.56 for weather data prior to Claver set
    Wavelength = pexConfig.Field('Wavelength of light (microns) for Claver '
                                 'Seeing & Cloud data', float, default=0.5)

    #################### Optimizations: Sky Brightness ####################
    ########## Do not change unless you know what you are doing ###########

    SBDateScale = pexConfig.Field('Sky brightness resolution scale for dates '
                                  '(seconds).', int, default=3600)

    SBRAScale = pexConfig.Field('Sky brightness resolution scale for RA '
                                '(decimal degrees).', float, default=7.0)

    SBDecScale = pexConfig.Field('Sky brightness resolution scale for Dec '
                                 '(decimal degrees).', float, default=7.0)

    ####################### Optimizations: Airmass ########################
    # Setting scales to 1. will effectively turn off cacheing.

    # Old default was 30.
    ADateScale = pexConfig.Field('Airmass resolution scale for dates '
                                 '(seconds).', int, default=1)

    # Old default was 5.0
    ARAScale = pexConfig.Field('Airmass resolution scale for RA (decimal '
                               'degrees).', float, default=1.0)

    # Old default was 5.0
    ADecScale = pexConfig.Field('Airmass resolution scale for Dec (decimal '
                                'degrees).', float, default=1.0)

    ###################### TWILIGHT PARAMETERS ###########################

    # NIGHT LIMITS
    SunAltitudeNightLimit = pexConfig.Field('Altitude of the Sun in degrees '
                                            'that define the start end end of '
                                            'the night for the purposes of '
                                            'observations', float,
                                            default=-12.0)

    # TWILIGHT LIMITS
    SunAltitudeTwilightLimit = pexConfig.Field('Altitude of the Sun in degrees '
                                               'that define the twilight. When '
                                               'the sun is above this limit '
                                               'and below the night limit, a '
                                               'special twilight factor is '
                                               'included in the sky brightness '
                                               'model', float, default=-18.0)

    # TWILIGHT BRIGHTNESS
    TwilightBrightness = pexConfig.Field('Sun brightness in magnitude/arcsec^2 '
                                         'added to the sky brightness model '
                                         'during the twilight period defined '
                                         'by the parameters '
                                         'SunAltitudeNightLimit and '
                                         'SunAltitudeTwilightLimit', float,
                                         default=17.3)
