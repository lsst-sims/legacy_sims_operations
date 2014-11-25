
// macro to plot hourglass plot
#define PTIME(d, t) {if(t>12.0) cpgpt1(d-date1,t-24.0,-2); else cpgpt1(d-date1,t,-2); }

// make hourglass plot of hours observed in which filter as a function
//   of day into the simulation
void hourglassPlot(void) {
  char str[1024];
  int i, ndays, twisum, nightsum;
  float xmin, xmax, ymin, ymax, eps;
  float sunrisetime, sunsettime, tmin, tmax;
  double sunrise, sunset, twibeg, twiend, nautbeg, nautend, setra, risera, sRA;
  double jd, date, date1, date2, time;
  double moonra, moondec, moonalt, moonill, moonphase;
  double sumtime, slewsum, nighttime;
  struct date_time dd;

  // reorder fields by date
  qsort(obs, numobs, sizeof(observation), compareDate);

  openPlot("hourglass");
  cpgbbuf();
  cpgsvp(0.1,0.9,0.07,0.85); // fraction of viewport for plot

  //#define SBHOUR
#ifdef SBHOUR
  setupImplot(15.0, 22.0);
#endif

  date1 = obs[0].date;
  date2 = obs[numobs-1].date;
  ndays = date2-date1;

  tmin = 100;
  tmax = -100;
  for(i=0; i<ndays*10; i++) {
    jd = date1 + (double)i/10.0;
    twilightparms(jd,
                  &sunrise, &sunset,
                  &twibeg, &twiend,
                  &nautbeg, &nautend,
                  &setra, &risera, &sRA);
    dd = mjd_to_date(sunrise-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if (time>12.0) time-=24.0;
    tmin = MIN(time,tmin);
    tmax = MAX(time,tmax);
    dd = mjd_to_date(sunset-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if (time>12.0) time-=24.0;
    tmin = MIN(time,tmin);
    tmax = MAX(time,tmax);
  }

  xmin = 0;
  xmax = ndays+1;
  ymin = tmin;
  ymax = tmax;
  cpgswin(xmin, xmax, ymin, ymax);
  cpgbox("BCNST",0.0,0,"BCNST",0.0,0);
  cpgmtxt("L",2.0,0.5,0.5,"hours from local midnight");
  cpgmtxt("B",2.0,0.5,0.5,"day");

  twisum = 0;
  nightsum = 0;
  for(i=1; i<numobs; i++) {
    jd = obs[i].date;
    dd = mjd_to_date(obs[i].date-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;

    // can make this as a colormap in surface brightness
#ifdef SBHOUR
    cpgsci(rint((__minind*(__maxval-obs[i].filtsky) + __maxind*(obs[i].filtsky-__minval))/
                (__maxval-__minval)));
    printf("%d %f\n", i, obs[i].filtsky);
#else
    cpgsci(filtercolor[obs[i].filter]);
#endif

    jd = floor(jd);
    PTIME(jd, time);
  }

  for(i=1; i<ndays*24; i++) {
    jd = date1 + (double)i/24.0;

    twilightparms(jd,
                  &sunrise, &sunset,
                  &twibeg, &twiend,
                  &nautbeg, &nautend,
                  &setra, &risera, &sRA);
    jd -= date1;
    cpgsci(LIGHTGRAY);
    dd = mjd_to_date(sunrise-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    dd = mjd_to_date(sunset-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    cpgsci(1);

    cpgsci(2);
    dd = mjd_to_date(nautbeg-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    dd = mjd_to_date(nautend-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    cpgsci(1);

    cpgsci(10);
    dd = mjd_to_date(twibeg-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    dd = mjd_to_date(twiend-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    cpgsci(1);

    moonData(jd+date1, &moonra, &moondec, &moonalt, &moonill, &moonphase);
    cpgpt1(jd, tmin + moonill,-2);
  }

  cpgswin(0.0,1.0,0.0,1.0);
  dd = mjd_to_date(date1 - TZ/24.0);
  sprintf(str,"starting observation:   %4d/%02d/%02d %02d:%02d:%02.0f local",
         dd.y,dd.mo,dd.d, dd.h,dd.mn,dd.s);
  cpgptxt(1.0,1.1,0.0,1.0,str);
  dd = mjd_to_date(date2 - TZ/24.0);
  sprintf(str,"  ending observation:   %4d/%02d/%02d %02d:%02d:%02.0f local",
         dd.y,dd.mo,dd.d, dd.h,dd.mn,dd.s);
  cpgptxt(1.0,1.05,0.0,1.0,str);

  cpgptxt(0.0,1.1,0.0,0.0,plotTitle);

  cpgsch(2.0);
  for(i=0; i<NFILTERS; i++) {
    cpgsci(filtercolor[i]);
    cpgptxt(1.03,0.95-i*0.05,0.0,0.0,filtername[i]);
  }
  cpgsch(1.0);
  cpgsci(1);
  cpgptxt(1.03,0.03,0.0,0.0,"moon");

  cpgebuf();

  closePlot();
}

/*
 One year hourglassPlot
*/
void oneYearhourglassPlot(void) {
  char str[1024];
  int i, ndays, twisum, nightsum;
  float xmin, xmax, ymin, ymax, eps;
  float sunrisetime, sunsettime, tmin, tmax;
  double sunrise, sunset, twibeg, twiend, nautbeg, nautend, setra, risera, sRA;
  double jd, date, date1, date2, time;
  double moonra, moondec, moonalt, moonill, moonphase;
  double sumtime, slewsum, nighttime;
  struct date_time dd;

  // reorder fields by date
  qsort(obs, numobs, sizeof(observation), compareDate);

  openPlot("oneyearhourglass");
  cpgbbuf();
  cpgsvp(0.1,0.9,0.07,0.85); // fraction of viewport for plot

  //#define SBHOUR
#ifdef SBHOUR
  setupImplot(15.0, 22.0);
#endif

  date1 = obs[0].date;
  date2 = obs[0].date + 365;
  ndays = 365;

  tmin = 100;
  tmax = -100;
  for(i=0; i<ndays*10; i++) {
    jd = date1 + (double)i/10.0;
    twilightparms(jd,
                  &sunrise, &sunset,
                  &twibeg, &twiend,
                  &nautbeg, &nautend,
                  &setra, &risera, &sRA);
    dd = mjd_to_date(sunrise-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if (time>12.0) time-=24.0;
    tmin = MIN(time,tmin);
    tmax = MAX(time,tmax);
    dd = mjd_to_date(sunset-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if (time>12.0) time-=24.0;
    tmin = MIN(time,tmin);
    tmax = MAX(time,tmax);
  }

  xmin = 0;
  xmax = ndays+1;
  ymin = tmin;
  ymax = tmax;
  cpgswin(xmin, xmax, ymin, ymax);
  cpgbox("BCNST",0.0,0,"BCNST",0.0,0);
  cpgmtxt("L",2.0,0.5,0.5,"hours from local midnight");
  cpgmtxt("B",2.0,0.5,0.5,"day");

  twisum = 0;
  nightsum = 0;
  for(i=1; i<numobs; i++) {
    jd = obs[i].date;
	if ( jd >= date1 && jd <= date2) {
		dd = mjd_to_date(obs[i].date-TZ/24.0);
		time = dd.h + dd.mn/60.0 + dd.s/3600.0;
	
		// can make this as a colormap in surface brightness
	#ifdef SBHOUR
		cpgsci(rint((__minind*(__maxval-obs[i].filtsky) + __maxind*(obs[i].filtsky-__minval))/
					(__maxval-__minval)));
		printf("%d %f\n", i, obs[i].filtsky);
	#else
		cpgsci(filtercolor[obs[i].filter]);
	#endif
	
		jd = floor(jd);
		PTIME(jd, time);
	}
  }

  for(i=1; i<ndays*24; i++) {
    jd = date1 + (double)i/24.0;

    twilightparms(jd,
                  &sunrise, &sunset,
                  &twibeg, &twiend,
                  &nautbeg, &nautend,
                  &setra, &risera, &sRA);
    jd -= date1;
    cpgsci(LIGHTGRAY);
    dd = mjd_to_date(sunrise-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    dd = mjd_to_date(sunset-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    cpgsci(1);

    cpgsci(2);
    dd = mjd_to_date(nautbeg-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    dd = mjd_to_date(nautend-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    cpgsci(1);

    cpgsci(10);
    dd = mjd_to_date(twibeg-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    dd = mjd_to_date(twiend-TZ/24.0);
    time = dd.h + dd.mn/60.0 + dd.s/3600.0;
    if(time>12.0) time -=24.0;
    cpgpt1(jd, time, -2);
    cpgsci(1);

    moonData(jd+date1, &moonra, &moondec, &moonalt, &moonill, &moonphase);
    cpgpt1(jd, tmin + moonill,-2);
  }

  cpgswin(0.0,1.0,0.0,1.0);
  dd = mjd_to_date(date1 - TZ/24.0);
  sprintf(str,"starting observation:   %4d/%02d/%02d %02d:%02d:%02.0f local",
         dd.y,dd.mo,dd.d, dd.h,dd.mn,dd.s);
  cpgptxt(1.0,1.1,0.0,1.0,str);
  dd = mjd_to_date(date2 - TZ/24.0);
  sprintf(str,"  ending observation:   %4d/%02d/%02d %02d:%02d:%02.0f local",
         dd.y,dd.mo,dd.d, dd.h,dd.mn,dd.s);
  cpgptxt(1.0,1.05,0.0,1.0,str);

  cpgptxt(0.0,1.1,0.0,0.0,plotTitle);

  cpgsch(2.0);
  for(i=0; i<NFILTERS; i++) {
    cpgsci(filtercolor[i]);
    cpgptxt(1.03,0.95-i*0.05,0.0,0.0,filtername[i]);
  }
  cpgsch(1.0);
  cpgsci(1);
  cpgptxt(1.03,0.03,0.0,0.0,"moon");

  cpgebuf();

  closePlot();
}
