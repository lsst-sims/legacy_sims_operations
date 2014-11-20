
struct coord {
  short sign;  /* carry sign explicitly since -0 not neg. */
  double hh;
  double mm;
  double ss;
};

struct date_time {
  short y;
  short mo;
  short d;
  short h;
  short mn;
  float s;
};

double atan_circ(double x, double y);
double circulo(double x);
void eclrot(double jd, double *x, double *y, double *z);
void geocent(double geolong, double geolat, double height, double *x_geo, double *y_geo, double *z_geo);
double etcorr(double jd);
double date_to_jd(struct date_time date);
double lst(double jd, double longit);
void caldat(double jdin, struct date_time *date, short *dow);
void lpsun(double jd, double *ra, double *dec);
void accusun(double jd, double lst, double geolat, double *ra, double *dec, double *dist, double *topora, double *topodec, double *x, double *y, double *z);
void accumoon(double jd, double geolat, double lst, double elevsea, double *geora, double *geodec, double *geodist, double *topora, double *topodec, double *topodist);
void min_max_alt(double lat, double dec, double *min, double *max);
double altit(double dec, double ha, double lat, double *az, double *parang);
double ha_alt(double dec, double lat, double alt);
double jd_sun_alt(double alt, double jdguess, double lat, double longit);
double subtend(double ra1, double dec1, double ra2, double dec2);
double adj_time(double x);
double secant_z(double alt);
double true_airmass(double secz);
double subtendRad(double ra1, double dec1, double ra2, double dec2);
struct date_time mjd_to_date(double mjd);
double date_to_mjd(struct date_time date);
void sunPosition(double mjd, double *sunra, double *sundec);
void moonData(double mjd, double *moonra, double *moondec, double *moonalt, double *moonill, double *moonphase);
void airmass(double mjd, double objra, double objdec, double *trueam, double *alt, double *ha);
void twilightparms(double mjd, double *mjdsunrise, double *mjdsunset, double *mjdtwibeg, double *mjdtwiend, double *mjdnautbeg, double *mjdnautend, double *ratwbeg, double *ratwend, double *sunRA);
void setUpSiteData(double latdeg, double longdeg, double elev, double tzw);
double moonSkyBrightness(double mjd, double objra, double objdec);
double lunskybright( double alpha, double rho, double kzen, double altmoon, double alt,  double moondist);
double mjdPrevNoon(double mjd);
void printDate(double mjd, double tz);
void put_coords(double deci, int prec, int showsign);
