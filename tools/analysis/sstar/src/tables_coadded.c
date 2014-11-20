/*
  tables visits code
  Srinivasan Chandrasekharan
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mysql.h>
#include <errno.h>
#include <unistd.h>
#include <math.h>

#include "stats.c"
#include "maketex.h"

double coadded_datafield[30000];
int coadded_datafield_length;

void openCoaddedTableTex() {
	sprintf(s, "../output/%s_%d_CoaddedTable.tex", hostname, sessionID);
	fp = fopen(s, "w");
	if ( fp ) {
		//printf("tex file opened\n");
	} else {
		printf("Error in opening file %s\n", strerror(errno));
		exit(1);
	}
}

void closeTex() {
	fflush(fp);
	fclose(fp);
}

void readCoaddedRawDataForFilter(char filter) {
	int fieldID;
	char f_filter;
	double coadded;
	
	sprintf(s, "../output/%s_%d_coadded_raw.dat", hostname, sessionID);
	FILE *fp_raw = fopen(s, "r");
	coadded_datafield_length = 0;
	if ( fp_raw ) {
		//printf("raw datafile file opened\n");
	} else {
		printf("Error in opening file %s\n", strerror(errno));
		exit(1);
	}
	
	while ( fscanf(fp_raw, "%d %c %lf", &fieldID, &f_filter, &coadded) != EOF ) {
		if ( filter == ' ' ) {
			coadded_datafield[coadded_datafield_length++] = coadded;
		} else if ( filter == f_filter ) {
			coadded_datafield[coadded_datafield_length++] = coadded;
		}
	}
	fclose(fp_raw);

    double temp;
	int i,j;
	for(i=coadded_datafield_length-1; i>=0; i--) {
		for(j=1; j<=i; j++) {
			if ( coadded_datafield[j-1] > coadded_datafield[j]) {
				temp = coadded_datafield[j-1];
				coadded_datafield[j-1] = coadded_datafield[j];
				coadded_datafield[j] = temp;
			}
		}
	}
}

void makeTable() {
	int i, j, outliers, inliers;
	char sql[512];
	double average, std_dev, median;
	
	write("\\begin{table}[H]{\\bf{Coadded Depth}} \\\\ [1.0ex]");
	write("\\begin{tabular*}{\\textwidth}{\\tblspace lcllrrr}");
	write("\\hline");
	write("\\colhead{Observing Mode ID} &");
	write("\\colhead{Filter} &");
	write("\\colhead{Median} &");
	write("\\colhead{Mean $\\pm$ rms} &");
	write("\\colhead{$+ 3\\sigma$} &");
	write("\\colhead{$- 3\\sigma$} &");
	write("\\colhead{Total} \\\\");
	write("\\hline");

	/* All proposals*/

	/* U filter */
	readCoaddedRawDataForFilter('u');
	comp_statistics (coadded_datafield, coadded_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, "All Observing Modes & u & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, coadded_datafield_length);
	write(s);

	/* G filter */
	readCoaddedRawDataForFilter('g');
	comp_statistics (coadded_datafield, coadded_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & g & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, coadded_datafield_length);
	write(s);

	/* R filter */ 
	readCoaddedRawDataForFilter('r');
	comp_statistics (coadded_datafield, coadded_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & r & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, coadded_datafield_length); 
	write(s);

	/* I filter */ 
	readCoaddedRawDataForFilter('i');
	comp_statistics (coadded_datafield, coadded_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & i & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, coadded_datafield_length); 
	write(s);

	/* Z filter */ 
	readCoaddedRawDataForFilter('z');
	comp_statistics (coadded_datafield, coadded_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & z & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, coadded_datafield_length); 
	write(s);

	/* Y filter */ 
	readCoaddedRawDataForFilter('y');
	comp_statistics (coadded_datafield, coadded_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & y & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, coadded_datafield_length); 
	write(s);

	write("\\hline");

	/* All filter All proposals*/ 
	readCoaddedRawDataForFilter(' ');
	comp_statistics (coadded_datafield, coadded_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, "All Observing Modes & All & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, coadded_datafield_length); 
	write(s);

	write("\\hline \\hline");
	write("\\end{tabular*}");
	write("\\caption{The median, mean and standard deviation of the coadded depth separated by filter for all fields regardless of observing mode. The $+3\\sigma$ column shows the number of fields which have a coadded depth more than $3\\sigma$ fainter than the median coadded depth; the $-3\\sigma$ column shows the number of fields with a coadded depth more than $3\\sigma$ brighter than the mean coadded depth. The Total column is the number of fields counted toward each filter combination.}");
	write("\\label{tab:visits}");
	write("\\end{table}");
}

int main(int argc, char **argv) {
	if ( argc == 2 || argc == 3) {
		if ( argc == 3 ) {
			sprintf(hostname, "%s", argv[1]);
		} else {
			if ( gethostname(identifier, identifier_length) == 0 ) {
				sprintf(hostname, "%s", identifier);
			} else {
				printf( "Hostname : %s\n", strerror(errno));
				exit(1);
			}
		}
		sessionID = atoi(argv[2]);
		sprintf(identifier, "%s.%d", hostname, sessionID);

		/* Write Table */
		openCoaddedTableTex();
		makeTable();
		closeTex();
	} else {
		printf("Error : Number of arguments");
		exit(1);
	}
}
