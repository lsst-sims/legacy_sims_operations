struct proposal {
	int propID;
	char propName[256];
	char propConf[256];
	double priority;
	int nUserRegions;
};
struct config {
	int configID;
	int sessionID;
	int propID;
	char moduleName[256];
	int paramIndex;
	char paramName[256];
	char paramValue[256];
	char comment[256];
};
struct config config_data[10000];
int config_data_length;
struct proposal proposal_list[100];
int proposal_list_length;

// make a single Aitoff sky projection plot
//   using the data in ravec[field], decvec[field], and value[filter][field],
//   using the min and max data values in valmin[filter] and valmax[filter]
//   with filter=0
void plotOne(double nfields, double *value,
             double *ravec, double *decvec,
             double valmin, double valmax,
             char *label, char *title, char *plotName) {
  int nf;
  double xmin, xmax, ymin, ymax;

  // set up the plot
  openPlot(plotName);
  cpgbbuf();

  cpgpap(PLOTSIZE/0.7,0.7);

  cpgsvp(0.02,0.98,0.02,0.98);

  xmax = M_PI;      xmin = -xmax;
  ymax = 0.67*M_PI; ymin = -ymax;
  ymin -= 0.1*ymax; ymax -= 0.1*ymax;

  setupImplot(0.0, 1.0);
  cpgswin(xmin,xmax,ymin,ymax);

  // make a projected field circle for each field
  cpgsch(1.0);
  for(nf=0; nf<nfields; nf++) {
    projCircle(ravec[nf], decvec[nf], FIELD_RADIUS, 
               (value[nf]-valmin)/(valmax-valmin));
  }
  // the grids and galactic exclusion
  aitoffGrid();
  galaxy(peakL, taperL, taperB);

  cpgslw(2);
  cpgsch(2.0);
  cpgswin(0,1,0,1);
  mywedg(0.21, 0.15, 1.0, 12.0, valmin, valmax, label);
  cpgptxt(0.5,0.95,0.0,0.5,title);
  cpgslw(1);

  cpgebuf();
  closePlot();
}


// make six Aitoff sky projection plots
//   using the data in ravec[field], decvec[field], and value[filter][field],
//   using the min and max data values in valmin[filter] and valmax[filter]
//   with filter=0 to NFILTERS-1
void plotSix(double nfields, double **value,
             double *ravec, double *decvec,
             double *valmin, double *valmax,
             int horizontal,
             char *label, char *title, char* plotName, int mask) {

	char str[1024];
	int filt, nf;
	double xmin, xmax, ymin, ymax;

	openPlot(plotName);
	cpgbbuf();

	if(horizontal==1) 
		cpgpap(PLOTSIZE/0.5,0.5); else cpgpap(PLOTSIZE/1.0,1.0);

	cpgsvp(0.02,0.98,0.15,0.95);
	xmax = 0.9*(M_PI);      
	xmin = -xmax;
	ymax = 0.9*(0.6*M_PI);  
	ymin = -ymax;
	ymin -= 0.18*ymax;      
	ymax -= 0.18*ymax;

	setupImplot(0.0, 1.0);

	if(horizontal==1) 
		cpgsubp(3,2); 
	else 
		cpgsubp(2,3);

	cpgsch(3.0); 
	cpgslw(2);

	for(filt=0; filt<NFILTERS; filt++) {
		int thereisdata = 0;
		for(nf=0; nf<nfields; nf++) {
			if (value[filt][nf] != 0.0) {
				thereisdata = 1;
			}
		}
		
		if ( thereisdata ) {
			if(horizontal==1) 
				cpgpanl(hpanelx[filt],hpanely[filt]); 
			else 
				cpgpanl(vpanelx[filt],vpanely[filt]);

			cpgswin(xmin,xmax,ymin,ymax);
			for(nf=0; nf<nfields; nf++) {
				if ( mask == 0 ) {
					if(value[filt][nf] > 0.0)
						projCircle(ravec[nf], decvec[nf], FIELD_RADIUS, (value[filt][nf]-valmin[filt])/(valmax[filt]-valmin[filt]));
				} else if ( mask == 1) {
					if(value[filt][nf] != 0.0)
						projCircle(ravec[nf], decvec[nf], FIELD_RADIUS, (value[filt][nf]-valmin[filt])/(valmax[filt]-valmin[filt]));
				}
			}
			aitoffGrid();
			galaxy(peakL, taperL, taperB);
			sprintf(str,"%s: %s", label, filtername[filt]);
			if(valmax[filt]>valmin[filt])
				mywedg(0.2, 0.15, 1.0, 8.0, valmin[filt], valmax[filt], str);
		}
	}

	cpgsch(1.0);
	cpgsubp(1,1);
	cpgswin(0,1,0,1);
	cpgptxt(0.5,1.02,0.0,0.5,title);
	cpgslw(1);    
	cpgebuf();

	closePlot();
}

#define NHIST 10
void visNumSix() {
  int i, j, filt, nf, nmax, nmin, sum, flag;
  int nFields, *start, *len, **count;
  int maxnum[NFILTERS];
  int hist[NFILTERS][NHIST], histmax[NFILTERS], histmin[NFILTERS], chist[NHIST], desired[NFILTERS], obsfilt[NFILTERS];
  double xmin, xmax, ymin, ymax;
  double *ravec, *decvec, **value, valmin[NFILTERS], valmax[NFILTERS], frac, least;
  FILE *out;
  char labstr[1024]; 

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

  /************************/
	int propID[50];
	int propIDcount = 0;
	for(i=0; i < proposal_list_length; i++) {
		if ( strcasestr(proposal_list[i].propConf, "Universal") != NULL && strcasestr(proposal_list[i].propConf, "Universalnorth") == NULL ) {
		// if ( strcasestr(proposal_list[i].propConf, "UniversalProp") != NULL ) {
			propID[propIDcount++] = proposal_list[i].propID;
		} 
	}

  // count the number of visits per field, per fiter
  for(nf=0; nf<nFields; nf++) {
    for(filt=0; filt<NFILTERS; filt++) {
		count[filt][nf]=0;
	}
    for(filt=0; filt<NFILTERS; filt++) {
      for(i=start[nf]; i<start[nf]+len[nf]; i++) {
		if(obs[i].filter==filt) {
			for(j=0; j < propIDcount; j++) {
				if ( obs[i].propid == propID[j] ) {
					count[filt][nf]++;
				}
			}
		}
	  }
	}
  }

  /************************/

  for(filt=0; filt<NFILTERS; filt++) {
    obsfilt[filt] = 0;
    for(nf=0; nf<nFields; nf++) obsfilt[filt] += count[filt][nf];
  }

  // find extrema
  printf("\nVisit counts:\n");
  printf("filter   # obs        min   max\n");
  for(filt=0; filt<NFILTERS; filt++) {
    nmin = 1000000;
    nmax = -nmin;
    for(nf=0; nf<nFields; nf++) {
      nmax = MAX(nmax,count[filt][nf]);
      nmin = MIN(nmin,count[filt][nf]);
    }
    printf("   %s     %6d   %6d %6d\n", filtername[filt], obsfilt[filt], nmin, nmax);
    valmax[filt] = nmax;
    valmin[filt] = 0.0;
  }

  // now fill the value array for plotting
  for(nf=0; nf<nFields; nf++) {
    ravec[nf] = obs[start[nf]].ra;
    decvec[nf] = obs[start[nf]].dec;
    for(filt=0; filt<NFILTERS; filt++) {
      value[filt][nf] = (double) count[filt][nf];
    }
  }

  // Actual Number range for 10-year survey
  for(filt=0; filt<NFILTERS; filt++) {
        double max = 0.0;
        for(nf=0; nf<nFields; nf++) {
                if ( value[filt][nf] > max ) {
                        max = value[filt][nf];
                }
        }
        valmax[filt] = max;
  }

  // make the plot for the raw numbers
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "acquired number of visits", plotTitle, "SixVisits-Num", 0);

  // Reference maximum from SRD for 10-year survey
  if ( useDesignStretch == 0 ) {
	  valmax[0] = 56;
	  valmax[1] = 80;
	  valmax[2] = 184;
	  valmax[3] = 184;
	  valmax[4] = 160;
	  valmax[5] = 160; 
  } else {
	  valmax[0] = 70;
	  valmax[1] = 100;
	  valmax[2] = 230;
	  valmax[3] = 230;
	  valmax[4] = 200;
	  valmax[5] = 200; 
  }

  // adjust the desired values for survey duration
  for(filt=0; filt<NFILTERS; filt++) valmax[filt] *= (endMJD-startMJD)/365.25/10.0;
  for(filt=0; filt<NFILTERS; filt++) desired[filt] = valmax[filt];

  for(nf=0; nf<nFields; nf++) {
    ravec[nf] = obs[start[nf]].ra;
    decvec[nf] = obs[start[nf]].dec;
    for(filt=0; filt<NFILTERS; filt++) {
      value[filt][nf] *= (100.0/desired[filt]);
    }
  }

  // This is for plotting now, we are standardizing for 70 - 110 
  for(filt=0; filt<NFILTERS; filt++) {
	valmin[filt] = 70.0;
    valmax[filt] = 110.0; 
  }

  // make the plot
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "% of WFD visits", plotTitle, "SixVisits", 0);

  // now make histograms of completion
  for(filt=0; filt<NFILTERS; filt++) for(j=0; j<NHIST; j++) hist[filt][j] = 0;
  for(filt=0; filt<NFILTERS; filt++) {
	histmax[filt] = 0;
	histmin[filt] = 0;
    for(nf=0; nf<nFields; nf++) {
	  if ((double)count[filt][nf]/(double)desired[filt] > 1.0 ) {
		histmax[filt]++;
	  } else if ( count[filt][nf] == 0 ) {
	  	histmin[filt]++;
      } else {
		i = (int)((double)count[filt][nf]*10.0/(double)desired[filt]);
        hist[filt][i]++;
	  }
    }
  }

  // intersection histogram
  for(j=0; j<NHIST; j++) {
    frac = (double)(j+1)/(double)NHIST;
    chist[j]=0;
    for(nf=0; nf<nFields; nf++) {
      flag = 1;
      for(filt=0; filt<NFILTERS; filt++) {
        if(count[filt][nf]<frac*desired[filt]) {
          flag = 0;
          break;
        }
      }
      if(flag==1) chist[j]++;
    }
  }

	/**
	* Making tex file for Six Visit
	*/
	FILE* tfp;
	char fName[80];
	char s[100];
	sprintf(fName, "../output/%s_%d_SixVisits.tex", hostname, sessionID);
	tfp = fopen(fName, "w");

	fprintf(tfp, "\\begin{table}[H]{\\textbf{Frequency Distribution of Fields with Completeness}} \\\\ [1.0ex]\n");
	fprintf(tfp, "\\begin{tabular*}{\\textwidth}{\\tblspace rrrrrrr}\n");
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\colhead{Percent Complete} &\n");
	fprintf(tfp, "\\colhead{u} &\n");
	fprintf(tfp, "\\colhead{g} &\n");
	fprintf(tfp, "\\colhead{r} &\n");
	fprintf(tfp, "\\colhead{i} &\n");
	fprintf(tfp, "\\colhead{z} &\n");
	fprintf(tfp, "\\colhead{y} \\\\ \n");
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\hline\n");

	fprintf(tfp, "$N \\ge 100$ & ");
	for (filt=0; filt<NFILTERS; filt++) {
		if ( filt == NFILTERS - 1) {
			fprintf(tfp, "%4d \\\\", histmax[filt]);
		}
		else {
			fprintf(tfp, "%4d &", histmax[filt]);
		}
	}
	fprintf(tfp, "\n");

	fprintf(quickfp, "SRD Fields &");
	for(j=NHIST-1; j>=0; j--) {
		if ( j==0 ) {
			sprintf(s, "~~$%d \\le N < %d$ & ", j * NHIST, (j+1) * NHIST);
		} else {
			sprintf(s, "$%d \\le N < %d$ & ", j * NHIST, (j+1) * NHIST);
		}
		fprintf(tfp, "%s", s);
		for (filt=0; filt<NFILTERS; filt++) {
			if ( j == 9 ) {
				if ( filt == NFILTERS - 1) {
					fprintf(quickfp, "%4d \\\\", hist[filt][j] + histmax[filt]);
				}
				else {
					fprintf(quickfp, "%4d &", hist[filt][j] + histmax[filt]);
				}
			}

			if ( filt == NFILTERS - 1) {
				fprintf(tfp, "%4d \\\\", hist[filt][j]);
			}
			else {
				fprintf(tfp, "%4d &", hist[filt][j]);
			}
		}
		fprintf(tfp, "\n");
	}
	/*fprintf(tfp, "~~~~~~~~~$N = 0$ & ");
	for (filt=0; filt<NFILTERS; filt++) {
		if ( filt == NFILTERS - 1) {
			fprintf(tfp, "%4d \\\\", histmin[filt]);
		}
		else {
			fprintf(tfp, "%4d &", histmin[filt]);
		}
	}
	fprintf(tfp, "\n");*/
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\end{tabular*}\n");
	fprintf(tfp, "\\caption{The distribution of the number of fields with a given completeness in 10 percent bins for each filter. A field's completeness is given by the ratio of the number of visits to that field compared to Scaled Design SRD number of visits - see Table 3. The values for N equals zero are not representative of the number of SRD proposal fields with no observations.}\n");
	fprintf(tfp, "\\label{tab:FreqNumTable}\n");
	fprintf(tfp, "\\end{table}\n");

	fflush(tfp);
	fclose(tfp);
	/**
	* End of Making tex file for Six Visit
	*/


  printf("\nField Completeness:\n");
  printf("        %% ");
  for(j=NHIST-1; j>=0; j--) printf("%4d ",(int)(100*(double)(j+1)/(double)NHIST));
  printf("\n");

  for(filt=0; filt<NFILTERS; filt++) {
    printf("%s    ",filtername[filt]);
    for(j=NHIST-1; j>=0; j--) printf("%4d ",hist[filt][j]);
    printf("\n");
  }

  printf("\nField Completeness (cumulative):\n");
  printf("        %% ");
  for(j=NHIST-1; j>=0; j--) printf("%4d ",(int)(100*(double)(j+1)/(double)NHIST));
  printf("\n");

  for(filt=0; filt<NFILTERS; filt++) {
    printf("%s    ",filtername[filt]);
    sum = 0;
    for(j=NHIST-1; j>=0; j--) {
      sum += hist[filt][j];
      printf("%4d ",sum);
      hist[filt][j] = sum;
    }
    printf("\n");
  }
  printf("all       ");
  for(j=NHIST-1; j>=0; j--) printf("%4d ",chist[j]);
  printf("\n");

  // plot of field completeness
  for(nf=0; nf<nFields; nf++) {
    least = 1.0;
    for(filt=0; filt<NFILTERS; filt++) {
      least = MIN(least,(double)count[filt][nf]/(double)desired[filt]);
    }
    value[0][nf] = least*100.0;
  }

  plotOne(nFields, value[0], ravec, decvec, 0.0, 100.0, "completed % in least-observed band", plotTitle, "completeness");

  for(i=0; i<NFILTERS; i++) free(value[i]);
  free(value);
  free(decvec);
  free(ravec);
  for(i=0; i<NFILTERS; i++) free(count[i]);
  free(count);
  free(len);
  free(start);
}

/*
ALL VISITS
*/
void visNumSixAll() {
  int i, j, filt, nf, nmax, nmin, sum, flag;
  int nFields, *start, *len, **count;
  int maxnum[NFILTERS];
  int hist[NFILTERS][NHIST], histmax[NFILTERS], histmin[NFILTERS], chist[NHIST], desired[NFILTERS], obsfilt[NFILTERS];
  double xmin, xmax, ymin, ymax;
  double *ravec, *decvec, **value, valmin[NFILTERS], valmax[NFILTERS], frac, least;
  FILE *out;
  char labstr[1024]; 

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
  // count the number of visits per field, per fiter
  for(nf=0; nf<nFields; nf++) {
    for(filt=0; filt<NFILTERS; filt++) count[filt][nf]=0;
    for(filt=0; filt<NFILTERS; filt++)
      for(i=start[nf]; i<start[nf]+len[nf]; i++)
		if(obs[i].filter==filt) {
			count[filt][nf]++;
		} 
  }

  for(filt=0; filt<NFILTERS; filt++) {
    obsfilt[filt] = 0;
    for(nf=0; nf<nFields; nf++) obsfilt[filt] += count[filt][nf];
  }

  // now fill the value array for plotting
  for(nf=0; nf<nFields; nf++) {
    ravec[nf] = obs[start[nf]].ra;
    decvec[nf] = obs[start[nf]].dec;
    for(filt=0; filt<NFILTERS; filt++) {
      value[filt][nf] = (double) count[filt][nf];
    }
  }

  // Reference maximum from SRD for 10-year survey
  if ( useDesignStretch == 0 ) {
	  valmax[0] = 56;
	  valmax[1] = 80;
	  valmax[2] = 184;
	  valmax[3] = 184;
	  valmax[4] = 160;
	  valmax[5] = 160; 
  } else {
	  valmax[0] = 70;
	  valmax[1] = 100;
	  valmax[2] = 230;
	  valmax[3] = 230;
	  valmax[4] = 200;
	  valmax[5] = 200; 
  } 

  // adjust the desired values for survey duration
  for(filt=0; filt<NFILTERS; filt++) valmax[filt] *= (endMJD-startMJD)/365.25/10.0;
  for(filt=0; filt<NFILTERS; filt++) desired[filt] = valmax[filt];


  // 120% SRD for 10-year survey
  for(filt=0; filt<NFILTERS; filt++) {
        valmax[filt] = 1.2 * desired[filt]; // 120% of SRD numbers
		valmin[filt] = 0.0;
  }

  // make the plot for the raw numbers
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "acquired number of visits", plotTitle, "SixVisitsAll-Num", 0);

  for(nf=0; nf<nFields; nf++) {
    ravec[nf] = obs[start[nf]].ra;
    decvec[nf] = obs[start[nf]].dec;
    for(filt=0; filt<NFILTERS; filt++) {
      value[filt][nf] *= (100.0/desired[filt]);
    }
  }

	// This is for plotting now, we are standardizing for 50 - 120 
	for(filt=0; filt<NFILTERS; filt++) {
		valmin[filt] = 50.0;
		valmax[filt] = 120.0; 
	}
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "% of WFD visits", plotTitle, "SixVisits-All", 0);

  // now make histograms of completion
  for(filt=0; filt<NFILTERS; filt++) for(j=0; j<NHIST; j++) hist[filt][j] = 0;
  for(filt=0; filt<NFILTERS; filt++) {
	histmax[filt] = 0;
	histmin[filt] = 0;
    for(nf=0; nf<nFields; nf++) {
	  if ((double)count[filt][nf]/(double)desired[filt] > 1.0 ) {
		histmax[filt]++;
	  } else if ( count[filt][nf] == 0 ) {
	  	histmin[filt]++;
      } else {
		i = (int)((double)count[filt][nf]*10.0/(double)desired[filt]);
        hist[filt][i]++;
	  }
    }
  }

  // intersection histogram
  for(j=0; j<NHIST; j++) {
    frac = (double)(j+1)/(double)NHIST;
    chist[j]=0;
    for(nf=0; nf<nFields; nf++) {
      flag = 1;
      for(filt=0; filt<NFILTERS; filt++) {
        if(count[filt][nf]<frac*desired[filt]) {
          flag = 0;
          break;
        }
      }
      if(flag==1) chist[j]++;
    }
  }

	/**
	* Making tex file for Six Visit
	*/
	FILE* tfp;
	char fName[80];
	char s[100];
	sprintf(fName, "../output/%s_%d_SixVisits-All.tex", hostname, sessionID);
	tfp = fopen(fName, "w");

	fprintf(tfp, "\\begin{table}[H]{\\textbf{Frequency Distribution of Fields with Completeness}} \\\\ [1.0ex]\n");
	fprintf(tfp, "\\begin{tabular*}{\\textwidth}{\\tblspace rrrrrrr}\n");
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\colhead{Percent Complete} &\n");
	fprintf(tfp, "\\colhead{u} &\n");
	fprintf(tfp, "\\colhead{g} &\n");
	fprintf(tfp, "\\colhead{r} &\n");
	fprintf(tfp, "\\colhead{i} &\n");
	fprintf(tfp, "\\colhead{z} &\n");
	fprintf(tfp, "\\colhead{y} \\\\ \n");
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\hline\n");

	fprintf(tfp, "$N \\ge 100$ & ");
	for (filt=0; filt<NFILTERS; filt++) {
		if ( filt == NFILTERS - 1) {
			fprintf(tfp, "%4d \\\\", histmax[filt]);
		}
		else {
			fprintf(tfp, "%4d &", histmax[filt]);
		}
	}
	fprintf(tfp, "\n");

	fprintf(quickfp, "All Fields &");
	for(j=NHIST-1; j>=0; j--) {
		if ( j==0 ) {
			sprintf(s, "~~$%d \\le N < %d$ & ", j * NHIST, (j+1) * NHIST);
		} else {
			sprintf(s, "$%d \\le N < %d$ & ", j * NHIST, (j+1) * NHIST);
		}
		fprintf(tfp, "%s", s);
		for (filt=0; filt<NFILTERS; filt++) {
			if ( j == 9 ) {
				if ( filt == NFILTERS - 1) {
					fprintf(quickfp, "%4d \\\\", hist[filt][j] + histmax[filt]);
				}
				else {
					fprintf(quickfp, "%4d &", hist[filt][j] + histmax[filt]);
				}
			}

			if ( filt == NFILTERS - 1) {
				fprintf(tfp, "%4d \\\\", hist[filt][j]);
			}
			else {
				fprintf(tfp, "%4d &", hist[filt][j]);
			}
		}
		fprintf(tfp, "\n");
	}
	/*fprintf(tfp, "~~~~~~~~~$N = 0$ & ");
	for (filt=0; filt<NFILTERS; filt++) {
		if ( filt == NFILTERS - 1) {
			fprintf(tfp, "%4d \\\\", histmin[filt]);
		}
		else {
			fprintf(tfp, "%4d &", histmin[filt]);
		}
	}
	fprintf(tfp, "\n");*/
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\end{tabular*}\n");
	fprintf(tfp, "\\caption{The distribution of the number of fields with a given completeness for each filter. A fields completeness is given by the ratio of the number of visits to that field compared to the Scaled Design SRD number of visits. The N equals zero bin does not accurately represent the number of fields with no observations.}\n");
	fprintf(tfp, "\\label{tab:FreqNumTable}\n");
	fprintf(tfp, "\\end{table}\n");

	fflush(tfp);
	fclose(tfp);
	/**
	* End of Making tex file for Six Visit
	*/


  printf("\nField Completeness:\n");
  printf("        %% ");
  for(j=NHIST-1; j>=0; j--) printf("%4d ",(int)(100*(double)(j+1)/(double)NHIST));
  printf("\n");

  for(filt=0; filt<NFILTERS; filt++) {
    printf("%s    ",filtername[filt]);
    for(j=NHIST-1; j>=0; j--) printf("%4d ",hist[filt][j]);
    printf("\n");
  }

  printf("\nField Completeness (cumulative):\n");
  printf("        %% ");
  for(j=NHIST-1; j>=0; j--) printf("%4d ",(int)(100*(double)(j+1)/(double)NHIST));
  printf("\n");

  for(filt=0; filt<NFILTERS; filt++) {
    printf("%s    ",filtername[filt]);
    sum = 0;
    for(j=NHIST-1; j>=0; j--) {
      sum += hist[filt][j];
      printf("%4d ",sum);
      hist[filt][j] = sum;
    }
    printf("\n");
  }
  printf("all       ");
  for(j=NHIST-1; j>=0; j--) printf("%4d ",chist[j]);
  printf("\n");

  // plot of field completeness
  for(nf=0; nf<nFields; nf++) {
    least = 1.0;
    for(filt=0; filt<NFILTERS; filt++) {
      least = MIN(least,(double)count[filt][nf]/(double)desired[filt]);
    }
    value[0][nf] = least*100.0;
  }

  plotOne(nFields, value[0], ravec, decvec, 0.0, 100.0, "completed % in least-observed band", plotTitle, "completeness-all");

  for(i=0; i<NFILTERS; i++) free(value[i]);
  free(value);
  free(decvec);
  free(ravec);
  for(i=0; i<NFILTERS; i++) free(count[i]);
  free(count);
  free(len);
  free(start);
}
/*
END OF ALL VISITS
*/

/**
plot the colormap of the number of visits per field in each filter per PROPOSAL
**/


char* getConfigValue(char* pName) {
	int i;
	for(i=0; i < config_data_length; i++) {
		if ( strcmp(config_data[i].paramName, pName) == 0 ) {
			return config_data[i].paramValue;
		}
	}
	return "?";
}

struct filtervalue {
	int size; // the first value will keep how many filtervals there are
	char value[256];
};

struct filtervalue* getFilterValues(char* pName, int propID) {
	struct filtervalue* fv = (struct filtervalue*)malloc(6 * sizeof(struct filtervalue));
	int i=0, j=0;
	for(i=0; i < 6; i++) {
		bzero(fv[i].value, 256);
	}
	
	for(i=0; i < config_data_length; i++) {
		if ( strcmp(config_data[i].paramName, pName) == 0 && propID == config_data[i].propID ) {
			strcpy(fv[j].value, config_data[i].paramValue);
			j++; 
		}
	}
	fv[0].size = j;
	return fv;
}

void visNumSixWith(int propID, struct filtervalue* filters, struct filtervalue* requiredvisits) {
	int i, j, filt, nf, nmax, nmin, sum, flag;
	int nFields, *start, *len, **count;
	int maxnum[NFILTERS];
	int hist[NFILTERS][NHIST], chist[NHIST], desired[NFILTERS], obsfilt[NFILTERS];
	double xmin, xmax, ymin, ymax;
	double *ravec, *decvec, **value, valmin[NFILTERS], valmax[NFILTERS], frac, least;
	FILE *out;
	char labstr[1024]; 

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

	// count the number of visits per field, per fiter per proposal
	for(nf=0; nf<nFields; nf++) {
		for(filt=0; filt<NFILTERS; filt++) count[filt][nf]=0;
		for(filt=0; filt<NFILTERS; filt++)
			for(i=start[nf]; i<start[nf]+len[nf]; i++)
				if(obs[i].filter==filt && obs[i].propid==propID) count[filt][nf]++;
	}

	for(filt=0; filt<NFILTERS; filt++) {
		valmin[filt] = 0.0;
		valmax[filt] = 0.0;
		obsfilt[filt] = 0;
		for(nf=0; nf<nFields; nf++) obsfilt[filt] += count[filt][nf];
	}

	// REQUIRED VISITS FOR EACH PROPOSAL
	if ( filters != NULL && requiredvisits != NULL) {
		for(filt=0; filt<filters[0].size; filt++) {
			if ( strcmp(filters[filt].value, "u") == 0 ) {
				valmax[0] = atof(requiredvisits[filt].value); 
			} else if ( strcmp(filters[filt].value, "g") == 0 ) {
				valmax[1] = atof(requiredvisits[filt].value);
			} else if ( strcmp(filters[filt].value, "r") == 0 ) {
				valmax[2] = atof(requiredvisits[filt].value);
			} else if ( strcmp(filters[filt].value, "i") == 0 ) {
				valmax[3] = atof(requiredvisits[filt].value);
			} else if ( strcmp(filters[filt].value, "z") == 0 ) {
				valmax[4] = atof(requiredvisits[filt].value);
			} else if ( strcmp(filters[filt].value, "y") == 0 ) {
				valmax[5] = atof(requiredvisits[filt].value);
			}
		}
		if ( filters[0].size == 1 ) {
			valmax[0] = atof(requiredvisits[0].value); 
			valmax[1] = atof(requiredvisits[0].value); 
			valmax[2] = atof(requiredvisits[0].value); 
			valmax[3] = atof(requiredvisits[0].value); 
			valmax[4] = atof(requiredvisits[0].value); 
			valmax[5] = atof(requiredvisits[0].value); 	
		}
	} else {
		for(filt=0; filt<NFILTERS; filt++) {
			double max = 0.0;
			for(nf=0; nf<nFields; nf++) {
				for(i=start[nf]; i<start[nf]+len[nf]; i++) {
					if ( count[filt][nf] > max ) {
						max = (double)count[filt][nf];
					}
				}
			}
			valmax[filt] = max;
		}
	}
	// END OF REQUIRED VISITS FOR EACH PROPOSAL

	// adjust the desired values for survey duration
	//for(filt=0; filt<NFILTERS; filt++) valmax[filt] *= (endMJD-startMJD)/365.25/10.0;
	//for(filt=0; filt<NFILTERS; filt++) desired[filt] = valmax[filt];

	// now fill the value array for plotting
	for(nf=0; nf<nFields; nf++) {
		ravec[nf] = obs[start[nf]].ra;
		decvec[nf] = obs[start[nf]].dec;
		for(filt=0; filt<NFILTERS; filt++) {
			value[filt][nf] = (double) count[filt][nf];
		}
	}

	char* fileName = (char*)malloc(100);
	sprintf(fileName, "SixVisits-Num-%d", propID);
	// make the plot for the raw numbers
    char* xlabel = (char*)malloc(100);
    if ( filters != NULL && requiredvisits != NULL) {
        sprintf(xlabel, "%s", "requested number of visits");
    } else {
        sprintf(xlabel, "%s", "acquired number of visits");
    }
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, xlabel, plotTitle, fileName, 0);

	/*for(nf=0; nf<nFields; nf++) {
		ravec[nf] = obs[start[nf]].ra;
		decvec[nf] = obs[start[nf]].dec;
		for(filt=0; filt<NFILTERS; filt++) {
			value[filt][nf] *= (100.0/desired[filt]);
		}
	}

	for(filt=0; filt<NFILTERS; filt++) {
		valmax[filt] = 110.0; 
		valmin[filt] = 70.0;
	}

	// make the plot  
	sprintf(fileName, "SixVisits-%d", propID);
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "% of requested visits", plotTitle, fileName, 0);

	for(i=0; i<NFILTERS; i++) free(value[i]);
	free(value);
	free(decvec);
	free(ravec);
	for(i=0; i<NFILTERS; i++) free(count[i]);
	free(count);
	free(len);
	free(start);*/
}
/**
END OF plot the colormap of the number of visits per field in each filter per PROPOSAL
**/

/**
VisitNumSix
**/

void readConfigData() {
	int i, k, flag;
	char sql[1024];
	
	sprintf(sql, "select configID, Session_sessionID as sessionID, nonPropID, moduleName, paramIndex, paramName, paramValue, comment from Config where Session_sessionID=%d;", sessionID);

	MYSQL_STMT *stmt;
	MYSQL_BIND bind[8];
	my_bool error[8];
	
	struct config cbuffer;

	//fprintf(stderr , "forming query..");
	if( (stmt = mysql_stmt_init(&mysql))== (MYSQL_STMT *) NULL) {
		fprintf(stderr,"error in mysql_stmt_init: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	flag = mysql_stmt_prepare(stmt, sql, strlen(sql));
	if(flag!=0) {
		fprintf(stderr,"error in mysql_stmt_prepare: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	memset(bind, 0, sizeof(bind));

	i = 0;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(cbuffer.configID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(cbuffer.sessionID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(cbuffer.propID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(cbuffer.moduleName);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(cbuffer.paramIndex);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(cbuffer.paramName);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(cbuffer.paramValue);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(cbuffer.comment);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	
	flag = mysql_stmt_bind_result(stmt, bind);
	if(flag!=0) {
		fprintf(stderr, "error in mysql_stmt_bind_result: %s", mysql_stmt_error(stmt));
		exit(1);
	}

	//fprintf(stderr,"executing query..");
	flag = mysql_stmt_execute(stmt);
	if(flag!=0) {
		fprintf(stderr, "error in mysql_stmt_execute: %s", mysql_stmt_error(stmt));
		exit(1);
	}

	//fprintf(stderr,"executed query..");
	
	flag = mysql_stmt_store_result(stmt);
	if(flag!=0) {
		fprintf(stderr, "error in mysql_stmt_store_result: %s", mysql_stmt_error(stmt));
		exit(1);
	}
	
	//fprintf(stderr,"stored result..");
	config_data_length = mysql_stmt_num_rows(stmt);
	//fprintf(stderr,"reading %d config_data..", config_data_length);

	i = 0;
	flag = 0;
	while(flag==0) {
		flag = mysql_stmt_fetch(stmt);
		if(flag!=0) {
			if(flag == MYSQL_NO_DATA) {
				//fprintf(stderr,"done fetching data..");
				flag = 1;
			}
			else if(flag == MYSQL_DATA_TRUNCATED) {
				flag = 1;
				for(k=0; k<10; k++) {
					if(error[k]!=0) printf("fetching data truncated in parameter %d\n",k);
				}
			}
			else {
				fprintf(stderr, "error in mysql_stmt_fetch: %s\n", mysql_stmt_error(stmt));
				exit(1);
			}
		}
	
		if(flag==0) {
			memcpy(&(config_data[i]), &(cbuffer), sizeof(struct config));
			i++;
		}
	}
	
	mysql_stmt_close(stmt);
	//fprintf(stderr,"done\n");

	/*for(i=0; i < config_data_length; i++) {
		printf("%d %d %d %s %d %s %s %s\n",
			config_data[i].configID,
			config_data[i].sessionID,
			config_data[i].propID,
			config_data[i].moduleName,
			config_data[i].paramIndex,
			config_data[i].paramName,
			config_data[i].paramValue,
			config_data[i].comment);
	}*/
}

void readProposalData() {
	int i, k, flag;
	char sql[1024];
	
	sprintf(sql, "select Proposal.propID as propID, propName, propConf, t3.Priority as priority, coalesce(userRegions, 0) as nUserRegions from Proposal, (select t2.propID, Priority, userRegions  from (select count(*) as userRegions, nonPropID as propID from Config where Session_sessionID=%d and paramName='userRegion' group by propID) t1 RIGHT OUTER JOIN (select paramValue as Priority, nonPropID as propID from Config where Session_sessionID=%d and paramName='RelativeProposalPriority' group by propID ) t2 ON t1.propID=t2.propID) t3 where Proposal.propID=t3.propID;", sessionID, sessionID);

	MYSQL_STMT *stmt;
	MYSQL_BIND bind[5];
	my_bool error[5];
	
	struct proposal pbuffer;

	//fprintf(stderr , "forming query..");
	if( (stmt = mysql_stmt_init(&mysql))== (MYSQL_STMT *) NULL) {
		fprintf(stderr,"error in mysql_stmt_init: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	flag = mysql_stmt_prepare(stmt, sql, strlen(sql));
	if(flag!=0) {
		fprintf(stderr,"error in mysql_stmt_prepare: %s\n", mysql_stmt_error(stmt));
		exit(1);
	}

	memset(bind, 0, sizeof(bind));

	i = 0;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(pbuffer.propID);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(pbuffer.propName);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_STRING;
	bind[i].buffer = &(pbuffer.propConf);
	bind[i].buffer_length = 256;
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_DOUBLE;
	bind[i].buffer = &(pbuffer.priority);
	bind[i].error = &error[i];
	i++;
	bind[i].buffer_type = FIELD_TYPE_LONG;
	bind[i].buffer = &(pbuffer.nUserRegions);
	bind[i].error = &error[i];

	flag = mysql_stmt_bind_result(stmt, bind);
	if(flag!=0) {
		fprintf(stderr, "error in mysql_stmt_bind_result: %s", mysql_stmt_error(stmt));
		exit(1);
	}

	//fprintf(stderr,"executing query..");
	flag = mysql_stmt_execute(stmt);
	if(flag!=0) {
		fprintf(stderr, "error in mysql_stmt_execute: %s", mysql_stmt_error(stmt));
		exit(1);
	}

	//fprintf(stderr,"executed query..");
	flag = mysql_stmt_store_result(stmt);
	if(flag!=0) {
		fprintf(stderr, "error in mysql_stmt_store_result: %s", mysql_stmt_error(stmt));
		exit(1);
	}
	
	//fprintf(stderr,"stored result..");
	proposal_list_length = mysql_stmt_num_rows(stmt);
	//fprintf(stderr,"reading %d proposals..", proposal_list_length);

	i = 0;
	flag = 0;
	while(flag==0) {
		flag = mysql_stmt_fetch(stmt);
		if(flag!=0) {
			if(flag == MYSQL_NO_DATA) {
				//fprintf(stderr,"done fetching data..");
				flag = 1;
			}
			else if(flag == MYSQL_DATA_TRUNCATED) {
				flag = 1;
				for(k=0; k<10; k++) {
					if(error[k]!=0) printf("fetching data truncated in parameter %d\n",k);
				}
			}
			else {
				fprintf(stderr, "error in mysql_stmt_fetch: %s\n", mysql_stmt_error(stmt));
				exit(1);
			}
		}
	
		if(flag==0) {
			memcpy(&(proposal_list[i]), &(pbuffer), sizeof(struct proposal));
			i++;
		}
	}
	
	mysql_stmt_close(stmt);
	//fprintf(stderr,"done\n");
}

void doVisNumSixByProposal() 
{
	int i;
	for(i=0; i < proposal_list_length; i++) {
		if ( strcmp(proposal_list[i].propName, "WL") == 0 ) {
			struct filtervalue* f = getFilterValues("Filter", proposal_list[i].propID);
			struct filtervalue* fv = getFilterValues("Filter_Visits", proposal_list[i].propID);
			//printf("WL [%s] filters=%s[%d] visits=%s\n", proposal_list[i].propConf, f->value, f->size, fv->value);
			visNumSixWith(proposal_list[i].propID, f, fv);		
		} else if ( strcmp(proposal_list[i].propName, "SNSS") == 0 ) {
			struct filtervalue* ssexposures = getFilterValues("SubSeqExposures", proposal_list[i].propID);
			struct filtervalue* ssfilters = getFilterValues("SubSeqFilters", proposal_list[i].propID);
			struct filtervalue* ssevents = getFilterValues("SubSeqEvents", proposal_list[i].propID);
			visNumSixWith(proposal_list[i].propID, NULL, NULL);
			//printf("SNSS [%s] exps=%s filters=%s[%d] events=%s\n", proposal_list[i].propConf, ssexposures->value, ssfilters->value, ssfilters->size, ssevents->value);
		} else if ( strcmp(proposal_list[i].propName, "NEA") == 0 ) {
			//printf("NEA [%s]\n", proposal_list[i].propConf);
			visNumSixWith(proposal_list[i].propID, NULL, NULL);
		} else if ( strcmp(proposal_list[i].propName, "WLTSS") == 0 ) {
			struct filtervalue* ssexposures = getFilterValues("SubSeqExposures", proposal_list[i].propID);
			struct filtervalue* ssfilters = getFilterValues("SubSeqFilters", proposal_list[i].propID);
			struct filtervalue* ssevents = getFilterValues("SubSeqEvents", proposal_list[i].propID);
            		int j;
            		for(j=0; j < ssfilters->size; j++) {
                		sprintf(ssexposures[j].value, "%f", atof(ssexposures[j].value) * atof(ssevents[j].value));
           		}
			visNumSixWith(proposal_list[i].propID, ssfilters, ssexposures);
			/*printf("WLTSS [%s] exps=%s filters=%s[%d] events=%s\n", proposal_list[i].propConf, ssexposures->value,  ssfilters->value, ssfilters->size, ssevents->value);*/
		}
	}
}

