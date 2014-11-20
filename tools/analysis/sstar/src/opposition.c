#define PHIMIN -185.0
#define PHIMAX 185.0
#define AMMIN 0.95
#define AMMAX 3.95
void oppositionPlot(void) {
  int i;
  double rasun, decsun, distsun, toporasun, topodecsun, x, y, z;
  double jd, lstm, trueam, alt, ha, phi, longEcliptic, latEcliptic;
  double objra, objdec;
  
  openPlot("opposition");
  cpgpap(PLOTSIZE/0.5,0.5);

  cpgbbuf();

  cpgsubp(2,2);

  cpgpanl(1,1);
  cpgswin(PHIMIN, PHIMAX, AMMIN, AMMAX);
  cpgbox("BCNTS",0.0,0,"BVCNTS",0.0,0);
  cpgmtxt("L",2.0,0.5,0.5,"airmass");
  cpgmtxt("B",2.0,0.5,0.5,"angle from Sun");

  cpgsci(2);
  for(i=0; i<numobs; i++) {

    jd = obs[i].date + 2400000.5;
    lstm = lst(jd,longitude_hrs);

    // get ecliptic coordinates
    slaEqecl(obs[i].ra, obs[i].dec, obs[i].date, &longEcliptic, &latEcliptic);

    if(fabs(latEcliptic) < 10.0/DEG_IN_RADIAN && obs[i].twilight==0) {

      // get position of Sun
      accusun(jd, lstm, latitude_deg, &rasun, &decsun, &distsun,
              &toporasun, &topodecsun, &x, &y, &z);

      // sun-object angle in degrees
      // takes ra in hours, dec in degrees
      objra = adj_time(obs[i].ra*HRS_IN_RADIAN);
      objdec = obs[i].dec*DEG_IN_RADIAN;
      phi = mysubtend(rasun, decsun, objra, objdec)*DEG_IN_RADIAN;
      
      // angle from opposition is 180-phi
      //      FIXRANGE(phi,-180.0,180.0);
      
      //airmass takes ra, dec, in radians, returns true airmass
      airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);
      
      cpgpt1(phi, trueam, -1);

    }
  }

  cpgsci(1);
  cpgptxt(0.0,3.0,0.0,0.5,"|ecliptic latitude|<10");
  cpgptxt(0.0,2.5,0.0,0.5,"night");

  cpgsci(3);
  cpgmove(-90.0,0.0);
  cpgdraw(-90.0,4.0);
  cpgmove( 90.0,0.0);
  cpgdraw( 90.0,4.0);
  cpgsci(1);


  cpgpanl(1,2);
  cpgswin(PHIMIN, PHIMAX, AMMIN, AMMAX);
  cpgbox("BCNTS",0.0,0,"BVCNTS",0.0,0);
  cpgmtxt("L",2.0,0.5,0.5,"airmass");
  cpgmtxt("B",2.0,0.5,0.5,"angle from Sun");

  cpgsci(2);
  for(i=0; i<numobs; i++) {

    jd = obs[i].date + 2400000.5;
    lstm = lst(jd,longitude_hrs);

    // get ecliptic coordinates
    slaEqecl(obs[i].ra, obs[i].dec, obs[i].date, &longEcliptic, &latEcliptic);

    if(fabs(latEcliptic) >= 10.0/DEG_IN_RADIAN  && obs[i].twilight==0 ) {

      // get position of Sun
      accusun(jd, lstm, latitude_deg, &rasun, &decsun, &distsun,
              &toporasun, &topodecsun, &x, &y, &z);

      // sun-object angle in degrees
      phi = mysubtend(rasun, decsun, obs[i].ra*HRS_IN_RADIAN, obs[i].dec*DEG_IN_RADIAN)*DEG_IN_RADIAN;
      
      // angle from opposition is 180-phi
      FIXRANGE(phi,-180.0,180.0);
      
      airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);
      
      cpgpt1(phi, trueam, -1);

    }
  }

  cpgsci(1);
  cpgptxt(0.0,3.0,0.0,0.5,"|ecliptic latitude|>10");
  cpgptxt(0.0,2.5,0.0,0.5,"night");

  cpgsci(3);
  cpgmove(-90.0,0.0);
  cpgdraw(-90.0,4.0);
  cpgmove( 90.0,0.0);
  cpgdraw( 90.0,4.0);
  cpgsci(1);


  cpgpanl(2,1);
  cpgswin(PHIMIN, PHIMAX, AMMIN, AMMAX);
  cpgbox("BCNTS",0.0,0,"BVCNTS",0.0,0);
  cpgmtxt("L",2.0,0.5,0.5,"airmass");
  cpgmtxt("B",2.0,0.5,0.5,"angle from Sun");

  cpgsci(2);
  for(i=0; i<numobs; i++) {

    jd = obs[i].date + 2400000.5;
    lstm = lst(jd,longitude_hrs);

    // get ecliptic coordinates
    slaEqecl(obs[i].ra, obs[i].dec, obs[i].date, &longEcliptic, &latEcliptic);

    if(fabs(latEcliptic) < 10.0/DEG_IN_RADIAN  && obs[i].twilight==1) {

      // get position of Sun
      accusun(jd, lstm, latitude_deg, &rasun, &decsun, &distsun,
              &toporasun, &topodecsun, &x, &y, &z);

      // sun-object angle in degrees
      // takes ra in hours, dec in degrees
      objra = adj_time(obs[i].ra*HRS_IN_RADIAN);
      objdec = obs[i].dec*DEG_IN_RADIAN;
      phi = mysubtend(rasun, decsun, objra, objdec)*DEG_IN_RADIAN;
      
      // angle from opposition is 180-phi
      //      FIXRANGE(phi,-180.0,180.0);
      
      //airmass takes ra, dec, in radians, returns true airmass
      airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);
      
      cpgpt1(phi, trueam, -1);

    }
  }

  cpgsci(1);
  cpgptxt(0.0,3.0,0.0,0.5,"|ecliptic latitude|<10");
  cpgptxt(0.0,2.5,0.0,0.5,"twilight");

  cpgsci(3);
  cpgmove(-90.0,0.0);
  cpgdraw(-90.0,4.0);
  cpgmove( 90.0,0.0);
  cpgdraw( 90.0,4.0);
  cpgsci(1);


  cpgpanl(2,2);
  cpgswin(PHIMIN, PHIMAX, AMMIN, AMMAX);
  cpgbox("BCNTS",0.0,0,"BVCNTS",0.0,0);
  cpgmtxt("L",2.0,0.5,0.5,"airmass");
  cpgmtxt("B",2.0,0.5,0.5,"angle from Sun");

  cpgsci(2);
  for(i=0; i<numobs; i++) {

    jd = obs[i].date + 2400000.5;
    lstm = lst(jd,longitude_hrs);

    // get ecliptic coordinates
    slaEqecl(obs[i].ra, obs[i].dec, obs[i].date, &longEcliptic, &latEcliptic);

    if(fabs(latEcliptic) >= 10.0/DEG_IN_RADIAN  && obs[i].twilight==1) {

      // get position of Sun
      accusun(jd, lstm, latitude_deg, &rasun, &decsun, &distsun,
              &toporasun, &topodecsun, &x, &y, &z);

      // sun-object angle in degrees
      phi = mysubtend(rasun, decsun, obs[i].ra*HRS_IN_RADIAN, obs[i].dec*DEG_IN_RADIAN)*DEG_IN_RADIAN;
      
      // angle from opposition is 180-phi
      FIXRANGE(phi,-180.0,180.0);
      
      airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);
      
      cpgpt1(phi, trueam, -1);

    }
  }

  cpgsci(1);
  cpgptxt(0.0,3.0,0.0,0.5,"|ecliptic latitude|>10");
  cpgptxt(0.0,2.5,0.0,0.5,"twilight");

  cpgsci(3);
  cpgmove(-90.0,0.0);
  cpgdraw(-90.0,4.0);
  cpgmove( 90.0,0.0);
  cpgdraw( 90.0,4.0);
  cpgsci(1);


  cpgebuf();
  closePlot();
}
