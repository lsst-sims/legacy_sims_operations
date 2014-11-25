// plot the maximum or median airmass per field in each filter
void airmassPlot(void) {
  int i, j, filt, nf, nmax, nmin, sum, flag;
  int nFields, *start, *len, **count;
  int maxnum[NFILTERS];
  double xmin, xmax, ymin, ymax;
  double *ravec, *decvec, **value, valmin[NFILTERS], valmax[NFILTERS], frac, least;
  double trueam, alt, ha;

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

  for(nf=0; nf<nFields; nf++) {
    ravec[nf] = obs[start[nf]].ra;
    decvec[nf] = obs[start[nf]].dec;
  }

  if(useMaxAirmass==1) {
    // get max airmass per field, per fiter
    for(nf=0; nf<nFields; nf++) {
      for(filt=0; filt<NFILTERS; filt++) value[filt][nf]=0;
      for(filt=0; filt<NFILTERS; filt++) {
        for(i=start[nf]; i<start[nf]+len[nf]; i++) {
          if(obs[i].filter==filt) {
            airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);
            value[filt][nf] = MAX(trueam, value[filt][nf]);
          }
        }
      }
    }
    // set x color limits
    for(filt=0; filt<NFILTERS; filt++) {
      valmax[filt] = 2.0;
      valmin[filt] = 1.0;
    }
    
    // make the plot
    plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "maximum airmass", plotTitle, "maxairmass", 0);
  }
  else {
    // get median airmass per field, per fiter
    for(nf=0; nf<nFields; nf++) {
      for(filt=0; filt<NFILTERS; filt++) value[filt][nf]=0;
      for(filt=0; filt<NFILTERS; filt++) {
		median_data_length = 0;
        for(i=start[nf]; i<start[nf]+len[nf]; i++) {
          if(obs[i].filter==filt) {
            airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);
            median_data[median_data_length++] = trueam;
          }
        }
		double temp;
		for(i = median_data_length-1; i>=0; i--) {
			for(j=1; j<=i; j++) {
				if ( median_data[j-1] > median_data[j]) {
					temp = median_data[j-1];
					median_data[j-1] = median_data[j];
					median_data[j] = temp;
				}
			}
		}
        for(i=start[nf]; i<start[nf]+len[nf]; i++) {
          if(obs[i].filter==filt) {
			value[filt][nf] = median_data[median_data_length/2];
		  }
		}
      }
    }
    // set x color limits
    for(filt=0; filt<NFILTERS; filt++) {
      valmax[filt] = 1.6;
      valmin[filt] = 1.0;
    }
    
    // make the plot
    plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "median airmass", plotTitle, "medianairmass", 0);
  }

  for(i=0; i<NFILTERS; i++) free(value[i]);
  free(value);
  free(decvec);
  free(ravec);
  for(i=0; i<NFILTERS; i++) free(count[i]);
  free(count);
  free(len);
  free(start);
}

void airmassPlotbyProposal(int propID) {
  int i, j, filt, nf, nmax, nmin, sum, flag;
  int nFields, *start, *len, **count;
  int maxnum[NFILTERS];
  double xmin, xmax, ymin, ymax;
  double *ravec, *decvec, **value, valmin[NFILTERS], valmax[NFILTERS], frac, least;
  double trueam, alt, ha;

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

  for(nf=0; nf<nFields; nf++) {
    ravec[nf] = obs[start[nf]].ra;
    decvec[nf] = obs[start[nf]].dec;
  }

  for(filt=0; filt<NFILTERS; filt++) {
    valmax[filt] = 3.0;
    valmin[filt] = 1.0;
  }
  
  char* fileName = (char*)malloc(100);
  if(useMaxAirmass==1) {
    // get max airmass per field, per fiter
    for(nf=0; nf<nFields; nf++) {
      for(filt=0; filt<NFILTERS; filt++) value[filt][nf]=0;
      for(filt=0; filt<NFILTERS; filt++) {
        for(i=start[nf]; i<start[nf]+len[nf]; i++) {
          if(obs[i].filter==filt && obs[i].propid == propID) {
            airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);
            value[filt][nf] = MAX(trueam, value[filt][nf]);
          }
        }
      }
    }

    sprintf(fileName, "maxairmass-%d", propID);
    // make the plot
    plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "maximum airmass", plotTitle, fileName, 0);
  }
  else {
    // get average airmass per field, per fiter
    for(nf=0; nf<nFields; nf++) {
      for(filt=0; filt<NFILTERS; filt++) value[filt][nf]=0;
      for(filt=0; filt<NFILTERS; filt++) count[filt][nf]=0;
      for(filt=0; filt<NFILTERS; filt++) {
		median_data_length = 0;
        for(i=start[nf]; i<start[nf]+len[nf]; i++) {
          if(obs[i].filter==filt && obs[i].propid == propID) {
            airmass(obs[i].date, obs[i].ra, obs[i].dec, &trueam, &alt, &ha);
			median_data[median_data_length++] = trueam;
          }
        }
		double temp;
		for(i = median_data_length-1; i>=0; i--) {
			for(j=1; j<=i; j++) {
				if ( median_data[j-1] > median_data[j]) {
					temp = median_data[j-1];
					median_data[j-1] = median_data[j];
					median_data[j] = temp;
				}
			}
		}
        for(i=start[nf]; i<start[nf]+len[nf]; i++) {
          if(obs[i].filter==filt && obs[i].propid == propID) {
			value[filt][nf] = median_data[median_data_length/2];
		  }
		}	
      }
    }

    sprintf(fileName, "medianairmass-%d", propID);
    // make the plot
    plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "median airmass", plotTitle, fileName, 0);
  }

  for(i=0; i<NFILTERS; i++) free(value[i]);
  free(value);
  free(decvec);
  free(ravec);
  for(i=0; i<NFILTERS; i++) free(count[i]);
  free(count);
  free(len);
  free(start);
}

void doAirmassPlotbyProposal() {
	int i;

	for(i=0; i < proposal_list_length; i++) {
		airmassPlotbyProposal(proposal_list[i].propID);
	}
}

