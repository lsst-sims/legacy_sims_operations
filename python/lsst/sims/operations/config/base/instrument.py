import lsst.pex.config as pexConfig
from lsst.pex.config.rangeField import RangeField

__all__ = ["InstrumentConfig"]

class InstrumentConfig(pexConfig.Config):
    """
    This class contains the configuration of telescope and camera parameters
    and is intended to be fully instatiable.
    DO NOT MODIFY UNLESS YOU'VE TALKED WITH CHUCK CLAVER!!
    """
    DomAlt_MaxSpeed = pexConfig.Field('Maximum speed (degrees/second) of dome '
                                      'altitude movement.', float, default=1.75)
    DomAlt_Accel = pexConfig.Field('Maximum acceleration (degrees/second**2) '
                                   'of dome altitude movement.', float,
                                   default=0.875)
    DomAlt_Decel = pexConfig.Field('Maximum deceleration (degrees/second**2) '
                                   'of dome altitude movement.', float,
                                   default=0.875)

    DomAz_MaxSpeed = pexConfig.Field('Maximum speed (degrees/second) of dome '
                                     'azimuth movement.', float, default=1.5)
    DomAz_Accel = pexConfig.Field('Maximum acceleration (degrees/second**2) '
                                  'of dome azimuth movement.', float,
                                  default=0.75)
    DomAz_Decel = pexConfig.Field('Maximum deceleration (degrees/second**2) '
                                  'of dome azimuth movement.', float,
                                  default=0.75)

    TelAlt_MaxSpeed = pexConfig.Field('Maximum speed (degrees/second) of '
                                      'telescope altitude movement.', float,
                                      default=3.5)
    TelAlt_Accel = pexConfig.Field('Maximum acceleration (degrees/second**2) '
                                   'of telescope altitude movement.', float,
                                   default=3.5)
    TelAlt_Decel = pexConfig.Field('Maximum deceleration (degrees/second**2) '
                                   'of telescope altitude movement.', float,
                                   default=3.5)

    TelAz_MaxSpeed = pexConfig.Field('Maximum speed (degrees/second) of '
                                     'telescope azimuth movement.', float,
                                     default=7.0)
    TelAz_Accel = pexConfig.Field('Maximum acceleration (degrees/second**2) '
                                  'of telescope azimuth movement.', float,
                                  default=7.0)
    TelAz_Decel = pexConfig.Field('Maximum deceleration (degrees/second**2) '
                                  'of telescope azimuth movement.', float,
                                  default=7.0)

    # The following are not used in slew calculation.
    Rotator_MaxSpeed = pexConfig.Field('Maximum speed (degrees/second) of '
                                       'rotator movement.', float, default=3.5)
    Rotator_Accel = pexConfig.Field('Maximum acceleration (degrees/second**2) '
                                    'of rotator movement.', float, default=1.0)
    Rotator_Decel = pexConfig.Field('Maximum deceleration (degrees/second**2) '
                                    'of rotator movement.', float, default=1.0)

    # Absolute position limits due to cable wrap the range [0 360] must be
    # included
    TelAz_MinPos = pexConfig.Field('Minimum absolute azimuth limit (degrees) '
                                   'of telescope.', float, default=-270.0)
    TelAz_MaxPos = pexConfig.Field('Maximum absolute azimuth limit (degrees) '
                                   'of telescope.', float, default=270.0)

    Rotator_MinPos = pexConfig.Field('Minimum position (degrees) of rotator.',
                                     float, default=-90.0)
    Rotator_MaxPos = pexConfig.Field('Maximum position (degrees) of rotator.',
                                     float, default=90.0)

    Rotator_FollowSky = pexConfig.Field('Flag that if True enables the '
                                        'movement of the rotator during slews '
                                        'to put North-Up. If range is '
                                        'insufficient, then the alignment is '
                                        'North-Down. If the flag is False, '
                                        'then the rotator does not move during '
                                        'the slews, it is only tracking during '
                                        'the exposures.', bool, default=False)

    Filter_MountTime = pexConfig.Field('Time (seconds) to mount a filter.',
                                       float, default=8 * 3600.0)
    Filter_MoveTime = pexConfig.Field('Time (seconds) to move a filter.',
                                      float, default=120.0)

    Settle_Time = pexConfig.Field('Time (seconds) for the mount to settle '
                                  'after stopping.', float, default=3.0)

    DomeSettle_Time = pexConfig.Field('Times (seconds) for the dome to settle '
                                      'after stopping.', float, default=1.0)

    Readout_Time = pexConfig.Field('Time (seconds) for the camera electronics '
                                   'readout.', float, default=1.0)

    TelOpticsOL_Slope = pexConfig.Field('Delay factor for Open Loop optics '
                                        'correction (units=seconds/(degrees in '
                                        'ALT slew)', float, default=1.0 / 3.5)

    # Table of delay factors for Closed Loop optics correction according to
    # the ALT slew range.
    TelOptics_AltLimit1 = pexConfig.RangeField('Altitude (degrees) limits for '
                                               'the 1st delay range.', float,
                                               default=0.0, min=0.0, max=9.0)
    TelOptics_AltLimit2 = pexConfig.RangeField('Altitude (degrees) limits for '
                                               'the 2nd delay range.', float,
                                               default=9.0, min=9.0, max=90.0)

    # Values are time in seconds.
    delay_dict = {TelOptics_AltLimit1: 0.0,
                  TelOptics_AltLimit2: 20.0}

    # Need to think about this one!
    #TelOpticsCL_Delay = pexConfig.ConfigDictField('Time delay (seconds) for '
    #                                              'the corresponding ALT slew '
    #                                              'range in the Closed Loop '
    #                                              'optics correction.',
    #                                              pexConfig.RangeField,
    #                                              float, default=delay_dict)

    # Dependencies between the slew activities.
    # For each activity there is a list of prerequisites activities, that
    # must be previously completed.
    # The Readout corresponds to the previous observation, that's why it doesn't
    # have prerequisites and it is a prerequisite for Exposure.
    #
    # NOTE: Each item in list of prerequisites needs to be enclosed in single
    #       quotes, not double quotes.
    prereq_DomAlt = pexConfig.ListField('Prerequisite list for dome altitude '
                                        'movement.', str, default=[])
    prereq_DomAz = pexConfig.ListField('Prerequisite list for dome azimuth '
                                       'movement.', str, default=[])
    prereq_TelAlt = pexConfig.ListField('Prerequisite list for telescope '
                                        'altitude movement.', str, default=[])
    prereq_TelAz = pexConfig.ListField('Prerequisite list for telescope '
                                       'azimuth movement.', str, default=[])
    prereq_TelOpticsOL = pexConfig.ListField('Prerequisite list for telescope '
                                             'optics open loop corrections.',
                                             str, default=['TelAlt', 'TelAz'])
    prereq_TelOpticsCL = pexConfig.ListField('Prerequisite list for telescope '
                                             'optics closed loop corrections.',
                                             str, default=['DomAlt', 'DomAz',
                                                           'Settle', 'Readout',
                                                           'TelOpticsOL',
                                                           'Filter', 'Rotator'])
    prereq_Rotator = pexConfig.ListField('Prerequisite list for rotator '
                                         'movement.', str, default=[])
    prereq_Filter = pexConfig.ListField('Prerequisite list for filter '
                                        'movement.', str, default=[])
    prereq_ADC = pexConfig.ListField('Prerequisite list for the ADC', str,
                                     default=[])
    prereq_InsOptics = pexConfig.ListField('Prerequisite list for instrument '
                                           'optics.', str, default=[])
    prereq_GuiderPos = pexConfig.ListField('Prerequisite list for the guider '
                                           'positioning.', str, default=[])
    prereq_GuiderAdq = pexConfig.ListField('Prerequisite list for the guider '
                                           'adq?', str, default=[])
    prereq_Settle = pexConfig.ListField('Prerequisite list for telescope '
                                        'settle time.', str,
                                        default=['TelAlt', 'TelAz'])
    prereq_DomSettle = pexConfig.ListField('Prerequisite list for the dome '
                                           'settle time.', str, default=[])
    prereq_Exposure = pexConfig.ListField('Prerequisite list for exposure '
                                          'time.', str,
                                          default=['TelOpticsCL'])
    prereq_Readout = pexConfig.ListField('Prerequisite list for camera '
                                         'electronics readout time.', str,
                                         default=[])

    Filter_Mounted = pexConfig.ListField('Initial state for the mounted '
                                         'filters. Empty positions must be '
                                         'filled with id="" no (filter).', str,
                                         default=['g', 'r', 'i', 'z', 'y'])

    Filter_Pos = pexConfig.Field('The currently mounted filter.', str,
                                 default='r')

    Filter_Removable = pexConfig.ListField('The list of filters that can be '
                                           'removed.', str, default=['y', 'z'])

    Filter_UnMounted = pexConfig.ListField('The list of unmounted but '
                                           'available to swap filters.', str,
                                           default=['u'])

    # Telescope altitude limits
    Telescope_AltMin = pexConfig.Field('The minimum altitude of the telescope '
                                       'from horizon (degrees)', float,
                                       default=20.0)

    Telescope_AltMax = pexConfig.Field('The maximum altitude of the telescope '
                                       'for zenith avoidance (degrees)', float,
                                       default=86.5)

    # ========================================================================
    # UNUSED
    # ========================================================================

    # This should be a dictionary once the DOF names are known.
    TelOptics_Speed = pexConfig.ListField('UNUSED: Speeds (nm/second) for each '
                                          'degree of freedom for the telescope '
                                          'optics.', float,
                                          default=[200.0, 200.0, 200.0, 200.0,
                                                   200.0])

    # This should be a dictionary once the DOF names are known.
    InsOptics_Speed = pexConfig.ListField('UNUSED: Speeds (nm/second) for each '
                                          'degree of freedom for the '
                                          'instrument optics.', float,
                                          default=[100.0, 100.0, 100.0, 100.0,
                                                   100.0])

    ADC_Speed = pexConfig.Field('UNUSED: ADC rotation speed (units=??).', float,
                                default=360.0 / 10.0)
