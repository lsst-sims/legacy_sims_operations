// Make histograms of slew time and slew distance
//  HISTINT is the bin size for slew time (seconds)
//  HISTDDIST is the bin size for slew distance (degrees)
#define HISTINT (2.0)
#define HISTDDIST (3.5)
void slewPlot(void) {
  int i, j, nhist;
  double stmax, stmin, minhist, maxhist, cntmax, *histbins, *counts, sum;
  float x[4], y[4];

  // find limits on slew times
  stmin = 1e9; stmax = -stmin;
  for(i=0; i<numobs; i++) {
    stmin = MIN(stmin, obs[i].slewtime);
    stmax = MAX(stmax, obs[i].slewtime);
  }

  printf("min,max slew times: %f, %f\n", stmin, stmax);
  
  minhist = floor(stmin/HISTINT)*HISTINT;
  maxhist = (floor(stmax/HISTINT)+1)*HISTINT;
  nhist = (maxhist-minhist)/HISTINT + 1;

  counts = (double *) malloc((nhist+1)*sizeof(double));
  histbins = (double *) malloc((nhist+1)*sizeof(double));

  // make bin limits for counting
  for(i=0; i<nhist; i++) {
    histbins[i] = minhist + i*HISTINT;
    counts[i] = 0;
  }
  histbins[nhist] = histbins[nhist-1] + 10000.0;
  counts[nhist] = 0;

  // count slew times in bins
  j = 0;
  for(i=0; i<numobs; i++) {
    hunt(histbins, nhist, obs[i].slewtime, &j);
    counts[j]++;
  }

  // check to see everyone has been counted
  sum = 0.0;
  cntmax = 0.0;
  for(i=0; i<=nhist; i++) {
    sum += counts[i];
    cntmax = MAX(cntmax,counts[i]);
  }
  if(floor(sum) != numobs) {
    fprintf(stderr,"bug in slewPlot counting: %d %d\n", numobs, (int) floor(sum));
    //exit(1);
  }

  // make plot
  openPlot("slews");
  cpgpap(PLOTSIZE/0.75,0.75);

  cpgbbuf();

  cpgsubp(1,2);

  cpgpanl(1,1);
  cpgsvp(0.15,0.9,0.15,0.9);
  cpgsch(2.0);

  cpgswin(stmin, stmax, 0.0, log10(1.05*cntmax));
  cpgbox("BCNTS",0.0,0,"BLVCNTS",0.0,0);
  cpgmtxt("B",2.5,0.5,0.5,"slew time [sec]");
  cpgmtxt("L",3.5,0.5,0.5,"number of slews");
  for(i=0; i<nhist; i++) {
    x[0] = histbins[i];
    y[0] = 0;
    x[1] = histbins[i+1];
    y[1] = 0;
    x[2] = histbins[i+1];
    if(counts[i]>0) y[2] = log10(counts[i]);  else  y[2] = 0.0;
    x[3] = histbins[i];
    y[3] = y[2];
    cpgpoly(4,x,y);
  }

  free(counts);
  free(histbins);

  // Now make slew distance plot

  // find limits on slew distances
  stmin = 1e9; stmax = -stmin;
  for(i=0; i<numobs; i++) {
    stmin = MIN(stmin, obs[i].slewdist*DEG_IN_RADIAN);
    stmax = MAX(stmax, obs[i].slewdist*DEG_IN_RADIAN);
  }

  printf("min,max slew times: %f, %f\n", stmin, stmax);
  
  minhist = floor(stmin/HISTINT)*HISTDDIST;
  maxhist = (floor(stmax/HISTINT)+1)*HISTDDIST;
  nhist = (maxhist-minhist)/HISTDDIST + 1;

  counts = (double *) malloc((nhist+1)*sizeof(double));
  histbins = (double *) malloc((nhist+1)*sizeof(double));

  // make bin limits for counting
  for(i=0; i<nhist; i++) {
    histbins[i] = minhist + i*HISTDDIST;
    counts[i] = 0;
  }
  histbins[nhist] = histbins[nhist-1] + 10000.0;
  counts[nhist] = 0;

  // count slew times in bins
  j = 0;
  for(i=0; i<numobs; i++) {
    hunt(histbins, nhist, obs[i].slewdist*DEG_IN_RADIAN, &j);
    counts[j]++;
  }

  // check to see everyone has been counted
  sum = 0.0;
  cntmax = 0.0;
  for(i=0; i<=nhist; i++) {
    sum += counts[i];
    cntmax = MAX(cntmax,counts[i]);
  }
  if(floor(sum) != numobs) {
    fprintf(stderr,"bug in slewPlot counting: %d %d\n", numobs, (int) floor(sum));
    //exit(1);
  }

  // make plot
  cpgpanl(1,2);
  cpgsvp(0.15,0.9,0.15,0.9);
  cpgsch(2.0);
  cpgswin(stmin, stmax, 0.0, log10(1.05*cntmax));
  cpgbox("BCNTS",0.0,0,"BLVCNTS",0.0,0);
  cpgmtxt("B",2.5,0.5,0.5,"slew distance [degree]");
  cpgmtxt("L",3.5,0.5,0.5,"number of slews");
  for(i=0; i<nhist; i++) {
    x[0] = histbins[i];
    y[0] = 0;
    x[1] = histbins[i+1];
    y[1] = 0;
    x[2] = histbins[i+1];
    if(counts[i]>0) y[2] = log10(counts[i]);  else  y[2] = 0.0;
    x[3] = histbins[i];
    y[3] = y[2];
    cpgpoly(4,x,y);
  }
  cpgebuf();

  free(counts);
  free(histbins);

  closePlot();
}
