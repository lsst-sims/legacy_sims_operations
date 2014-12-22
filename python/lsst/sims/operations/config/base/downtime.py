import lsst.pex.config as pexConfig

__all__ = ["DowntimeConfig", "DowntimeEventConfig"]

class DowntimeEventConfig(pexConfig.Config):
    """
    This class is for holding downtime event information.
    """
    activity = pexConfig.Field('The downtime activity or state', str)

    startNight = pexConfig.Field('Days from simulation start (startNight=0) '
                                 'when the event occurs.', int)

    startNightComment = pexConfig.Field('An optional comment about the '
                                        'startnight.', str, optional=True)

    duration = pexConfig.Field('The time in days of the downtime.', int)

class DowntimeConfig(pexConfig.Config):
    """
    This class is for holding a set of downtime events.
    """
    events = pexConfig.ConfigDictField('List of downtime events.', int,
                                       DowntimeEventConfig)
