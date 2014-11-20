// Aitoff projection and plotting routines

// Aitoff projection from (ra,dec) to (x,y)
/*
  The Hammer-Aitoff projection, for longitude on [-pi,pi] and
latitude on [-pi/2,pi/2] is
     z2 = 1 + cos(latitude) cos(longitude/2)
     x = cos(latitude) sin(longitude/2) / z
     y = sin(latitude) / z
where (x,y) are on -1 to 1

I choose to scale x by two so that the figure has a 2:1 axis ratio
like that of the range in inputs.
*/
void project(double ra, double dec, double *x, double *y) {
  double z;

  // Zeljko likes things to go the other way around...
  ra = -ra;

  z = sqrt((1+cos(dec)*cos(ra/2.0))*0.5)+0.00001;
  *x = 2.0*cos(dec)*sin(ra/2.0)/z;
  *y = sin(dec)/z;
}

#define NCIRC 90
void plotCirc(double cenra, double cendec, double diam, int fill) {
  int i;
  double phi, ra, dec, xx, yy;

  for(i=0; i<NCIRC; i++) {
    phi = 2.0*M_PI * (double)i/(double)(NCIRC-1);
    dec = cendec + diam*cos(phi);
    ra = cenra - diam*sin(phi)/cos(dec);
    if(dec<-M_PI/2.0) {dec = -M_PI - dec; ra += M_PI/2.0;}
    if(dec>M_PI/2.0) {dec = M_PI - dec; ra += 2*M_PI;}
    FIXRA(ra);
    FIXRA(ra);
    project(ra, dec, &xx, &yy);
    cpgpt1(xx,yy,-1);
  }
}

void projCircle(double racen, double deccen, double radius, double val) {
  int i, j, ip, in, sign, pixval;
  float mx[NCIRC], my[NCIRC];
  double t, axialvec[3], cenvec[3], angvec[3], rotvec[3], rmat[3][3];
  double ra[NCIRC], rap[NCIRC], ran[NCIRC];
  double dec[NCIRC], decp[NCIRC], decn[NCIRC];
  double x, y;

  // make Cartesian representation of the vector pointing to center
  slaDcs2c(racen, deccen, cenvec);

  // make Cartesian representation of a vector pointing radius away
  if(deccen>0.0)
    slaDcs2c(racen, deccen-radius, angvec);
  else
    slaDcs2c(racen, deccen+radius, angvec);

  t = 0;
  for(i=0; i<NCIRC; i++) {
    // length of axial vector is angle of rotation
    for(j=0;j<3;j++) axialvec[j] = cenvec[j]*t;
    // get rotation matrix
    slaDav2m(axialvec, rmat);
    // apply rotation to angled vector
    slaDmxv(rmat, angvec, rotvec);
    // get new ra, dec
    slaDcc2s(rotvec, &(ra[i]), &(dec[i]));
    //    if(ra[i] < 0 && racen > 0.0) ra[i] += 2*M_PI;
    //    if(ra[i] > 0 && racen < 0.0) ra[i] -= 2*M_PI;
    // update rotation angle
    t += 2.0*M_PI/(double) (NCIRC-1);
  }

  pixval = rint((__minind*(__maxval-val) + __maxind*(val-__minval))/
               (__maxval-__minval));

  // saturate properly
  pixval = MIN(__maxind, pixval);
  pixval = MAX(__minind, pixval);

  cpgsci(pixval);

  // determine if the polygon wraps around
  sign = 0;
  for(i=0; i<NCIRC-1; i++) {
    if(dec[i]>deccen && ra[i+1]*ra[i] < 0 && ra[i+1]<ra[i]) sign = 1;
  }

  // if so, draw two polygons separately
  if(sign) {
    in = 0;
    ip = 0;
    for(i=0; i<NCIRC; i++) {
      if(ra[i]<0.0) {
        ran[in] = ra[i]; decn[in] = dec[i]; in++;
      }
      else {
        ran[in] = -0.99999*M_PI; decn[in] = dec[i]; in++;
      }
      if(ra[i]>0.0) {
        rap[ip] = ra[i]; decp[ip] = dec[i]; ip++;
      }
      else {
        rap[ip] = 0.99999*M_PI; decp[ip] = dec[i]; ip++;
      }
    }
    
    for(i=0; i<ip; i++) {
      // Hammer-Aitoff projection
      project(rap[i], decp[i], &x, &y);
      mx[i] = x; my[i] = y;
    }
    cpgpoly(ip,mx,my);
    
    for(i=0; i<in; i++) {
      // Hammer-Aitoff projection
      project(ran[i], decn[i], &x, &y);
      mx[i] = x; my[i] = y;
    }
    cpgpoly(in,mx,my);
  }
  // otherwise draw only one
  else {
    for(i=0; i<NCIRC; i++) {
      // Hammer-Aitoff projection
      project(ra[i], dec[i], &x, &y);
      mx[i] = x; my[i] = y;
    }
    cpgpoly(NCIRC,mx,my);
  }

  cpgsci(1);
}
#undef NCIRC


// convert from (l,b) to (ra,dec) (all in radians)
void eqgal(double l, double b, double *ra, double *dec) {
  double sind, sinra, cosra;

  sind = sin(b)*cos(1.0926) + cos(b)*sin(l-0.5760)*sin(1.0926);
  CLIP(sind,-1.0,1.0);
  *dec = asin(sind);
  sinra = (cos(b)*sin(l - 0.5760)*cos(1.0926) -
           sin(b)*sin(1.0926))/cos(*dec);
  cosra = cos(b)*cos(l - 0.5760)/cos(*dec);
  CLIP(cosra,-1.0,1.0);
  *ra = acos(cosra);
  if(sinra<0) *ra = 2.0*M_PI-(*ra);
  FIXRA(*ra);
  *ra += 282.25 * M_PI/180.0;
  FIXRA(*ra);
}

// Plots the galactic exclusion region
#define NG 3000
void galaxy(double peakL, double taperL, double taperB) {
  int i;
  double band;
  double galL[NG], xb[NG], ra, dec;
  double x, y;

  band = peakL - taperL;

  // (-180,180)
  for(i=0; i<NG;i++) {
    galL[i] = -M_PI + ((double)i/(double)(NG-1)) * 2.0*M_PI;
    xb[i] = peakL - band*fabs(galL[i])/taperB;
  }

  // plot galactic plane
  cpgsci(2);
  for(i=1;i<NG;i++) {
    eqgal(galL[i],0.0,&ra,&dec);
    project(ra,dec,&x,&y);
    cpgpt1(x,y,-2);
  }


  for(i=0; i<NG;i++) {
    galL[i] = 0.0 + ((double)i/(double)(NG-1)) * taperB;
    xb[i] = peakL - band*fabs(galL[i])/taperB;
  }

  // Northern boundary of exclusion zone
  cpgsci(LIGHTGRAY);
  for(i=1;i<NG;i++) {
    eqgal(galL[i],xb[i],&ra,&dec);
    project(ra,dec,&x,&y);
    cpgpt1(x,y,-2);
  }
  // Southern boundary of exclusion zone
  for(i=1;i<NG;i++) {
    eqgal(galL[i],-xb[i],&ra,&dec);
    project(ra,dec,&x,&y);
    cpgpt1(x,y,-2);
  }


  for(i=0; i<NG;i++) {
    galL[i] = 0.0 - ((double)i/(double)(NG-1)) * taperB;
    xb[i] = peakL - band*fabs(galL[i])/taperB;
  }

  // Northern boundary of exclusion zone
  cpgsci(LIGHTGRAY);
  for(i=1;i<NG;i++) {
    eqgal(galL[i],xb[i],&ra,&dec);
    project(ra,dec,&x,&y);
    cpgpt1(x,y,-2);
  }
  // Southern boundary of exclusion zone
  for(i=1;i<NG;i++) {
    eqgal(galL[i],-xb[i],&ra,&dec);
    project(ra,dec,&x,&y);
    cpgpt1(x,y,-2);
  }

  cpgsci(1);

#if 0
  // galactic center
  cpgsci(2);
  ra = 17.76*15.0/DEG_IN_RADIAN;
  FIXRA(ra);
  dec = -28.9333/DEG_IN_RADIAN;
  project(ra,dec,&x,&y);
  cpgpt1(x,y,71);
  cpgsci(2);

  // galactic anticenter
  cpgsci(2);
  ra = (180+17.76*15.0)/DEG_IN_RADIAN;
  FIXRA(ra);
  dec = 27.117/DEG_IN_RADIAN;
  project(ra,dec,&x,&y);
  cpgpt1(x,y,103);
  cpgsci(2);
#endif

  // plot ecliptic
  cpgslw(5);
  cpgsci(2);
  // (-180,180)
  for(i=0; i<NG;i++) {
    galL[i] = -M_PI + ((double)i/(double)(NG-1)) * 2.0*M_PI;
    xb[i] = peakL - band*fabs(galL[i])/taperB;
  }
  for(i=0; i<NG; i++) {
    dec = atan(sin(galL[i])*tan(23.43333*M_PI/180.0));
    project(galL[i],dec,&x,&y);
    cpgpt1(x,y,-2);
  }
  cpgslw(1);
  cpgsci(1);
}
#undef NG

#define NM 25  // every hour
//#define NM 13    // every 2 hours
//#define NP 19  // every 10 degrees
#define NP 13    // every 15 degrees
#define MM 3000
void aitoffGrid(void) {

  int i,j;
  double phi[MM], lam[MM], x[MM], y[MM];
  double rr, dd;

  cpgsci(DARKGRAY);
  cpgslw(1);

  for(i=0; i<MM; i++) phi[i] = i*M_PI/(double)(MM-1) - M_PI/2.0;

  // make meridians for each ra in (-180,180)
  for(i=0; i<NM; i++) {
    rr = i*2.0*M_PI/(double)(NM-1) - M_PI;

    // steps in dec on (-90,90)
    for(j=0; j<MM; j++) {
      project(rr,phi[j],&x[j],&y[j]);
    }
    for(j=1; j<MM; j++) {
      cpgmove(x[j-1],y[j-1]);
      cpgdraw(x[j],y[j]);
    }
  }

  // make parallels
  // steps in dec on (-90,90)
  for(i=0; i<MM; i++) phi[i] *= 2.0;
  for(i=0; i<NP; i++) {
    dd = i*M_PI/(double)(NP-1) - M_PI/2.0;

    // steps in RA from (-180,180)
    for(j=0; j<MM; j++) {
      project(phi[j],dd,&x[j],&y[j]);
    }
    for(j=1; j<MM; j++) {
      cpgmove(x[j-1],y[j-1]);
      cpgdraw(x[j],y[j]);
    }
  }

  cpgsci(1);
  cpgslw(1);

}
#undef NM
#undef NP
#undef MM
