// utility macros
#define MIN(a,b) ((a)<(b) ? (a) : (b))
#define MAX(a,b) ((a)>(b) ? (a) : (b))
#define CLIP(x,a,b) {if(x<a) x=a; if(x>b) x=b;}
#define FIXRANGE(a,low,hi) {while((a)<(low)) (a) += ((hi)-(low)); while((a)>(hi)) (a)-= ((hi)-(low));}
#define FIXRA(ra) FIXRANGE((ra),(-M_PI),(M_PI))

// map filter name to filter index
int filterToNumber(char *name) {
  int j, num, found;

  found = 0;
  for(j=0; j<NFILTERS; j++) {
    if(strncmp(name,filtername[j],FILTLEN)==0) {
      num = j;
      found = 1;
      break;
    }
  }
  if(found==0) {
      printf("bad filter: \"%s\"\n", name);
      exit(1);
  }
  return num;
}

// comparison routines for system qsort
//  Comparison by expdate
int compareDate(const void *m1, const void *m2) {
  observation *obs1 = (observation *) m1;
  observation *obs2 = (observation *) m2;
  if(obs1->expdate < obs2->expdate) return (-1);
  if(obs1->expdate > obs2->expdate) return (1);
  return (0);
}
// comparison by field number
int compareField(const void *m1, const void *m2) {
  observation *obs1 = (observation *) m1;
  observation *obs2 = (observation *) m2;
  if(obs1->field < obs2->field) return (-1);
  if(obs1->field > obs2->field) return (1);
  return (0);
}
// comparison by filter number
int compareFilter(const void *m1, const void *m2) {
  observation *obs1 = (observation *) m1;
  observation *obs2 = (observation *) m2;
  if(obs1->filter < obs2->filter) return (-1);
  if(obs1->filter > obs2->filter) return (1);
  return (0);
}
// comparison by dec, then ra
int comparePosition(const void *m1, const void *m2) {
  observation *obs1 = (observation *) m1;
  observation *obs2 = (observation *) m2;
  if(obs1->dec < obs2->dec) return (-1);
  if(obs1->dec > obs2->dec) return (1);
  if(obs1->ra < obs2->ra) return (-1);
  if(obs1->ra > obs2->ra) return (1);
  return (0);
}

void printCircumstances(observation thisobs) {
  struct date_time date;
  double mjd, mjdloc, lstm, jd;
  double myAlt, myAz, ZD;
  double sunra, sundec;
  double moonra, moondec, moonalt, moonaz, moonill, moonphase;
  double moon_obs;
  double rasun, decsun, distsun, toporasun, topodecsun, x, y, z, sunalt, sunaz;
  double sun_moon;
  double trueam;
  double sunrise, sunset, twibeg, twiend, ratwbeg, ratwend;
  double nautbeg, nautend;


  mjd = thisobs.date;
  jd = mjd + 2400000.5;
  printf("      observation MJD: %f\n", mjd);
  date = mjd_to_date(mjd);
  printf("             obs date: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  mjdloc = mjd - tz/24.0;
  date = mjd_to_date(mjdloc);
  printf("  %4d/%02d/%02d %02d:%02d:%05.2f local\n",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  lstm = lst(jd,longitude_hrs);
  printf(" local mean sidereal time: %f hours     %f (rad)\n", lstm, 
         lstm/DEG_IN_RADIAN*360.0/24.0);
  printf("     observation position:   ");
  put_coords(thisobs.ra*HRS_IN_RADIAN,2,1);  printf("    ");
  put_coords(thisobs.dec*DEG_IN_RADIAN,2,1); printf("     %9.6f  %9.6f (rad)\n",
                                                thisobs.ra, thisobs.dec);
  myAlt = altit(thisobs.dec*DEG_IN_RADIAN,
                (lstm-thisobs.ra*HRS_IN_RADIAN), latitude_deg,
                &myAz, &trueam);
  printf("      observation alt, az: %11.6f  %11.6f     %9.6f  %9.6f (rad)\n",
         myAlt, myAz, myAlt/DEG_IN_RADIAN, myAz/DEG_IN_RADIAN);
  ZD = 90.0-myAlt;
  printf("          Zenith distance: %11.6f  %9.6f\n\n", ZD, ZD/DEG_IN_RADIAN);

  moonData(mjd, &moonra, &moondec, &moonalt, &moonill, &moonphase);
  printf("  moon position (RA, Dec):   ");
  put_coords(moonra*HRS_IN_RADIAN,2,1);  printf("    ");
  put_coords(moondec*DEG_IN_RADIAN,2,1); printf("     %9.6f  %9.6f (rad)\n",
                                    moonra, moondec);
  moonalt = altit(moondec*DEG_IN_RADIAN,(lstm - moonra*HRS_IN_RADIAN),latitude_deg,&moonaz,&trueam);
  printf("             moon alt, az: %11.6f  %11.6f     %9.6f  %9.6f (rad)\n",
         moonalt, moonaz, moonalt/DEG_IN_RADIAN, moonaz/DEG_IN_RADIAN);
  moon_obs = mysubtend(moonra*HRS_IN_RADIAN,moondec*DEG_IN_RADIAN,thisobs.ra,thisobs.dec);
  printf("   moon-object separation: %11.6f   %9.6f\n", moon_obs*DEG_IN_RADIAN, moon_obs);
  printf(" moon illumination, phase: %f   %f\n\n", moonill, moonphase);

  accusun(jd,lstm,latitude_deg,&rasun,&decsun,&distsun,
		&toporasun,&topodecsun,&x,&y,&z);
  sunalt=altit(topodecsun,(lstm-toporasun),latitude_deg,&sunaz,&z);
  sun_moon = mysubtend(moonra*HRS_IN_RADIAN,moondec*DEG_IN_RADIAN,toporasun,topodecsun);
  printf("   sun position (RA, Dec):   ");
  put_coords(rasun,2,1);  printf("    ");
  put_coords(decsun,2,1); printf("     %9.6f  %9.6f (rad)\n",
                                    rasun/HRS_IN_RADIAN, decsun/DEG_IN_RADIAN);
  printf("        sun-moon distance:  %f   %f (rad)\n\n", sun_moon*DEG_IN_RADIAN, sun_moon);


  twilightparms(mjd, &sunrise, &sunset, &twibeg, &twiend,
                &nautbeg, &nautend,
                &ratwbeg, &ratwend, &sunra);

  date = mjd_to_date(sunset);
  printf("                   sunset: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  sunset -= tz/24.0;
  date = mjd_to_date(sunset);
  printf("  %4d/%02d/%02d %02d:%02d:%05.2f local\n",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  
  date = mjd_to_date(nautbeg);
  printf("    nautical night begins: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  nautbeg -= tz/24.0;
  date = mjd_to_date(nautbeg);
  printf("  %4d/%02d/%02d %02d:%02d:%05.2f local\n",
         date.y,date.mo,date.d, date.h,date.mn,date.s);

  date = mjd_to_date(twibeg);
  printf("astronomical night begins: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  twibeg -= tz/24.0;
  date = mjd_to_date(twibeg);
  printf("  %4d/%02d/%02d %02d:%02d:%05.2f local\n",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
 
  date = mjd_to_date(twiend);
  printf("  astronomical night ends: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  twiend -= tz/24.0;
  date = mjd_to_date(twiend);
  printf("  %4d/%02d/%02d %02d:%02d:%05.2f local\n",
         date.y,date.mo,date.d, date.h,date.mn,date.s);

  date = mjd_to_date(nautend);
  printf("      nautical night ends: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  nautend -= tz/24.0;
  date = mjd_to_date(nautend);
  printf("  %4d/%02d/%02d %02d:%02d:%05.2f local\n",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  
  date = mjd_to_date(sunrise);
  printf("                  sunrise: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  sunrise -= tz/24.0;
  date = mjd_to_date(sunrise);
  printf("  %4d/%02d/%02d %02d:%02d:%05.2f local\n",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  
}
