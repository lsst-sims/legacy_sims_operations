#!/usr/bin/env python


from utilities import *
from AstronomicalSky import *


obsProfile = (-29.666667,-70.59,2737.,53407,1010.,12.,0.)

def computeDateProfile(date):
        """
        """
        (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = obsProfile
        mjd = (float (date) / float (DAY)) + epoch_MJD
        lst_RAD = slalib.sla_gmst(mjd) + lon_RAD
        return (date, mjd, lst_RAD)
                                                                                

def computeMoonProfile(sky,dateProfile):
        """
        """
        (date,mjd,lst_RAD) = dateProfile
        (lon_RAD,lat_RAD,elev_M,epoch_MJD,d1,d2,d3) = obsProfile
                                                                                
        # Get the Moon RA/Dec  in radians
        (moonRA_RAD,moonDec_RAD,moonDiam) =  slalib.sla_rdplan(mjd,
                                                    3,
                                                    lon_RAD,
                                                    lat_RAD)
        moonPhase_PERCENT = sky.getMoonPhase(dateProfile, obsProfile)
                                                                                
        return(moonRA_RAD,moonDec_RAD,moonPhase_PERCENT,0,0)

    
if (__name__ == '__main__'):
    # Init the Astronomical Sky
    sky = AstronomicalSky (obsProfile=obsProfile, date=0.)


    date = 0
    while date < YEAR :
        dateProfile = computeDateProfile(date)
        moonProfile = computeMoonProfile(sky,dateProfile)
        (moonRA_RAD,moonDec_RAD,moonPhase_PERCENT) = moonProfile
        print "date: %d MOON: RA:%f Dec:%f Phase:%f " %(date,moonRA_RAD,moonDec_RAD,moonPhase_PERCENT)
        date += DAY

    sys.exit (0)
