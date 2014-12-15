#!/usr/bin/env python

from Instrument import *
from utilities import *

def printstate(headstr, state):
        print("%s tracking=%5s TelAlt=%7.2f TelAz=%7.2f Rot=%7.2f" % (headstr, str(state.Tracking), state.TelAlt_Pos_RAD*RAD2DEG, state.TelAz_Pos_RAD*RAD2DEG, state.Rotator_Pos_RAD*RAD2DEG))
        print("%s DomAlt=%7.2f DomAz=%7.2f Filter=%s" % (headstr, state.DomAlt_Pos_RAD*RAD2DEG, state.DomAz_Pos_RAD*RAD2DEG, state.Filter_Pos))
        print("%s RA=%8.3f Dec=%8.3f Angle=%8.3f Time=%f" % (headstr, state.RA_RAD*RAD2DEG, state.DEC_RAD*RAD2DEG, state.ANG_RAD*RAD2DEG, state.TIME))

def computeDateProfile(obsProfile, date):
    (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = obsProfile
    mjd = (float (date) / float (DAY)) + float(epoch_MJD)
    lst_RAD = slalib.sla_gmst(mjd)  + lon_RAD
    return (date, mjd, lst_RAD)

###################################################################################
site_config = utilities.readConfFile("SiteCP.conf")[0]

longitude   = site_config["longitude" ]
latitude    = site_config["latitude"]
height      = site_config["height"]
pressure    = site_config["pressure"]
temperature = site_config["temperature"]
relativeHumidity = site_config["relativeHumidity"]
simEpoch    = site_config["seeingEpoch"]
obsProfile = (longitude *DEG2RAD, latitude *DEG2RAD, height, simEpoch,pressure,temperature,relativeHumidity)

inst_config_file = "Instrument.conf"
inst_config = utilities.readConfFile(inst_config_file)[0]

test_state = InstrumentState(config_dict=inst_config, obsProfile=obsProfile)

###################################################################################
ALT_DEG = [  59.6,  59.6,  60.0,  60.0 ]
AZ_DEG  = [ 219.5, 223.0, 356.5,   3.5 ]
TIME_SEC= [  5000,  5000,  5248,  5248 ]

for k in range(len(ALT_DEG)):
    alt_DEG  = ALT_DEG[k]
    az_DEG   = AZ_DEG[k]
    time_SEC= TIME_SEC[k]
    (ra_RAD, dec_RAD) = test_state.AltAz2RaDec(alt_DEG*DEG2RAD, az_DEG*DEG2RAD, time_SEC)
    print("AltAz2RaDec() alt=%7.2f az=%7.2f time=%8.0f ==> ra=%8.3f dec=%8.3f" % (alt_DEG, az_DEG, time_SEC, ra_RAD*RAD2DEG, dec_RAD*RAD2DEG))

###################################################################################
RA_DEG  = [  50.0,  50.0,  50.0,  50.0,  50.0,  50.0,  50.0,  50.0,  50.0,  50.0, \
             50  ,  50  ,  50  ,  50  ,  50  ,  50  ,  50  ,  50  ,  50  ,  50  , \
             50.00, 51.75, 53.50]
              
DEC_DEG = [ -90.0, -90.0, -90.0, -90.0, -90.0, -30.0, -30.0, -30.0, -30.0, -30.0, \
              0  ,   0  ,   0  ,   0  ,   0  ,  30  ,  30  ,  30  ,  30  ,  30  , \
              0.287,  0.287, 0.287]
             
TIME_SEC= [     0,  1800,  3600,  5400,  7200,     0,  1800,  3600,  5400,  7200, \
                0,  1800,  3600,  5400,  7200,     0,  1800,  3600,  5400,  7200, \
            5248, 5248, 5248]

for k in range(len(RA_DEG)):
	ra_DEG  = RA_DEG[k]
	dec_DEG = DEC_DEG[k]
	time_SEC= TIME_SEC[k]
	(alt_RAD, az_RAD, pa_RAD, ha_HOU) = test_state.RaDec2AltAz(ra_DEG*DEG2RAD, dec_DEG*DEG2RAD, time_SEC)
	print("RaDec2AltAz() ra=%8.3f dec=%8.3f time=%8.0f ==> alt=%7.2f az=%7.2f pa=%8.3f ha=%8.3f" % (ra_DEG, dec_DEG, time_SEC, alt_RAD*RAD2DEG, az_RAD*RAD2DEG, pa_RAD*RAD2DEG, ha_HOU))

###################################################################################
telescope = Instrument( sessionID=0,
                        dbTableDict    = None,
                        obsProfile     = obsProfile,
                        instrumentConf = inst_config_file)

print
ra1_DEG  = 20.656
dec1_DEG =-50.013
time_SEC = 5000
ra2_DEG  = 19.355
dec2_DEG =-48.459
sky_dist_DEG = distance([ra1_DEG*DEG2RAD, dec1_DEG*DEG2RAD],
                        [[ra2_DEG*DEG2RAD, dec2_DEG*DEG2RAD]])[0]*RAD2DEG
print "distance on sky = %7.3f" % (sky_dist_DEG)
dateprofile = computeDateProfile(obsProfile, date=5000)
telescope.Observe(  ra_RAD  = ra1_DEG*DEG2RAD,
                    dec_RAD = dec1_DEG*DEG2RAD,
                    dateProfile = dateprofile,
                    exposureTime = 0,
                    filter       = 'r',
                    delay        = 0)
printstate("init :",telescope.current_state)
telescope.Observe(  ra_RAD  = ra2_DEG*DEG2RAD,
                    dec_RAD = dec2_DEG*DEG2RAD,
                    dateProfile = dateprofile,
                    exposureTime = 0,
                    filter       = 'r',
                    delay        = 0)
printstate("final:",telescope.current_state)

print
ra1_DEG  = 50.000
dec1_DEG =  0.287
time_SEC = 5248
ra2_DEG  = 53.5
dec2_DEG = 0.287
sky_dist_DEG = distance([ra1_DEG*DEG2RAD, dec1_DEG*DEG2RAD],
                        [[ra2_DEG*DEG2RAD, dec2_DEG*DEG2RAD]])[0]*RAD2DEG
print "distance on sky = %7.3f" % (sky_dist_DEG)
dateprofile = computeDateProfile(obsProfile, date=5248)
telescope.Observe(  ra_RAD  = ra1_DEG*DEG2RAD,
                    dec_RAD = dec1_DEG*DEG2RAD,
                    dateProfile = dateprofile,
                    exposureTime = 0,
                    filter       = 'r',
                    delay        = 0)
printstate("init :",telescope.current_state)
telescope.Observe(  ra_RAD  = ra2_DEG*DEG2RAD,
                    dec_RAD = dec2_DEG*DEG2RAD,
                    dateProfile = dateprofile,
                    exposureTime = 0,
                    filter       = 'r',
                    delay        = 0)
printstate("final:",telescope.current_state)


