import lsst.pex.config as pexConfig

class UserRegionConfig(pexConfig.Config):
    """
    This class configures a given user sky region.
    """
    ra = pexConfig.Field('RA of region in degrees', float)
    dec = pexConfig.Field('Dec of region in degrees', float)
    diameter = pexConfig.Field('Width of region in degrees', float)

class FieldSelectionConfig(pexConfig.Config):
    """
    This class handles the configuration for the field selection criteria.
    """
    userRegions = pexConfig.ConfigDictField('List of locations on the sky to '
                                            'target.', int, UserRegionConfig,
                                            optional=True)

    # Galactic plane exclusion zone
    # Currently defines two triangular regions.
    #                    -----                   L=+20
    #               -----     -----
    #          -----               -----         L=+2
    #          |-----------|-----------|         L=0
    #   B=-180 -----      B=0      ----- B=+180  L=-2
    #               -----     -----
    #                    -----                   L=-20
    taperL = pexConfig.Field('The half width in galactic latitude (degrees) at '
                             'the galactic longitude specified by taperB.',
                             float, default=2.0)
    taperB = pexConfig.Field('The galactic longitude (degrees) where taperL is '
                             'in effect.', float, default=180.0)
    peakL = pexConfig.Field('The half width in galactic latitude (degrees) at '
                            'the galactic longitude of 0.', float, default=20.0)

    deltaLST = pexConfig.Field('During night potentially visible fields are '
                               'bracketed by region: [LST@sunSet-deltaLST, '
                               'LST@sunRise+deltaLST], '
                               '[Dec-arccos(1/MaxAirmass), '
                               'Dec+arccos(1/MaxAirmass)]', float, default=60.0)

    maxReach = pexConfig.Field('Min/Max Declination (degrees) of allowable '
                               'observations', float, default=90.0)

class TransientFieldSelectionConfig(FieldSelectionConfig):
    """
    This class adds parameters to handle transient proposals.
    """

    newFieldsLimitEast_afterLSTatSunset = pexConfig.Field('Limits in degrees '
                                                          'for the range of '
                                                          'the sky to build '
                                                          'the list of new '
                                                          'targets every '
                                                          'night.', float,
                                                          default=0.0)
    newFieldsLimitWest_beforeLSTatSunrise = pexConfig.Field('Limits in degrees '
                                                            'for the range of '
                                                            'the sky to build '
                                                            'the list of new '
                                                            'targets every '
                                                            'night.', float,
                                                            default=0.0)

    #  Ecliptic inclusion zone
    EB = pexConfig.Field('The half width (degrees) of the inclusion zone '
                         'around the ecliptic. A zero means don\'t use.',
                         float, default=0.0)
