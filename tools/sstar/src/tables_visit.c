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

#define TOTAL_FIELDS 6000

double visit_datafield[TOTAL_FIELDS];
int visit_datafield_length = 0;
int useDesignStretch = 0;

void openVisitTableTex() {
	sprintf(s, "../output/%s_%d_VisitsTable.tex", hostname, sessionID);
	fp = fopen(s, "w");
	if ( fp ) {
		//printf("tex file opened\n");
	} else {
		printf("Error in opening file %s\n", strerror(errno));
		exit(1);
	}
}

void openHistogramTableTex() {
	sprintf(s, "../output/%s_%d_VisitsHistogram.tex", hostname, sessionID);
	fp = fopen(s, "w");
	if ( fp ) {
		//printf("tex file opened\n");
	} else {
		printf("Error in opening file %s\n", strerror(errno));
		exit(1);
	}
}

void openHistogramTableAllTex() {
	sprintf(s, "../output/%s_%d_VisitsHistogramAll.tex", hostname, sessionID);
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

void openDB(char* dbname) {
	openLSSTdb("localhost", "www", "zxcvbnm", dbname);
}

void closeDB() {
	closeLSSTdb();
}

void createVisitDataField() {
	int i,j;
	double temp_datafield[TOTAL_FIELDS];
	int temp_datafield_length = 0;
	visit_datafield_length = 0;

	for(i=0; i < TOTAL_FIELDS; i++) temp_datafield[i] = 0;
	for(i=0; i < observation_datafield_length; i++) {
		temp_datafield[(int)observation_datafield[i]]++;
		if ( observation_datafield[i] > temp_datafield_length) {
			temp_datafield_length = observation_datafield[i];
		}
	}

	for(i=0; i < TOTAL_FIELDS; i++) visit_datafield[i] = 0;
	for(i=0; i < TOTAL_FIELDS; i++) {
		if ( temp_datafield[i] > 0 ) {
			visit_datafield[visit_datafield_length] = temp_datafield[i];
			visit_datafield_length++;
		}
	}
	//printf("Total fields visited %d\n", visit_datafield_length);
    double temp;
    for(i=visit_datafield_length-1; i>=0; i--) {
        for(j=1; j<=i; j++) {
			if ( visit_datafield[j-1] > visit_datafield[j]) {
                temp = visit_datafield[j-1];
                visit_datafield[j-1] = visit_datafield[j];
                visit_datafield[j] = temp;
            }
        }
	}
}

#define NHIST 10
void makeHistogramTable() {
	int i, j;
	int valmax[6];
	int hist[NHIST][7]; // Why 7, 6 filters and 7th is for joint completeness
	int histmax[7];
	int histmin[7];
	char sql[1024];

	/* Initializations */
	double nRunSup = 10.00/atof(getConfigValue("nRun"));
	if ( useDesignStretch == 0 ) {	
		valmax[0] = 56/nRunSup;
		valmax[1] = 80/nRunSup;
		valmax[2] = 184/nRunSup;
		valmax[3] = 184/nRunSup;
		valmax[4] = 160/nRunSup;
		valmax[5] = 160/nRunSup;
	} else {
	  	valmax[0] = 70/nRunSup;
		valmax[1] = 100/nRunSup;
		valmax[2] = 230/nRunSup;
		valmax[3] = 230/nRunSup;
		valmax[4] = 200/nRunSup;
		valmax[5] = 200/nRunSup; 
	}

	for(i=0; i < NHIST; i++) {
		for (j=0; j < 7; j++) {
			hist[i][j] = 0;
			histmax[j] = 0;
		}
	}
	for (j=0; j < 7; j++) {
		histmax[j] = 0;
		histmin[j] = 0;
	}

	/* Initializations */

	int propID[50];
	int propIDcount = 0;
	for(i=0; i < proposal_list_length; i++) {
		if ( (char*)strcasestr(proposal_list[i].propConf, "Universal") != NULL && (char*)strcasestr(proposal_list[i].propConf, "Universalnorth") == NULL ) {
		//if ( strcasestr(proposal_list[i].propConf, "UniversalProp") != NULL ) {
			propID[propIDcount++] = proposal_list[i].propID;
		}
	}

	if ( propIDcount == 0 ) 
		return;

	// You have the fields list.
	// Cycle through the fields list and get all the observations for that field
	// Make sure that the field is observed for propID of Universal
	for(j=0; j < field_data_length; j++) {
		sprintf(sql, "select filter, count(*) as count from output_%s_%d where fieldID=%d and", hostname, sessionID, field_data[j].fieldID);
		for(i=0; i < propIDcount; i++) {
			if ( i == propIDcount - 1 ) {
				sprintf(sql, "%s propID=%d", sql, propID[i]);
			} else {		
				sprintf(sql, "%s propID=%d and", sql, propID[i]);
			}
		}
		//sprintf(sql, "%s group by expDate", sql); // There is no need because multiple propIDs with same propID IS NOT possible
		sprintf(sql, "%s group by filter", sql);
		//printf("Field : %d : %s\n", field_data[j].fieldID, sql);
		readFilterDataField(sql);
		
		// Now you have for each field - filter and how many times the field was visited in that filter
		// mysql> select filter, count(*) as count from output_hewelhog_56 where fieldID=368 and propID=100 group by filter;
		// +--------+-------+
		// | filter | count |
		// +--------+-------+
		// | g      |    26 |
		// | i      |    46 |
		// | r      |    50 |
		// | u      |    19 |
		// | y      |    77 |
		// | z      |    60 |
		// +--------+-------+
		// 6 rows in set (0.01 sec)
		double min_complete_filter_value = 10.00; // This is 1000 % very high % never possible
		int total_visits_per_field = 0;
        int number_of_filters_visited = 0;
		for (i=0; i < filter_datafield_length; i++) {
			double filter_completeness = 0.0;
			if (strcmp(filter_datafield[i].filter, "u") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[0];
				if ( filter_completeness >= 1.00 ) {
					histmax[0]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[0]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][0]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "g") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[1];
				if ( filter_completeness >= 1.00 ) {
					histmax[1]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[1]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][1]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "r") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[2];
				if ( filter_completeness >= 1.00 ) {
					histmax[2]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[2]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][2]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "i") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[3];
				if ( filter_completeness >= 1.00 ) {
					histmax[3]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[3]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][3]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "z") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[4];
				if ( filter_completeness >= 1.00 ) {
					histmax[4]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[4]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][4]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "y") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[5];
				if ( filter_completeness >= 1.00 ) {
					histmax[5]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[5]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][5]++;
				}
                number_of_filters_visited++;
			}
			if ( filter_completeness < min_complete_filter_value )
				min_complete_filter_value = filter_completeness;
			total_visits_per_field += filter_datafield[i].count;
			//printf(	"%s %d\n", filter_datafield[i].filter, filter_datafield[i].count);
		}
		/*if ( min_complete_filter_value >= 1.00 && min_complete_filter_value < 10.00 ) {
			histmax[6]++;
		} else if (total_visits_per_field == 0 ) {
			histmin[6]++;
		} else {
            if ( min_complete_filter_value < 10.00 )
                hist[(int)(min_complete_filter_value*(double)NHIST)][6]++;
		}*/
        if ( number_of_filters_visited == 6) {
            if ( min_complete_filter_value >= 0.0 && min_complete_filter_value < 1.00 ) {
                // Good range
                hist[(int)(min_complete_filter_value*(double)NHIST)][6]++;
            } else if ( min_complete_filter_value >= 1.00 && min_complete_filter_value < 10.00 ) {
                // All filters fulfiled
                histmax[6]++;
            } else if ( min_complete_filter_value >= 10.00 ) {
                // Total = 0
                histmin[6]++;
            }
        }
		//printf("Total : %d Minimum Filter Completeness %lf\n", total_visits_per_field, min_complete_filter_value);
	}

	// Distribution of Fields by Completeness
	char s[100];
	fprintf(fp, "\\begin{table}[H]{\\bf{Distribution of Fields by Completeness - WFD Observing Mode Only}} \\\\ [1.0ex]\n");
	fprintf(fp, "\\begin{tabular*}{\\textwidth}{\\tblspace lrrrrrrr}\n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\colhead{\\%% Complete} &\n");
	fprintf(fp, "\\colhead{u} &\n");
	fprintf(fp, "\\colhead{g} &\n");
	fprintf(fp, "\\colhead{r} &\n");
	fprintf(fp, "\\colhead{i} &\n");
	fprintf(fp, "\\colhead{z} &\n");
	fprintf(fp, "\\colhead{y} &\n");
	fprintf(fp, "\\colhead{Joint} \\\\ \n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\hline\n");	
	fprintf(fp, "$100 \\le P$ & ");
	for(i=0; i < 7; i++) {
		if ( i == 6) {
			fprintf(fp, "%4d \\\\", histmax[i]);
		}
		else {
			fprintf(fp, "%4d &", histmax[i]);
		}
	}
	fprintf(fp, "\n");
	for(i=NHIST-1; i >= 0; i--) {
		if ( i==0 ) {
			sprintf(s, "\\hspace{0.4cm}$%d < P < %d$ & ", i * (100/NHIST), (i+1) * (100/NHIST));
		} else {
			sprintf(s, "\\hspace{0.2cm}$%d \\le P < %d$ & ", i * (100/NHIST), (i+1) * (100/NHIST));
		}
		fprintf(fp, "%s", s);
		for(j=0; j < 7; j++) {
			if ( j == 6) {
				fprintf(fp, "%4d \\\\", hist[i][j]);
			}
			else {
				fprintf(fp, "%4d &", hist[i][j]);
			}
		}
		fprintf(fp, "\n");
	}
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\end{tabular*}\n");
	fprintf(fp, "\\caption{The distribution of the number of fields with a given percent completeness for each filter. A field's completeness is given by the percentage of the number of visits to that field compared to the WFD spec number of visits scaled to the length of this run (see Table \\ref{tab:SRDNumberTable}). Only visits acquired by observing modes designed to meet the WFD number of visits are included. Note that the number of fields that reached or exceeded the above condition is given by the $100 \\le P$ bin. Also note that creating the bins using the number of fields expected, $N$, is less precise than $P$ and results in a slightly different distribution. The last column is the joint completeness, which is the number of fields having a percent completeness, $P$, in \\emph{all} filters of \\emph{at least} a certain value.}\n");
	fprintf(fp, "\\label{tab:HistogramTable}\n");
	fprintf(fp, "\\end{table}\n");

	// Cumulative Distribution of Fields by Completeness
	fprintf(fp, "\\begin{table}[H]{\\bf{Cumulative Distribution of Fields by Completeness - WFD Observing Mode Only}} \\\\ [1.0ex]\n");
	fprintf(fp, "\\begin{tabular*}{\\textwidth}{\\tblspace lrrrrrrr}\n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\colhead{\\%% Complete} &\n");
	fprintf(fp, "\\colhead{u} &\n");
	fprintf(fp, "\\colhead{g} &\n");
	fprintf(fp, "\\colhead{r} &\n");
	fprintf(fp, "\\colhead{i} &\n");
	fprintf(fp, "\\colhead{z} &\n");
	fprintf(fp, "\\colhead{y} &\n");
	fprintf(fp, "\\colhead{Joint} \\\\ \n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\hline\n");	
	fprintf(fp, "$100 \\le P$ & ");
	for(i=0; i < 7; i++) {
		if ( i == 6) {
				fprintf(fp, "%4d \\\\", histmax[i]);
		}
		else {
				fprintf(fp, "%4d &", histmax[i]);
		}
	}
	fprintf(fp, "\n");
	for(i=NHIST-1; i >= 0; i--) {
		for(j=0; j < 7; j++) {
			if ( i == NHIST-1 ) {
				hist[i][j] += histmax[j];	
			} else {
				hist[i][j] += hist[i+1][j];
			}
		}
	}
	for(i=NHIST-1; i >= 0; i--) {
		if ( i==0 ) {
				sprintf(s, "\\hspace{0.4cm}$%d < P$ & ", i * (100/NHIST));
		} else {
				sprintf(s, "\\hspace{0.2cm}$%d \\le P$ & ", i * (100/NHIST));
		}
		fprintf(fp, "%s", s);
		for(j=0; j < 7; j++) {
			if ( j == 6) {
					fprintf(fp, "%4d \\\\", hist[i][j]);
			}
			else {
					fprintf(fp, "%4d &", hist[i][j]);
			}
		}
		fprintf(fp, "\n");
	}
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\end{tabular*}\n");
	fprintf(fp, "\\caption{The cumulative distribution of the number of fields with a given percent completeness for each filter. A field's completeness is given by the percentage of the number of visits to that field compared to the WFD spec number of visits scaled to the length of this run (see Table \\ref{tab:SRDNumberTable}). Only visits acquired by observing modes designed to meet the WFD number of visits are included. Note that the number of fields that reached or exceeded the above condition is given by the $100 \\le P$ bin. Also note that creating the bins using the number of fields expected, $N$, is less precise than $P$ and results in a slightly different distribution. The last column is the joint completeness, which is the number of fields having a percent completeness, $P$, in \\emph{all} filters of \\emph{at least} a certain value.}\n");
	fprintf(fp, "\\label{tab:CumHistogramTable}\n");
	fprintf(fp, "\\end{table}\n");
}

void makeHistogramTableAll() {
	int i, j;
	int valmax[6];
	int hist[NHIST][7]; // Why 7, 6 filters and 7th is for joint completeness
	int histmax[7];
	int histmin[7];
	char sql[1024];

	/* Initializations */
	double nRunSup = 10.00/atof(getConfigValue("nRun"));
	if ( useDesignStretch == 0 ) {	
		valmax[0] = 56/nRunSup;
		valmax[1] = 80/nRunSup;
		valmax[2] = 184/nRunSup;
		valmax[3] = 184/nRunSup;
		valmax[4] = 160/nRunSup;
		valmax[5] = 160/nRunSup;
	} else {
	  	valmax[0] = 70/nRunSup;
		valmax[1] = 100/nRunSup;
		valmax[2] = 230/nRunSup;
		valmax[3] = 230/nRunSup;
		valmax[4] = 200/nRunSup;
		valmax[5] = 200/nRunSup; 
	}

	for(i=0; i < NHIST; i++) {
		for (j=0; j < 7; j++) {
			hist[i][j] = 0;
			histmax[j] = 0;
		}
	}
	for (j=0; j < 7; j++) {
		histmax[j] = 0;
		histmin[j] = 0;
	}

	/* Initializations */

	// You have the fields list.
	// Cycle through the fields list and get all the observations for that field
	for(j=0; j < field_data_length; j++) {
		sprintf(sql, "select filter, count(*) as count from (select filter from output_%s_%d where fieldID=%d group by expDate) as t group by filter", hostname, sessionID, field_data[j].fieldID);
		//printf("Field : %d : %s\n", field_data[j].fieldID, sql);
		readFilterDataField(sql);
		
		// Now you have for each field - filter and how many times the field was visited in that filter
		// mysql> select filter, count(*) from (select filter from output_hewelhog_56 where fieldID=368 group by expDate) as t group by filter;
		// +--------+----------+
		// | filter | count(*) |
		// +--------+----------+
		// | g      |       26 |
		// | i      |       46 |
		// | r      |       51 |
		// | u      |       19 |
		// | y      |       79 |
		// | z      |       61 |
		// +--------+----------+
		// 6 rows in set (0.01 sec)

		double min_complete_filter_value = 10.00; // This is 1000 % very high % never possible
		int total_visits_per_field = 0;
		int number_of_filters_visited = 0;
        for (i=0; i < filter_datafield_length; i++) {
			double filter_completeness = 0.0;
			if (strcmp(filter_datafield[i].filter, "u") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[0];
				if ( filter_completeness >= 1.00 ) {
					histmax[0]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[0]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][0]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "g") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[1];
				if ( filter_completeness >= 1.00 ) {
					histmax[1]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[1]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][1]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "r") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[2];
				if ( filter_completeness >= 1.00 ) {
					histmax[2]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[2]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][2]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "i") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[3];
				if ( filter_completeness >= 1.00 ) {
					histmax[3]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[3]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][3]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "z") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[4];
				if ( filter_completeness >= 1.00 ) {
					histmax[4]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[4]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][4]++;
				}
                number_of_filters_visited++;
			} else if (strcmp(filter_datafield[i].filter, "y") == 0) {
				filter_completeness = (double)filter_datafield[i].count/valmax[5];
				if ( filter_completeness >= 1.00 ) {
					histmax[5]++;
				} else if (filter_datafield[i].count == 0 ) {
					histmin[5]++;
				} else {
					hist[(int)(filter_completeness*(double)NHIST)][5]++;
				}
                number_of_filters_visited++;
			}
			if ( filter_completeness < min_complete_filter_value )
				min_complete_filter_value = filter_completeness;
			total_visits_per_field += filter_datafield[i].count;
			//printf(	"%s %d\n", filter_datafield[i].filter, filter_datafield[i].count);
		}
		/*if ( min_complete_filter_value >= 1.00 && min_complete_filter_value < 10.00 ) {
			histmax[6]++;
		} else if (total_visits_per_field == 0 ) {
			histmin[6]++;
		} else {
            if ( min_complete_filter_value < 10.00 )
                hist[(int)(min_complete_filter_value*(double)NHIST)][6]++;
		}*/
        if ( number_of_filters_visited == 6) {
            if ( min_complete_filter_value >= 0.0 && min_complete_filter_value < 1.00 ) {
                // Good range
                hist[(int)(min_complete_filter_value*(double)NHIST)][6]++;
            } else if ( min_complete_filter_value >= 1.00 && min_complete_filter_value < 10.00 ) {
                // All filters fulfiled
                histmax[6]++;
            } else if ( min_complete_filter_value >= 10.00 ) {
                // Total = 0
                histmin[6]++;
            }
        }
        //printf("Total : %d Minimum Filter Completeness %lf\n", total_visits_per_field, min_complete_filter_value);
	}
	
	char s[100];
	fprintf(fp, "\\begin{table}[H]{\\bf{Distribution of Fields by Completeness - All Observing Modes}} \\\\ [1.0ex]\n");
	fprintf(fp, "\\begin{tabular*}{\\textwidth}{\\tblspace lrrrrrrr}\n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\colhead{\\%% Complete} &\n");
	fprintf(fp, "\\colhead{u} &\n");
	fprintf(fp, "\\colhead{g} &\n");
	fprintf(fp, "\\colhead{r} &\n");
	fprintf(fp, "\\colhead{i} &\n");
	fprintf(fp, "\\colhead{z} &\n");
	fprintf(fp, "\\colhead{y} &\n");
	fprintf(fp, "\\colhead{Joint} \\\\ \n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\hline\n");
	
	fprintf(fp, "$100 \\le P$ & ");
	for(i=0; i < 7; i++) {
		if ( i == 6) {
				fprintf(fp, "%4d \\\\", histmax[i]);
		}
		else {
				fprintf(fp, "%4d &", histmax[i]);
		}
	}
	fprintf(fp, "\n");
	for(i=NHIST-1; i >= 0; i--) {
		if ( i==0 ) {
				sprintf(s, "\\hspace{0.4cm}$%d < P < %d$ & ", i * (100/NHIST), (i+1) * (100/NHIST));
		} else {
				sprintf(s, "\\hspace{0.2cm}$%d \\le P < %d$ & ", i * (100/NHIST), (i+1) * (100/NHIST));
		}
		fprintf(fp, "%s", s);
		for(j=0; j < 7; j++) {
			if ( j == 6) {
					fprintf(fp, "%4d \\\\", hist[i][j]);
			}
			else {
					fprintf(fp, "%4d &", hist[i][j]);
			}
		}
		fprintf(fp, "\n");
	}
	/*fprintf(fp, "N = 0    \t\t");
	for(i=0; i < 7; i++) {
		fprintf(fp, "%d\t", histmin[i]);
	}
	fprintf(fp, "\n");*/
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\end{tabular*}\n");
	fprintf(fp, "\\caption{The distribution of the number of fields with a given percent completeness for each filter. A field's completeness is given by the percentage of the number of visits to that field compared to the WFD spec number of visits scaled to the length of this run (see Table \\ref{tab:SRDNumberTable}). All visits acquired by all observing modes are included and are not limited only to modes that were designed to meet the WFD number of visits. Note that the number of fields that reached or exceeded the above condition is given by the $100 \\le P$ bin. Also note that creating the bins using the number of fields expected, $N$, is less precise than $P$ and results in a slightly different distribution. The last column is the joint completeness, which is the number of fields having a percent completeness, $P$, in \\emph{all} filters of \\emph{at least} a certain value.}\n");
	fprintf(fp, "\\label{tab:HistogramTableAll}\n");
	fprintf(fp, "\\end{table}\n");

	// Cumulative Distribution of Fields by Completeness
	fprintf(fp, "\\begin{table}[H]{\\bf{Cumulative Distribution of Fields by Completeness - All Observing Modes}} \\\\ [1.0ex]\n");
	fprintf(fp, "\\begin{tabular*}{\\textwidth}{\\tblspace lrrrrrrr}\n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\colhead{\\%% Complete} &\n");
	fprintf(fp, "\\colhead{u} &\n");
	fprintf(fp, "\\colhead{g} &\n");
	fprintf(fp, "\\colhead{r} &\n");
	fprintf(fp, "\\colhead{i} &\n");
	fprintf(fp, "\\colhead{z} &\n");
	fprintf(fp, "\\colhead{y} &\n");
	fprintf(fp, "\\colhead{Joint} \\\\ \n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\hline\n");	
	fprintf(fp, "$100 \\le P$ & ");
	for(i=0; i < 7; i++) {
		if ( i == 6) {
				fprintf(fp, "%4d \\\\", histmax[i]);
		}
		else {
				fprintf(fp, "%4d &", histmax[i]);
		}
	}
	fprintf(fp, "\n");
	for(i=NHIST-1; i >= 0; i--) {
		for(j=0; j < 7; j++) {
			if ( i == NHIST-1 ) {
				hist[i][j] += histmax[j];	
			} else {
				hist[i][j] += hist[i+1][j];
			}
		}
	}
	for(i=NHIST-1; i >= 0; i--) {
		if ( i==0 ) {
				sprintf(s, "\\hspace{0.4cm}$%d < P$ & ", i * (100/NHIST));
		} else {
				sprintf(s, "\\hspace{0.2cm}$%d \\le P$ & ", i * (100/NHIST));
		}
		fprintf(fp, "%s", s);
		for(j=0; j < 7; j++) {
			if ( j == 6) {
					fprintf(fp, "%4d \\\\", hist[i][j]);
			}
			else {
					fprintf(fp, "%4d &", hist[i][j]);
			}
		}
		fprintf(fp, "\n");
	}
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\hline\n");
	fprintf(fp, "\\end{tabular*}\n");
	fprintf(fp, "\\caption{The cumulative distribution of the number of fields with a given percent completeness for each filter. A field's completeness is given by the percentage of the number of visits to that field compared to the WFD spec number of visits scaled to the length of this run (see Table \\ref{tab:SRDNumberTable}). Only visits acquired by observing modes designed to meet the WFD number of visits are included. Note that the number of fields that reached or exceeded the above condition is given by the $100 \\le P$ bin. Also note that creating the bins using the number of fields expected, $N$, is less precise than $P$ and results in a slightly different distribution. The last column is the joint completeness, which is the number of fields having a percent completeness, $P$, in \\emph{all} filters of \\emph{at least} a certain value.}\n");
	fprintf(fp, "\\label{tab:CumHistogramTable}\n");
	fprintf(fp, "\\end{table}\n");
}

void makeTable() {
	int i, j, outliers, inliers;
	char sql[1024];
	double average, std_dev, median;
	char whatsql[128];
	
	sprintf(whatsql, "%s", "fieldID");


	/*write("\\begin{table}[H]{\\bf{Characteristics of the Distributions}} \\\\ [1.0ex]");
	write("\\begin{tabular*}{\\textwidth}{\\tblspace lcrrrrr}");
	write("\\hline");
	write("\\colhead{Observing Mode ID} &");
	write("\\colhead{Filter} &");
	write("\\colhead{Median} &");
	write("\\colhead{Mean $\\pm$ rms} &");
	write("\\colhead{$+ 3\\sigma$} &");
	write("\\colhead{$- 3\\sigma$} &");
	write("\\colhead{Total} \\\\");
	write("\\hline");*/

	write("{\\bf Characteristics of the Distributions}");
	write("\\begin{longtable}[H]{lcrrrrr}");
	write("\\hline \\hline");
	write("\\bfseries Observing Mode ID & \\bfseries Filter & \\bfseries Median & \\bfseries Mean $\\pm$ rms & \\bfseries $+3\\sigma$ & \\bfseries $- 3\\sigma$ & \\bfseries Total \\\\"); 
	write("\\hline");
	write("\\endfirsthead");
	write("\\multicolumn{7}{l}{\\bf Characteristics of the Distributions \\emph{(con't)}} \\\\ [1.0ex]");
	write("\\hline");
	write("\\bfseries Observing Mode ID & \\bfseries Filter & \\bfseries Median & \\bfseries Mean $\\pm$ rms & \\bfseries $+3\\sigma$ & \\bfseries $- 3\\sigma$ & \\bfseries Total \\\\");
	write("\\hline");
	write("\\endhead");
	write("\\hline");
	write("\\multicolumn{7}{r}{\\emph{Continued on next page}}");
	write("\\endfoot");
	write("\\endlastfoot");


	for(i=0; i < proposal_list_length; i++) {
		/* U filter */
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='u' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		createVisitDataField();
		comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, "Observing Mode %d & u & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", proposal_list[i].propID, median, average, std_dev, outliers, inliers, visit_datafield_length);
		write(s);
 
		/* G filter */
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='g' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		createVisitDataField();
		comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, "\\emph{%s} & g & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", proposal_list[i].propConf, median, average, std_dev, outliers, inliers, visit_datafield_length);
		write(s);
 
		/* R filter */ 
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='r' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		createVisitDataField();
		comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, " & r & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length); 
		write(s);
 
		/* I filter */ 
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='i' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		createVisitDataField();
		comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, " & i & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length); 
		write(s);
 
		/* Z filter */ 
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='z' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		createVisitDataField();
		comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, " & z & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length); 
		write(s);
 
		/* Y filter */ 
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='y' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		createVisitDataField();
		comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, " & y & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length); 
		write(s);

 		write("\\hline");
	        
		/* page break */
		if (i==5) write("\\newpage");
 	}

	/* All proposals*/

	/* U filter */
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='u' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	createVisitDataField();
	comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, "All Observing Modes & u & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length);
	write(s);

	/* G filter */
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='g' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	createVisitDataField();
	comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & g & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length);
	write(s);

	/* R filter */ 
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='r' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	createVisitDataField();
	comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & r & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length); 
	write(s);

	/* I filter */ 
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='i' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	createVisitDataField();
	comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & i & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length); 
	write(s);

	/* Z filter */ 
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='z' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	createVisitDataField();
	comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & z & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length); 
	write(s);

	/* Y filter */ 
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='y' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	createVisitDataField();
	comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & y & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length); 
	write(s);

	write("\\hline");

	/* All filter All proposals*/ 
	sprintf(sql, "select %s as obuffer from output_%s_%d group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	createVisitDataField();
	comp_statistics (visit_datafield, visit_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, "All Observing Modes & All & %3.0f & %3.1f $\\pm$ %3.1f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, visit_datafield_length); 
	write(s);

	write("\\hline \\hline \\\\ [0.5ex]");
	/*write("\\end{tabular*}");*/
	write("\\caption{The median, mean and standard deviation for number of visits to a field separated by observing mode and by filter. The $+3\\sigma$ column shows the number of fields which had a number of visits more than $3\\sigma$ greater than the median number of visits; the $-3\\sigma$ column shows the number of fields with number of visits fewer than $3\\sigma$ less than the mean value. The Total column shows the number of fields evaluated in each observing mode/filter combination.}");
	write("\\label{tab:visits}");
	write("\\end{longtable}");
}

int main(int argc, char **argv) {
	if (argc == 5) {
		if ( argc == 5 ) {
			sprintf(hostname, "%s", argv[1]);
		} else {
			if ( gethostname(identifier, identifier_length) == 0 ) {
				sprintf(hostname, "%s", identifier);
			} else {
				printf( "Hostname : %s\n", strerror(errno));
				exit(1);
			}
		}
		sessionID = atoi(argv[3]);
		useDesignStretch = atoi(argv[4]);
		sprintf(identifier, "%s.%d", hostname, sessionID);
		// Open Database Connection
		openDB(argv[2]);
		// Read Config Data
		readConfigData();
		// Read Session Data
		readSessionData();
		// Read Proposal Data
		readPropData();
		// Read Fields Data
		readFieldsData();

		/* Write Table */
		openVisitTableTex();
		makeTable();
		closeTex();

		/* Write Histogram For only Universal */
		openHistogramTableTex();
		makeHistogramTable();
		/* End Write Table */
		closeTex();

		/* Write Histogram For all Observations */
		openHistogramTableAllTex();
		makeHistogramTableAll();
		/* End Write Table */
		closeTex();


		closeDB();
	} else {
		printf("Error : Number of arguments");
		exit(1);
	}
}
