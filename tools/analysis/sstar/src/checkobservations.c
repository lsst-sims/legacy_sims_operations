// perform sanity checks on the observations

void checkObservations(void) {
	char text[1204];
	int i, j, z, ierr, flag;
	double xmin, xmax, ymin, ymax;
	double *x, *y;
	double sunrise, sunset, twibeg, twiend, setra, risera, sRA, ra1, ra2;
	double nautbeg, nautend;
	double xx, yy;
	double trueam, alt, ha;
	double moonra, moondec, moonalt, moonill, moon_field, moonphase;
	double osraxx, osrayy, osetxx, osetyy, orisexx, oriseyy;
	double ora1xx, ora1yy, ora2xx, ora2yy, omoonxx, omoonyy;
	int ntwilight, ndawn;
	struct date_time date;

	// initialize
	sunrise = -1; sunset = -1;
	ntwilight = 0; ndawn = 0;
	printf("\n");
	
	for(i=0; i<numobs; i++) {
		if(obs[i].date >= obs[i+1].date) {
			printf("visits not ordered in time\n");
			printf(" mjd %f  ", obs[i].date); printDate(obs[i].date,TZ);
			printf(" mjd %f  ", obs[i+1].date); printDate(obs[i+1].date,TZ);
			exit(1);
		}
	
		// compute new day data if observation is after sunrise
		if(obs[i].date > sunrise) {
			twilightparms(obs[i].date, &sunrise, &sunset, &twibeg, &twiend, &nautbeg, &nautend, &setra, &risera, &sRA);
			
			FIXRA(sRA); FIXRA(setra); FIXRA(risera); FIXRA(ra1); FIXRA(ra2);
			
			moonData(obs[i].date, &moonra, &moondec, &moonalt, &moonill, &moonphase);
			FIXRA(moonra);
	
			if(debug) {
				printf("\n\nnew day:\n");
				printCircumstances(obs[i]);
				printf("\n\n");
				printf("-------------------------------------------------\n");
			}
		}
	
		// error flag
		ierr = 0;
	
		// check twilight observations
		if(obs[i].date>nautbeg && obs[i].date<twibeg-GRACE) {
			flag = 0;
			for(j=0; j<ntwilightFilters; j++) if(obs[i].filter == twilightFilters[j]) flag=1;
			if(flag==0) {
				printf("\nwrong filter for evening twilight: %s\n", filtername[obs[i].filter]);
				printf("        nautical twilight: "); printDate(nautbeg, TZ);
				printf("           observation at: "); printDate(obs[i].date, TZ);
				printf("  astrononomical twilight: "); printDate(nautbeg, TZ);
				printf("   %f minutes before twilight begins\n", (obs[i].date-twibeg)*1440.0);
			
				ierr = 1;
			}
			// evening twilight tally
			ntwilight++;
		}
	
		if(obs[i].date>twiend+GRACE && obs[i].date<nautend) {
			flag = 0;
			for(j=0; j<ntwilightFilters; j++) if(obs[i].filter == twilightFilters[j]) flag=1;
			if(flag==0) {
				printf("\nwrong filter for morning twilight: %s\n", filtername[obs[i].filter]);
				printf("  astrononomical twilight: "); printDate(twiend, TZ);
				printf("           observation at: "); printDate(obs[i].date, TZ);
				printf("        nautical twilight: "); printDate(nautend, TZ);
				printf("   %f minutes after twilight ends\n", (obs[i].date-twiend)*1440.0);
				ierr = 1;
			}
			// morning twilight tally
			ndawn++;
		}
	
		// find airmass
		airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);
		// find moon-field distance
		moon_field = subtendRad(moonra,moondec,obs[i].ra,obs[i].dec);
	
		// check sunrise and sunset times
		if(obs[i].date<sunset) {
			printf("\nfield %d observed %f minutes before sunset!\n", obs[i].field, (sunset-obs[i].date)*1440.0);
			ierr = 1;
		}
		else if(obs[i].date<nautbeg-GRACE) {
			printf("\nfield %d observed %f minutes before nautical twilight!\n", obs[i].field, (nautbeg-obs[i].date)*1440.0);
			ierr = 1;
		}
	
		if(obs[i].date>nautend+GRACE) {
			printf("\nfield %d observed %f minutes after nautical twilight!\n", obs[i].field, (obs[i].date-nautend)*1440.0);
			ierr = 1;
		}
		else if(obs[i].date>sunrise) {
			printf("\nfield %d observed %f minutes after sunrise!\n", obs[i].field, (obs[i].date-sunrise)*1440.0);
			ierr = 1;
		}
	
		// check airmass is withing limits
		if(trueam>LARGE_AIRMASS) {
			printf("\nfield %d with large airmass: %f  zenith distance: %4.1f\n", obs[i].field, trueam, 90.0 - alt);
			ierr = 1;
		}
	
		// check moon-field separation
		if(moon_field<MOON_AVOID) {
			printf("\nfield %d is %f from moon\n", obs[i].field,moon_field*DEG_IN_RADIAN);
			ierr = 1;
		}
		//****************************************
		// could check most of the numbers edited into the db
		//****************************************
		// print if there was an error
		if(ierr && debug) printCircumstances(obs[i]);
	}
	// summary of numbers of observations
	printf("ntwilight: %d   ndawn: %d   numobs: %d\n", ntwilight, ndawn, numobs);
}


// print a summary of the times spent doing various things

// summary of time spent doing various things
void timeSummary(void) {
  char str[1024];
  int i, filt, ndays, eveningtwisum, morningtwisum, twisum, nightsum, daysum;
  int fchangecount, fchangenight, fchangenmin, fchangenmax, dtime, badnights;
  int obsfilt[NFILTERS];
  float xmin, xmax, ymin, ymax, eps;
  float sunrisetime, sunsettime, tmin, tmax;
  double sunrise, sunset, twibeg, twiend, nautbeg, nautend, setra, risera, sRA;
  double jd, date, date1, date2, time, error, errmax;
  double moonra, moondec, moonalt, moonill, sumtime, slewsum, nighttime;
  double alt, trueam, ha, meanam, sigam, meanalt, sigalt, meanha, sigha, del;
  double meanVsky[NFILTERS], sigVsky[NFILTERS];
  struct date_time dd;

  printf("\n");

  date1 = obs[0].date;
  date2 = obs[numobs-1].date;
  ndays = date2-date1;

  // get the total amount of observing time
  sumtime = 0;
  nighttime = 0;
  for(i=0; i<ndays; i++) {
    jd = date1 + (double)i;
    // get beginning/ending of astronomical and nautical twilights
    twilightparms(jd,
                  &sunrise, &sunset,
                  &twibeg, &twiend,
                  &nautbeg, &nautend,
                  &setra, &risera, &sRA);

    sumtime += nautend-nautbeg;
    nighttime += twiend-twibeg;
  }
  printf("                total night observing time possible: %f hours (%f years)\n",
         nighttime*24.0, nighttime/365.25);
  printf("                      total observing time possible: %f hours (%f years)\n",
         sumtime*24.0, sumtime/365.25);
  printf("              fraction of time in nautical twilight: %f\n",
         (sumtime-nighttime)/sumtime);


  // now count observations
  sunrise = -1; ndays = 0; badnights = 0;
  eveningtwisum = 0;
  morningtwisum = 0;
  twisum = 0;
  nightsum = 0;
  daysum = 0;
  errmax = 0;
  meanam = sigam = meanalt = sigalt = meanha = sigha = 0.0;
  fchangecount = fchangenmax = 0; fchangenmin = 1000000000;
  for(filt=0; filt<NFILTERS; filt++) {
    meanVsky[filt] = sigVsky[filt] = 0.0;
    obsfilt[filt] = 0;
  }
  for(i=1; i<numobs; i++) {

    // MJD changes over at midnight...
    dtime = (int) (obs[i].date+TZ+0.5) - (int) (obs[i-1].date+TZ+0.5);
    if(dtime>0) {
      fchangenight = 0;
      ndays+= dtime;
      badnights += MAX(0,dtime-1);
    }

    jd = obs[i].date;
    twilightparms(jd,
                  &sunrise, &sunset,
                  &twibeg, &twiend,
                  &nautbeg, &nautend,
                  &setra, &risera, &sRA);
    if( (obs[i].date >= nautbeg-GRACE) && (obs[i].date < twibeg) ) {
      eveningtwisum++;
      obs[i].twilight = 1;
    }
    else if( (obs[i].date > twiend) && (obs[i].date <= nautend+GRACE) ) {
      morningtwisum++;
      obs[i].twilight = 1;
    }
    else if( (obs[i].date >= twibeg) && (obs[i].date <= twiend) ) {
      nightsum++;
      obs[i].twilight = 0;
    }
    else {
      daysum++;
      if(obs[i].date < nautbeg) {
        error = obs[i].date - nautbeg;
        //printf("before nautical twilight by %e minutes\n",error*86400.0/60.0);
      }
      else if(obs[i].date > nautend) {
        error = nautend - obs[i].date;
        //printf("after nautical twilight by %e minutes\n",error*86400.0/60.0);
      }
      else {
        printf("Bad day!\n");
        exit(1);
      }
      errmax = MAX(errmax,-error);
    }

    // sky brightness average
    filt = obs[i].filter;
    obsfilt[filt]++;
    del = obs[i].vskybright - meanVsky[filt];
    meanVsky[filt] += del/(double)obsfilt[filt];
    sigVsky[filt] += del*(obs[i].vskybright - meanVsky[filt]);

    // get airmass statistics
    airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);

    del = trueam - meanam;
    meanam += del/(double)i;
    sigam += del*(trueam - meanam);

    del = alt - meanalt;
    meanalt += del/(double)i;
    sigalt += del*(alt - meanalt);

    del = ha - meanha;
    meanha += del/(double)i;
    sigha += del*(ha - meanha);

    if(obs[i].filter != obs[i-1].filter) {
      fchangenight++;
      fchangecount++;
      fchangenmin = MIN(fchangenight, fchangenmin);
      fchangenmax = MAX(fchangenight, fchangenmax);
    }
  }
  for(filt=0; filt<NFILTERS; filt++) sigVsky[filt] = sqrt(sigVsky[filt]/(double)obsfilt[filt]);
  
  sigam = sqrt(sigam/(double)(numobs-1));
  sigalt = sqrt(sigalt/(double)(numobs-1));
  sigha = sqrt(sigha/(double)(numobs-1));

  twisum = eveningtwisum + morningtwisum;

  printf("\n");

  // warn if observations made during the day
  if(daysum != 0) {
    printf("\n\n******************************************************************\n");
    printf("           WARNING!!!\n");
    printf("           %d observations made during the day!\n", daysum);
    printf("           worst by %e minutes\n",errmax*86400.0/60.0);
    printf("           WARNING!!!\n");
    printf("******************************************************************\n\n");
  }

  // write summary of observations
  printf("                               evening twilight obs: %d\n", eveningtwisum);
  printf("                               morning twilight obs: %d\n", morningtwisum);
  printf("                                       twilight obs: %d\n", twisum);
  printf("                                           nightobs: %d\n", nightsum);
  printf("                                          total obs: %d\n", numobs);
  printf("               fraction of observations in twilight: %f\n",
         (double)twisum/(double)(twisum+nightsum));
  printf("                               total observing time: %f hours\n",
         (nightsum+twisum)*30.0/3600.0);

  // add all slewing time
  slewsum = 0;
  for(i=0; i<numobs; i++) slewsum += obs[i].slewtime;

  printf("                                total slew time was: %f hours\n", slewsum/3600.0);
  printf("                 ratio of slew time to observe time: %f\n", slewsum/(double)(nightsum+twisum)/30.0);
  printf("     ratio of observe time to possible observe time: %f\n",
         (double)(nightsum+twisum)*30.0/(sumtime*24.0*3600.0));
  printf("ratio of observe+slew time to possible observe time: %f\n",
         ((double)(nightsum+twisum)*30.0+slewsum)/(sumtime*24.0*3600.0));
  printf("\n");

  printf("              number of nights with no observations: %d\n", badnights);
  printf("\n");

  printf("                                       mean airmass: %6.3f +/- %6.3f \n", meanam, sigam);
  printf("                               mean zenith distance: %6.3f +/- %6.3f \n", 90.0-meanalt,sigalt);
  printf("                                    mean hour angle: %6.3f +/- %6.3f \n", meanha,sigha);
  printf("\n");

  for(filt=0; filt<NFILTERS; filt++) {
    printf("                                     %s observations: %d\n",
           filtername[filt],  obsfilt[filt]);
  }
  printf("\n");

  for(filt=0; filt<NFILTERS; filt++) {
    printf("                      V sky brightness for %s visits: %f +/ %f\n",
           filtername[filt], meanVsky[filt], sigVsky[filt]);
  }
  printf("\n");

  printf("              average # of filter changes per night: %7.3f  (min: %d,  max: %d)\n", 
         (double)fchangecount/(double)ndays, fchangenmin, fchangenmax);
  printf("\n");
}

