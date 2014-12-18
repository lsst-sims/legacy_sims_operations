import base
import utils

class ScheduledDowntime(base.DowntimeConfig):
    """
    List of scheduled downtimes.
    DO NOT MODIFY UNLESS YOU TALK TO CHUCK CLAVER!
    """
    __events__ = (('general maintenance', 158, 'June 8th in 1st year', 7),
                  ('general maintenance', 307, 'November 4th in 1st year', 7),
                  ('general maintenance', 523, 'June 8th in 2nd year', 7),
                  ('general maintenance', 672, 'November 4th in 2nd year', 7),
                  ('recoat mirror', 888, 'June 8th in 3rd year', 14),
                  ('general maintenance', 1253, 'June 8th in 4th year', 7),
                  ('general maintenance', 1402, 'November 4th in 4thyear', 7),
                  ('recoat mirror', 1618, 'June 8th in 5th year', 14),
                  ('general maintenance', 1983, 'June 8th in 6th year', 7),
                  ('general maintenance', 2132, 'November 4th in 6th year', 7),
                  ('recoat mirror', 2348, 'June 8th in 7th year', 14),
                  ('general maintenance', 2713, 'June 8th in 8th year', 7),
                  ('general maintenance', 2862, 'November 4th in 8th year', 7),
                  ('recoat mirror', 378, 'June 8th in 9th year', 14),
                  ('general maintenance', 3443, 'June 8th in 10th year', 7),
                  ('general maintenance', 3592, 'November 4th in 10th year', 7))

    def setDefaults(self):
        """
        Create the list of downtime events.
        """
        base.DowntimeConfig.setDefaults(self)
        elist = []
        for ev in self.__events__:
            elist.append(base.DowntimeEventConfig(activity=ev[0],
                                                  startNight=ev[1],
                                                  startNightComment=ev[2],
                                                  duration=ev[3]))

        self.events = utils.makeIntDict(elist)
