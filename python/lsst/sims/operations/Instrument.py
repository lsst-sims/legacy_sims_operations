#!/usr/bin/env python

"""
Instrument

Inherits from:

Class Description
The Instrument class computes a simulated delay time of all the considered
activities in the instrument and the telescope in order to execute
the requested observation in the given current status.

===================================
Interface methods

- __init__
- GetDelayForTarget
- Observe
- Park

===================================
Additional operational methods

- StartTracking
- StopTracking
- GetParkState
- GetDependencies
- GetStateForObservation
- GetStateForTime
- SetState

===================================
Cinematics and coordinates calculation

- Date2LSTrad
- RaDec2AltAz
- AltAz2RaDec
- TimeAccelMove

===================================
Delay calculation for individual activities
- GetDelayFor
- GetDelayFor_DomAlt
- GetDelayFor_DomAz
- GetDelayFor_TelAlt
- GetDelayFor_TelAz
- GetDelayFor_TelOpticsOL
- GetDelayFor_TelOpticsCL
- GetDelayFor_InsRot
- GetDelayFor_InsFilter
- GetDelayFor_InsADC
- GetDelayFor_InsOptics
- GetDelayFor_InsGuidePos
- GetDelayFor_InsGuideAdq
- GetDelayFor_InsExpose
- GetDelayFor_InsReadout

==================================
Accumulated delay calculation
- GetDelayAfter
- GetSlewDelay

"""

from utilities import *
from LSSTObject import *
from Observation import *
from Proposal import *
import copy
import utilities

TWOPI   = 2 * math.pi
HOU2RAD = math.pi / 12.0
RAD2HOU = 12.0    / math.pi
SEC2RAD = math.pi / 43200.0
RAD2SEC = 43200.0 / math.pi
ZENITH_RAD = math.radians(90)

DefaultConfigFile = "./Instrument.conf"

######################################################################
class InstrumentParams(object):
    # This class is used as a data structure to store all the "construction"
    # or design parameters for the dome-telescope-instrument-camera set.
    def __init__ (self, 
                  latitude_RAD,
                  longitude_RAD,
                  height):
        # meters
        self.Height    = height

        # radians 
        self.latitude_RAD  = latitude_RAD
        self.longitude_RAD = longitude_RAD

######################################################################
class InstrumentPosition (object):

    def __init__ (self,
    		ra_RAD	    =0.0,
                dec_RAD	    =0.0,
                angle_RAD   =0.0,
                filter      ='r',
                exptime     =0.0,
                time        =0.0,
                alt_RAD     =1.553343,
                az_RAD      =0.0,
                pa_RAD      =0.0):
                                                                                                                                   
        self.RA_RAD  = ra_RAD
        self.DEC_RAD = dec_RAD
        self.ANG_RAD = angle_RAD
        self.Filter_Pos    = filter
        self.Exposure_Time = exptime
        self.TIME    = time
        self.ALT_RAD = alt_RAD
        self.AZ_RAD  = az_RAD
        self.PA_RAD  = pa_RAD

    def Set(self,
		ra_RAD,
		dec_RAD,
                angle_RAD,
                filter,
                exptime,
                date,
                alt_RAD,
                az_RAD,
                pa_RAD):

        az_RAD=divmod(az_RAD,TWOPI)[1]
        pa_RAD=divmod(pa_RAD,TWOPI)[1]

	self.RA_RAD  = ra_RAD
	self.DEC_RAD = dec_RAD
	self.ANG_RAD = angle_RAD
	self.Filter_Pos    = filter
	self.Exposure_Time = exptime
	self.TIME    = date
        self.ALT_RAD = alt_RAD
        self.AZ_RAD  = az_RAD
        self.PA_RAD  = pa_RAD

    def Copy(self, newpos):

	self.Set(	newpos.RA_RAD,
                	newpos.DEC_RAD,
                	newpos.ANG_RAD,
                	newpos.Filter_Pos,
                	newpos.Exposure_Time,
                	newpos.TIME,
                	newpos.ALT_RAD,
                	newpos.AZ_RAD,
                	newpos.PA_RAD)

######################################################################
class dataSlew(object):
    def __init__(self,
		slewCount = 0,
		startDate = 0,
		endDate   = 0,
		slewTime  = 0.0,
		slewDist  = 0.0):

	self.slewCount = slewCount
	self.startDate = startDate
	self.endDate   = endDate
	self.slewTime  = slewTime
	self.slewDist  = slewDist

SLEWINITSTATE = 0
SLEWFINALSTATE = 1
class stateSlew(object):
    def __init__(self,
		slewStateDate = 0,
		tra = 0.0,
		tdec = 0.0,
		tracking = "False",
		alt = 0.0,
		az = 0.0,
		pa = 0.0,
		DomAlt = 0.0,
		DomAz = 0.0,
		TelAlt = 0.0,
		TelAz = 0.0,
		RotTelPos = 0.0,
		Filter = "r",
		state = SLEWINITSTATE):


        self.slewStateDate = slewStateDate
        self.tra = tra
        self.tdec = tdec
        self.tracking = tracking
        self.alt = alt
        self.az = az
        self.pa = pa
        self.DomAlt = DomAlt
        self.DomAz = DomAz
        self.TelAlt = TelAlt
        self.TelAz = TelAz
        self.RotTelPos = RotTelPos
        self.Filter = Filter
        self.state = state

class speedsSlew(object):
    def __init__(self,
		DomAltSpd = 0.0,
		DomAzSpd = 0.0,
		TelAltSpd = 0.0,
		TelAzSpd = 0.0,
		RotSpd = 0.0):

	self.DomAltSpd = DomAltSpd
	self.DomAzSpd = DomAzSpd
	self.TelAltSpd = TelAltSpd
	self.TelAzSpd = TelAzSpd
	self.RotSpd = RotSpd

class activitySlew(object):
    def __init__(self,
		activity = "",
		actDelay = 0.0,
		inCriticalPath = "False"):

	self.activity = activity
	self.actDelay = actDelay
	self.inCriticalPath = inCriticalPath


######################################################################
class InstrumentState (InstrumentPosition):
    # This class describes a state of all the moving systems in Instrument.
    # The default values correspond to a Park position.
    def __init__ (self, 
                  alt_RAD=1.553343, 
                  az_RAD=0.0, 
                  pa_RAD=0.0, 
                  filter='r', 
                  exptime=0.0, 
                  ra=0.0, 
                  dec=0.0, 
                  time=0.0, 
                  config_dict=None,
                  instrumentConf=None,
		  obsProfile=(-70.59*DEG2RAD, -29.67*DEG2RAD, 2737, 49353, 0,0,0)):
        # 89.0 deg -> 1.553343 rad

	super (InstrumentState, self).__init__(	ra*DEG2RAD,
						dec*DEG2RAD,
				                0.0,
				                filter,
				                exptime,
				                time,
				                alt_RAD,
				                az_RAD,
				                pa_RAD)

        (self.longitude_RAD,self.latitude_RAD,self.height,self.simEpoch,d1,d2,d3) = obsProfile

        if config_dict == None:
            if instrumentConf == None:
                config_dict, pairs = utilities.readConfFile(DefaultConfigFile)
            else :
                config_dict, pairs = utilities.readConfFile(instrumentConf)

        # Tracking status for the instrument.
        # True => instrument tracking to maintain sky coordinates constant
        # False=> instrument doesn't move maintaining earth coordinates constant
        self.Tracking = False

        # earth coordinates, valid if Tracking is False
        # angles in radians

        self.DomAlt_Pos_RAD = alt_RAD
	self.DomAlt_Spd_RDS = 0.0
        self.DomAz_Pos_RAD  = az_RAD
	self.DomAz_Spd_RDS  = 0.0

        self.TelAlt_Pos_RAD = alt_RAD 
        self.TelAlt_Spd_RDS = 0.0
        self.TelAz_Pos_RAD  = az_RAD
        self.TelAz_Spd_RDS  = 0.0
        # absolute position limits due to cable wrap
        self.TelAz_MinPos_RAD = eval(str(config_dict["TelAz_MinPos"])) * DEG2RAD
        self.TelAz_MaxPos_RAD = eval(str(config_dict["TelAz_MaxPos"])) * DEG2RAD

        self.TelOptics_Total = len(config_dict["TelOptics_Speed"])
        self.TelOptics_Pos = [0.0]*self.TelOptics_Total

        self.Rotator_Pos_RAD = pa_RAD
        self.Rotator_Spd_RDS = 0.0
        # absolute position limits due to cable wrap
        self.Rotator_MinPos_RAD = eval(str(config_dict["Rotator_MinPos"])) * DEG2RAD
        self.Rotator_MaxPos_RAD = eval(str(config_dict["Rotator_MaxPos"])) * DEG2RAD

        #self.Filter_DefinedList = config_dict["Filter_Defined"]
        self.Filter_MountedList = config_dict["Filter_Mounted"]
        self.Filter_MountedTotal= len(self.Filter_MountedList)
        self.Filter_Pos = config_dict["Filter_Pos"]
	#print "Mounted Filters list = "+str(self.Filter_MountedList)

	if config_dict.has_key("Filter_Removable"):
            self.Filter_RemovableList = config_dict["Filter_Removable"]
            if (not isinstance(self.Filter_RemovableList,list)):
                self.Filter_RemovableList = [self.Filter_RemovableList]
	else:
	    self.Filter_RemovableList = []
        #print "Removable Filters list = "+str(self.Filter_RemovableList)


        if config_dict.has_key("Filter_Unmounted"):
            self.Filter_UnmountedList = config_dict["Filter_Unmounted"]
	    if (not isinstance(self.Filter_UnmountedList,list)):
	        self.Filter_UnmountedList = [self.Filter_UnmountedList]
	else:
	    self.Filter_UnmountedList = []
	#print "Unmounted Filters list = "+str(self.Filter_UnmountedList)

        self.ADC_Pos =  0.0

        self.InsOptics_Total = len(config_dict["InsOptics_Speed"])
        self.InsOptics_Pos = [0.0]*self.InsOptics_Total

        self.GuiderPos_X = 0.0
        self.GuiderPos_Y = 0.0

        # sky coordinates in radians, valid if Tracking is True
        # the time corresponds to the instant in which tracking started
        # measure in seconds sin SIMEPOCH

        #self.Filter_MinBrig = config_dict["Filter_MinBrig"]
        #self.Filter_MaxBrig = config_dict["Filter_MaxBrig"]

    def GetShortestDistanceWithWrap(self, target_RAD, current_abs_RAD, min_abs_RAD=None, max_abs_RAD=None):

        # 360 Degree -> TWOPI radians 

	# normalizes the target angle to the wrap range
	if min_abs_RAD != None:
	    norm_target_RAD = divmod(target_RAD - min_abs_RAD, TWOPI)[1] + min_abs_RAD
	    # if the target angle is unreachable
	    # then sets an arbitrary value
	    if norm_target_RAD > max_abs_RAD:
		norm_target_RAD -= math.pi
	else:
	    norm_target_RAD = target_RAD

        # computes the distance clockwise
        distance_RAD  = divmod(norm_target_RAD-current_abs_RAD, TWOPI)[1]

        # takes the counter-clockwise distance if it is shorter
        if distance_RAD > math.pi:
            distance_RAD = distance_RAD - TWOPI

        # if there are limits because of a cable-wrap
        if min_abs_RAD!=None and max_abs_RAD!=None:
            # computes the accumulated angle
            accum_abs_RAD = current_abs_RAD + distance_RAD

            # checks if any limit has been reached to chose the other direction
            if accum_abs_RAD > max_abs_RAD:
                distance_RAD = distance_RAD - TWOPI
            if accum_abs_RAD < min_abs_RAD:
                distance_RAD = distance_RAD + TWOPI

        # computes the final accumulated angle
        final_abs_RAD = current_abs_RAD + distance_RAD

        return(distance_RAD, final_abs_RAD)

    def GetTelAzDistanceWithWrap(self, az_RAD):

        return self.GetShortestDistanceWithWrap(az_RAD, self.TelAz_Pos_RAD, self.TelAz_MinPos_RAD, self.TelAz_MaxPos_RAD)

    def GetRotatorDistanceWithWrap(self, newangle_RAD):

        return self.GetShortestDistanceWithWrap(newangle_RAD, self.Rotator_Pos_RAD, self.Rotator_MinPos_RAD, self.Rotator_MaxPos_RAD)

    def GetRotatorTelPos(self):

	return divmod(self.Rotator_Pos_RAD,TWOPI)[1]

    def GetRotatorSkyPos(self):

        return divmod(self.Rotator_Pos_RAD-self.PA_RAD,TWOPI)[1]

    def GetFilter(self):

        return self.Filter_Pos

    def GetMountedFiltersList(self):

        return self.Filter_MountedList

    def GetRemovableFiltersList(self):
                                                                                                                                                                                                                             
        return self.Filter_RemovableList

    def GetUnmountedFiltersList(self):
                                                                                                                                                                                                                             
        return self.Filter_UnmountedList

    def IsFilterMounted(self, filter):

        try:
            idx=self.Filter_MountedList.index(filter)
            mounted=True
        except:
            mounted=False

        return mounted

    def MountFilter(self, newfilter=None, oldfilter=None):

        if newfilter == None:
            #for filter in self.Filter_DefinedList:
            #    if not self.IsFilterMounted(filter):
            #        break
            #newf = filter
            return
        elif self.IsFilterMounted(newfilter):
            return
        else:
            newf = newfilter

        try:
            oldidx = self.Filter_MountedList.index(oldfilter)
            oldf = oldfilter
        except:
            # picks the first in the list and shifts all others
            # leaving the last space for the new one
            oldf = self.Filter_MountedList[0]
            oldidx = -1
            for idx in range(len(self.Filter_MountedList)-1):
                self.Filter_MountedList[idx] = self.Filter_MountedList[idx+1]

        self.Filter_MountedList[oldidx] = newf
        if self.Filter_Pos == oldf:
            self.Filter_Pos = newf

	newidx = self.Filter_UnmountedList.index(newfilter)
	self.Filter_UnmountedList[newidx] = oldf

	if oldf in self.Filter_RemovableList:
	    remidx = self.Filter_RemovableList.index(oldf)
	    self.Filter_RemovableList[remidx] = newf

        return
    
    def SetFilter(self, filter):

        if not self.IsFilterMounted(filter):
#            self.MountFilter(filter)
	    raise(ValueError, 'filter not mounted')
            
        self.Filter_Pos = filter

        return

    def SetPosition(self, newpos):

	super (InstrumentState, self).Copy(newpos)

    def SetClosestState(self, targetpos, initstate):

	self.SetPosition(targetpos)

        self.DomAlt_Pos_RAD  = self.ALT_RAD
        self.DomAz_Pos_RAD   = initstate.GetShortestDistanceWithWrap(self.AZ_RAD, initstate.DomAz_Pos_RAD)[1]
        self.TelAlt_Pos_RAD  = self.ALT_RAD
	self.TelAz_Pos_RAD   = initstate.GetTelAzDistanceWithWrap(self.AZ_RAD)[1]
	if ( initstate.GetFilter() == self.GetFilter() ):
	    self.Rotator_Pos_RAD = initstate.GetRotatorDistanceWithWrap(self.PA_RAD-self.ANG_RAD)[1]
	else:
	    self.Rotator_Pos_RAD = 0.0;

    def UpdateState(self, date):

	if self.Tracking:
            (alt_RAD,az_RAD,pa_RAD, HA_HOU) = self.RaDec2AltAz(self.RA_RAD, self.DEC_RAD, date)

            az_RAD=divmod(az_RAD,TWOPI)[1]
            pa_RAD=divmod(pa_RAD,TWOPI)[1]
                                                                                                    
            self.ALT_RAD = alt_RAD
            self.AZ_RAD  = az_RAD
            self.PA_RAD  = pa_RAD
                                                                                                    
            self.DomAlt_Pos_RAD = alt_RAD
            self.DomAz_Pos_RAD  = az_RAD
            self.TelAlt_Pos_RAD = alt_RAD
            self.TelAz_Pos_RAD  = self.GetTelAzDistanceWithWrap(az_RAD)[1]
            self.Rotator_Pos_RAD= self.GetRotatorDistanceWithWrap(pa_RAD-self.ANG_RAD)[1]

    def RaDec2AltAz(self, RA_RAD, DEC_RAD, DATE):
        """
        Converts RA_RAD, DEC_RAD coordinates into ALT_RAD AZ_RAD for given DATE.
        inputs:
               RA_RAD:  Right Ascension in radians
               DEC_RAD: Declination in radians
               DATE: Time in seconds since simulation reference (SIMEPOCH)
        output:
               (ALT_RAD, AZ_RAD, PA_RAD, HA_HOU)
               ALT_RAD: Altitude in radians [-90.0  90.0] 90=>zenith
               AZ_RAD:  Azimuth in radians [  0.0 360.0] 0=>N 90=>E
               PA_RAD:  Parallactic Angle in radians
               HA_HOU:  Hour Angle in hours
        """
        LST_RAD  = self.Date2LSTrad(DATE)
        HA_RAD   = LST_RAD - RA_RAD

        #result = slalib.sla_altaz(HA_RAD, DEC_RAD, self.latitude_RAD)
        result = pal.altaz(HA_RAD, DEC_RAD, self.latitude_RAD) 

        AZ_RAD  = result[0]
        ALT_RAD = result[3]
        PA_RAD  = result[6]

        HA_HOU  = HA_RAD  * RAD2HOU

        return (ALT_RAD, AZ_RAD, PA_RAD, HA_HOU)

    def AltAz2RaDec(self, ALT_RAD, AZ_RAD, DATE):
        """
        Converts ALT, AZ coordinates into RA DEC for the given DATE.
                                                                                                                                        
        inputs:
               ALT_RAD: Altitude in radians [-90.0deg  90.0deg] 90deg=>zenith
               AZ_RAD:  Azimuth in radians [  0.0deg 360.0deg] 0deg=>N 90deg=>E
                DATE: Time in seconds since simulation reference (SIMEPOCH)
        output:
               (RA_RAD, DEC_RAD)
               RA_RAD:  Right Ascension in radians
               DEC_RAD: Declination in radians
        """
        LST_RAD  = self.Date2LSTrad(DATE)
                                                                                                                                        
        #(HA_RAD,DEC_RAD) = slalib.sla_dh2e(AZ_RAD, ALT_RAD, self.latitude_RAD)
        (HA_RAD, DEC_RAD) = pal.dh2e(AZ_RAD, ALT_RAD, self.latitude_RAD)
        
        RA_RAD  = LST_RAD - HA_RAD
                                                                                                                                        
        return (RA_RAD, DEC_RAD)

    def Date2LSTrad(self, DATE):
        """
        Computes the Local Sidereal Time for the given DATE.
        inputs:
               DATE: Time in seconds since simulation reference (SIMEPOCH)
        output:
               LST:  Local Sidereal Time in radians.
        """
                                                                                            
        UT_day   = self.simEpoch + DATE/86400.0
        #RAA  changed to conform to LSST convention of West=negative, East=pos
        #LST_RAD  = slalib.sla_gmst(UT_day) + self.longitude_RAD
        LST_RAD = pal.gmst(UT_day) + self.longitude_RAD
                                                                                            
        return LST_RAD

    def StartTracking(self, starttime):
                                                                                                                                        
        if not self.Tracking:
            # computes RA DEC from the ALT AZ at given time.
            ALT_RAD = self.ALT_RAD
            AZ_RAD  = self.AZ_RAD
            (RA_RAD,DEC_RAD) = self.AltAz2RaDec(ALT_RAD, AZ_RAD, starttime)
                                                                                                                                        
            # supposing 0 delay with no slew
            self.RA_RAD =  RA_RAD
            self.DEC_RAD = DEC_RAD
            self.TIME= starttime
            self.Tracking = True
                                                                                                                                        
    def StopTracking(self, stoptime):
                                                                                                                                        
        if self.Tracking:
        # computes ALT AZ from RA DEC TIME at given new time.
            RA_RAD  = self.RA_RAD
            DEC_RAD = self.DEC_RAD
            TIME= self.TIME
            (ALT_RAD,AZ_RAD,PA_RAD, HA_HOU) = self.RaDec2AltAz(RA_RAD, DEC_RAD, stoptime)
                                                                                                                                        
            self.ALT_RAD = ALT_RAD
            self.AZ_RAD  = AZ_RAD
            self.Tracking = False
                                                                                                                                        
######################################################################
class InstrumentSlewParams (object):
    # This class stores all the cinematic and timing parameters
    # involved in the computation of the slew time.

    def __init__ (self, 
                  config_dict,
                  instrumentConf=None):

        # speed in degrees/second
        self.DomAlt_MaxSpeed = eval(str(config_dict["DomAlt_MaxSpeed"]))
        # acceleration in degrees/second**2
        self.DomAlt_Accel = eval(str(config_dict["DomAlt_Accel"]))
        # deceleration in degrees/second**2
        self.DomAlt_Decel = eval(str(config_dict["DomAlt_Decel"]))

        # speed in degrees/second
        self.DomAz_MaxSpeed = eval(str(config_dict["DomAz_MaxSpeed"]))
        # acceleration in degrees/second**2
        self.DomAz_Accel = eval(str(config_dict["DomAz_Accel"]))
        # deceleration in degrees/second**2
        self.DomAz_Decel = eval(str(config_dict["DomAz_Decel"]))

        # speed in degrees/second
        self.TelAlt_MaxSpeed = eval(str(config_dict["TelAlt_MaxSpeed"]))
        # acceleration in degrees/second**2
        self.TelAlt_Accel = eval(str(config_dict["TelAlt_Accel"]))
        # deceleration in degrees/second**2
        self.TelAlt_Decel = eval(str(config_dict["TelAlt_Decel"]))

        # speed in degrees/second
        self.TelAz_MaxSpeed = eval(str(config_dict["TelAz_MaxSpeed"]))
        # acceleration in degrees/second**2
        self.TelAz_Accel = eval(str(config_dict["TelAz_Accel"]))
        # deceleration in degrees/second**2
        self.TelAz_Decel = eval(str(config_dict["TelAz_Decel"]))

        # speed in degrees/second
        self.Rotator_MaxSpeed = eval(str(config_dict["Rotator_MaxSpeed"]))
        # acceleration in degrees/second**2
        self.Rotator_Accel = eval(str(config_dict["Rotator_Accel"]))
        # deceleration in degrees/second**2
        self.Rotator_Decel = eval(str(config_dict["Rotator_Decel"]))
        # Boolean flag that if True enables the movement of the rotator during
        # slews to put North-Up. If range is insufficient, then the alignment
        # is North-Down
        # If the flag is False, then the rotator does not move during the slews,
        # it is only tracking during the exposures.
        self.Rotator_FollowSky = eval(str(config_dict["Rotator_FollowSky"]))

        # speed in nm/sec for now in all degrees of freedom
        self.TelOptics_Speed = eval(str(config_dict["TelOptics_Speed"]))
        self.TelOptics_Total = len(self.TelOptics_Speed)

	# Delay factor for Open Loop optics correction,
	# in units of seconds/(degrees in ALT slew)
        self.TelOpticsOL_Slope = eval(str(config_dict["TelOpticsOL_Slope"]))

	# Table of delay factors for Closed Loop optics correction
	# according to the ALT slew range.
	# _AltLimit is the Altitude upper limit in degrees of a range.
	# The lower limit is the upper limit of the previous range.
	# The lower limit for the first range is 0
	# _Delay is the time delay in seconds for the corresponding range.
        self.TelOpticsCL_Delay   = eval(str(config_dict["TelOpticsCL_Delay"]))
        self.TelOpticsCL_AltLimit= eval(str(config_dict["TelOpticsCL_AltLimit"]))
        self.TelOpticsCL_Total   = len(self.TelOpticsCL_Delay)
 
        # speed in nm/sec for now in all degrees of freedom
        self.InsOptics_Speed = eval(str(config_dict["InsOptics_Speed"]))
        self.InsOptics_Total = len(self.InsOptics_Speed)
 
        self.ADC_Speed = eval(str(config_dict["ADC_Speed"]))

        self.Settle_Time = eval(str(config_dict["Settle_Time"]))
        self.DomSettle_Time = eval(str(config_dict["DomSettle_Time"]))

        self.Readout_Time = eval(str(config_dict["Readout_Time"]))

        self.Filter_MountTime = eval(str(config_dict["Filter_MountTime"]))
        self.Filter_MoveTime  = eval(str(config_dict["Filter_MoveTime"]))

        # List of activities defined.
        self.activities = ["DomAlt",
                           "DomAz",
                           "TelAlt",
                           "TelAz",
                           "TelOpticsOL",
                           "TelOpticsCL",
                           "Rotator",
                           "Filter",
                           "ADC",
                           "InsOptics",
                           "GuiderPos",
                           "GuiderAdq",
                           "Settle",
			   "DomSettle",
                           "Exposure",
                           "Readout"]

        # Table of dependencies between the activities.
        # Each element in the list is associated to the corresponding element in
        # self.components, and contains the list of activities
        # that must be previously completed.

	self.prerequisites = {}
        for activity in self.activities:
            key = "prereq_" + activity
	    self.prerequisites[activity] = eval(config_dict[key])

        # minimum altitud from horizon (degrees)
        self.Telescope_AltMin_RAD = eval(str(config_dict["Telescope_AltMin"])) * DEG2RAD
        # maximum altitud for zenith avoidance (degrees)
        self.Telescope_AltMax_RAD = eval(str(config_dict["Telescope_AltMax"])) * DEG2RAD

######################################################################
#class Instrument (Simulation.Process):
class Instrument (object):
    """
    This class involves status, interaction and timing for the activities
    in the Instrument and the Telescope for a given exposure request.
    """
    def __init__ (self, 
                  lsstDB,
		  sessionID,
                  dbTableDict,
                  obsProfile,
                  instrumentConf=DefaultConfigFile,
                  log=False, 
                  logfile="./Instrument.log",
                  verbose=0):

#        Simulation.Process.__init__ (self)
        """
        Standard initializer.
        inputs:
            lsstDB      LSST DB Access
	    sessionID   An integer identifying this particular run.
            dbTableDict Dictionary of DB table names
            obsProfile  ...
                        latitude_RAD:
                        longitude_RAD:
                        height:
                        simEpoch:
            instrumentConf: Configuration file with parameters for Instrument.
                            Default is "./Instrument.conf"
            log         False if not set, else: log = logging.getLogger("...")
            logfile     Name (and path) of the desired log file.
                        Defaults "./Instrument.log".
            verbose:    Log verbosity:-1=none, 0=minimal, 1=wordy, >1=verbose

        The initial state for the instrument is in park position and no
        tracking.
        """
        (longitude_RAD,latitude_RAD,height,self.simEpoch,d1,d2,d3) = obsProfile

	self.lsstDB = lsstDB	
	self.sessionID = sessionID
	self.slewCount = 0

        # Setup logging
        if (verbose < 0):
            logfile = "/dev/null"
        elif ( not log ):
            #print "Setting up Instrument logger"
            log = logging.getLogger("Instrument")
            hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            hdlr.setFormatter(formatter)
            log.addHandler(hdlr)
            log.setLevel(logging.INFO)

        self.log=log
        self.logfile=logfile
        self.verbose = verbose

        if ( self.log ):
            self.log.info('Instrument: init()')

        self.config_dict, pairs = utilities.readConfFile(instrumentConf)

        # store config in DB
        for line in pairs:
            storeParam (self.lsstDB, sessionID, 0, 'instrument', line['index'], line['key'], line['val'])

        self.instrumentConf=instrumentConf
        self.params        = InstrumentParams(latitude_RAD,
                                              longitude_RAD,
                                              height)
        self.current_state = InstrumentState(config_dict=self.config_dict,
                                             instrumentConf=instrumentConf,
						obsProfile=obsProfile)
        self.target_state  = InstrumentState(config_dict=self.config_dict,
                                             instrumentConf=instrumentConf,
						obsProfile=obsProfile)
        self.park_state    = InstrumentState(config_dict=self.config_dict,
                                             instrumentConf=instrumentConf,
						obsProfile=obsProfile)
        self.next_state    = InstrumentState(config_dict=self.config_dict,
                                             instrumentConf=instrumentConf,
						obsProfile=obsProfile)
        self.slew_params   = InstrumentSlewParams(config_dict=self.config_dict,
                                                  instrumentConf=instrumentConf)
	self.targetposition = InstrumentPosition()

	self.delay_time_for = {}
	self.longest_prereq_for = {}
        self.functionGetDelayFor = {}
	for activity in self.slew_params.activities:
	    self.delay_time_for[activity] = 0.0
	    self.longest_prereq_for[activity] = ""
            function_name = "GetDelayFor_" + activity
            GetDelayFor_Activity = getattr(self, function_name)
            self.functionGetDelayFor[activity] = GetDelayFor_Activity

        return

    def GetDependencies (self):
        """
        Returns the dependencies table
        """
	return self.slew_params.prerequisites

    def TimeAccelMove (self, distance_RAD, maxspeed, accel, decel):
        """
        Computes the delay in a linear movement with 0 initial speed,
        constant acceleration, constant maximum speed if reached,
        constant deceleration and 0 final speed.
        """

        # computation of delay does not care about direction
        distance_DEG = abs(distance_RAD * RAD2DEG)
 
        # supposing maximum speed is not reached
        Vpeak = ( 2.0*distance_DEG / (1.0/accel + 1.0/decel) )**0.5

        # checking the supposition
        if Vpeak <= maxspeed:
        # applies triangular formula
            delay = Vpeak/accel + Vpeak/decel

        else:
        # applies trapezoidal formula
            d1 = 0.5*(maxspeed**2)/accel
            d3 = 0.5*(maxspeed**2)/decel
            d2 = distance_DEG - d1 - d3

            t1 = maxspeed/accel
            t3 = maxspeed/decel
            t2 = d2/maxspeed

            delay = t1+t2+t3
	    Vpeak = maxspeed

        return (delay, Vpeak*DEG2RAD*cmp(distance_RAD,0))

    # Computation of the delay in each activity given the current status
    # and target position.
    def GetDelayFor_DomAlt(self, target_state, prev_state):

        distance_RAD = target_state.DomAlt_Pos_RAD - prev_state.DomAlt_Pos_RAD 

        accel       = self.slew_params.DomAlt_Accel
        decel       = self.slew_params.DomAlt_Decel
        maxspeed    = self.slew_params.DomAlt_MaxSpeed

        (delay, speed) = self.TimeAccelMove(distance_RAD, maxspeed, accel, decel)
	target_state.DomAlt_Spd_RDS = speed

        return delay

    # Assume dome is crawling in correct direction for next exposure. MM
    def GetDelayFor_DomAz(self, target_state, prev_state):

#        buffer_RAD = self.GetSlitBuffer (target_state.DomAlt_Pos_RAD,
#                                         prev_state.DomAlt_Pos_RAD)
	buffer_RAD = 0.0

        distance_RAD = math.fabs(target_state.DomAz_Pos_RAD - prev_state.DomAz_Pos_RAD) - buffer_RAD

        accel       = self.slew_params.DomAz_Accel
        decel       = self.slew_params.DomAz_Decel
        maxspeed    = self.slew_params.DomAz_MaxSpeed

        # If buffer angle larger than required slew, distance will be negative.
        # No slew required.
        if distance_RAD < 0:
           delay = 0
           speed = 0  
        else:
           (delay, speed) = self.TimeAccelMove(distance_RAD, maxspeed, accel, decel)
        target_state.DomAz_Spd_RDS = speed

        return delay

    def GetDelayFor_TelAlt(self, target_state, prev_state):

        distance_RAD = target_state.TelAlt_Pos_RAD - prev_state.TelAlt_Pos_RAD

        accel       = self.slew_params.TelAlt_Accel
        decel       = self.slew_params.TelAlt_Decel
        maxspeed    = self.slew_params.TelAlt_MaxSpeed

        (delay, speed) = self.TimeAccelMove(distance_RAD, maxspeed, accel, decel)
        target_state.TelAlt_Spd_RDS = speed

        return delay

    def GetDelayFor_TelAz(self, target_state, prev_state):

        distance_RAD   = target_state.TelAz_Pos_RAD - prev_state.TelAz_Pos_RAD

        accel       = self.slew_params.TelAz_Accel
        decel       = self.slew_params.TelAz_Decel
        maxspeed    = self.slew_params.TelAz_MaxSpeed

        (delay, speed) = self.TimeAccelMove(distance_RAD, maxspeed, accel, decel)
        target_state.TelAz_Spd_RDS = speed

        return delay

    def GetDelayFor_TelOpticsOL(self, target_state, prev_state):

        distance_RAD = target_state.TelAlt_Pos_RAD - prev_state.TelAlt_Pos_RAD

        delay = abs(distance_RAD*RAD2DEG)*self.slew_params.TelOpticsOL_Slope

        return delay
    
    def GetDelayFor_TelOpticsCL(self, target_state, prev_state):

        distance_DEG = abs(target_state.TelAlt_Pos_RAD - prev_state.TelAlt_Pos_RAD)*RAD2DEG

	delay = 0.0                                                                                  
	for k in range(self.slew_params.TelOpticsCL_Total):
	    if distance_DEG < self.slew_params.TelOpticsCL_AltLimit[k]:
		delay = self.slew_params.TelOpticsCL_Delay[k]
		break

        return delay

    def GetDelayFor_Rotator(self, target_state, prev_state):

        distance_RAD = target_state.Rotator_Pos_RAD - prev_state.Rotator_Pos_RAD

        accel       = self.slew_params.Rotator_Accel
        decel       = self.slew_params.Rotator_Decel
        maxspeed    = self.slew_params.Rotator_MaxSpeed

        (delay, speed) = self.TimeAccelMove(distance_RAD, maxspeed, accel, decel)
        target_state.Rotator_Spd_RDS = speed

        return delay

    def GetDelayFor_Filter(self, target_state, prev_state):

        target_filter = target_state.GetFilter()
        
        if target_filter == prev_state.GetFilter():
            delay = 0.0
        else:
            if prev_state.IsFilterMounted(target_filter):
                delay = self.slew_params.Filter_MoveTime
            else:
                delay = self.slew_params.Filter_MountTime

        return delay

    def GetDelayFor_ADC(self, target_state, prev_state):

        d = target_state.ADC_Pos - prev_state.ADC_Pos
        delay = abs(d)/self.slew_params.ADC_Speed

        return delay

    def GetDelayFor_InsOptics(self, target_state, prev_state):

        delay = 0.0
        for k in range(prev_state.InsOptics_Total):
            d = target_state.InsOptics_Pos[k]-prev_state.InsOptics_Pos[k]
            t = abs(d)/self.slew_params.InsOptics_Speed[k]

            delay = max(t,delay)

        return delay

    def GetDelayFor_GuiderPos(self, target_state, prev_state):
        return 0

    def GetDelayFor_GuiderAdq(self, target_state, prev_state):
        return 0

    def GetDelayFor_Settle(self, target_state, prev_state):
	if (target_state.TelAlt_Pos_RAD == prev_state.TelAlt_Pos_RAD) and (target_state.TelAz_Pos_RAD == prev_state.TelAz_Pos_RAD):
	    return 0.0
	else:
            return self.slew_params.Settle_Time

    def GetDelayFor_DomSettle(self, target_state, prev_state):
	if target_state.DomAz_Pos_RAD == prev_state.DomAz_Pos_RAD:
	    return 0.0
	else:
            return self.slew_params.DomSettle_Time
                                                                                              
    def GetDelayFor_Exposure(self, target_state, prev_state):

        # No exposure delay time returned, so the total slew delay
        # does not include the exposure time, which is handled
        # separately in the higher simulator layers.
        return 0

    def GetDelayFor_Readout(self, target_state, prev_state):

        return self.slew_params.Readout_Time

#    def GetDelayFor(self, activity, target_state, prev_state):
#
#        method_name = "GetDelayFor_" + activity
#        GetDelayFor_Activity = getattr(self, method_name)
#        return GetDelayFor_Activity(target_state, prev_state)
#
    def GetDelayAfter(self, activity, target_state, prev_state):
        """
        Computation of the accumulated delay time just after the indicated
        activity.
        Implemented in a recursive way and using the table of dependencies for
        flexibility.
        """

        # Computes the delay in the current activity
#        activity_delay = self.GetDelayFor(activity, target_state, prev_state)
        activity_delay = self.functionGetDelayFor[activity](target_state, prev_state)

        if activity_delay == None:
            return None

#        if self.log and self.verbose>1 and activity_delay!=0:
#            self.log.info("Instrument: GetDelayAfter(): delay for %s  = %f" % (activity, activity_delay))

        # Obtains from the table the list of previous activities that must be
        # completed.
	prereq_list = self.slew_params.prerequisites[activity]

        # Computes the accumulated delay after each one of the previous
        # activities, and finds the longest.
        longest_previous_delay = 0.0
        longest_prereq = ""
        for prereq in prereq_list:
            prev_delay = self.GetDelayAfter(prereq, target_state, prev_state)
            if prev_delay > longest_previous_delay:
                longest_previous_delay = prev_delay
                longest_prereq = prereq

        # Updates the table of longest prerequisites for future
        # calculation of the critical path.
	self.longest_prereq_for[activity] = longest_prereq
	self.delay_time_for[activity]     = activity_delay

        # Accumulates the delays.
	return activity_delay + longest_previous_delay

    def GetSlewDelay(self, target_position, prev_state, allSlewData=False):
        """
        Computes the total delay in a slew given the provided target state or
        position of the instrument and the current state.
        """

	self.target_state.SetClosestState(target_position, prev_state)
	
	if prev_state.Tracking == False:
	    self.lastslew_delays = {}
            self.lastslew_criticalpath = []
	    if allSlewData:
		return (0.0, self.target_state)
	    else:
		return (0.0, None)

        last_activity = "Exposure"

        slew_delay = self.GetDelayAfter(last_activity, self.target_state, prev_state)

        if allSlewData:
	    self.lastslew_delays = {}
	    self.lastslew_criticalpath = []
	    for ac in self.slew_params.activities:
		dt = self.delay_time_for[ac]
                if dt>0:
		    self.lastslew_delays[ac] = dt
                                                                                        
            activity = last_activity
            while activity != "":
                # gets the stored delay time for this activity
		dt = self.delay_time_for[activity]
                if dt>0:
                    # adds the activity info in the critical path chain
		    self.lastslew_criticalpath.append(activity)
                # gets the following activity in the critical path
		activity = self.longest_prereq_for[activity]

	    #if self.log and self.verbose>0:
            #     self.log.info("Instrument: GetSlewDelay(): all delays: %s" % (self.all))
            #     self.log.info("Instrument: GetSlewDelay(): critical path: %s" % (self.critical_path))

	    return (slew_delay, self.target_state)

	else:
	    return (slew_delay, None)

    def Slew(self, new_position):

	(delay, new_state) = self.GetSlewDelay(new_position, self.current_state, allSlewData=True)

	new_state.Tracking = True
	self.SetState(new_state)

	return delay

    def SetState(self, target_state):

        self.current_state = copy.deepcopy(target_state)

    def Park(self):

        if ( self.log ):
            self.log.info("Instrument: PARK")

        self.SetState(self.park_state)
	self.next_state = copy.deepcopy(self.park_state)

    def GetCurrentTelescopePosition(self,dateProfile):
        """
        Returns the current position (RA_Rad,DEC_Rad) of the telescope.
        """
        if self.log and self.verbose>1:
            self.log.info("Instrument: GetCurrentTelescopePosition():")

        if self.current_state.Tracking == True :
            return((self.current_state.RA_RAD,self.current_state.DEC_RAD))
        else:
            # need to calculate postion for 'stopped' telescope
            # computes RA DEC from the ALT AZ at given time.
            ALT_RAD = self.current_state.ALT_RAD
            AZ_RAD  = self.current_state.AZ_RAD
            (curdate,mjd,lst_RAD) = dateProfile
            (RA_RAD,DEC_RAD) = self.current_state.AltAz2RaDec(ALT_RAD, AZ_RAD, curdate)
            return (RA_RAD,DEC_RAD)

    def GetDelayForTarget(self,
                                    ra_RAD,dec_RAD,
                                    dateProfile, exposureTime,filter):
        """
        Computes the delay in seconds for the given observation depending
        on the current status of the instrument.

        Does not affect the state of the instrument.

        A previous observation is also supposed, considering then the
        readout-time for the previous exposure as a prerequisite for the
        exposure of the new observation.

        If the instrument is not tracking (park or stopped), then the slew
        starts in the current alt-az position.
        If the instrument is tracking (taking observations continuosly) then the
        slew starts from the alt-az position for the ra-dec of the previous
        observation at the time of the new observation.
        """
        if self.log and self.verbose>1:
            self.log.info("Instrument: GetDelayForTarget(): COMPUTING OBSERVATION DELAY")

	# Do not allow filter mount as result from ranks.
	if not self.current_state.IsFilterMounted(filter):
	    return -1.0

        (date,mjd,lst_RAD) = dateProfile

        ha_RAD = lst_RAD - ra_RAD 
        #(az_RAD,d1,d2,alt_RAD,d4,d5,pa_RAD,d7,d8) = slalib.sla_altaz (ha_RAD,
        #                                   dec_RAD,
        #                                   self.params.latitude_RAD)
        (az_RAD,d1,d2,alt_RAD,d4,d5,pa_RAD,d7,d8) = pal.altaz (ha_RAD,
                                           dec_RAD,
                                           self.params.latitude_RAD)

        if self.slew_params.Rotator_FollowSky:
            angle_RAD = 0.0
        else:
            angle_RAD = pa_RAD - self.next_state.Rotator_Pos_RAD
        self.targetposition.Set(ra_RAD,
                                dec_RAD,
                                angle_RAD,
                                filter,
                                exposureTime,
                                date,
                                alt_RAD,
                                az_RAD,
                                pa_RAD)

        ALT_RAD = self.targetposition.ALT_RAD
        if ALT_RAD < self.slew_params.Telescope_AltMin_RAD :
            delay = -1.0
            if self.log and self.verbose>1:
                self.log.info("Instrument: GetDelayForTarget(): target too low ALT_RAD = %f" % (ALT_RAD))
        elif ALT_RAD > self.slew_params.Telescope_AltMax_RAD :
            delay = -1.0
            if self.log and self.verbose>1:
                self.log.info("Instrument: GetDelayForTarget(): target too high ALT_RAD = %f" % (ALT_RAD))
        else:
            (delay, null_state) = self.GetSlewDelay(self.targetposition, self.next_state, allSlewData=False)

        if self.log and self.verbose>1:
            self.log.info("Instrument: GetDelayForTarget(): OBSERVATION DELAY = %f" % (delay))

        return delay

    def Observe(self, ra_RAD,dec_RAD, dateProfile, exposureTime,filter,delay,
                     log=False):
        """
        Performs the provided observation. 
        
        The final state is tracking the ra-dec coordinate.

        A previous observation is also supposed, considering then the
        readout-time for the previous exposure as a prerequisite for the
        exposure of the new observation.

        If the instrument is not tracking (park or stopped), then the slew
        starts in the current alt-az position.
        If the instrument is tracking (taking observations continuosly) then the
        slew starts from the alt-az position for the ra-dec of the previous
        observation at the time of the new observation.
        """ 

        if self.log and self.verbose>1:
            self.log.info("Instrument: Observe(): PERFORMING AN OBSERVATION")

        self.slewCount += 1
        
        (date,mjd,lst_RAD) = dateProfile

        self.current_state.UpdateState(date)
	init_state = copy.deepcopy(self.current_state)
        slewInitState = self.DBrecordState(self.current_state, SLEWINITSTATE)

        ha_RAD = lst_RAD - ra_RAD
        #(az_RAD,d1,d2,alt_RAD,d4,d5,pa_RAD,d7,d8) = slalib.sla_altaz (ha_RAD, dec_RAD, self.params.latitude_RAD)
        (az_RAD,d1,d2,alt_RAD,d4,d5,pa_RAD,d7,d8) = pal.altaz (ha_RAD, dec_RAD, self.params.latitude_RAD)

        if self.slew_params.Rotator_FollowSky:
            angle_RAD = 0.0
        else:
            angle_RAD = pa_RAD - self.current_state.Rotator_Pos_RAD

        self.targetposition.Set(ra_RAD,	dec_RAD, angle_RAD, filter, exposureTime, date, alt_RAD, az_RAD, pa_RAD)

        delay = self.Slew(self.targetposition)

        slewFinalState = self.DBrecordState(self.current_state, SLEWFINALSTATE)
        slewMaxSpeeds = self.DBrecordMaximumSpeeds()

        rotator_skypos = self.current_state.GetRotatorSkyPos()
        rotator_telpos = self.current_state.GetRotatorTelPos()
        altitude = self.current_state.ALT_RAD
        azimuth = self.current_state.AZ_RAD
	#slewDistance = slalib.sla_dsep(ra_RAD, dec_RAD, init_state.RA_RAD, init_state.DEC_RAD)
        slewDistance = pal.dsep(ra_RAD, dec_RAD, init_state.RA_RAD, init_state.DEC_RAD)
	
        slewdata = dataSlew(self.slewCount, date, date+delay, delay, slewDistance)

#        sql = 'INSERT INTO %s VALUES (NULL, ' % ('SlewHistory')
#        sql += '%d, ' % (self.sessionID)
#        sql += '%d, ' % (self.slewCount)
#        sql += '%f, ' % (date)
#        sql += '%f, ' % (date+delay)
#        sql += '%f )' % (delay)
        #(n, dummy) = self.lsstDB.executeSQL(sql)

	listSlewActivities = []
        for activity in self.lastslew_delays.keys():
            if activity in self.lastslew_criticalpath:
                cp = 'True'
            else:
                cp = 'False'
	    slewactivity = activitySlew(activity,
					self.lastslew_delays[activity],
					cp)
	    listSlewActivities.append(slewactivity)

#            sql = 'INSERT INTO %s VALUES (NULL, ' % ('SlewActivities')
#            sql += '%d, ' % (self.sessionID)
#            sql += '%d, ' % (self.slewCount)
#            sql += '"%s", ' % (activity)
#            sql += '%f, ' % (self.lastslew_delays[activity])
#            sql += '"%s" )' % (cp)
            #(n, dummy) = self.lsstDB.executeSQL(sql)

        self.next_state = copy.deepcopy(self.current_state)
        self.next_state.UpdateState(date+delay+exposureTime)

        return (delay, rotator_skypos, rotator_telpos, altitude, azimuth, slewdata, slewInitState, slewFinalState, slewMaxSpeeds, listSlewActivities)

    def DBrecordState(self, state, initfinal):

        if state.Tracking:
            tracking = 'True'
        else:
            tracking = 'False'

	slewState = stateSlew(state.TIME,
				state.RA_RAD,
				state.DEC_RAD,
				tracking,
				state.ALT_RAD,
				state.AZ_RAD,
				state.PA_RAD,
				state.DomAlt_Pos_RAD,
				state.DomAz_Pos_RAD,
				state.TelAlt_Pos_RAD,
				state.TelAz_Pos_RAD,
				state.Rotator_Pos_RAD,
				state.Filter_Pos,
				initfinal)

#        sql = 'INSERT INTO %s VALUES (NULL, ' % (dbTable)
#        sql += '%d, ' % (self.sessionID)
#        sql += '%d, ' % (self.slewCount)
#        sql += '%f, %f, %f, ' % (state.TIME, state.RA_RAD, state.DEC_RAD)
#        sql += '"%s", ' % (tracking)
#        sql += '%f, %f, %f, ' % (state.ALT_RAD, state.AZ_RAD, state.PA_RAD)
#        sql += '%f, %f, ' % (state.DomAlt_Pos_RAD, state.DomAz_Pos_RAD)
#        sql += '%f, %f, ' % (state.TelAlt_Pos_RAD, state.TelAz_Pos_RAD)
#        sql += '%f, ' % (state.Rotator_Pos_RAD)
#        sql += '"%s" )' % (state.Filter_Pos)
#        (n, dummy) = self.lsstDB.executeSQL(sql)

#	return n
	return slewState

    def DBrecordMaximumSpeeds(self):
        
	slewSpeeds = speedsSlew(self.current_state.DomAlt_Spd_RDS,
				self.current_state.DomAz_Spd_RDS,
				self.current_state.TelAlt_Spd_RDS,
				self.current_state.TelAz_Spd_RDS,
				self.current_state.Rotator_Spd_RDS)                                                                                                                 
#        sql = 'INSERT INTO %s VALUES (NULL, ' % ('SlewMaxSpeeds')
#        sql += '%d, ' % (self.sessionID)
#        sql += '%d, ' % (self.slewCount)
#        sql += '%f, %f, ' % (self.current_state.DomAlt_Spd_RDS, self.current_state.DomAz_Spd_RDS)
#        sql += '%f, %f, ' % (self.current_state.TelAlt_Spd_RDS, self.current_state.TelAz_Spd_RDS)
#        sql += '%f )    ' % (self.current_state.Rotator_Spd_RDS)
#        (n, dummy) = self.lsstDB.executeSQL(sql)
        
#        return n
	return slewSpeeds

    def GetFilter(self):
        """
        Returns the filter id which is currently in position
        
        """

        return self.current_state.GetFilter()

    def GetMountedFiltersList(self):
        """
        Returns the list of filters id currently mounted.

        """
        
        return self.current_state.GetMountedFiltersList()

    def GetRemovableFiltersList(self):
        """
        Returns the list of filters id currently mounted and are removable.
                                                                                                                                                                                                                             
        """
                                                                                                                                                                                                                             
        return self.current_state.GetRemovableFiltersList()

    def GetUnmountedFiltersList(self):
        """
        Returns the list of filters id currently mounted.
                                                                                                                                                                                                                             
        """
                                                                                                                                                                                                                             
        return self.current_state.GetUnmountedFiltersList()
    
    def IsFilterMounted(self, filter):
        """
        Returns True when the specified filter is currently mounted.

        """
        
        return self.current_state.IsFilterMounted(filter)

    def MountFilter(self, newfilter=None, oldfilter=None):
        """
        Mounts "newfilter" in the instrument, taking the place of "oldfilter".
        If "oldfilter" is not given, then the instrument takes one of the mounted
        filters following an arbitrary scheme.
        If "newfilter" is not given, then the instrument takes one of the defined
        filters in the configuration file.
        If "newfilter" is specified, it does not need to be one of the defined list.

        MountFilter(new, old) swaps new and old.
        MountFilter(new) mounts new and will removes any.
        MountFilter() swaps filters arbitrarly.
        
        """

	if (self.log):
	    self.log.info('Instrument: MountFilter(): mounting %s - unmounting %s' % (newfilter, oldfilter))

        self.current_state.MountFilter(newfilter, oldfilter)
	self.next_state.MountFilter(newfilter, oldfilter)
	self.park_state.MountFilter(newfilter, oldfilter)
#	if not self.IsFilterMounted(self.park_state.Filter_Pos):
#	    self.park_state.Filter_Pos = newfilter

	return
    
    def SetFilter(self, filter):
        """
        Puts the specified filter in position. If it is not mounted, the instrument
        mounts it automatically.

        """
        
        self.current_state.SetFilter(filter)

        if not IsFilterMounted(self.park_state.Filter_Pos):
            self.park_state.Filter_Pos = filter
                                                                                                                               
        return

    def GetSlitBuffer (self, target_DomAlt_RAD, prev_DomAlt_RAD):
        """
        Calculate the available dome slit excess (buffer) based on telescope
        elevation angle (ALT) and dome geometry. Note that DRN equation gives
        entire distance for a move from A to B.  Must divide by 2 to get
        static slit buffer excess at position A or B.
        """

        # If elevation constant or previous position was parked, calculate
        # buffer angle. Otherwise calculate buffer angle at original
        # elevation and target elevation and take the average.

        if (target_DomAlt_RAD == prev_DomAlt_RAD) or (prev_DomAlt_RAD == 1.553343):
           zenith_angle = ZENITH_RAD - target_DomAlt_RAD
           r = 16.6 / (1 /math.tan(zenith_angle) + math.tan(14.5*DEG2RAD))
           buffer_angle_RAD = 2 * math.asin (0.5 / r)
        # note: store prev_buffer angle so it doesn't need to be recalculated
        else:
           prev_zenith_angle = ZENITH_RAD - prev_DomAlt_RAD
           prev_r = 16.6 / (1 /math.tan(prev_zenith_angle) + math.tan(14.5*DEG2RAD))
           prev_buffer_angle = 2 * math.asin (0.5 / prev_r)

           targ_zenith_angle = ZENITH_RAD - target_DomAlt_RAD
           targ_r = 16.6 / (1 /math.tan(targ_zenith_angle) + math.tan(14.5*DEG2RAD))
           targ_buffer_angle = 2 * math.asin (0.5 / targ_r)

           buffer_angle_RAD = (prev_buffer_angle + targ_buffer_angle) / 2
        return buffer_angle_RAD

