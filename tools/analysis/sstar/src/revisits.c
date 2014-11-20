#define NFITLERSPLUS 8
double revisit_time[NFITLERSPLUS][5000000];
int revisit_time_length[NFITLERSPLUS];

void revisit_table(int filter) { // Value of filter goes from 0 - 7 (where 6 is g,r,i,z and 7 is all filters)
	int i;
	for(i=0; i < median_data_length; i++) {
		revisit_time[filter][i] = median_data[i];
	}
	revisit_time_length[filter] = median_data_length;
	median_data_length=0;
}

void openRevisitFile() {
	char fName[80];
	sprintf(fName, "../output/%s_%d_revisit-time.tex", hostname, sessionID);
	revisitfp = fopen(fName, "w");
	fprintf(revisitfp, "\\begin{table}[H]{\\textbf{Field Revisit Time}} \\\\ [1.0ex]");
	fprintf(revisitfp, "\\begin{tabular*}{\\textwidth}{\\tblspace lrrrrrrrr}");
	fprintf(revisitfp, "\\hline");
	fprintf(revisitfp, "\\colhead{Minutes} &");
	fprintf(revisitfp, "\\colhead{u} &");
	fprintf(revisitfp, "\\colhead{g} &");
	fprintf(revisitfp, "\\colhead{r} &");
	fprintf(revisitfp, "\\colhead{i} &");
	fprintf(revisitfp, "\\colhead{z} &");
	fprintf(revisitfp, "\\colhead{y} &");
	fprintf(revisitfp, "\\colhead{griz} &");
	fprintf(revisitfp, "\\colhead{All} \\\\");
	fprintf(revisitfp, "\\hline");
	fprintf(revisitfp, "\\hline");
}

void doRevisitTimeStats() {
	int bins[NFITLERSPLUS][11]; // NFILTERS+1 is for griz and NFILTERS+2 is for all
	int bin_size = 9;

	int i, j;
	for( i=0; i < NFITLERSPLUS; i++) {
		for (j=0; j < 11; j++) {
			bins[i][j] = 0;
		}
	}
	for( i=0; i < NFITLERSPLUS; i++) {
		int index = 0;
		for( j=0; j < revisit_time_length[i]; j++) {
			if ( revisit_time[i][j] < 90.0 ) { // We disregard those revisits that are greater than 90 minutes right now
				index = (int)(revisit_time[i][j] / bin_size);
				bins[i][index]++;
			} else {
				// For all revisit times > 90 minutes
				bins[i][10]++;
			}
		}
	}

	for( j=0; j < 11; j++) {
		if ( j == 10 ) {
			fprintf(revisitfp, "$90 \\le t$ & ");
		} else {
			fprintf(revisitfp, "$%d \\le t < %d$ & ", j*bin_size, (j+1)*bin_size);
		}
		for( i=0; i < NFITLERSPLUS; i++) {
			if ( i == NFITLERSPLUS-1 ) {
				fprintf(revisitfp, "%d \\\\ ", bins[i][j]);
			} else {
				fprintf(revisitfp, "%d & ", bins[i][j]);
			}
		}
		fprintf(revisitfp, "\n");
	}
}

void closeRevisitFile() {
	fprintf(revisitfp, "\\hline");
	fprintf(revisitfp, "\\hline");
	fprintf(revisitfp, "\\end{tabular*}");
	fprintf(revisitfp, "\\caption{The distribution of the revisit time - the interval of time between two successive observations of a field (in minutes) - is calculated. The columns give the number of pairs where both observations are in u, both are in g, both in r, both in i, both in z, and both in y. The second to last column gives the number of pairs observed in any combination of g, r, i \\& z. The last column gives the number of pairs observed in any combination of any of the filters.}");
	fprintf(revisitfp, "\\label{tab:RevisitTimeTable}");
	fprintf(revisitfp, "\\end{table}");
	fflush(revisitfp);
	fclose(revisitfp);
}

// if obsa and obsb are both in pairsFilters, return true
//  argument filt is IGNORED
int pairTestMany(observation obsa, observation obsb, int filt) {
  int i, flag;

  // test obsa
  flag = 0;
  for(i=0; i<npairsFilters; i++) {
    if(obsa.filter == pairsFilters[i]) {flag = 1; break;}
  }
  if(flag==0) return 0;

  for(i=0; i<npairsFilters; i++) {
    if(obsb.filter == pairsFilters[i]) return 1;
  }

  return 0;
}

// if obsa and obsb are both in filter filt, return true
int pairTestFilter(observation obsa, observation obsb, int filt) {
  if(obsa.filter == filt && obsb.filter == filt) return 1;
  else return 0;
}

// visit pairs can span 15 minutes to 1.5 hours, but are best when about 1/2 hour apart
#define MAXDTIME (1.5/24.0)
#define MINDTIME (0.25/24.0)
#define IDEALINTERVAL (0.5/24.0)

// count the number of non-overlapping pairs with timing as above and
//   satisfying the filter combinations allowed by testfilters
void countPairs(int numfields, int *start, int *len, 
                int (*testfilters)(observation, observation, int), int filt,
                int **count, int *sum) {

  int k, nf, end, kbest;
  int paircount, firstvisit, nextvisit, lastpossible;
  double dinterval, dbest;

  for(nf=0; nf<numfields; nf++) {
    // number of qualifying pairs for this field
    paircount = 0; 
    // sort observations by time within field
    qsort(&(obs[start[nf]]), len[nf], sizeof(observation), compareDate);

    firstvisit = start[nf];
    end = start[nf]+len[nf]-1;

    // consider all as a first visit until the next-but-last
    while(firstvisit < end-1) {

      // soonest next visit
      nextvisit = firstvisit;
      // go through until we find a next visit more than MINDTIME later
      while(obs[nextvisit].date-obs[firstvisit].date<MINDTIME && nextvisit<end) nextvisit++;

      // having the nextvisit later than MINDTIME after the firstvisit,
      // if the next one is less than MAXDTIME later, it is a potential match
      if(obs[nextvisit].date-obs[firstvisit].date<=MAXDTIME && nextvisit<end) {
        // look through all possible nextvisits to find the one which is closest to
        //   IDEALINTERVAL away
        lastpossible = nextvisit;
        while(obs[lastpossible].date - obs[firstvisit].date <= MAXDTIME && lastpossible<end) lastpossible++;
        // now find the closest to IDEALINTERVAL which satisfies the filter selection test
        dbest = 1e30;
        kbest = -1;
        for(k=firstvisit+1; k<=lastpossible; k++) {
          dinterval = fabs(obs[k].date-obs[firstvisit].date-IDEALINTERVAL);
          if(dinterval<dbest && testfilters(obs[k],obs[firstvisit],filt)) {dbest=dinterval; kbest=k;}
        }
        // if we found a second visit, count it, and use it as the next firstvisit 
        if(kbest>0) {
          paircount++;
		  median_data[median_data_length++] = fabs(obs[kbest].date - obs[firstvisit].date) * 24.00 * 60.00;
          firstvisit = kbest;
        }
        // otherwise, don't count, and increment the first visit
        else {
          firstvisit++;
        }
      }
      // no nextvisit within the alloted time, choose a next firstvisit & try again
      else
        firstvisit++;
    }
    // store the counts for each field
    count[filt][nf] = paircount;
  }
  
  // find the sum over all fields
  *sum = 0;
  for(nf=0; nf<numfields; nf++) {
    *sum += count[filt][nf];
  }
}

/* Counting the number of pairs for NEO per lunation */
void revisitsNEO(void) {
  char tmpstr[1024], tstr[1024], label[1024], plotName[1024];
  int i, nf, filt, sum, sumbyfilter[NFILTERS];
  int nFields, *start, *len, **count;
  double *ravec, *decvec, **value;
  double valmin[NFILTERS], valmax[NFILTERS];
  double fac;

  median_data_length = 0;
  // set up which filters "count" as filter-pair partners
  npairsFilters = 4; // We keep it 4 here and then change it to 6 so that it compares to the rest also
  pairsFilters[0] = filterToNumber("g");
  pairsFilters[1] = filterToNumber("r");
  pairsFilters[2] = filterToNumber("i");
  pairsFilters[3] = filterToNumber("z");
  pairsFilters[4] = filterToNumber("u");
  pairsFilters[5] = filterToNumber("y");

  start = malloc((numFields+1)*sizeof(int));
  len = malloc(numFields*sizeof(int));
  ravec = malloc(numFields*sizeof(double));
  decvec =malloc(numFields*sizeof(double));
  count = malloc(NFILTERS*sizeof(int *));
  for(i=0; i<NFILTERS; i++) count[i] = malloc(numFields*sizeof(int));
  value = malloc(NFILTERS*sizeof(double *));
  for(i=0; i<NFILTERS; i++) value[i] = malloc(numFields*sizeof(double));

  // order visits by field and get pointers
  getFieldData(&nFields, start, len);

  // use filt=0 for this summary plot
  filt = 0;

  openRevisitFile(); // This is the revisit time open file call
  countPairs(nFields, start, len, pairTestMany, filt, count, &sum);
  revisit_table(6); // index 6 = griz, 5 would be y

  printf("\n");
  printf("         number of visits: %d\n", numobs);
  printf(" non-overlapping ");
  for(i=0; i<npairsFilters; i++) printf("%s", filtername[pairsFilters[i]]);
  printf(" pairs: %d\n", sum);

  valmax[filt] = -100000000;
  valmin[filt] = -valmax[filt];
  for(nf=0; nf<nFields; nf++) {
    valmax[filt] = MAX(valmax[filt],count[filt][nf]);
    valmin[filt] = MIN(valmin[filt],count[filt][nf]);
  }
  printf("  min, max of these pairs: %d, %d\n", (int) valmin[filt], (int) valmax[filt]);

  // save the colormap values to plot & the ra,dec of the fields
  for(nf=0; nf<nFields; nf++) {
    ravec[nf] = obs[start[nf]].ra;
    decvec[nf] = obs[start[nf]].dec;
    value[filt][nf] = (double) count[filt][nf];
  }

  tmpstr[0] = '\0';
  for(i=0; i<npairsFilters; i++) {
    sprintf(tstr,"%s",filtername[pairsFilters[i]]);
    strcat(tmpstr, tstr);
  }

  // number of lunations in run
  fac = (double)lengthDays/29.5;

  for(nf=0; nf<nFields; nf++) {
    ravec[nf] = obs[start[nf]].ra;
    decvec[nf] = obs[start[nf]].dec;
    value[0][nf] /= fac;
  }
  valmin[0] /= fac;
  valmax[0] /= fac;

  // number of lunations at night varies with declination.
  for(nf=0; nf<nFields; nf++) {
    value[0][nf] /= (1.0 - 0.5*cos(decvec[nf]));
  }
  valmax[0] *= 2.0;

  strcpy(label, "NEO pairs per lunation in ");
  strcat(label, tmpstr);
  strcpy(plotName,"revisit_");
  strcat(plotName,tmpstr);
  plotOne(nFields, value[filt], ravec, decvec, valmin[filt], valmax[filt], label, plotTitle, plotName);

  // now we do it all over again with all filters
  npairsFilters = 6; // so that it looks for pairs in all filters
  countPairs(nFields, start, len, pairTestMany, filt, count, &sum);
  revisit_table(7); // this is for all filters 7 = u,g,r,i,z,y (we are looking for pairs in all filters)
  
  // now do it all over again with individual filters
  for(filt=0; filt<NFILTERS; filt++) {
    countPairs(nFields, start, len, pairTestFilter, filt, count, &(sumbyfilter[filt]));
	revisit_table(filt);
  }
  doRevisitTimeStats();
  closeRevisitFile();

  // find the maximum number of observations
  for(filt=0; filt<NFILTERS; filt++) {
    valmax[filt] = -100000000;
    valmin[filt] = -valmax[filt];
    for(nf=0; nf<nFields; nf++) {
      valmax[filt] = MAX(valmax[filt],count[filt][nf]);
      valmin[filt] = MIN(valmin[filt],count[filt][nf]);
    }
  }

  printf("\nPair data:\n");
  printf("filter   # obs   # pairs   frac      min    max\n");
  for(filt=0; filt<NFILTERS; filt++) {
    sum = 0;
    for(i=0; i<numobs; i++) if(obs[i].filter==filt) sum++;
    if(sum>0) {
      printf("  %s     %6d    %6d   %4.2f      %3d    %3d\n",
             filtername[filt], sum, sumbyfilter[filt], 2.0*(double)sumbyfilter[filt]/(double)sum,
             (int) valmin[filt], (int) valmax[filt]);
    }
    else {
      printf("  %s     %6d    %6d     -       %3d    %3d\n",
             filtername[filt], sum, sumbyfilter[filt], 
             (int) valmin[filt], (int) valmax[filt]);
    }
  }
  printf("\n");

  // save the colormap values
  for(filt=0; filt<NFILTERS; filt++) {
    for(nf=0; nf<nFields; nf++) {
      value[filt][nf] = (double) count[filt][nf];
    }
  }

  // number of lunations in run
  fac = (double)lengthDays/29.5;

  for(nf=0; nf<nFields; nf++) {
    ravec[nf] = obs[start[nf]].ra;
    decvec[nf] = obs[start[nf]].dec;
    for(filt=0; filt<NFILTERS; filt++) value[filt][nf] /= fac;
  }
  for(filt=0; filt<NFILTERS; filt++) {
    valmin[filt] /= fac;
    valmax[filt] /= fac;
  }

  // number of lunations at night varies with declination.
  for(nf=0; nf<nFields; nf++) {
    for(filt=0; filt<NFILTERS; filt++) value[filt][nf] /= (1.0 - 0.5*cos(decvec[nf]));
  }
  for(filt=0; filt<NFILTERS; filt++) valmax[filt] *= 2.0;


  // now plot it up
  plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "NEO pairs per lunation", plotTitle, "revisit_all", 0);

  for(i=0; i<NFILTERS; i++) free(value[i]);
  free(value);
  free(decvec);
  free(ravec);
  for(i=0; i<NFILTERS; i++) free(count[i]);
  free(count);
  free(len);
  free(start);
}
