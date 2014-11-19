void seeingPlot() {
	int i, j, filt, nf, nmax, nmin, sum, flag;
	int nFields, *start, *len, **count, **countAll;
	int maxnum[NFILTERS];
	int hist[NFILTERS][NHIST], histmax[NFILTERS], histmin[NFILTERS], desired[NFILTERS];
	double xmin, xmax, ymin, ymax;
	double *ravec, *decvec, **value, valmin[NFILTERS], valmax[NFILTERS], frac, least;
	double trueam, alt, ha;
	
	start = malloc((numFields+1)*sizeof(int));
	len = malloc(numFields*sizeof(int));
	ravec = malloc(numFields*sizeof(double));
	decvec =malloc(numFields*sizeof(double));
	count = malloc(NFILTERS*sizeof(int *));
	countAll = malloc(NFILTERS*sizeof(int *));
	for(i=0; i<NFILTERS; i++) {
		count[i] = malloc(numFields*sizeof(int));
		countAll[i] = malloc(numFields*sizeof(int));
	}
	value = malloc(NFILTERS*sizeof(double *));
	for(i=0; i<NFILTERS; i++) value[i] = malloc(numFields*sizeof(double));
	
	// order visits by field and get pointers
	getFieldData(&nFields, start, len);

	for(nf=0; nf<nFields; nf++) {
		ravec[nf] = obs[start[nf]].ra;
		decvec[nf] = obs[start[nf]].dec;
	}
	
	for(filt=0; filt<NFILTERS; filt++) {
		valmax[filt] = 1.5;
		valmin[filt] = 0.8;
	}
	
	double required_scaled_m5[NFILTERS];
	if ( useDesignStretch == 0 ) {
		required_scaled_m5[0] = 23.9;
		required_scaled_m5[1] = 25.0;
		required_scaled_m5[2] = 24.7;
		required_scaled_m5[3] = 24.0;
		required_scaled_m5[4] = 23.3;
		required_scaled_m5[5] = 22.1;
    } else {
		required_scaled_m5[0] = 24.0;
		required_scaled_m5[1] = 25.1;
		required_scaled_m5[2] = 24.8;
		required_scaled_m5[3] = 24.1;
		required_scaled_m5[4] = 23.4;
		required_scaled_m5[5] = 22.2;
    }

	for(nf=0; nf<nFields; nf++) {
		for(filt=0; filt<NFILTERS; filt++) {
			value[filt][nf]=0;
			count[filt][nf]=0;
			countAll[filt][nf]=0;
		}

		for(filt=0; filt<NFILTERS; filt++) {
			median_data_length = 0;
			for(i=start[nf]; i<start[nf]+len[nf]; i++) {
				if(obs[i].filter == filt) {
					countAll[filt][nf]++;
					median_data[median_data_length++] = obs[i].seeing;
					// We should be counting only those ( m5 > (m5(srd) - 0.5))
					if (filt == 0) { // u
						if ( obs[i].etc_m5 > (required_scaled_m5[0] - 0.5) && obs[i].seeing / 0.77 < 1.5) {
							count[filt][nf]++;
						}
					} else if (filt == 1) { // g
						if ( obs[i].etc_m5 > (required_scaled_m5[1] - 0.5) && obs[i].seeing / 0.73 < 1.5) {
							count[filt][nf]++;						
						}
					} else if (filt == 2) { // r
						if ( obs[i].etc_m5 > (required_scaled_m5[2] - 0.5) && obs[i].seeing / 0.70 < 1.5) {
							count[filt][nf]++;
						}
					} else if (filt == 3) { // i
						if ( obs[i].etc_m5 > (required_scaled_m5[3] - 0.5) && obs[i].seeing / 0.67 < 1.5) {
							count[filt][nf]++;
						}
					} else if (filt == 4) { // z
						if ( obs[i].etc_m5 > (required_scaled_m5[4] - 0.5) && obs[i].seeing / 0.65 < 1.5) {
							count[filt][nf]++;
						}
					} else if (filt == 5) { // y
						if ( obs[i].etc_m5 > (required_scaled_m5[5] - 0.5) && obs[i].seeing / 0.63 < 1.5) {
							count[filt][nf]++;
						}
					}
				}
			}
			
			// sort the median_data values
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
					// By request of Bug 59 : SSTAR (SRD expected median zenith seeing from document - Table 2)
					if (filt == 0) { // u
						value[filt][nf] /= 0.77;
					} else if (filt == 1) { // g
						value[filt][nf] /= 0.73;
					} else if (filt == 2) { // r
						value[filt][nf] /= 0.70;
					} else if (filt == 3) { // i
						value[filt][nf] /= 0.67;
					} else if (filt == 4) { // z
						value[filt][nf] /= 0.65;
					} else if (filt == 5) { // y
						value[filt][nf] /= 0.63;
					}
				}
			}
		}
	}
	
	// make the plot
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "median seeing", plotTitle, "medianseeing", 1);

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

	for(filt=0; filt<NFILTERS; filt++) valmax[filt] *= (endMJD-startMJD)/365.25/10.0;
	for(filt=0; filt<NFILTERS; filt++) desired[filt] = valmax[filt];

	for(filt=0; filt<NFILTERS; filt++) for(j=0; j<NHIST; j++) hist[filt][j] = 0;
	for(filt=0; filt<NFILTERS; filt++) {
		histmax[filt] = 0;
		histmin[filt] = 0;
		for(nf=0; nf<nFields; nf++) {
			if ((double)count[filt][nf]/(double)desired[filt] > 1.0 ) {
				histmax[filt]++;
			} else if (count[filt][nf] == 0) {
				histmin[filt]++;
			}	else {
				//i = MIN((double)count[filt][nf]/(double)desired[filt],0.999999999)*(double)NHIST;
				i = (int)((double)count[filt][nf]*10.0/(double)desired[filt]);
				hist[filt][i]++;
			}
		}
	}

	/**
	* Making tex file for 5sigma
	*/
	FILE* tfp;
	char fName[80];
	char s[100];
	sprintf(fName, "../output/%s_%d_seeing.tex", hostname, sessionID);
	tfp = fopen(fName, "w");

	fprintf(tfp, "\\begin{table}[H]{\\textbf{Complete Fields Filtered by Single Visit Depth - 0.5 and Seeing}} \\\\ [1.0ex]\n");
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

	fprintf(tfp, "~~~~~~~~~$N \\ge 100$ & ");
	for (filt=0; filt<NFILTERS; filt++) {
		if ( filt == NFILTERS - 1) {
			fprintf(tfp, "%4d \\\\", histmax[filt]);
		}
		else {
			fprintf(tfp, "%4d &", histmax[filt]);
		}
	}
	fprintf(tfp, "\n");

	fprintf(quickfp, "By Depth and Seeing &");
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
	fprintf(tfp, "\\caption{The number of fields for which completeness was achieved which also met the condition that the median 5$\\sigma$ single visit depth is greater than the SRD 5$\\sigma$ - 0.5 single visit depth and that the ratio of the observed median seeing to the SRD expected median zenith seeing is less than 1.5. Completeness is defined as the percentage of scaled SRD number of visits per field. Note that the number of fields that reached or exceeded the above condition is given by the $N \\ge 100$ bin.}\n");
	fprintf(tfp, "\\label{tab:SeeingNumTable}\n");
	fprintf(tfp, "\\end{table}\n");

	fflush(tfp);
	fclose(tfp);
	/**
	* End of Making tex file for seeing
	*/

	for(i=0; i<NFILTERS; i++) free(value[i]);
	free(value);
	free(decvec);
	free(ravec);
	for(i=0; i<NFILTERS; i++) free(count[i]);
	free(count);
	free(len);
	free(start);
}

void seeingPlotbyProposal(int propID) {
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
		valmax[filt] = 1.5;
		valmin[filt] = 0.8;
	}
	
	for(nf=0; nf<nFields; nf++) {
		for(filt=0; filt<NFILTERS; filt++) value[filt][nf]=0;
		for(filt=0; filt<NFILTERS; filt++) {
			median_data_length = 0;
			for(i=start[nf]; i<start[nf]+len[nf]; i++) {
				if(obs[i].filter == filt && obs[i].propid == propID) {
					median_data[median_data_length++] = obs[i].seeing;
				}
			}
			
			// sort the median_data values
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
					// By request of Bug 59 : SSTAR (SRD expected median zenith seeing from document - Table 2)
					if (filt == 0) { // u
						value[filt][nf] /= 0.77;
					} else if (filt == 1) { // g
						value[filt][nf] /= 0.73;
					} else if (filt == 2) { // r
						value[filt][nf] /= 0.70;
					} else if (filt == 3) { // i
						value[filt][nf] /= 0.67;
					} else if (filt == 4) { // z
						value[filt][nf] /= 0.65;
					} else if (filt == 5) { // y
						value[filt][nf] /= 0.63;
					}
				}
			}
		}
	}
	
	char* fileName = (char*)malloc(100);
	sprintf(fileName, "medianseeing-%d", propID);
	// make the plot
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "median seeing", plotTitle, fileName, 1);
	for(i=0; i<NFILTERS; i++) free(value[i]);
	free(value);
	free(decvec);
	free(ravec);
	for(i=0; i<NFILTERS; i++) free(count[i]);
	free(count);
	free(len);
	free(start);
}

void doSeeingPlotbyProposal() {
	int i;
	for(i=0; i < proposal_list_length; i++) {
		seeingPlotbyProposal(proposal_list[i].propID);
	}
}

void skybPlot() {
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
		// By request of Bug 60 : SSTAR
		//valmax[filt] = 23.0;
		//valmin[filt] = 16.5;
		valmax[filt] = 1.0;
		valmin[filt] = -2.0;
	}

	for(nf=0; nf<nFields; nf++) {
		for(filt=0; filt<NFILTERS; filt++) 
			value[filt][nf]=0;
		for(filt=0; filt<NFILTERS; filt++) {
			median_data_length = 0;
			for(i=start[nf]; i<start[nf]+len[nf]; i++) {
				if(obs[i].filter == filt) {
					median_data[median_data_length++] = obs[i].etc_skyb;
				}
			}
			
			// sort the median_data values
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
					// By request of Bug 60 : SSTAR (SRD expected median zenith sky brightness from document - Table 2)
					if (filt == 0) { // u
						value[filt][nf] -= 21.8;
					} else if (filt == 1) { // g
						value[filt][nf] -= 22.0;
					} else if (filt == 2) { // r
						value[filt][nf] -= 21.3;
					} else if (filt == 3) { // i
						value[filt][nf] -= 20.0;
					} else if (filt == 4) { // z
						value[filt][nf] -= 19.1;
					} else if (filt == 5) { // y
						value[filt][nf] -= 17.5;
					}
				}
			}
		}
	}
	
	// make the plot
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "median sky brightness", plotTitle, "medianskyb", 1);
	for(i=0; i<NFILTERS; i++) free(value[i]);
	free(value);
	free(decvec);
	free(ravec);
	for(i=0; i<NFILTERS; i++) free(count[i]);
	free(count);
	free(len);
	free(start);
}

void skybPlotByProposal(int propID) {
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
		// By request of Bug 60 : SSTAR
		//valmax[filt] = 23.0;
		//valmin[filt] = 16.5;
		valmax[filt] = 1.0;
		valmin[filt] = -2.0;
	}
	
	for(nf=0; nf<nFields; nf++) {
		for(filt=0; filt<NFILTERS; filt++) 
			value[filt][nf]=0;
		for(filt=0; filt<NFILTERS; filt++) {
			median_data_length = 0;
			for(i=start[nf]; i<start[nf]+len[nf]; i++) {
				if(obs[i].filter == filt && obs[i].propid == propID) {
					median_data[median_data_length++] = obs[i].etc_skyb;
				}
			}
			
			// sort the median_data values
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
					// By request of Bug 60 : SSTAR (SRD expected median zenith sky brightness from document - Table 2)
					if (filt == 0) { // u
						value[filt][nf] -= 21.8;
					} else if (filt == 1) { // g
						value[filt][nf] -= 22.0;
					} else if (filt == 2) { // r
						value[filt][nf] -= 21.3;
					} else if (filt == 3) { // i
						value[filt][nf] -= 20.0;
					} else if (filt == 4) { // z
						value[filt][nf] -= 19.1;
					} else if (filt == 5) { // y
						value[filt][nf] -= 17.5;
					}
				}
			}
		}
	}
	
	char* fileName = (char*)malloc(100);
	sprintf(fileName, "medianskyb-%d", propID);
	// make the plot
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "median sky brightness", plotTitle, fileName, 1);
	for(i=0; i<NFILTERS; i++) free(value[i]);
	free(value);
	free(decvec);
	free(ravec);
	for(i=0; i<NFILTERS; i++) free(count[i]);
	free(count);
	free(len);
	free(start);
}

void doSkybPlotbyProposal() {
	int i;
	for(i=0; i < proposal_list_length; i++) {
		skybPlotByProposal(proposal_list[i].propID);
	}
}

void m5Plot() {
	int i, j, filt, nf, nmax, nmin, sum, flag;
	int nFields, *start, *len, **count, **count2;
	int maxnum[NFILTERS];
	int hist[NFILTERS][NHIST], histmax[NFILTERS], histmin[NFILTERS], desired[NFILTERS];
	int hist2[NFILTERS][NHIST], histmax2[NFILTERS], histmin2[NFILTERS];
	double xmin, xmax, ymin, ymax;
	double *ravec, *decvec, **value, **covalue_orig, **covalue_wfd, **covalue_wfd_d, **covalue, valmin[NFILTERS], valmax[NFILTERS], frac, least;
	double trueam, alt, ha;

    FILE* coadded_raw_fp;
	FILE* coadded_wfd_fp;
    char fName[80];

    sprintf(fName, "../output/%s_%d_coadded_raw.dat", hostname, sessionID);
	coadded_raw_fp = fopen(fName, "w");
	sprintf(fName, "../output/%s_%d_coadded_wfd.dat", hostname, sessionID);
	coadded_wfd_fp = fopen(fName, "w");

	start = malloc((numFields+1)*sizeof(int));
	len = malloc(numFields*sizeof(int));
	ravec = malloc(numFields*sizeof(double));
	decvec =malloc(numFields*sizeof(double));
	count = malloc(NFILTERS*sizeof(int *));
	count2 = malloc(NFILTERS*sizeof(int *));
	for(i=0; i<NFILTERS; i++) {
		count[i] = malloc(numFields*sizeof(int));
		count2[i] = malloc(numFields*sizeof(int));
	}
	value = malloc(NFILTERS*sizeof(double *));
	covalue = malloc(NFILTERS*sizeof(double *));
	covalue_wfd = malloc(NFILTERS*sizeof(double *));
	covalue_wfd_d = malloc(NFILTERS*sizeof(double *));
	covalue_orig = malloc(NFILTERS*sizeof(double *));
	for(i=0; i<NFILTERS; i++) {
		value[i] = malloc(numFields*sizeof(double));
		covalue[i] = malloc(numFields*sizeof(double));
		covalue_wfd[i] = malloc(numFields*sizeof(double));
		covalue_wfd_d[i] = malloc(numFields*sizeof(double));
		covalue_orig[i] = malloc(numFields*sizeof(double));
	}
	
	// order visits by field and get pointers
	getFieldData(&nFields, start, len);
	int propID[50];
	int propIDcount = 0;
	for(i=0; i < proposal_list_length; i++) {
		if ( strcasestr(proposal_list[i].propConf, "Universal") != NULL 
			 && strcasestr(proposal_list[i].propConf, "Universalnorth") == NULL ) {
			propID[propIDcount++] = proposal_list[i].propID;
		} 
	}
	
	for(nf=0; nf<nFields; nf++) {
		ravec[nf] = obs[start[nf]].ra;
		decvec[nf] = obs[start[nf]].dec;
	}
	for(filt=0; filt<NFILTERS; filt++) {
		valmax[filt] = 0.75;
		valmin[filt] = -0.75;
	}

	double required_scaled_m5[NFILTERS];
	double required_scaled_coadded[NFILTERS];
	if ( useDesignStretch == 0 ) {
        required_scaled_coadded[0] = 56;
        required_scaled_coadded[1] = 80;
        required_scaled_coadded[2] = 184;
        required_scaled_coadded[3] = 184;
        required_scaled_coadded[4] = 160;
        required_scaled_coadded[5] = 160;
		required_scaled_m5[0] = 23.9;
		required_scaled_m5[1] = 25.0;
		required_scaled_m5[2] = 24.7;
		required_scaled_m5[3] = 24.0;
		required_scaled_m5[4] = 23.3;
		required_scaled_m5[5] = 22.1;
    } else {
		required_scaled_coadded[0] = 70;
		required_scaled_coadded[1] = 100;
		required_scaled_coadded[2] = 230;
		required_scaled_coadded[3] = 230;
		required_scaled_coadded[4] = 200;
		required_scaled_coadded[5] = 200;
		required_scaled_m5[0] = 24.0;
		required_scaled_m5[1] = 25.1;
		required_scaled_m5[2] = 24.8;
		required_scaled_m5[3] = 24.1;
		required_scaled_m5[4] = 23.4;
		required_scaled_m5[5] = 22.2;
    }
	for(filt=0; filt<NFILTERS; filt++) {
		required_scaled_coadded[filt] *= (endMJD-startMJD)/365.25/10.0;
		required_scaled_coadded[filt] = required_scaled_m5[filt] + 1.25 * log10(required_scaled_coadded[filt]);
	}

	for(nf=0; nf<nFields; nf++) {
		for(filt=0; filt<NFILTERS; filt++) {
			value[filt][nf]=0;
			covalue[filt][nf]=0;
			covalue_wfd[filt][nf]=0;
			covalue_wfd_d[filt][nf]=0;
			covalue_orig[filt][nf]=0;
			count[filt][nf]=0;
			count2[filt][nf]=0;
		}
		for(filt=0; filt<NFILTERS; filt++) {
			median_data_length = 0;
			for(i=start[nf]; i<start[nf]+len[nf]; i++) {
				if(obs[i].filter == filt) {
					median_data[median_data_length++] = obs[i].etc_m5;
					
					if ( obs[i].etc_m5 > required_scaled_m5[filt] ) {
						count[filt][nf]++;
					}
					if ( obs[i].etc_m5 > required_scaled_m5[filt] - 0.5 ) {
						count2[filt][nf]++;
					}						
				}
			}
			
			// sort the median_data values
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
					double teff = 0.0;
					for(j=0; j < median_data_length; j++) {
						teff += pow(10.0, ( (median_data[j] - 25.0) / 1.25 ) );
					}
					covalue[filt][nf] = 1.25 * log10(teff) + 25.0;
					covalue_orig[filt][nf] = 1.25 * log10(teff) + 25.0;
					for(j=0; j < propIDcount; j++) {
						if ( obs[i].propid == propID[j] ) {
							covalue_wfd[filt][nf] = covalue_orig[filt][nf];
							covalue_wfd_d[filt][nf] = covalue_orig[filt][nf] - required_scaled_coadded[filt];
						}
					}
					// By request of Bug 57 : SSTAR (SRD expected median m5 from document - Table 2)
					// By request of Bug 58 : SSTAR (SRD expected median coadded m5 from document - Table 1)
					value[filt][nf] -= required_scaled_m5[filt];
					covalue[filt][nf] -= required_scaled_coadded[filt];
				}
			}
		}
	}
	
	// Coadded Depth for all visits
	for(nf=0; nf<nFields; nf++) {
		for(filt=0; filt<NFILTERS; filt++) {
			if ( covalue_orig[filt][nf] > 0.0 ) {
                if (filt == 0) { // u
                    fprintf(coadded_raw_fp, "%d %c %lf\n", nf, 'u', covalue_orig[filt][nf]);
    	        } else if (filt == 1) { // g
        	        fprintf(coadded_raw_fp, "%d %c %lf\n", nf, 'g', covalue_orig[filt][nf]);
                } else if (filt == 2) { // r
                    fprintf(coadded_raw_fp, "%d %c %lf\n", nf, 'r', covalue_orig[filt][nf]);
                } else if (filt == 3) { // i
                    fprintf(coadded_raw_fp, "%d %c %lf\n", nf, 'i', covalue_orig[filt][nf]);
                } else if (filt == 4) { // z
                    fprintf(coadded_raw_fp, "%d %c %lf\n", nf, 'z', covalue_orig[filt][nf]);
                } else if (filt == 5) { // y
                    fprintf(coadded_raw_fp, "%d %c %lf\n", nf, 'y', covalue_orig[filt][nf]);
                }
			}
		}
	}
	fflush(coadded_raw_fp);
	fclose(coadded_raw_fp);
	
	// Coadded Depth for WFD visits
	for(nf=0; nf<nFields; nf++) {
		for(filt=0; filt<NFILTERS; filt++) {
			if ( covalue_wfd[filt][nf] > 0.0 ) {
                if (filt == 0) { // u
                    fprintf(coadded_wfd_fp, "%d %c %lf\n", nf, 'u', covalue_wfd[filt][nf]);
    	        } else if (filt == 1) { // g
        	        fprintf(coadded_wfd_fp, "%d %c %lf\n", nf, 'g', covalue_wfd[filt][nf]);
                } else if (filt == 2) { // r
                    fprintf(coadded_wfd_fp, "%d %c %lf\n", nf, 'r', covalue_wfd[filt][nf]);
                } else if (filt == 3) { // i
                    fprintf(coadded_wfd_fp, "%d %c %lf\n", nf, 'i', covalue_wfd[filt][nf]);
                } else if (filt == 4) { // z
                    fprintf(coadded_wfd_fp, "%d %c %lf\n", nf, 'z', covalue_wfd[filt][nf]);
                } else if (filt == 5) { // y
                    fprintf(coadded_wfd_fp, "%d %c %lf\n", nf, 'y', covalue_wfd[filt][nf]);
                }
			}
		}
	}
	fflush(coadded_wfd_fp);
	fclose(coadded_wfd_fp);

	// make the 5 sigma plot
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "median single visit depth", plotTitle, "median5sigma", 1);
	// make the 5 sigma coadded plot
	plotSix(nFields, covalue, ravec, decvec, valmin, valmax, 1, "coadded depth", plotTitle, "coadded5sigma", 1);
	plotSix(nFields, covalue_wfd_d, ravec, decvec, valmin, valmax, 1, "coadded depth", plotTitle, "coadded5sigmaWFD", 1);
	
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

	for(filt=0; filt<NFILTERS; filt++) valmax[filt] *= (endMJD-startMJD)/365.25/10.0;
	for(filt=0; filt<NFILTERS; filt++) desired[filt] = valmax[filt];

	for(filt=0; filt<NFILTERS; filt++) for(j=0; j<NHIST; j++) {
		hist[filt][j] = 0;
		hist2[filt][j] = 0;
	}
	for(filt=0; filt<NFILTERS; filt++) {
		histmax[filt] = 0;
		histmin[filt] = 0;
		histmax2[filt] = 0;
		histmin2[filt] = 0;
		for(nf=0; nf<nFields; nf++) {
			if ((double)count[filt][nf]/(double)desired[filt] > 1.0 ) {
				histmax[filt]++;
			} else if ( count[filt][nf] == 0) {
				histmin[filt]++;
			} else {
				i = (int)((double)count[filt][nf]*10.0/(double)desired[filt]);
				//i = MIN((double)count[filt][nf]/(double)desired[filt],0.999999999)*(double)NHIST;
				hist[filt][i]++;
			}

			if ((double)count2[filt][nf]/(double)desired[filt] > 1.0 ) {
				histmax2[filt]++;
			} else if ( count2[filt][nf] == 0) {
				histmin2[filt]++;
			} else {
				i = (int)((double)count2[filt][nf]*10.0/(double)desired[filt]);
				//i = MIN((double)count[filt][nf]/(double)desired[filt],0.999999999)*(double)NHIST;
				hist2[filt][i]++;
			}
		}
	}

	/**
	* Making tex file for 5sigma
	*/
	FILE* tfp;
	char s[100];
	sprintf(fName, "../output/%s_%d_5sigma.tex", hostname, sessionID);
	tfp = fopen(fName, "w");

	fprintf(tfp, "\\begin{table}[H]{\\textbf{Complete Fields Filtered by Single Visit Depth}} \\\\ [1.0ex]\n");
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

	fprintf(tfp, "~~~~~~~~~$N \\ge 100$ & ");
	for (filt=0; filt<NFILTERS; filt++) {
		if ( filt == NFILTERS - 1) {
			fprintf(tfp, "%4d \\\\", histmax[filt]);
		}
		else {
			fprintf(tfp, "%4d &", histmax[filt]);
		}
	}
	fprintf(tfp, "\n");

	fprintf(quickfp, "By Depth &");
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
	fprintf(tfp, "\\caption{The number of fields for which completeness was achieved which also met the condition that the median 5$\\sigma$ single visit depth is greater than the Design SRD 5$\\sigma$ single visit depth. Completeness is defined as the percentage of Scaled Design SRD number of visits per field. Note that the number of fields that reached or exceeded the above condition is given by the $N \\ge 100$ bin.}\n");
	fprintf(tfp, "\\label{tab:5sigmaNumTable}\n");
	fprintf(tfp, "\\end{table}\n");

	fflush(tfp);
	fclose(tfp);
	/**
	* End of Making tex file for 5sigma
	*/

	/**
	* Making tex file for 5sigma2
	*/
	sprintf(fName, "../output/%s_%d_5sigma2.tex", hostname, sessionID);
	tfp = fopen(fName, "w");

	fprintf(tfp, "\\begin{table}[H]{\\textbf{Complete Fields Filtered by Single Visit Depth - 0.5 }} \\\\ [1.0ex]\n");
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

	fprintf(tfp, "~~~~~~~~~$N \\ge 100$ & ");
	for (filt=0; filt<NFILTERS; filt++) {
		if ( filt == NFILTERS - 1) {
			fprintf(tfp, "%4d \\\\", histmax2[filt]);
		}
		else {
			fprintf(tfp, "%4d &", histmax2[filt]);
		}
	}
	fprintf(tfp, "\n");

	fprintf(quickfp, "By Depth &");
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
					fprintf(quickfp, "%4d \\\\", hist2[filt][j] + histmax2[filt]);
				}
				else {
					fprintf(quickfp, "%4d &", hist2[filt][j] + histmax2[filt]);
				}
			}

			if ( filt == NFILTERS - 1) {
				fprintf(tfp, "%4d \\\\", hist2[filt][j]);
			}
			else {
				fprintf(tfp, "%4d &", hist2[filt][j]);
			}
		}
		fprintf(tfp, "\n");
	}
	/*fprintf(tfp, "~~~~~~~~~$N = 0$ & ");
	for (filt=0; filt<NFILTERS; filt++) {
		if ( filt == NFILTERS - 1) {
			fprintf(tfp, "%4d \\\\", histmin2[filt]);
		}
		else {
			fprintf(tfp, "%4d &", histmin2[filt]);
		}
	}
	fprintf(tfp, "\n");*/
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\hline\n");
	fprintf(tfp, "\\end{tabular*}\n");
	fprintf(tfp, "\\caption{The number of fields for which completeness was achieved which also met the condition that the median 5$\\sigma$ single visit depth is greater than the Design SRD 5$\\sigma$ - 0.5 single visit depth. Completeness is defined as the percentage of Scaled Design SRD number of visits per field. Note that the number of fields that reached or exceeded the above condition is given by the $N \\ge 100$ bin.}\n");
	fprintf(tfp, "\\label{tab:5sigma2NumTable}\n");
	fprintf(tfp, "\\end{table}\n");

	fflush(tfp);
	fclose(tfp);
	/**
	* End of Making tex file for 5sigma
	*/

	for(i=0; i<NFILTERS; i++) free(value[i]);
	free(value);
	free(decvec);
	free(ravec);
	for(i=0; i<NFILTERS; i++) free(count[i]);
	free(count);
	free(len);
	free(start);
}

void m5PlotByProposal(int propID) {
	int i, j, filt, nf, nmax, nmin, sum, flag;
	int nFields, *start, *len, **count;
	int maxnum[NFILTERS];
	double xmin, xmax, ymin, ymax;
	double *ravec, *decvec, **value, **covalue, valmin[NFILTERS], valmax[NFILTERS], frac, least;
	double trueam, alt, ha;
	
	start = malloc((numFields+1)*sizeof(int));
	len = malloc(numFields*sizeof(int));
	ravec = malloc(numFields*sizeof(double));
	decvec =malloc(numFields*sizeof(double));
	count = malloc(NFILTERS*sizeof(int *));
	for(i=0; i<NFILTERS; i++) count[i] = malloc(numFields*sizeof(int));
	value = malloc(NFILTERS*sizeof(double *));
	covalue = malloc(NFILTERS*sizeof(double *));
	for(i=0; i<NFILTERS; i++) {
		value[i] = malloc(numFields*sizeof(double));
		covalue[i] = malloc(numFields*sizeof(double));
	}
	
	// order visits by field and get pointers
	getFieldData(&nFields, start, len);

	for(nf=0; nf<nFields; nf++) {
		ravec[nf] = obs[start[nf]].ra;
		decvec[nf] = obs[start[nf]].dec;
	}

	for(filt=0; filt<NFILTERS; filt++) {
		valmax[filt] = 0.75;
		valmin[filt] = -0.75;
	}

    double required_scaled_m5[NFILTERS];
    double required_scaled_coadded[NFILTERS];

	if ( useDesignStretch == 0 ) {
	    required_scaled_coadded[0] = 56;
	    required_scaled_coadded[1] = 80;
	    required_scaled_coadded[2] = 184;
	    required_scaled_coadded[3] = 184;
	    required_scaled_coadded[4] = 160;
	    required_scaled_coadded[5] = 160;
	    required_scaled_m5[0] = 23.9;
	    required_scaled_m5[1] = 25.0;
	    required_scaled_m5[2] = 24.7;
	    required_scaled_m5[3] = 24.0;
	    required_scaled_m5[4] = 23.3;
	    required_scaled_m5[5] = 22.1;
	} else {
		required_scaled_coadded[0] = 70;
		required_scaled_coadded[1] = 100;
		required_scaled_coadded[2] = 230;
		required_scaled_coadded[3] = 230;
		required_scaled_coadded[4] = 200;
		required_scaled_coadded[5] = 200; 
	    required_scaled_m5[0] = 24.0;
	    required_scaled_m5[1] = 25.1;
	    required_scaled_m5[2] = 24.8;
	    required_scaled_m5[3] = 24.1;
	    required_scaled_m5[4] = 23.4;
	    required_scaled_m5[5] = 22.2;
	}	

    for(filt=0; filt<NFILTERS; filt++) {
        required_scaled_coadded[filt] *= (endMJD-startMJD)/365.25/10.0;
        required_scaled_coadded[filt] = required_scaled_m5[filt] + 1.25 * log10(required_scaled_coadded[filt]);
    }

	for(nf=0; nf<nFields; nf++) {
		for(filt=0; filt<NFILTERS; filt++) { 
			value[filt][nf]=0;
			covalue[filt][nf]=0;
		}

		for(filt=0; filt<NFILTERS; filt++) {
			median_data_length = 0;
			for(i=start[nf]; i<start[nf]+len[nf]; i++) {
				if(obs[i].filter == filt && obs[i].propid == propID) {
					median_data[median_data_length++] = obs[i].etc_m5;
				}
			}
			
			// sort the median_data values
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
					double teff = 0.0;
					for(j=0; j < median_data_length; j++) {
						teff += pow(10.0, ( (median_data[j] - 25.0) / 1.25 ) );
					}
					covalue[filt][nf] = 1.25 * log10(teff) + 25.0;
					// By request of Bug 57 : SSTAR (SRD expected median m5 from document - Table 2)
					// By request of Bug 58 : SSTAR (SRD expected median coadded m5 from document - Table 1)
                    value[filt][nf] -= required_scaled_m5[filt];
                    covalue[filt][nf] -= required_scaled_coadded[filt];				
				}
			}
		}
	}
	
	char* fileName = (char*)malloc(100);
	sprintf(fileName, "median5sigma-%d", propID);
	// make the 5 sigma plot
	plotSix(nFields, value, ravec, decvec, valmin, valmax, 1, "median single visit depth", plotTitle, fileName, 1);
	sprintf(fileName, "coadded5sigma-%d", propID);
	// make the 5 sigma coadded plot
	plotSix(nFields, covalue, ravec, decvec, valmin, valmax, 1, "coadded depth", plotTitle, fileName, 1);

	for(i=0; i<NFILTERS; i++) free(value[i]);
	free(value);
	free(decvec);
	free(ravec);
	for(i=0; i<NFILTERS; i++) free(count[i]);
	free(count);
	free(len);
	free(start);
}

void dom5PlotbyProposal() {
	int i;
	for(i=0; i < proposal_list_length; i++) {
		m5PlotByProposal(proposal_list[i].propID);
	}
}

