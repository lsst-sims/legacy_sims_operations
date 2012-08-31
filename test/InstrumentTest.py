#!/usr/bin/env python

from Instrument import *
from utilities import *

def printstate(headstr, state):
        print("%s tracking=%5s TelAlt=%8.3f TelAz=%8.3f Rot=%8.3f" % (headstr, str(state.Tracking), state.TelAlt_Pos_RAD*RAD2DEG, state.TelAz_Pos_RAD*RAD2DEG, state.Rotator_Pos_RAD*RAD2DEG))
        print("%s DomAlt=%8.3f DomAz=%8.3f Filter=%s" % (headstr, state.DomAlt_Pos_RAD*RAD2DEG, state.DomAz_Pos_RAD*RAD2DEG, state.Filter_Pos))
        print("%s RA=%8.3f Dec=%8.3f Angle=%8.3f Time=%f" % (headstr, state.RA_RAD*RAD2DEG, state.DEC_RAD*RAD2DEG, state.ANG_RAD*RAD2DEG, state.TIME))

site_config = utilities.readConfFile("SiteCP.conf")
longitude   = site_config["longitude" ]
latitude    = site_config["latitude"]
height      = site_config["height"]
pressure    = site_config["pressure"]
temperature = site_config["temperature"]
relativeHumidity = site_config["relativeHumidity"]
simEpoch    = site_config["seeingEpoch"]
obsProfile = (longitude *DEG2RAD, latitude *DEG2RAD, height, simEpoch,pressure,temperature,relativeHumidity)

inst_config = utilities.readConfFile("Instrument.conf")

test_state = InstrumentState(config_dict=inst_config, obsProfile=obsProfile)


# 2.3.1 RaDec2AltAz
RA_DEG  = [   0.0,  10.0,  20.0,  30.0,  40.0,  50.0,  60.0,  70.0,  80.0,  90.0]
DEC_DEG = [ -90.0, -90.0, -80.0, -80.0, -70.0, -70.0, -60.0, -60.0, -50.0, -50.0]
TIME_SEC= [     0,   000,  0000,  0000,  0000,  0000, 00000, 00000, 00000, 00000]

for k in range(len(RA_DEG)):
	ra_DEG  = RA_DEG[k]
	dec_DEG = DEC_DEG[k]
	time_SEC= TIME_SEC[k]
	(alt_RAD, az_RAD, pa_RAD, ha_HOU) = test_state.RaDec2AltAz(ra_DEG*RAD2DEG, dec_DEG*RAD2DEG, time_SEC)
	print("RaDec2AltAz() ra=%8.3f dec=%8.3f time=%8.0f ==> alt=%8.3f az=%8.3f pa=%8.3f" % (ra_DEG, dec_DEG, time_SEC, alt_RAD*RAD2DEG, az_RAD*RAD2DEG, pa_RAD*RAD2DEG))

# 2.3.3 GetShortestDistanceWithWrap
min_angle_DEG = -270.0
max_angle_DEG =  270.0
start_angle_DEG = [-240.0, -60.0, 30.0, 120.0, 210.0]
target_angle_DEG = [-260.0, -90.0, 30.0, 150.0, 260.0]

for j in range(len(start_angle_DEG)):
	for k in range(len(target_angle_DEG)):
		start_DEG = start_angle_DEG[j]
		target_DEG = target_angle_DEG[k]
		(distance_RAD, final_RAD) = test_state.GetShortestDistanceWithWrap(target_DEG*DEG2RAD, start_DEG*DEG2RAD, min_angle_DEG*DEG2RAD, max_angle_DEG*DEG2RAD)
		print("GetShortestDistanceWithWrap() start=%6.1f target=%6.1f ==> distance=%6.1f final=%6.1f" % (start_DEG, target_DEG, distance_RAD*RAD2DEG, final_RAD*RAD2DEG))

# 2.3.6 SetClosestState

INI_ALT_DEG = [30.0, 45.0, 60.0,  75.0,  85.0]
INI_AZ_DEG  = [ 0.0, 40.0, 80.0, 100.0, 120.0]
INI_FILTER  = [ 'r',  'g',  'i',   'y',   'z']

FIN_ALT_DEG = [30.0, 48.0, 70.0,  65.0,  45.0]
FIN_AZ_DEG  = [ 0.0, 40.0, 80.0, 110.0, 240.0]
FIN_FILTER  = [ 'r',  'g',  'g',   'g',   'g']

for j in range(len(INI_ALT_DEG)):
	init_state = InstrumentState(	alt_RAD=INI_ALT_DEG[j]*DEG2RAD,
					az_RAD =INI_AZ_DEG[j]*DEG2RAD,
					filter =INI_FILTER[j],
					config_dict=inst_config, obsProfile=obsProfile)
	printstate("SetClosestState() INI_STATE:", init_state)
	for k in range(len(FIN_ALT_DEG)):
		target_position = InstrumentPosition(	alt_RAD=FIN_ALT_DEG[k]*DEG2RAD,
							az_RAD =FIN_AZ_DEG[k]*DEG2RAD,
							filter =FIN_FILTER[k])

		test_state.SetClosestState(target_position, init_state)
		printstate("SetClosestState() FIN_STATE:", test_state)




