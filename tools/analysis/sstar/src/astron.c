#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define  DEG_IN_RADIAN     57.2957795130823
#define  HRS_IN_RADIAN     3.819718634205
#define  J2000             2451545.        /* Julian date at standard epoch */
#define  SEC_IN_DAY        86400.
#define  FLATTEN           0.003352813   /* flattening of earth, 1/298.257 */
#define  EQUAT_RAD         6378137.    /* equatorial radius of earth, meters */
#define  ASTRO_UNIT        1.4959787066e11 /* 1 AU in meters */
#define  TWOPI             6.28318530717959
#define  PI_OVER_2         1.57079632679490
#define  EQUAT_RAD         6378137.    /* equatorial radius of earth, meters */

// these should be in decimal hours and decimal degrees
double latitude_deg, longitude_hrs, elev_meters, horiz;
// this should be in hours west of Greenwich
double tz;

//#define TEST
#ifdef TEST
// little test program

int main(void) {

  struct date_time date;
  short dow;
  double obsjd, obsmjd, mjd;
  double sunra, sundec;
  double moonra, moondec, moonalt, moonill, moonphase;
  double objra, objdec, trueam, alt, ha;
  double sunrise, sunset, twibeg, twiend, ratwbeg, ratwend;
  double nautbeg, nautend;
  observation obs;

  // set site global vars
  //  setUpSiteData(31.044444, -114.516667, 2830.0, 8.0);
  // don't forget that sunrise etc. depends upon altitude;
  // the USNO tables assume sea level
  setUpSiteData(-30.33333, -70.98333, 0.0, 4.0);
  // 31 03  -114 31

  // observation data
  obs.date = 49354.056852; // 1 January, 1994

  obs.ra = 0.463959 / HRS_IN_RADIAN;
  obs.dec = 0.577318 / DEG_IN_RADIAN;

  date = mjd_to_date(obs.date);
  printf("date: %4d/%02d/%02d %02d:%02d:%05.2f\n", date.y,date.mo,date.d,
         date.h,date.mn,date.s);

  mjd = date_to_mjd(date);
  printf("error converting jd->date->jd: %e\n", mjd-obs.date);

  // get sun data
  sunPosition(mjd, &sunra, &sundec);
  printf("sun position:  %f h   %f d\n",
         sunra * HRS_IN_RADIAN, sundec*DEG_IN_RADIAN);

  // get moon data
  moonData(mjd, &moonra, &moondec, &moonalt, &moonill, &moonphase);
  printf("moon position: %f h  %f d\n",
         moonra * HRS_IN_RADIAN, moondec * DEG_IN_RADIAN);
  printf("moon altitude: %f d\n", moonalt);
  printf("moon illumination: %f\n", moonill);

  // airmass data
  airmass(obs.date, obs.ra, obs.dec, &trueam, &alt, &ha);
  printf("airmass: %f   altitude: %f\n", trueam, alt);

  // twilight data
  twilightparms(mjd, &sunrise, &sunset, &twibeg, &twiend,
                &nautbeg, &nautend,
                &ratwbeg, &ratwend, &sunra);

  date = mjd_to_date(sunset);
  printf("               sunset: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  sunset -= tz/24.0;
  date = mjd_to_date(sunset);
  printf("  %02d:%02d:%05.2f local\n", date.h,date.mn,date.s);


  date = mjd_to_date(twibeg);
  printf("twilight night begins: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  twibeg -= tz/24.0;
  date = mjd_to_date(twibeg);
  printf("  %02d:%02d:%05.2f local\n", date.h,date.mn,date.s);

  date = mjd_to_date(twiend);
  printf("  twilight night ends: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  twiend -= tz/24.0;
  date = mjd_to_date(twiend);
  printf("  %02d:%02d:%05.2f local\n", date.h,date.mn,date.s);

  date = mjd_to_date(sunrise);
  printf("              sunrise: %4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  sunrise -= tz/24.0;
  date = mjd_to_date(sunrise);
  printf("  %02d:%02d:%05.2f local\n", date.h,date.mn,date.s);

  printf("18 twilight day length: %f h\n", (sunrise-sunset)*24.0);

  printf(" setra (RAD): %f\n", ratwbeg);
  printf("risera (RAD): %f\n", ratwend);

  printf("\n\n\n\n\n\n");

  printCircumstances(obs);

}
#endif


// ----------------------------------------------------------------------------
// -----------------  this stuff from skycalc.v5 ------------------------------
// ----------------------------------------------------------------------------


// rounds argument x to places places, e.g. 2.32839,1 -> 2.3.
double round_prec(double x, int places) {
  double tmp, base = 1.;
  int i, ip;

  for(i = 1; i <= places; i++) {  /* bet this is faster than pow ... */
    base *= 10.;
  }
  tmp = x * base;
  if(tmp >= 0.)
    tmp += 0.5;
  else tmp -= 0.5;
  ip = (int) tmp;
  tmp = ((double) ip) / base;
  return(tmp);
}

// Rounds the seconds of a struct coord to a specified precision;
// if they turn out to be sixty, does the carry to the other fields.
//
//	precision 0 -- whole minutes  (seconds set to zero)
//	          1 -- tenths of a minute (seconds set to zero)
//		  2 -- whole seconds
//		  3 -- tenths of a second
//	  	  4 -- hundredths ...
//				etc.
//
void round_coord(struct coord *incoord, struct coord *outcoord, int prec) {
  outcoord->sign = incoord->sign;

  /* initialize */

  outcoord->ss = incoord->ss;
  outcoord->mm = incoord->mm;
  outcoord->hh = incoord->hh;

  if(prec <= 1) {
    outcoord->mm = round_prec((outcoord->mm + outcoord->ss / 60.),prec);
    outcoord->ss = 0.;
    if(outcoord->mm >= 59.99) {  /* permissible because of limit
                                    on prec */
      outcoord->mm -= 60.;
      outcoord->hh += 1.;
    }
  }
  else {
    outcoord->ss = round_prec(outcoord->ss,(prec-2));
    if( outcoord->ss >= 59.999999999) {  /* as many digits as
                                            one would ever want ... */
      outcoord->ss -= 60.;
      outcoord->mm += 1.;
      if(outcoord->mm >= 59.999999999) {
        outcoord->mm -= 60.;
        outcoord->hh += 1.;
      }
    }
  }
}

// Puts out the hours (or decimal degrees) with the
// following format information:
//
//   -- Allows "width" digits of space for hours;
//       e.g. -20 would be width 2.
//   -- if showpos == 1, prints a + sign if result is
//       positive.
//   -- if alignsign == 1, prints sign before the field;
//       otherwise places sign flush with digit.
void put_hrs(double hrs, short sign, int width, int showpos, int alignsign) {
  int i, digitsout, leadblanks;
  char outform[20];
  double tmp;

  if(alignsign == 1) {
    if(sign < 0) printf("-");
    else if(showpos == 1) printf("+");
    sprintf(outform,"%%%d.0f",width);
    printf(outform,hrs);
  }
  else {
    tmp = fabs(hrs);
    digitsout = 1;
    while(tmp >= 10.) {
      digitsout++;
      tmp /= 10.;
    }
    if(digitsout >= width) {
      if(sign < 0) printf("-");
      else if (showpos == 1) printf("+");
      printf("%.0f",hrs);
    }
    else {
      for(i = 1; i < width - digitsout; i++)
        printf(" ");
      if(sign < 0) printf("-");
      else if (showpos == 1) printf("+");
      else printf(" ");
      sprintf(outform,"%%%d.0f",digitsout);
      printf(outform,hrs);
    }
  }
}

// function for converting decimal to babylonian hh mm ss.ss
void dec_to_bab (double deci, struct coord *bab) {
  int hr_int, min_int;

  if (deci >= 0.) bab->sign = 1;
  else {
    bab->sign = -1;
    deci = -1. * deci;
  }
  hr_int = deci;   /* use conversion conventions to truncate */
  bab->hh = hr_int;
  min_int = 60. * (deci - bab->hh);
  bab->mm = min_int;
  bab->ss = 3600. * (deci - bab->hh - bab->mm / 60.);
}

void put_coords(double deci, int prec, int showsign) {
  struct coord bab, babout;
  char formstr[20];
  int outstringlen;

  dec_to_bab(deci,&bab);

  round_coord(&bab,&babout,prec);

  if(prec == 0) {
    put_hrs(babout.hh, babout.sign, 3, showsign, 0);
    printf(" %02.0f",babout.mm);
  }
  else if (prec == 1) {
    put_hrs(babout.hh, babout.sign, 3, showsign, 0);
    printf(" %04.1f",babout.mm);
  }
  else {
    if(prec == 2) {
      put_hrs(babout.hh, babout.sign, 3, showsign, 0);
      printf(" %02.0f %02.0f",
             babout.mm,babout.ss);
    }
    else {
      put_hrs(babout.hh, babout.sign, 3, showsign, 0);
      sprintf(formstr," %%02.0f %%0%d.%df",
              prec+1,prec-2);
      printf(formstr,babout.mm,babout.ss);
    }
  }
}

// given a julian date,
//   prints a year, month, day, hour, minute, second
//   (pap modified for format)
void print_all(double jdin) {

  struct date_time date;
  int ytemp, mtemp, dtemp; /* compiler bug workaround ... SUN
                       and silicon graphics */
  double out_time;
  short dow;

  caldat(jdin,&date,&dow);

  //  print_day(dow);
  //  printf(", ");

  /* going through the rigamarole to avoid 60's */
  out_time = date.h + date.mn / 60. + date.s / 3600.;

  ytemp = (int) date.y;
  mtemp = (int) date.mo;
  dtemp = (int) date.d;
  printf("%4d/%02d/%02d",ytemp,mtemp,dtemp);
  put_coords(out_time,3,0);
}

// returns radian angle 0 to 2pi for coords x, y 
//   get that quadrant right !!
double atan_circ(double x, double y) {
  double theta;
  
  if((x == 0.) && (y == 0.)) return(0.);  /* guard ... */
  
  theta = atan2(y,x);  /* turns out there is such a thing in math.h */
  while(theta < 0.) theta += TWOPI;
  return(theta);
}

// assuming x is an angle in degrees, returns
// modulo 360 degrees.
double circulo(double x) {
  int n;
  
  n = (int)(x / 360.);
  return(x - 360. * n);
}

// rotates ecliptic rectangular coords x, y, z to
//   equatorial (all assumed of date.)
void eclrot(double jd, double *x, double *y, double *z) {
  double incl;
  double xpr,ypr,zpr;
  double T;

  T = (jd - J2000) / 36525;  /* centuries since J2000 */
  
  incl = (23.439291 + T * (-0.0130042 - 0.00000016 * T))/DEG_IN_RADIAN;
  /* 1992 Astron Almanac, p. B18, dropping the
		   cubic term, which is 2 milli-arcsec! */
  ypr = cos(incl) * *y - sin(incl) * *z;
  zpr = sin(incl) * *y + cos(incl) * *z;
  *y = ypr;
  *z = zpr;
	/* x remains the same. */
}

// computes the geocentric coordinates from the geodetic
//  (standard map-type) longitude, latitude, and height.
//  These are assumed to be in decimal hours, decimal degrees, and
//  meters respectively.  Notation generally follows 1992 Astr Almanac,
//  p. K11
void geocent(double geolong, double geolat, double height,
             double *x_geo, double *y_geo, double *z_geo) {
  double denom, C_geo, S_geo;

  geolat = geolat / DEG_IN_RADIAN;
  geolong = geolong / HRS_IN_RADIAN;
  denom = (1. - FLATTEN) * sin(geolat);
  denom = cos(geolat) * cos(geolat) + denom*denom;
  C_geo = 1. / sqrt(denom);
  S_geo = (1. - FLATTEN) * (1. - FLATTEN) * C_geo;
  C_geo = C_geo + height / EQUAT_RAD;  /* deviation from almanac
                                          notation -- include height here. */
  S_geo = S_geo + height / EQUAT_RAD;
  *x_geo = C_geo * cos(geolat) * cos(geolong);
  *y_geo = C_geo * cos(geolat) * sin(geolong);
  *z_geo = S_geo * sin(geolat);
}

// Given a julian date in 1900-2100, returns the correction
// delta t which is:
//    TDT - UT (after 1983 and before 1998)
//    ET - UT (before 1983)
//    an extrapolated guess  (after 1998).
//
// For dates in the past (<= 1998 and after 1900) the value is linearly
// interpolated on 5-year intervals; for dates after the present,
// an extrapolation is used, because the true value of delta t
// cannot be predicted precisely.  Note that TDT is essentially the
// modern version of ephemeris time with a slightly cleaner
// definition.
//
// Where the algorithm shifts there is an approximately 0.1 second
// discontinuity.  Also, the 5-year linear interpolation scheme can
// lead to errors as large as 0.5 seconds in some cases, though
// usually rather smaller.
double etcorr(double jd) {
  double jd1900 = 2415019.5;
  double dates[22];
  double delts[21];  /* can't initialize this look-up table
                        with stupid old sun compiler .... */
  double year, delt;
  int i;

  // this stupid patch for primitive sun C compilers ....
  // do not allow automatic initialization of arrays!

  for(i = 0; i <= 19; i++) dates[i] = 1900 + (double) i * 5.;
  dates[20] = 1998.;  /* the last accurately tabulated one in the
                         2000 Almanac ... */

  delts[0] = -2.72;  delts[1] = 3.86; delts[2] = 10.46;
  delts[3] = 17.20;  delts[4] = 21.16; delts[5] = 23.62;
  delts[6] = 24.02;  delts[7] = 23.93; delts[8] = 24.33;
  delts[9] = 26.77;  delts[10] = 29.15; delts[11] = 31.07;
  delts[12] = 33.15;  delts[13] = 35.73; delts[14] = 40.18;
  delts[15] = 45.48;  delts[16] = 50.54; delts[17] = 54.34;
  delts[18] = 56.86;  delts[19] = 60.78; delts[20] = 62.97;
  
  year = 1900. + (jd - 2415019.5) / 365.25;
  
  if(year < 1998. && year >= 1900.) {
    i = (year - 1900) / 5;
    delt = delts[i] +
      ((delts[i+1] - delts[i])/(dates[i+1] - dates[i])) * (year - dates[i]);
  }
  
  else if (year >= 1998. && year < 2100.)
    delt = 33.15 + (2.164e-3) * (jd - 2436935.4);  /* rough extrapolation */
  
  else if (year < 1900) {
    printf("etcorr ... no ephemeris time data for < 1900.\n");
    delt = 0.;
  }
  
  else if (year >= 2100.) {
    printf("etcorr .. very long extrapolation in delta T - inaccurate.\n");
    delt = 180.; /* who knows? */
  }
  
  return(delt);
}

// From Meeus' Astronomical Formulae for Calculators.  The two JD
//   conversion routines routines were replaced 1998 November 29 to
//   avoid inclusion of copyrighted "Numerical Recipes" code.  A test
//   of 1 million random JDs between 1585 and 3200 AD gave the same
//   conversions as the NR routines.
double date_to_jd(struct date_time date) {
  double jd;
  int y, m;
  long A, B;
  
  if(date.mo <= 2) {
    y = date.y - 1;
    m = date.mo + 12;
  }
  else {
    y = date.y;
    m = date.mo;
  }
  
  A = (long) (y / 100.);
  B = 2 - A + (long) (A / 4.);
  
  jd = (long) (365.25 * y) + (long) (30.6001 * (m + 1)) + date.d +
    1720994.5;
  
  jd += date.h / 24. + date.mn / 1440. + date.s / 86400.;
  
  if(date.y > 1583) return(jd + B);
  else return(jd);
  /* Not quite right, since Gregorian calendar first
     adopted around Oct 1582.  But fine for modern. */
}


// returns the local MEAN sidereal time (dec hrs) at julian date jd
//   at west longitude long (decimal hours).  Follows
//   definitions in 1992 Astronomical Almanac, pp. B7 and L2.
//   Expression for GMST at 0h ut referenced to Aoki et al, A&A 105,
//   p.359, 1982.  On workstations, accuracy (numerical only!)
//   is about a millisecond in the 1990s. */
double lst(double jd, double longit) {
  double t, ut, jdmid, jdint, jdfrac, sid_g, sid;
  long jdin, sid_int;

  jdin = jd;         /* fossil code from earlier package which
			split jd into integer and fractional parts ... */
  jdint = jdin;
  jdfrac = jd - jdint;
  if(jdfrac < 0.5) {
    jdmid = jdint - 0.5;
    ut = jdfrac + 0.5;
  }
  else {
    jdmid = jdint + 0.5;
    ut = jdfrac - 0.5;
  }
  t = (jdmid - J2000)/36525;
  sid_g = (24110.54841+8640184.812866*t+0.093104*t*t-6.2e-6*t*t*t)/SEC_IN_DAY;
  sid_int = sid_g;
  sid_g = sid_g - (double) sid_int;
  sid_g = sid_g + 1.0027379093 * ut - longit/24.;
  sid_int = sid_g;
  sid_g = (sid_g - (double) sid_int) * 24.;
  if(sid_g < 0.) sid_g = sid_g + 24.;
  return(sid_g);
}

// from Jean Meeus, Astronomical Formulae for Calculators,
//   published by Willman-Bell Inc.
// Avoids a copyrighted routine from Numerical Recipes.
// Tested and works properly from the beginning of the
//   Gregorian calendar era (1583) to beyond 3000 AD. */
void caldat(double jdin, struct date_time *date, short *dow) {
  double jdtmp;
  long alpha;
  long Z;
  long A, B, C, D, E;
  double F;
  double x;   /* for day-of-week calculation */
  
  jdtmp = jdin + 0.5;
  
  Z = (long) jdtmp;
  
  x = Z/7.+0.01;
  *dow = 7.*(x - (long) x);   /* truncate for day of week */
  
  F = jdtmp - Z;
  
  if(Z < 2299161) A = Z;
  else {
    alpha = (long) ((Z - 1867216.25) / 36524.25);
    A = Z + 1 + alpha - (long) (alpha / 4);
  }
  
  B = A + 1524;
  C = ((B - 122.1) / 365.25);
  D =  (365.25 * C);
  E =  ((B - D) / 30.6001);
  
  date->d = B - D - (long)(30.6001 * E);
  if(E < 13.5) date->mo = E - 1;
  else date->mo = E - 13;
  if(date->mo  > 2.5)  date->y = C - 4716;
  else date->y = C - 4715;
  
  date->h = F * 24.;  /* truncate */
  date->mn = (F - ((float) date->h)/24.) * 1440.;
  date->s = (F - ((float) date->h)/24. -
             ((float) date->mn)/1440.) * 86400;
}

// Low precision formulae for the sun, from Almanac p. C24 (1990)
// ra and dec are returned as decimal hours and decimal degrees.
void lpsun(double jd, double *ra, double *dec) {
  double n, L, g, lambda,epsilon,alpha,delta,x,y,z;
  
  n = jd - J2000;
  L = 280.460 + 0.9856474 * n;
  g = (357.528 + 0.9856003 * n)/DEG_IN_RADIAN;
  lambda = (L + 1.915 * sin(g) + 0.020 * sin(2. * g))/DEG_IN_RADIAN;
  epsilon = (23.439 - 0.0000004 * n)/DEG_IN_RADIAN;
  
  x = cos(lambda);
  y = cos(epsilon) * sin(lambda);
  z = sin(epsilon)*sin(lambda);
  
  *ra = (atan_circ(x,y))*HRS_IN_RADIAN;
  *dec = (asin(z))*DEG_IN_RADIAN;
}

// implemenataion of Jean Meeus' more accurate solar
//  ephemeris.  For ultimate use in helio correction! From
//  Astronomical Formulae for Calculators, pp. 79 ff.  This
//  gives sun's position wrt *mean* equinox of date, not
//  *apparent*.  Accuracy is << 1 arcmin.  Positions given are
//  geocentric ... parallax due to observer's position on earth is
//  ignored. This is up to 8 arcsec; routine is usually a little
//  better than that.
//         // -- topocentric correction *is* included now. -- //
//  Light travel time is apparently taken into
//  account for the ra and dec, but I don't know if aberration is
//  and I don't know if distance is simlarly antedated.
//
//  x, y, and z are heliocentric equatorial coordinates of the
//  EARTH, referred to mean equator and equinox of date. */
void accusun( double jd, double lst, double geolat,
              double *ra, double *dec, double *dist,
              double *topora, double *topodec,
              double *x, double *y, double *z) {
  double L, T, Tsq, Tcb;
  double M, e, Cent, nu, sunlong;
  double Lrad, Mrad, nurad, R;
  double A, B, C, D, E, H;
  double xtop, ytop, ztop, topodist, l, m, n, xgeo, ygeo, zgeo;
  
  jd = jd + etcorr(jd)/SEC_IN_DAY;  /* might as well do it right .... */
  T = (jd - 2415020.) / 36525.;  /* 1900 --- this is an oldish theory*/
  Tsq = T*T;
  Tcb = T*Tsq;
  L = 279.69668 + 36000.76892*T + 0.0003025*Tsq;
  M = 358.47583 + 35999.04975*T - 0.000150*Tsq - 0.0000033*Tcb;
  e = 0.01675104 - 0.0000418*T - 0.000000126*Tsq;
  
  L = circulo(L);
  M = circulo(M);
  /*      printf("raw L, M: %15.8f, %15.8f\n",L,M); */
  
  A = 153.23 + 22518.7541 * T;  /* A, B due to Venus */
  B = 216.57 + 45037.5082 * T;
  C = 312.69 + 32964.3577 * T;  /* C due to Jupiter */
  /* D -- rough correction from earth-moon
     barycenter to center of earth. */
  D = 350.74 + 445267.1142*T - 0.00144*Tsq;
  E = 231.19 + 20.20*T;    /* "inequality of long period .. */
  H = 353.40 + 65928.7155*T;  /* Jupiter. */
  
  A = circulo(A) / DEG_IN_RADIAN;
  B = circulo(B) / DEG_IN_RADIAN;
  C = circulo(C) / DEG_IN_RADIAN;
  D = circulo(D) / DEG_IN_RADIAN;
  E = circulo(E) / DEG_IN_RADIAN;
  H = circulo(H) / DEG_IN_RADIAN;
  
  L = L + 0.00134 * cos(A)
    + 0.00154 * cos(B)
    + 0.00200 * cos(C)
    + 0.00179 * sin(D)
    + 0.00178 * sin(E);
  
  Lrad = L/DEG_IN_RADIAN;
  Mrad = M/DEG_IN_RADIAN;
  
  Cent = (1.919460 - 0.004789*T -0.000014*Tsq)*sin(Mrad)
    + (0.020094 - 0.000100*T) * sin(2.0*Mrad)
    + 0.000293 * sin(3.0*Mrad);
  sunlong = L + Cent;
  
  
  nu = M + Cent;
  nurad = nu / DEG_IN_RADIAN;
  
  R = (1.0000002 * (1 - e*e)) / (1. + e * cos(nurad));
  R = R + 0.00000543 * sin(A)
    + 0.00001575 * sin(B)
    + 0.00001627 * sin(C)
    + 0.00003076 * cos(D)
    + 0.00000927 * sin(H);
  /*      printf("solar longitude: %10.5f  Radius vector %10.7f\n",sunlong,R);
          printf("eccentricity %10.7f  eqn of center %10.5f\n",e,Cent);   */
  
  sunlong = sunlong/DEG_IN_RADIAN;
  
  *dist = R;
  *x = cos(sunlong);  /* geocentric */
  *y = sin(sunlong);
  *z = 0.;
  eclrot(jd, x, y, z);
  
  /*      --- code to include topocentric correction for sun .... */
  
  geocent(lst,geolat,0.,&xgeo,&ygeo,&zgeo);
  
  xtop = *x - xgeo*EQUAT_RAD/ASTRO_UNIT;
  ytop = *y - ygeo*EQUAT_RAD/ASTRO_UNIT;
  ztop = *z - zgeo*EQUAT_RAD/ASTRO_UNIT;
  
  topodist = sqrt(xtop*xtop + ytop*ytop + ztop*ztop);
  
  l = xtop / (topodist);
  m = ytop / (topodist);
  n = ztop / (topodist);
  
  *topora = atan_circ(l,m) * HRS_IN_RADIAN;
  *topodec = asin(n) * DEG_IN_RADIAN;
  
  *ra = atan_circ(*x,*y) * HRS_IN_RADIAN;
  *dec = asin(*z) * DEG_IN_RADIAN;
  
  *x = *x * R * -1;  /* heliocentric */
  *y = *y * R * -1;
  *z = *z * R * -1;
}

// More accurate (but more elaborate and slower) lunar
//   ephemeris, from Jean Meeus' *Astronomical Formulae For Calculators*,
//   pub. Willman-Bell.  Includes all the terms given there.
// jd, dec. degr., dec. hrs., meters */
void accumoon( double jd, double geolat, double lst, double elevsea,
               double *geora, double *geodec, double *geodist,
               double *topora, double *topodec, double *topodist) {
  double pie, dist;  /* horiz parallax */
  double Lpr,M,Mpr,D,F,Om,T,Tsq,Tcb;
  double e,lambda,B,beta,om1,om2;
  double sinx, x, y, z, l, m, n;
  double x_geo, y_geo, z_geo;  /* geocentric position of *observer* */

  jd = jd + etcorr(jd)/SEC_IN_DAY;   /* approximate correction to ephemeris time */
  T = (jd - 2415020.) / 36525.;   /* this based around 1900 ... */
  Tsq = T * T;
  Tcb = Tsq * T;
  
  Lpr = 270.434164 + 481267.8831 * T - 0.001133 * Tsq
    + 0.0000019 * Tcb;
  M = 358.475833 + 35999.0498*T - 0.000150*Tsq
    - 0.0000033*Tcb;
  Mpr = 296.104608 + 477198.8491*T + 0.009192*Tsq
    + 0.0000144*Tcb;
  D = 350.737486 + 445267.1142*T - 0.001436 * Tsq
    + 0.0000019*Tcb;
  F = 11.250889 + 483202.0251*T -0.003211 * Tsq
    - 0.0000003*Tcb;
  Om = 259.183275 - 1934.1420*T + 0.002078*Tsq
    + 0.0000022*Tcb;
  
  Lpr = circulo(Lpr);
  Mpr = circulo(Mpr);
  M = circulo(M);
  D = circulo(D);
  F = circulo(F);
  Om = circulo(Om);
  
  
  sinx =  sin((51.2 + 20.2 * T)/DEG_IN_RADIAN);
  Lpr = Lpr + 0.000233 * sinx;
  M = M - 0.001778 * sinx;
  Mpr = Mpr + 0.000817 * sinx;
  D = D + 0.002011 * sinx;
  
  sinx = 0.003964 * sin((346.560+132.870*T -0.0091731*Tsq)/DEG_IN_RADIAN);
  
  Lpr = Lpr + sinx;
  Mpr = Mpr + sinx;
  D = D + sinx;
  F = F + sinx;
  
  
  sinx = sin(Om/DEG_IN_RADIAN);
  Lpr = Lpr + 0.001964 * sinx;
  Mpr = Mpr + 0.002541 * sinx;
  D = D + 0.001964 * sinx;
  F = F - 0.024691 * sinx;
  F = F - 0.004328 * sin((Om + 275.05 -2.30*T)/DEG_IN_RADIAN);

  e = 1 - 0.002495 * T - 0.00000752 * Tsq;

  M = M / DEG_IN_RADIAN;   /* these will all be arguments ... */
  Mpr = Mpr / DEG_IN_RADIAN;
  D = D / DEG_IN_RADIAN;
  F = F / DEG_IN_RADIAN;

  lambda = Lpr + 6.288750 * sin(Mpr)
    + 1.274018 * sin(2*D - Mpr)
    + 0.658309 * sin(2*D)
    + 0.213616 * sin(2*Mpr)
    - e * 0.185596 * sin(M)
    - 0.114336 * sin(2*F)
    + 0.058793 * sin(2*D - 2*Mpr)
    + e * 0.057212 * sin(2*D - M - Mpr)
    + 0.053320 * sin(2*D + Mpr)
    + e * 0.045874 * sin(2*D - M)
    + e * 0.041024 * sin(Mpr - M)
    - 0.034718 * sin(D)
    - e * 0.030465 * sin(M+Mpr)
    + 0.015326 * sin(2*D - 2*F)
    - 0.012528 * sin(2*F + Mpr)
    - 0.010980 * sin(2*F - Mpr)
    + 0.010674 * sin(4*D - Mpr)
    + 0.010034 * sin(3*Mpr)
    + 0.008548 * sin(4*D - 2*Mpr)
    - e * 0.007910 * sin(M - Mpr + 2*D)
    - e * 0.006783 * sin(2*D + M)
    + 0.005162 * sin(Mpr - D);

  /* And furthermore.....*/

  lambda = lambda + e * 0.005000 * sin(M + D)
    + e * 0.004049 * sin(Mpr - M + 2*D)
    + 0.003996 * sin(2*Mpr + 2*D)
    + 0.003862 * sin(4*D)
    + 0.003665 * sin(2*D - 3*Mpr)
    + e * 0.002695 * sin(2*Mpr - M)
    + 0.002602 * sin(Mpr - 2*F - 2*D)
    + e * 0.002396 * sin(2*D - M - 2*Mpr)
    - 0.002349 * sin(Mpr + D)
    + e * e * 0.002249 * sin(2*D - 2*M)
    - e * 0.002125 * sin(2*Mpr + M)
    - e * e * 0.002079 * sin(2*M)
    + e * e * 0.002059 * sin(2*D - Mpr - 2*M)
    - 0.001773 * sin(Mpr + 2*D - 2*F)
    - 0.001595 * sin(2*F + 2*D)
    + e * 0.001220 * sin(4*D - M - Mpr)
    - 0.001110 * sin(2*Mpr + 2*F)
    + 0.000892 * sin(Mpr - 3*D)
    - e * 0.000811 * sin(M + Mpr + 2*D)
    + e * 0.000761 * sin(4*D - M - 2*Mpr)
    + e * e * 0.000717 * sin(Mpr - 2*M)
    + e * e * 0.000704 * sin(Mpr - 2 * M - 2*D)
    + e * 0.000693 * sin(M - 2*Mpr + 2*D)
    + e * 0.000598 * sin(2*D - M - 2*F)
    + 0.000550 * sin(Mpr + 4*D)
    + 0.000538 * sin(4*Mpr)
    + e * 0.000521 * sin(4*D - M)
    + 0.000486 * sin(2*Mpr - D);

  /*              *eclongit = lambda;  */

  B = 5.128189 * sin(F)
    + 0.280606 * sin(Mpr + F)
    + 0.277693 * sin(Mpr - F)
    + 0.173238 * sin(2*D - F)
    + 0.055413 * sin(2*D + F - Mpr)
    + 0.046272 * sin(2*D - F - Mpr)
    + 0.032573 * sin(2*D + F)
    + 0.017198 * sin(2*Mpr + F)
    + 0.009267 * sin(2*D + Mpr - F)
    + 0.008823 * sin(2*Mpr - F)
    + e * 0.008247 * sin(2*D - M - F)
    + 0.004323 * sin(2*D - F - 2*Mpr)
    + 0.004200 * sin(2*D + F + Mpr)
    + e * 0.003372 * sin(F - M - 2*D)
    + 0.002472 * sin(2*D + F - M - Mpr)
    + e * 0.002222 * sin(2*D + F - M)
    + e * 0.002072 * sin(2*D - F - M - Mpr)
    + e * 0.001877 * sin(F - M + Mpr)
    + 0.001828 * sin(4*D - F - Mpr)
    - e * 0.001803 * sin(F + M)
    - 0.001750 * sin(3*F)
    + e * 0.001570 * sin(Mpr - M - F)
    - 0.001487 * sin(F + D)
    - e * 0.001481 * sin(F + M + Mpr)
    + e * 0.001417 * sin(F - M - Mpr)
    + e * 0.001350 * sin(F - M)
    + 0.001330 * sin(F - D)
    + 0.001106 * sin(F + 3*Mpr)
    + 0.001020 * sin(4*D - F)
    + 0.000833 * sin(F + 4*D - Mpr);
  /* not only that, but */
  B = B + 0.000781 * sin(Mpr - 3*F)
    + 0.000670 * sin(F + 4*D - 2*Mpr)
    + 0.000606 * sin(2*D - 3*F)
    + 0.000597 * sin(2*D + 2*Mpr - F)
    + e * 0.000492 * sin(2*D + Mpr - M - F)
    + 0.000450 * sin(2*Mpr - F - 2*D)
    + 0.000439 * sin(3*Mpr - F)
    + 0.000423 * sin(F + 2*D + 2*Mpr)
    + 0.000422 * sin(2*D - F - 3*Mpr)
    - e * 0.000367 * sin(M + F + 2*D - Mpr)
    - e * 0.000353 * sin(M + F + 2*D)
    + 0.000331 * sin(F + 4*D)
    + e * 0.000317 * sin(2*D + F - M + Mpr)
    + e * e * 0.000306 * sin(2*D - 2*M - F)
    - 0.000283 * sin(Mpr + 3*F);


  om1 = 0.0004664 * cos(Om/DEG_IN_RADIAN);
  om2 = 0.0000754 * cos((Om + 275.05 - 2.30*T)/DEG_IN_RADIAN);

  beta = B * (1. - om1 - om2);
  /*      *eclatit = beta; */

  pie = 0.950724
    + 0.051818 * cos(Mpr)
    + 0.009531 * cos(2*D - Mpr)
    + 0.007843 * cos(2*D)
    + 0.002824 * cos(2*Mpr)
    + 0.000857 * cos(2*D + Mpr)
    + e * 0.000533 * cos(2*D - M)
    + e * 0.000401 * cos(2*D - M - Mpr)
    + e * 0.000320 * cos(Mpr - M)
    - 0.000271 * cos(D)
    - e * 0.000264 * cos(M + Mpr)
    - 0.000198 * cos(2*F - Mpr)
    + 0.000173 * cos(3*Mpr)
    + 0.000167 * cos(4*D - Mpr)
    - e * 0.000111 * cos(M)
    + 0.000103 * cos(4*D - 2*Mpr)
    - 0.000084 * cos(2*Mpr - 2*D)
    - e * 0.000083 * cos(2*D + M)
    + 0.000079 * cos(2*D + 2*Mpr)
    + 0.000072 * cos(4*D)
    + e * 0.000064 * cos(2*D - M + Mpr)
    - e * 0.000063 * cos(2*D + M - Mpr)
    + e * 0.000041 * cos(M + D)
    + e * 0.000035 * cos(2*Mpr - M)
    - 0.000033 * cos(3*Mpr - 2*D)
    - 0.000030 * cos(Mpr + D)
    - 0.000029 * cos(2*F - 2*D)
    - e * 0.000029 * cos(2*Mpr + M)
    + e * e * 0.000026 * cos(2*D - 2*M)
    - 0.000023 * cos(2*F - 2*D + Mpr)
    + e * 0.000019 * cos(4*D - M - Mpr);

  beta = beta/DEG_IN_RADIAN;
  lambda = lambda/DEG_IN_RADIAN;
  l = cos(lambda) * cos(beta);
  m = sin(lambda) * cos(beta);
  n = sin(beta);
  eclrot(jd,&l,&m,&n);

  dist = 1/sin((pie)/DEG_IN_RADIAN);
  x = l * dist;
  y = m * dist;
  z = n * dist;

  *geora = atan_circ(l,m) * HRS_IN_RADIAN;
  *geodec = asin(n) * DEG_IN_RADIAN;
  *geodist = dist;

  geocent(lst,geolat,elevsea,&x_geo,&y_geo,&z_geo);

  x = x - x_geo;  /* topocentric correction using elliptical earth fig. */
  y = y - y_geo;
  z = z - z_geo;

  *topodist = sqrt(x*x + y*y + z*z);

  l = x / (*topodist);
  m = y / (*topodist);
  n = z / (*topodist);

  *topora = atan_circ(l,m) * HRS_IN_RADIAN;
  *topodec = asin(n) * DEG_IN_RADIAN;
}

// computes minimum and maximum altitude for a given dec and
// latitude.
void min_max_alt( double lat, double dec,
                  double *min, double *max) {
  double x;

  lat = lat / DEG_IN_RADIAN; /* pass by value! */
  dec = dec / DEG_IN_RADIAN;
  x = cos(dec)*cos(lat) + sin(dec)*sin(lat);
  if(fabs(x) <= 1.) {
    *max = asin(x) * DEG_IN_RADIAN;
  }
  else fprintf(stderr,"Error in min_max_alt -- arcsin(>1)\n");
  x = sin(dec)*sin(lat) - cos(dec)*cos(lat);
  if(fabs(x) <= 1.) {
    *min = asin(x) * DEG_IN_RADIAN;
  }
  else fprintf(stderr,"Error in min_max_alt -- arcsin(>1)\n");
}

// returns altitude(degr) for dec, ha, lat (decimal degr, hr, degr);
//   also computes and returns azimuth through pointer argument,
//   and as an extra added bonus returns parallactic angle (decimal degr)
//   through another pointer argument.
double altit(double dec, double ha, double lat,
             double *az, double *parang) {
  double x,y,z;
  double sinp, cosp;  /* sin and cos of parallactic angle */
  double cosdec, sindec, cosha, sinha, coslat, sinlat;
  /* time-savers ... */
  
  dec = dec / DEG_IN_RADIAN;
  ha = ha / HRS_IN_RADIAN;
  lat = lat / DEG_IN_RADIAN;  /* thank heavens for pass-by-value */
  cosdec = cos(dec); sindec = sin(dec);
  cosha = cos(ha); sinha = sin(ha);
  coslat = cos(lat); sinlat = sin(lat);
  x = DEG_IN_RADIAN * asin(cosdec*cosha*coslat + sindec*sinlat);
  y =  sindec*coslat - cosdec*cosha*sinlat; /* due N comp. */
  z =  -1. * cosdec*sinha; /* due east comp. */
  *az = atan2(z,y);
  
  /* as it turns out, having knowledge of the altitude and
     azimuth makes the spherical trig of the parallactic angle
     less ambiguous ... so do it here!  Method uses the
     "astronomical triangle" connecting celestial pole, object,
     and zenith ... now know all the other sides and angles,
     so we can crush it ... */
  
  if(cosdec != 0.) { /* protect divide by zero ... */
    sinp = -1. * sin(*az) * coslat / cosdec;
    /* spherical law of sines .. note cosdec = sin of codec,
       coslat = sin of colat .... */
    cosp = -1. * cos(*az) * cosha - sin(*az) * sinha * sinlat;
    /* spherical law of cosines ... also transformed to local
       available variables. */
    *parang = atan2(sinp,cosp) * DEG_IN_RADIAN;
    /* let the library function find the quadrant ... */
  }
  else { /* you're on the pole */
    if(lat >= 0.) *parang = 180.;
    else *parang = 0.;
  }
  
  *az *= DEG_IN_RADIAN;  /* done with taking trig functions of it ... */
  while(*az < 0.) *az += 360.;  /* force 0 -> 360 */
  while(*az >= 360.) *az -= 360.;
  
  return(x);
}

// returns hour angle at which object at dec is at altitude alt.
//  If object is never at this altitude, signals with special
//  return values 1000 (always higher) and -1000 (always lower).
double ha_alt(double dec, double lat, double alt) {
  double x,coalt,min,max;

  min_max_alt(lat,dec,&min,&max);
  if(alt < min)
    return(1000.);  /* flag value - always higher than asked */
  if(alt > max)
    return(-1000.); /* flag for object always lower than asked */
  dec = PI_OVER_2 - dec / DEG_IN_RADIAN;
  lat = PI_OVER_2 - lat / DEG_IN_RADIAN;
  coalt = PI_OVER_2 - alt / DEG_IN_RADIAN;
  x = (cos(coalt) - cos(dec)*cos(lat)) / (sin(dec)*sin(lat));
  if(fabs(x) <= 1.) return(acos(x) * HRS_IN_RADIAN);
  else {
    fprintf(stderr,"Error in ha_alt ... acos(>1).\n");
    return(1000.);
  }
}

// returns jd at which sun is at a given
//  altitude, given jdguess as a starting point. Uses
//  low-precision sun, which is plenty good enough.
double jd_sun_alt( double alt, double jdguess, double lat, double longit) {
  double jdout;
  double deriv, err, del = 0.002;
  double ra,dec,ha,alt2,alt3,az,par;
  short i = 0;
  
  /* first guess */
  lpsun(jdguess,&ra,&dec);
  ha = lst(jdguess,longit) - ra;
  alt2 = altit(dec,ha,lat,&az,&par);
  jdguess = jdguess + del;
  lpsun(jdguess,&ra,&dec);
  alt3 = altit(dec,(lst(jdguess,longit) - ra),lat,&az,&par);
  err = alt3 - alt;
  deriv = (alt3 - alt2) / del;
  while((fabs(err) > 0.1) && (i < 10)) {
    jdguess = jdguess - err/deriv;
    lpsun(jdguess,&ra,&dec);
    alt3 = altit(dec,(lst(jdguess,longit) - ra),lat,&az,&par);
    err = alt3 - alt;
    i++;
    if(i == 9) fprintf(stderr,
                       "Sunrise, set, or twilight calculation not converging!\n");
  }
  if(i >= 9) jdguess = -1000.;
  jdout = jdguess;
  return(jdout);
}

// angle subtended by two positions in the sky --
//   return value is in radians.  Hybrid algorithm works down
//   to zero separation except very near the poles. */
// args in dec hrs and dec degrees
double subtend( double ra1, double dec1, double ra2, double dec2) {
  double x1, y1, z1, x2, y2, z2;
  double theta;
  
  ra1 = ra1 / HRS_IN_RADIAN;
  dec1 = dec1 / DEG_IN_RADIAN;
  ra2 = ra2 / HRS_IN_RADIAN;
  dec2 = dec2 / DEG_IN_RADIAN;
  x1 = cos(ra1)*cos(dec1);
  y1 = sin(ra1)*cos(dec1);
  z1 = sin(dec1);
  x2 = cos(ra2)*cos(dec2);
  y2 = sin(ra2)*cos(dec2);
  z2 = sin(dec2);
  theta = acos(x1*x2+y1*y2+z1*z2);
  /* use flat Pythagorean approximation if the angle is very small
   *and* you're not close to the pole; avoids roundoff in arccos. */
  if(theta < 1.0e-5) {  /* seldom the case, so don't combine test */
    if(fabs(dec1) < (PI_OVER_2 - 0.001) &&
       fabs(dec2) < (PI_OVER_2 - 0.001))    {
      /* recycled variables here... */
      x1 = (ra2 - ra1) * cos((dec1+dec2)/2.);
      x2 = dec2 - dec1;
      theta = sqrt(x1*x1 + x2*x2);
    }
  }
  return(theta);
}

// adjusts a time (decimal hours) to be between -12 and 12,
//  generally used for hour angles.
double adj_time(double x) {
  if(fabs(x) < 100000.) {  /* too inefficient for this! */
    while(x > 12.) {
      x = x - 24.;
    }
    while(x < -12.) {
      x = x + 24.;
    }
  }
  else fprintf(stderr,"Out of bounds in adj_time!\n");
  return(x);
}

// Computes the secant of z, assuming the object is not
//  too low to the horizon; returns 100. if the object is
//  low but above the horizon, -100. if the object is just
//  below the horizon.
double secant_z(double alt) {
  double secz;
  if(alt != 0) secz = 1. / sin(alt / DEG_IN_RADIAN);
  else secz = 100.;
  if(secz > 100.) secz = 100.;
  if(secz < -100.) secz = -100.;
  return(secz);
}

// returns the true airmass for a given secant z. */
// The expression used is based on a tabulation of the mean KPNO
//  atmosphere given by C. M. Snell & A. M. Heiser, 1968,
//  PASP, 80, 336.  They tabulated the airmass at 5 degr
//  intervals from z = 60 to 85 degrees; I fit the data with
//  a fourth order poly for (secz - airmass) as a function of
//  (secz - 1) using the IRAF curfit routine, then adjusted the
//  zeroth order term to force (secz - airmass) to zero at
//  z = 0.  The poly fit is very close to the tabulated points
//  (largest difference is 3.2e-4) and appears smooth.
//  This 85-degree point is at secz = 11.47, so for secz > 12
//  I just return secz - 1.5 ... about the largest offset
//  properly determined. */
double true_airmass(double secz) {
  double seczmin1;
  int i, ord = 4;
  double coef[5];
  double result = 0;
  
  coef[1] = 2.879465E-3;  /* sun compilers do not allow automatic
                             initializations of arrays. */
  coef[2] = 3.033104E-3;
  coef[3] = 1.351167E-3;
  coef[4] = -4.716679E-5;
  if(secz < 0.) return(-1.);  /* out of range. */
  if(secz > 12) return (secz - 1.5);  /* shouldn't happen .... */
  seczmin1 = secz - 1.;
  /* evaluate polynomial ... */
  for(i = ord; i > 0; i--)
    result = (result + coef[i]) * seczmin1;
  /* no zeroth order term. */
  result = secz - result;
  return(result);
}

// Evaluates predicted LUNAR part of sky brightness, in
//   V magnitudes per square arcsecond, following K. Krisciunas
//   and B. E. Schaeffer (1991) PASP 103, 1033.
//
//   alpha = separation of sun and moon as seen from earth,
//   converted internally to its supplement,
//   rho = separation of moon and object,
//   kzen = zenith extinction coefficient,
//   altmoon = altitude of moon above horizon,
//   alt = altitude of object above horizon
//   moondist = distance to moon, in earth radii
//
//   all are in decimal degrees.
//
//   MODIFIED: (pap) to return brightness in nanolamberts
double lunskybright( double alpha, double rho, double kzen,
                     double altmoon, double alt,  double moondist) {
  double istar,Xzm,Xo,Z,Zmoon,Bmoon,fofrho,rho_rad,test;
  
  rho_rad = rho/DEG_IN_RADIAN;
  alpha = (180. - alpha);
  Zmoon = (90. - altmoon)/DEG_IN_RADIAN;
  Z = (90. - alt)/DEG_IN_RADIAN;

  moondist = moondist/(60.27);  /* divide by mean distance */
  
  // illuminance of moon
  istar = -0.4*(3.84 + 0.026*fabs(alpha) + 4.0e-9*pow(alpha,4.)); /*eqn 20*/
  istar =  pow(10.,istar)/(moondist * moondist);

  /* crude accounting for opposition effect 
     35 per cent brighter at full, effect tapering linearly to
     zero at 7 degrees away from full. mentioned peripherally in
     Krisciunas and Scheafer, p. 1035. */
  if(fabs(alpha) < 7.)
    istar = istar * (1.35 - 0.05 * fabs(istar));

  // Rayleigh scattering
  fofrho = 229087.0 * (1.06 + cos(rho_rad)*cos(rho_rad));

  // Mie scattering
  if(fabs(rho) > 10.)
    fofrho = fofrho + pow(10.,(6.15 - rho/40.));            /* eqn 21 */
  else if (fabs(rho) > 0.25)
    fofrho = fofrho + 6.2e7 / (rho*rho);   /* eqn 19 */
  else fofrho = fofrho + 9.9e8;  /*for 1/4 degree -- radius of moon! */

  // optical pathlength
  Xzm = sqrt(1.0 - 0.96*sin(Zmoon)*sin(Zmoon));
  if(Xzm != 0.) Xzm = 1./Xzm;
  else Xzm = 10000.;
  Xo = sqrt(1.0 - 0.96*sin(Z)*sin(Z));
  if(Xo != 0.) Xo = 1./Xo;
  else Xo = 10000.;

  // Moon brightness
  Bmoon = fofrho * istar * pow(10.,(-0.4*kzen*Xzm))
    * (1. - pow(10.,(-0.4*kzen*Xo)));   /* nanoLamberts */

  // return brightness is nanoLamberts
  return(Bmoon);

  //  if(Bmoon > 0.001)
  //    return(22.50 - 1.08574 * log(Bmoon/34.08)); /* V mag per sq arcs-eqn 1 */
  //  else return(99.);
}

// ----------------------------------------------------------------------------
// -----------------  my stuff begins here ------------------------------------
// ----------------------------------------------------------------------------

// angle subtended by two positions in the sky --
//  return value is in radians.  Hybrid algorithm works down
//  to zero separation except very near the poles.
// copy of subtend above, but for args in radians
double subtendRad(double ra1, double dec1, double ra2, double dec2) {
  double x1, y1, z1, x2, y2, z2;
  double theta;

  x1 = cos(ra1)*cos(dec1);
  y1 = sin(ra1)*cos(dec1);
  z1 = sin(dec1);
  x2 = cos(ra2)*cos(dec2);
  y2 = sin(ra2)*cos(dec2);
  z2 = sin(dec2);
  theta = acos(x1*x2+y1*y2+z1*z2);
  /* use flat Pythagorean approximation if the angle is very small
   *and* you're not close to the pole; avoids roundoff in arccos. */
  if(theta < 1.0e-5) {  /* seldom the case, so don't combine test */
    if(fabs(dec1) < (PI_OVER_2 - 0.001) &&
       fabs(dec2) < (PI_OVER_2 - 0.001))    {
      /* recycled variables here... */
      x1 = (ra2 - ra1) * cos((dec1+dec2)/2.);
      x2 = dec2 - dec1;
			theta = sqrt(x1*x1 + x2*x2);
    }
  }
  return(theta);
}


// get the date from the MJD
struct date_time mjd_to_date(double mjd) {
  double jd;
  struct date_time date;
  short dow;

  // convert MJD to JD. Note JD starts at noon, MJD starts at midnight before
  jd = mjd + 2400000.5;
  caldat(jd, &date, &dow);
  return date;
}

// get the mjd from a date struct
double date_to_mjd(struct date_time date) {
  double jd;

  jd = date_to_jd(date);
  return(jd - 2400000.5);
}

// get the mjd of the previous noon, local time
double mjdPrevNoon(double mjd) {
  struct date_time date;
  short dow;
  double jd;

  jd = mjd + 2400000.5;
  jd = jd - tz/24.0;     // "local" jd
  caldat(jd, &date, &dow);
  date.h = 12.0;         // local noon
  date.mn = 1;           // one minute past for explicitness on the day
  date.s = 0;
  jd = date_to_jd(date); // we now have the local JD of afternoon
  return jd - 2400000.5;
}

// get the sun RA,DEC in radians (-PI,PI) (-PI/2,PI/2) from mjd
void sunPosition(double mjd, double *sunra, double *sundec) {
  double jd, lstm, ra, dec, dist, topora, topodec, x, y, z;

  jd = mjd + 2400000.5;
  lstm = lst(jd,longitude_hrs); // need west longitude here, gives mean lst
  accusun(jd,lstm,latitude_deg,
          &ra, &dec, &dist, &topora, &topodec, &x, &y, &z);

  *sunra = ra / HRS_IN_RADIAN;
  *sundec = dec / DEG_IN_RADIAN;
}


double mysubtend( double ra1, double dec1, double ra2, double dec2) {
  double x1, y1, z1, x2, y2, z2;
  double theta;
  double q3;
  
  ra1 = ra1 / HRS_IN_RADIAN;
  dec1 = dec1 / DEG_IN_RADIAN;
  ra2 = ra2 / HRS_IN_RADIAN;
  dec2 = dec2 / DEG_IN_RADIAN;
  x1 = cos(ra1)*cos(dec1);
  y1 = sin(ra1)*cos(dec1);
  z1 = sin(dec1);
  x2 = cos(ra2)*cos(dec2);
  y2 = sin(ra2)*cos(dec2);
  z2 = sin(dec2);
  theta = acos(x1*x2+y1*y2+z1*z2);
  q3 = x1*y2-x2*y1;

  /* use flat Pythagorean approximation if the angle is very small
   *and* you're not close to the pole; avoids roundoff in arccos. */
  if(theta < 1.0e-5) {  /* seldom the case, so don't combine test */
    if(fabs(dec1) < (PI_OVER_2 - 0.001) &&
       fabs(dec2) < (PI_OVER_2 - 0.001))    {
      /* recycled variables here... */
      x1 = (ra2 - ra1) * cos((dec1+dec2)/2.);
      x2 = dec2 - dec1;
      theta = sqrt(x1*x1 + x2*x2);
    }
  }
  if(q3<0.0) theta = -theta;
  return(theta);
}

// get the moon ra, dec in radians (-PI,PI) (-PI/2,PI/2)
// also get altitude above horizon (radians), and percent illumination
// from mjd and goegraphic position
void moonData(double mjd,
              double *moonra, double *moondec,
              double *moonalt, double *moonill, double *moonphase) {
  double jd, lstm, georamoon, geodecmoon, geodistmoon;
  double ramoon, decmoon, distmoon;
  double rasun, decsun, distsun, toporasun, topodecsun, x, y, z;
  double alt, sun_moon, az, par;
  double sign;
  
  jd = mjd + 2400000.5;
  lstm = lst(jd,longitude_hrs); // need west longitude here, gives mean lst
  accumoon(jd,lstm,latitude_deg,elev_meters,
           &georamoon,&geodecmoon,&geodistmoon,
           &ramoon,&decmoon,&distmoon);
  adj_time(ramoon);
  *moonra = ramoon / HRS_IN_RADIAN;
  *moondec = decmoon / DEG_IN_RADIAN;
  accusun(jd,lstm,latitude_deg,&rasun,&decsun,&distsun,
		&toporasun,&topodecsun,&x,&y,&z);
  alt=altit(topodecsun,(lstm-toporasun),latitude_deg,&az,&par);
  sun_moon = mysubtend(ramoon,decmoon,toporasun,topodecsun);
  *moonill = 0.5*(1.-cos(sun_moon));
  if(sun_moon<0.0) {
    *moonphase = 0.5*(*moonill);
  }
  else {
    *moonphase = 0.5 + 0.5*(1.0-(*moonill));
  }
  *moonalt=altit(decmoon,(lstm-ramoon),latitude_deg,&az,&par) / DEG_IN_RADIAN;
}

double skyBrightness(double mjd, double objra, double objdec,
                     double extinction, double skyBrightness) {
  double jd, lstm, georamoon, geodecmoon, geodistmoon;
  double ramoon, decmoon, distmoon, rasun, decsun, distsun;
  double toporasun, topodecsun, x, y, z;
  double sun_moon, moon_obj, moonalt, objalt, result, az, par;
  double moonbr, objzd, skybr, Msky, Xzm;

  // first get sky brightness from moon
  objra *= HRS_IN_RADIAN;
  objdec *= DEG_IN_RADIAN;
  jd = mjd + 2400000.5;
  lstm = lst(jd,longitude_hrs); // need west longitude here, gives mean lst
  accumoon(jd,lstm,latitude_deg,elev_meters,
           &georamoon,&geodecmoon,&geodistmoon,
           &ramoon,&decmoon,&distmoon);
  accusun(jd,lstm,latitude_deg,&rasun,&decsun,&distsun,
		&toporasun,&topodecsun,&x,&y,&z);
  sun_moon = subtend(ramoon,decmoon,toporasun,topodecsun);
  moon_obj = subtend(ramoon,decmoon,objra,objdec);
  moonalt = altit(decmoon,(lstm-ramoon),latitude_deg,&az,&par);
  objalt = altit(objdec,(lstm-objra),latitude_deg,&az,&par);
  objzd = 90.0 - objalt;
  if((moonalt>0.0) && (objalt>0.5)) {
    moonbr = lunskybright(sun_moon, moon_obj, extinction, moonalt, objalt, distmoon);
  }
  else
    moonbr = 0.0;

  printf("       lst: %f\n", lstm);
  printf("object alt: %f\n", objalt/DEG_IN_RADIAN); 
  printf("  moon alt: %f\n", moonalt/DEG_IN_RADIAN); 

  // compute dark sky brightness at objzd in nanolamberts
  skybr = 34.08*exp(20.7233 - 0.92104 * skyBrightness);

  // optical pathlength
  Xzm = sqrt(1.0 - 0.96*sin(objzd)*sin(objzd));
  if(Xzm != 0.) Xzm = 1./Xzm;
  else Xzm = 10000.;
  skybr *= Xzm * pow(10.0,-0.4 * extinction * (Xzm - 1.0));

  // add this to the brightness from the moon
  //  skybr += moonbr;

  // and convert to mag/arcsec^2
  Msky = (1. / 0.92104) * log (34.08 * exp (20.7233) / skybr);


  return(Msky);
}

// get the airmass secz from the mjd and object ra/dec in radians
void airmass(double mjd, double objra, double objdec,
             double *trueam, double *alt, double *retha) {
  double jd, lstm, ha, secz, az, par;

  objra *= HRS_IN_RADIAN;
  objdec *= DEG_IN_RADIAN;

  jd = mjd + 2400000.5;
  lstm = lst(jd,longitude_hrs); // need west longitude here, gives mean lst
  ha = adj_time(lstm-objra);
  *alt = altit(objdec,ha,latitude_deg,&az,&par);
  secz = secant_z(*alt);
  // don't overflow in airmass
  if(secz >= 0.0)
    if(secz < 12.0)
      *trueam = true_airmass(secz);
    else
      *trueam = secz;
  else
    *trueam = -1.0;  // object below horizon

  *retha = ha;
}

// get the time (in mjd) of sunrise/sunset, astronomical twilight at
// beginning and ending of the night, and the RA which is
// at the local meridian at the twilight times from the mjd
// and geographic data
void twilightparms(double mjd, double *mjdsunrise, double *mjdsunset,
                   double *mjdtwibeg, double *mjdtwiend,
                   double *mjdnautbeg, double *mjdnautend,
                   double *ratwbeg, double *ratwend,
                   double *sunRA) {

  struct date_time date;
  short dow;
  double jd, jdmid, rasun, decsun, hatwilight,jdtwilight;
  double jdeveningtwilight, jdmorningtwilight, lstm, stmid;
  double hasunset, hasunrise, jdsunset, jdsunrise, jdtwiend, jdtwibeg;

#if 0
  jd = mjd + 2400000.5;
  jd = jd - tz/24.0;     // "local" jd
  caldat(jd, &date, &dow);
  date.h = 18.0;         // local afternoon
  date.mn = 0;
  date.s = 0;
  jd = date_to_jd(date); // we now have the local JD of afternoon
  jd = jd + 0.25;        // jd of local midnight
  jdmid = jd + tz/24.0;  // true jd of midnight (UT)
#else
  // we need to get the midnight closest to the given date
  // if local morning, the jd of the previous midnight
  // if local afternoon, the jd of the next midnight
  jd = mjd + 2400000.5;
  jd = jd - tz/24.0;     // "local" jd
  caldat(jd, &date, &dow);
  if(date.h<12.0) {
    jd = jd - 1.0;
    caldat(jd, &date, &dow);
  }
  date.h = 18.0;         // local afternoon
  date.mn = 0;
  date.s = 0;
  jd = date_to_jd(date); // we now have the local JD of afternoon
  jd = jd + 0.25;        // jd of local midnight
  jdmid = jd + tz/24.0;  // true jd of midnight (UT)
#endif
  stmid = lst(jdmid,longitude_hrs);
  lpsun(jdmid,&rasun,&decsun);
  *sunRA = adj_time(rasun) / HRS_IN_RADIAN;

  // sunset 
  hasunset = ha_alt(decsun,latitude_deg,-(0.83+horiz));
  jdsunset = jdmid + adj_time(rasun+hasunset-stmid)/24.; /* initial guess */
  jdsunset = jd_sun_alt(-(0.83+horiz),jdsunset,latitude_deg,longitude_hrs);
  *mjdsunset = jdsunset - 2400000.5;

  // sunrise the following day
  jdsunrise = jdmid + adj_time(rasun-hasunset-stmid)/24.;
  jdsunrise = jd_sun_alt(-(0.83+horiz),jdsunrise,latitude_deg,longitude_hrs);
  *mjdsunrise = jdsunrise - 2400000.5;
  
  // 18 degree twilight evening and subsequent morning
  hatwilight = ha_alt(decsun,latitude_deg,-18.);
  jdtwilight = jdmid + adj_time(rasun+hatwilight-stmid)/24.;
  jdtwibeg = jd_sun_alt(-18.,jdtwilight,latitude_deg,longitude_hrs);
  *mjdtwibeg = jdtwibeg - 2400000.5;

  jdtwilight = jdmid + adj_time(rasun-hatwilight-stmid)/24.;
  jdtwiend = jd_sun_alt(-18.,jdtwilight,latitude_deg,longitude_hrs);
  *mjdtwiend = jdtwiend - 2400000.5;

  // ra's overhead at twilight boundaries
  // the lst of twilight is the ra at the meridian at that time
  *ratwbeg = lst(jdtwibeg,longitude_hrs);
  *ratwbeg = adj_time(*ratwbeg) / HRS_IN_RADIAN;
  *ratwend = lst(jdtwiend,longitude_hrs);
  *ratwend = adj_time(*ratwend) / HRS_IN_RADIAN;

  // 12 degree twilight evening and subsequent morning
#define NAUTANG (-12.0)
  hatwilight = ha_alt(decsun,latitude_deg,NAUTANG);
  jdtwilight = jdmid + adj_time(rasun+hatwilight-stmid)/24.;
  jdtwibeg = jd_sun_alt(NAUTANG,jdtwilight,latitude_deg,longitude_hrs);
  *mjdnautbeg = jdtwibeg - 2400000.5;

  jdtwilight = jdmid + adj_time(rasun-hatwilight-stmid)/24.;
  jdtwiend = jd_sun_alt(NAUTANG,jdtwilight,latitude_deg,longitude_hrs);
  *mjdnautend = jdtwiend - 2400000.5;
#undef NAUTANG

}

void setUpSiteData(double latdeg, double longdeg, double elev, double tzw) {
  // set site global vars
  latitude_deg = latdeg;
  longitude_hrs = -longdeg / 15.0;
  elev_meters = elev;
  horiz = sqrt(2. * elev_meters / EQUAT_RAD) * DEG_IN_RADIAN;
  tz = tzw;
}  

void printDate(double mjd, double tz) {
  struct date_time date;

  date = mjd_to_date(mjd);
  printf("%4d/%02d/%02d %02d:%02d:%05.2f UT",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
  mjd = mjd - tz/24.0;
  date = mjd_to_date(mjd);
  printf("  %4d/%02d/%02d %02d:%02d:%05.2f local\n",
         date.y,date.mo,date.d, date.h,date.mn,date.s);
}

void lpmoon(jd,lat,sid,ra,dec,dist)

	double jd,lat,sid,*ra,*dec,*dist;

/* implements "low precision" moon algorithms from
   Astronomical Almanac (p. D46 in 1992 version).  Does
   apply the topocentric correction.
Units are as follows
jd,lat, sid;   decimal hours
*ra, *dec,   decimal hours, degrees
	*dist;      earth radii */
{

	double T, lambda, beta, pie, l, m, n, x, y, z, alpha, delta,
		rad_lat, rad_lst, distance, topo_dist;

	T = (jd - J2000) / 36525.;  /* jul cent. since J2000.0 */

	lambda = 218.32 + 481267.883 * T
	   + 6.29 * sin((134.9 + 477198.85 * T) / DEG_IN_RADIAN)
	   - 1.27 * sin((259.2 - 413335.38 * T) / DEG_IN_RADIAN)
	   + 0.66 * sin((235.7 + 890534.23 * T) / DEG_IN_RADIAN)
	   + 0.21 * sin((269.9 + 954397.70 * T) / DEG_IN_RADIAN)
	   - 0.19 * sin((357.5 + 35999.05 * T) / DEG_IN_RADIAN)
	   - 0.11 * sin((186.6 + 966404.05 * T) / DEG_IN_RADIAN);
	lambda = lambda / DEG_IN_RADIAN;
	beta = 5.13 * sin((93.3 + 483202.03 * T) / DEG_IN_RADIAN)
	   + 0.28 * sin((228.2 + 960400.87 * T) / DEG_IN_RADIAN)
	   - 0.28 * sin((318.3 + 6003.18 * T) / DEG_IN_RADIAN)
	   - 0.17 * sin((217.6 - 407332.20 * T) / DEG_IN_RADIAN);
	beta = beta / DEG_IN_RADIAN;
	pie = 0.9508
	   + 0.0518 * cos((134.9 + 477198.85 * T) / DEG_IN_RADIAN)
	   + 0.0095 * cos((259.2 - 413335.38 * T) / DEG_IN_RADIAN)
	   + 0.0078 * cos((235.7 + 890534.23 * T) / DEG_IN_RADIAN)
	   + 0.0028 * cos((269.9 + 954397.70 * T) / DEG_IN_RADIAN);
	pie = pie / DEG_IN_RADIAN;
	distance = 1 / sin(pie);

	l = cos(beta) * cos(lambda);
	m = 0.9175 * cos(beta) * sin(lambda) - 0.3978 * sin(beta);
	n = 0.3978 * cos(beta) * sin(lambda) + 0.9175 * sin(beta);

	x = l * distance;
	y = m * distance;
	z = n * distance;  /* for topocentric correction */

	rad_lat = lat / DEG_IN_RADIAN;
	rad_lst = sid / HRS_IN_RADIAN;
	x = x - cos(rad_lat) * cos(rad_lst);
	y = y - cos(rad_lat) * sin(rad_lst);
	z = z - sin(rad_lat);


	topo_dist = sqrt(x * x + y * y + z * z);

	l = x / topo_dist;
	m = y / topo_dist;
	n = z / topo_dist;

	alpha = atan_circ(l,m);
	delta = asin(n);
	*ra = alpha * HRS_IN_RADIAN;
	*dec = delta * DEG_IN_RADIAN;
	*dist = topo_dist;
}

#if 0
#undef  DEG_IN_RADIAN
#undef  HRS_IN_RADIAN
#undef  J2000
#undef  SEC_IN_DAY
#undef  FLATTEN
#undef  EQUAT_RAD
#undef  ASTRO_UNIT
#undef  TWOPI
#undef  PI_OVER_2
#undef  EQUAT_RAD
#endif
