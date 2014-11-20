/*
  maketex code
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

void openTex() {
	sprintf(s, "../output/%s_%d_sstar.tex", hostname, sessionID);
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

void makeFreqVisitTable() {
	FILE* tfp;
	sprintf(s, "../output/%s_%d_SixVisits.tex", hostname, sessionID);
	tfp = fopen(s, "r");
	char line[1000];
	while (fgets(line, 1000, tfp) != NULL) {
		write(line);
	}	
	fclose(tfp);
}

void makeAllFreqVisitTable() {
	FILE* tfp;
	sprintf(s, "../output/%s_%d_SixVisits-All.tex", hostname, sessionID);
	tfp = fopen(s, "r");
	char line[1000];
	while (fgets(line, 1000, tfp) != NULL) {
		write(line);
	}	
	fclose(tfp);
}

void make5sigmaTable() {
	FILE* tfp;
	sprintf(s, "../output/%s_%d_5sigma.tex", hostname, sessionID);
	tfp = fopen(s, "r");
	char line[1000];
	while (fgets(line, 1000, tfp) != NULL) {
		write(line);
	}	
	fclose(tfp);
}

void make5sigma2Table() {
        FILE* tfp;
        sprintf(s, "../output/%s_%d_5sigma2.tex", hostname, sessionID);
        tfp = fopen(s, "r");
        char line[1000];
        while (fgets(line, 1000, tfp) != NULL) {
                write(line);
        }
        fclose(tfp);
}

void makeSeeingTable() {
	FILE* tfp;
	sprintf(s, "../output/%s_%d_seeing.tex", hostname, sessionID);
	tfp = fopen(s, "r");
	char line[1000];
	while (fgets(line, 1000, tfp) != NULL) {
		write(line);
	}	
	fclose(tfp);
}

void makeRevisitTimeTable() {
	FILE* tfp;
	sprintf(s, "../output/%s_%d_revisit-time.tex", hostname, sessionID);
	tfp = fopen(s, "r");
	char line[1000];
	while (fgets(line, 1000, tfp) != NULL) {
		write(line);
	}	
	fclose(tfp);
}

void addQuickFireStatistics() {
	FILE* tfp;
	sprintf(s, "../output/%s_%d_quickstats.tex", hostname, sessionID);
	tfp = fopen(s, "r");
	char line[1000];
	while (fgets(line, 1000, tfp) != NULL) {
		write(line);
	}	
	fclose(tfp);
}

void addSummaryReport() {
	FILE* tfp;
	sprintf(s, "../output/%s_%d_summaryreport_sec1.txt", hostname, sessionID);
    	tfp = fopen(s, "r");
	char line[1000];
	while (fgets(line, 1000, tfp) != NULL) {
		line[strlen(line)-1] = '\0';
        	write(line);
	//	printf("%s\n", line);
	}
	fclose(tfp);

	write("\n");
        sprintf(s, "../output/%s_%d_summaryreport_sec2.txt", hostname, sessionID);
        tfp = fopen(s, "r");
        while (fgets(line, 1000, tfp) != NULL) {
                line[strlen(line)-1] = '\0';
                write(line);
        //        printf("%s\n", line);
        }
        fclose(tfp);
}

void makeTable(char* what) {
	int i, j, outliers, inliers;
	char sql[1024];
	char whatsql[80];
	char table_heading[80];
	double average, std_dev, median;

	if (strcmp(what, "Limiting Magnitude") == 0) {
		sprintf(whatsql, "fivesigma_ps");
		sprintf(table_heading, "Single Visit Depth");
	} else if (strcmp(what, "Sky Brightness") == 0) {
		sprintf(whatsql, "perry_skybrightness");
		sprintf(table_heading, "Sky Brightness");
	} else if (strcmp(what, "Seeing") == 0) {
		sprintf(whatsql, "finSeeing");
		sprintf(table_heading, "Seeing");
	} else if (strcmp(what, "Airmass") == 0) {
		sprintf(whatsql, "airmass");
		sprintf(table_heading, "Airmass");
	} 

	/*sprintf(s, "\\begin{table}[H]{\\textbf{%s}} \\\\ [1.0ex]", table_heading);
	write(s);
	write("\\begin{tabular*}{\\textwidth}{\\tblspace lcllrrr}");
	write("\\hline");
	write("\\colhead{Observing Mode ID} &");
	write("\\colhead{Filter} &");
	write("\\colhead{Median} &");
	write("\\colhead{Mean $\\pm$ rms} &");
	write("\\colhead{$+ 3\\sigma$} &");
	write("\\colhead{$- 3\\sigma$} &");
	write("\\colhead{Total} \\\\");
	write("\\hline");*/

    sprintf(s, "{\\bf %s}", table_heading);
	write(s);
	write("\\begin{longtable}[H]{lcrrrrr}");
	write("\\hline \\hline");
	write("\\bfseries Observing Mode ID & \\bfseries Filter & \\bfseries Median & \\bfseries Mean $\\pm$ rms & \\bfseries $+3\\sigma$ & \\bfseries $- 3\\sigma$ & \\bfseries Total \\\\"); 
	write("\\hline");
	write("\\endfirsthead");
	sprintf(s, "\\multicolumn{7}{l}{\\bf %s \\emph{(con't)}} \\\\ [1.0ex]", table_heading);
	write(s);
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
		comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, "Observing Mode %d & u & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", proposal_list[i].propID, median, average, std_dev, outliers, inliers, observation_datafield_length);
		write(s);
 
		/* G filter */
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='g' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, "\\emph{%s} & g & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", proposal_list[i].propConf, median, average, std_dev, outliers, inliers, observation_datafield_length);
		write(s);
 
		/* R filter */ 
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='r' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, " & r & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length); 
		write(s);
 
		/* I filter */ 
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='i' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, " & i & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length); 
		write(s);
 
		/* Z filter */ 
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='z' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, " & z & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length); 
		write(s);
 
		/* Y filter */ 
		sprintf(sql, "select %s as obuffer from output_%s_%d where propID=%d and filter='y' order by %s;", whatsql, hostname, sessionID, proposal_list[i].propID, whatsql);
		readObservationDataField(sql);
		comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
		sprintf(s, " & y & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length); 
		write(s);

 		write("\\hline");

		/* Page break */
		if (i==5) write("\\newpage");
 	}

	/* All proposals*/

	/* U filter */
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='u' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, "All Observing Modes & u & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length);
	write(s);

	/* G filter */
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='g' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & g & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length);
	write(s);

	/* R filter */ 
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='r' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & r & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length); 
	write(s);

	/* I filter */ 
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='i' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & i & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length); 
	write(s);

	/* Z filter */ 
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='z' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & z & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length); 
	write(s);

	/* Y filter */ 
	sprintf(sql, "select %s as obuffer from output_%s_%d where filter='y' group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, " & y & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length); 
	write(s);

	write("\\hline");

	/* All filter All proposals*/ 
	sprintf(sql, "select %s as obuffer from output_%s_%d group by expDate order by %s;", whatsql, hostname, sessionID, whatsql);
	readObservationDataField(sql);
	comp_statistics (observation_datafield, observation_datafield_length, &average, &std_dev, &median, &outliers, &inliers);
	sprintf(s, "All Observing Modes & All & %5.3f & %5.3f $\\pm$ %5.3f & %d & %d & %d\\\\", median, average, std_dev, outliers, inliers, observation_datafield_length); 
	write(s);

	write("\\hline \\hline \\\\ [0.5ex]");
	/*write("\\end{tabular*}");*/
	if (strcmp(what, "Limiting Magnitude") == 0) {
		write("\\caption{The median, mean and standard deviation of the single visit depth ($5\\sigma$ limiting magnitude) values for all visits separated by observing mode and by filter. The $+3\\sigma$ column shows the number of visits which had a single visit depth more than $3\\sigma$ fainter than the median single visit depth; the $-3\\sigma$ column shows the number of visits with a single visit depth more than $3\\sigma$ brighter than the median single depth. The Total column shows the number of visits counted toward each observing mode/filter combination.}");
	} else if (strcmp(what, "Sky Brightness") == 0) {
		write("\\caption{The median, mean and standard deviation of the sky brightness values for all visits separated by observing mode and by filter. The $+3\\sigma$ column shows the number of visits which had a sky brightness more than $3\\sigma$ fainter than the median single visit depth; the $-3\\sigma$ column shows the number of visits with a sky brightness more than $3\\sigma$ brighter than the median sky brightness. The Total column shows the number of visits counted toward each observing mode/filter combination.}");
	} else if (strcmp(what, "Seeing") == 0) {
		write("\\caption{The median, mean and standard deviation of the seeing values for all visits separated by observing mode and by filter. The $+3\\sigma$ column shows the number of visits which had a seeing more than $3\\sigma$ greater than the median seeing; the $-3\\sigma$ column shows the number of visits with a seeing more than $3\\sigma$ smaller than the median seeing. The Total column shows the number of visits counted toward each observing mode/filter combination.}");
	} else if (strcmp(what, "Airmass") == 0) {
		write("\\caption{The median, mean and standard deviation of the airmass values for all visits separated by observing mode and by filter. The $+3\\sigma$ column shows the number of visits which had an airmass more than $3\\sigma$ greater than the median airmass; the $-3\\sigma$ column shows the number of visits with an airmass more than $3\\sigma$ smaller than the median airmass. The Total column shows the number of visits counted toward each observing mode/filter combination.}");
	} 
	sprintf(s, "\\label{tab:%s}", what);
	write(s);
	write("\\end{longtable}");
}

void writeTitlePage() {
	write("\\documentclass{hitec}");
	write("\\newcommand\\colhead[1]{\\multicolumn{1}{l}{#1}}");
	write("\\newcommand\\tblspace{@{\\hspace{6pt}}@{\\extracolsep\\fill}}");
	write("\\setlength\\textheight{8.6in}");
	write("\\setlength\\topmargin{-0.2in}");
	if ( useDesignStretch == 0 ) {
		sprintf(s, "\\title{Operations Simulator Tools for Analysis and Reporting \\\\ Standard Report for {\\it %s} \\\\ Compared to Design Specifications \\\\ Version 4.0}", identifier);
	} else {
		sprintf(s, "\\title{Operations Simulator Tools for Analysis and Reporting \\\\ Standard Report for {\\it %s} \\\\ Compared to Stretch Specifications \\\\ Version 4.0}", identifier);
	}
	write(s);
	write("\\author{Operations Simulation Team}");
	write("\\company{Large Synoptic Survey Telescope}");
	write("\\usepackage{hyperref}");
	write("\\usepackage[pdftex]{graphicx}");
	write("\\usepackage{verbatim,moreverb}");
	write("\\usepackage{listings}");
	write("\%\\lstset{breaklines=true}");
	write("\\usepackage{float}");
	write("\\usepackage{longtable}");
	write("\\setlength\\LTcapwidth{\\textwidth}");
	write("\\restylefloat{figure}");
	write("\\restylefloat{table}");
	write("\\usepackage{color}");
	write("\\setlength\\marginparwidth{1.25in}");
	write("\\setlength\\marginparsep{.25in}");
	write("\\setlength\\marginparpush{.25in}");
	write("\\reversemarginpar");
	write("\\begin{document}");
	write("\\maketitle");
	write("\\tableofcontents");
	write("\\clearpage");
}

void write1stSection() {
	write("\\section{Introduction}");
	sprintf(s, "This report is intended to assist in the evaluation of the performance of this simulated survey, {\\it %s.%d}, which was generated by the Operations Simulator code base. Please be aware that this simulated survey is just one of many that the Operations Simulation (OpSim) team have prepared. The Operations Simulator is currently still under development; many aspects of its performance (with regards to LSST's operations) are still subject to optimization and certainly are subject to change. These modifications could potentially include changes to the number of visits per field, the number of fields on the sky, and almost certainly will include changes in the observational cadence.", hostname, sessionID);
	write(s);
	write("\n");
	write("This report is not the final word on ``how LSST will perform'' ten years from now; instead it should be considered as an aid to help users and the OpSim team decide what changes will optimize the scientific return from LSST. Thus this evaluation should be considered a ``work in progress''. We encourage science collaboration members to provide feedback to the Operations Simulation team, through their collaboration chair, if they have suggestions for additional figures of merit or other methods for evaluation of the Operations Simulator runs.");

}

void write2ndSection() {
	write("\\section{Cadence Design}");
	
	write("\\subsection{Observing Modes}");
	write("A simulated survey is driven by at least one but usually more ``observing modes.'' An observing mode is a cadence strategy designed to visit and revisit specific fields on the sky in a way that meets a particular science objective. The observing mode is described by a set of parameters specified in one or more a configuration files (*.conf). Visits made by observing modes designed to acquire fields such that the deep cosmology or wide-fast-deep (WFD) science specifications (specs) of the Science Requirements Document (SRD) are met can be singled out for analysis.");
	write("\n");
	write("There are currently two classes of observing mode: weakLensConf (WL) and WLpropConf (WLTSS).  These classes denote two different cadence strategies, and while their names originated in the type of science they were historically intended to do, now they simply represent different ways to survey the sky. The weakLensConf class is used to accumulate visits in field-filter combinations up to the requested number of visits set in the configuration file.  The WLpropConf class is used to set up sequences or nested sequences to collect a series of visits at particular time intervals in addition to a number field-filter combinations.");
	write("\n");
	write("A typical simulation may use some or all of the following configuration files.");
	
	write("\\begin{description}");
	write("\\item[Universal-18-0824.conf] The ``universal'' cadence for the WFD survey; covers $\\sim$18,000 deg$^2$ where fields are visited twice per night separated by about 30 minutes on average every few nights in different filters.");
	write("\\item[NorthEclipticSpur-18.conf] Covers the north ecliptic spur (NES) in order to detect solar system objects throughout the ecliptic plane, and uses a similar cadence as Universal-18-0824.conf with no u or y observations.");
	write("\\item[DDcosmology1.conf] Consists of 5 target fields, also known as the ``deep drilling'' fields, which acquire about 2 hours of exposure time in all bands in rapid sequence, every three days.");
	write("\\item[GalacticPlaneProp.conf] Covers the plane of the Milky Way with a defined number of visits per field.");
	write("\\item[SouthCelestialPole-18.conf] Covers the south celestial pole with a defined number of visits per field.");
	write("\\item[Standby.conf] Essentially the WFD cadence which requests observations only when no other mode requests observations. This mode was used in OpSim v2.x versions to fill observing time when no other proposal needed visits, however, in OpSim v3.x a different strategy will be implemented.");
	write("\\end{description}");

	write("\\begin{table}[H]{\\bf Observing Modes in this Survey} \\\\ [1.0ex]");
	write("\\begin{tabular*}{\\textwidth}{\\tblspace lllrrr}");
	write("\\hline\\hline");
	write("\\colhead{ID} &");
	write("\\colhead{Type} &");
	write("\\colhead{Name} &");
	write("\\colhead{Relative} &");
	write("\\colhead{User Regions} &");
    write("\\colhead{Look Ahead}\\\\");
	write("\\colhead{(propID)} &");
	write("\\colhead{(propName)} &");
	write("\\colhead{(propConf)} &");
	write("\\colhead{Priority} &");
	write("\\colhead{(userRegion)} &");
	write("\\colhead{(lookahead)} \\\\");
	write("\\hline");
	
	int i;
	for(i=0; i < proposal_list_length; i++) {
		sprintf(s, "%d & %s & %s & %5.3f & %d & %s\\\\",
				proposal_list[i].propID, proposal_list[i].propName, proposal_list[i].propConf, proposal_list[i].priority, proposal_list[i].nUserRegions, proposal_list[i].lookahead);
		write(s);
	}

	write("\\hline \\hline");
	write("\\end{tabular*}"); 
	write("\\caption{The identification number, type, and name for each observing mode configuration file used in this simulated survey. The identification number is unique to each simulation. Regions of special interest are defined by a list of fields or User Regions; the number of user regions is given along with the relative priority assigned to each mode. If the number of User Regions is zero, the number of fields are defined by the available sky. User Regions are not required to have a one-to-one mapping to the list of field centers used by the Simulator. A selected group of parameters from each configuration file are presented in \\S \\ref{sec:PropSpecs}}");
	write("\\label{tab:Proposals}");
	write("\\end{table}");

	write("\\subsection{Configuration Files}");
	
    write("\\begin{table}[H]{\\bf Filter Specifications} \\\\ [1.0ex]");
    write("\\begin{tabular*}{\\textwidth}{\\tblspace lllllll}");
    write("\\hline \\hline");
    write("\\colhead{Parameter} &");
    write("\\colhead{u} &");
    write("\\colhead{g} &");
    write("\\colhead{r} &");
    write("\\colhead{i} &");
    write("\\colhead{z} &");
    write("\\colhead{y} \\\\");
    write("\\hline");
    sprintf(s, "Filter\\_MinBrig%s \\\\", getTexStringForConfigValue("Filter_MinBrig", "filters"));
    write(s);
    sprintf(s, "Filter\\_MaxBrig%s \\\\", getTexStringForConfigValue("Filter_MaxBrig", "filters"));
    write(s);
    sprintf(s, "Filter\\_Wavelen%s \\\\", getTexStringForConfigValue("Filter_Wavelen", "filters"));
    write(s);
    sprintf(s, "Filter\\_ExpFactor%s \\\\", getTexStringForConfigValue("Filter_ExpFactor", "filters"));
    write(s);
    
    write("\\hline \\hline");
    write("\\end{tabular*}");
    write("\\caption{A subset of parameters from Filters.conf}");
    write("\\label{tab:Filters}");
    write("\\end{table}");
    
    write("\\begin{table}[H]{\\bf Survey Specifications} \\\\ [1.0ex]");
    write("\\begin{tabular*}{\\textwidth}{\\tblspace lll}");
    write("\\hline \\hline");
    write("\\colhead{Characteristic} &");
    write("\\colhead{Parameter} &");
    write("\\colhead{Value} \\\\");
    write("\\hline");
	sprintf(s, "\\ \\ Run Identifier & sessionHost.sessionID & %s \\\\", identifier);
	write(s);
	sprintf(s, "\\ \\ Run Start Date & sessionDate &  %s \\\\", session_data.sessionDate);
	write(s);
	sprintf(s, "\\ \\ Code Version & version & %s \\\\", session_data.version);
	write(s);
    write("\\hline");
    write("LSST.conf & & \\\\");
    write("\\hline");
	sprintf(s, "\\ \\ Length of Run & nRun	& %s year(s) \\\\", getConfigValue("nRun"));
	write(s);
	sprintf(s, "\\ \\ Start Day of Weather Data & simStartDay	& %s \\\\", getConfigValue("simStartDay"));
	write(s);
    sprintf(s, "\\ \\ Field of View & fov & %s deg\\\\", getConfigValue("fov"));
    write(s);
    sprintf(s, "\\ \\ Telescope adds to PSF & telSeeing & %s arcsec\\\\", getConfigValue("telSeeing"));
    write(s);
    sprintf(s, "\\ \\ Optical Design adds to PSF & opticalDesSeeing & %s arcsec\\\\", getConfigValue("opticalDesSeeing"));
    write(s);
    sprintf(s, "\\ \\ Camera adds to PSF & cameraSeeing & %s arcsec\\\\", getConfigValue("cameraSeeing"));
    write(s);
    sprintf(s, "\\ \\ Site Information & siteConf	& %s \\\\", getConfigValue("siteConf"));
    write(s);
    sprintf(s, "\\ \\ Cloudiness Threshold & maxCloud & %s \\\\", getConfigValue("maxCloud"));
    write(s);
    write("\\hline");
    write("SchedulingData.conf & &  \\\\");
    write("\\hline");
    sprintf(s, "\\ \\ Look-ahead Period & lookAheadNights & %s \\\\", getConfigValue("lookAheadNights"));
    write(s);
    sprintf(s, "\\ \\ Look-ahead Increment & lookAheadInterval & %s sec\\\\", getConfigValue("lookAheadInterval"));
    write(s);
    write("\\hline");
    write("Scheduler.conf & & \\\\");
    write("\\hline");
    sprintf(s, "\\ \\ Slew Bonus & MaxSlewTimeBonus & %s \\\\", getConfigValue("MaxSlewTimeBonus"));
    write(s);
    sprintf(s, "\\ \\ Proposal Target Suggestions & NumSuggestedObsPerProposal & %s  \\\\", getConfigValue("NumSuggestedObsPerProposal"));
    write(s);
    sprintf(s, "\\ \\ Sky Recalculation & recalcSkyCount & %s \\\\", getConfigValue("recalcSkyCount"));
    write(s);
    sprintf(s, "\\ \\ Target List Length & reuseRankingCount & %s \\\\", getConfigValue("reuseRankingCount"));
    write(s);
    sprintf(s, "\\ \\ Minimum Seeing & tooGoodSeeingLimit & %s arcsec\\\\", getConfigValue("tooGoodSeeingLimit"));
    write(s);
    sprintf(s, "\\ \\ Randomization & randomizeSequencesSelection & %s \\\\", getConfigValue("randomizeSequencesSelection"));
    write(s);
    sprintf(s, "\\ \\ Dark Time Illumination & NewMoonPhaseThreshold & %s \\%% \\\\", getConfigValue("NewMoonPhaseThreshold"));
    write(s);
    sprintf(s, "\\ \\ Filter Swap Minimum & NminFiltersToSwap & %s \\\\", getConfigValue("NminFiltersToSwap"));
    write(s);
    sprintf(s, "\\ \\ Filter Swap Maximum & NmaxFiltersToSwap & %s \\\\", getConfigValue("NmaxFiltersToSwap"));
    write(s);
    sprintf(s, "\\ \\ Moon-Target Limit & MinDistance2Moon & %s \\\\", getConfigValue("MinDistance2Moon"));
    write("\\hline");
    write("AstronomicalSky.conf & &  \\\\");
    write("\\hline");
    sprintf(s, "\\ \\ Night Boundary & SunAltitudeNightLimit & %s deg \\\\", getConfigValue("SunAltitudeNightLimit"));
    write(s);
    sprintf(s, "\\ \\ Twilight Boundary & SunAltitudeTwilightLimit & %s deg \\\\", getConfigValue("SunAltitudeTwilightLimit"));
    write(s);
    sprintf(s, "\\ \\ Twilight Sky Brightness & TwilightBrightness & %s V mags \\\\", getConfigValue("TwilightBrightness"));
    write(s);
    write("\\hline");
    write("Instrument.conf & & \\\\");
    write("\\hline");
    sprintf(s, "\\ \\ Rotator Tracking & Rotator\\_FollowSky & %s \\\\", getConfigValue("Rotator_FollowSky"));
    write(s);
    sprintf(s, "\\ \\ Filter Change Time & Filter\\_MoveTime  & %s sec\\\\", getConfigValue("Filter_MoveTime"));
    write(s);
    sprintf(s, "\\ \\ Settle Time & Settle\\_Time  & %s sec\\\\", getConfigValue("Settle_Time"));
    write(s);
    sprintf(s, "\\ \\ Dome Settle Time & DomSettle\\_Time & %s sec\\\\", getConfigValue("DomSettle_Time"));
    write(s);
    sprintf(s, "\\ \\ Readout Time & Readout\\_Time & %s sec\\\\", getConfigValue("Readout_Time"));
    write(s);
    sprintf(s, "\\ \\ Telescope Minimum & Telescope\\_AltMin & %s deg\\\\", getConfigValue("Telescope_AltMin"));
    write(s);
    sprintf(s, "\\ \\ Telescope Maximum & Telescope\\_AltMax & %s deg\\\\", getConfigValue("Telescope_AltMax"));
    write(s);
    sprintf(s, "\\ \\ Seeing Table & seeingTbl & %s \\\\", getConfigValue("seeingTbl"));
    write(s);
    sprintf(s, "\\ \\ Cloud Table & cloudTbl & %s \\\\", getConfigValue("cloudTbl"));
    write(s);
    write("\\hline \\hline");
    write("\\end{tabular*}");
    write("\\caption{A  list of the most frequently modified or monitored parameters from the configuration files which completely specify a simulated survey.}");
    write("\\label{tab:SurveySpec}");
    write("\\end{table}");
	write("\\clearpage");

	write("\\subsection{Benchmarks}");
	double nRun = (double)atof(getConfigValue("nRun"));
	write("\\begin{table}[H]{\\bf Wide-Fast-Deep (WFD) Benchmarks} \\\\ [1.0ex]");
	write("\\begin{tabular*}{\\textwidth}{\\tblspace llrrrrrr}"); 
	write("\\hline\\hline");
	write("\\colhead{Row} &");
	write("\\colhead{Benchmark} &");
	write("\\colhead{u} &");
	write("\\colhead{g} &");
	write("\\colhead{r} &");
	write("\\colhead{i} &");
	write("\\colhead{z} &");
	write("\\colhead{y} \\\\");
    write("\\hline");
    sprintf(s, "1 & Seeing & %4.2f & %4.2f & %4.2f & %4.2f & %4.2f & %4.2f \\\\", 0.77, 0.73, 0.70, 0.67, 0.65, 0.63);
    write(s);	
    sprintf(s, "2 & Sky Brightness & %4.2f & %4.2f & %4.2f & %4.2f & %4.2f & %4.2f \\\\", 21.8, 22.0, 21.3, 20.0, 19.1, 17.5);
    write(s);
	write("\\hline"); 
 	write("& 10 Year Design Specs & & & & & & \\\\");
	write("\\hline");
	write("3 & \\ \\ \\ Number of Visits & 56 & 80 & 184 & 184 & 160 & 160 \\\\");
	sprintf(s, "4 & \\ \\ \\ Single Visit Depth & %4.1f & %4.1f & %4.1f & %4.1f & %4.1f & %4.1f \\\\", 23.9, 25.0, 24.7, 24.0, 23.3, 22.1);
	write(s);
	sprintf(s, "5 & \\ \\ \\ Coadded Depth & %4.1f & %4.1f & %4.1f & %4.1f & %4.1f & %4.1f \\\\", 26.1, 27.4, 27.5, 26.8, 26.1, 24.9);
	write(s);
	write("\\hline");
    write("& 10 Year Stretch Specs & & & & & & \\\\");
    write("\\hline");
    write("6 & \\ \\ \\ Number of Visits & 70 & 100 & 230 & 230 & 200 & 200 \\\\");
    sprintf(s, "7 & \\ \\ \\ Single Visit Depth & %4.1f & %4.1f & %4.1f & %4.1f & %4.1f & %4.1f \\\\", 24.0, 25.1, 24.8, 24.1, 23.4, 22.2);
    write(s);
    sprintf(s, "8 & \\ \\ \\ Coadded Depth & %4.1f & %4.1f & %4.1f & %4.1f & %4.1f & %4.1f \\\\", 26.3, 27.5, 27.7, 27.0, 26.2, 24.9);
    write(s);
    write("\\hline");
 	write("& \\multicolumn{3}{l}{Specs Scaled to Length of Run} & & & \\\\");
	write("\\hline");
	sprintf(s, "9 & \\ \\ \\ Design Number of Visits & %d & %d & %d & %d & %d & %d \\\\", (int)(56.00*nRun/10.00), (int)(80.00*nRun/10.00), (int)(184.00*nRun/10.00), (int)( 184.00*nRun/10.00), (int)(160.00*nRun/10.00), (int)(160.00*nRun/10.00));
	write(s);
	sprintf(s, "10 & \\ \\ \\ Stretch Number of Visits & %d & %d & %d & %d & %d & %d \\\\", (int)(70.00*nRun/10.00), (int)(100.00*nRun/10.00), (int)(230.00*nRun/10.00), (int)( 230.00*nRun/10.00), (int)(200.00*nRun/10.00), (int)(200.00*nRun/10.00));
	write(s);
	write("\\hline \\hline");
	write("\\end{tabular*}"); 
	write("\\caption{A summary of the benchmarks to which many statistics in this document compare. Rows 1 and 2 are the expected median values of seeing (arcsec) and sky brightness (arcsec/mag$^2$) at zenith (Ivezic et al., astroph/0805.2366v1, Table 1). The Wide-Fast-Deep (WFD) design and stretch specs are listed for a 10-year survey. The design and stretch single visit depths (rows 4 and 7) are the 5$\\sigma$ limiting magnitude for each filter at zenith in new moon with median seeing in AB magnitudes (DocuShare Document-212, ``The LSST Science Requirements Document'', Table 6). Rows 3 and 5 list the design specification for the number of visits and coadded depth by filter (Document-212, Table 22); Rows 6 and 8 list the stretch specification for the number of visits and coadded depth by filter (Ivezic et al., astroph/0805.2366v1, Table 1). In rows 9 and 10, the design and stretch number of visits are scaled linearly by the length of this run (nRun) and will be identical to rows 3 and 6 for a 10-year simulation. For $nRun < 10$ the scaled value of number of visits is truncated, not rounded, when used in comparison graphs and tables. Currently evaluations of the areal sky coverage are not made directly in this report; however, the design and stretch specifications are 18,000 deg$^2$ and 20,000 deg$^2$, respectively.}");
	write("\\label{tab:SRDNumberTable}");
	write("\\end{table}");		
}

void write3rdSection() {
	write("\\section{Survey Visits}");
	
	write("\\subsection{A Visit Defined}");
	write("An observation of a target field is simulated by a ``visit.'' Currently, a visit comprises two 15-second exposures, each exposure requires one second for the shutter action, $t_{shutter}$, and  two seconds for the CCD readout, $t_{readout}$. The second readout is assumed to occur while moving to the next field, so the length of each visit for the WFD observing mode, $T_{visit}$, is 34 seconds where the total integration time on the sky, $T_{obs}$, is 30 seconds.  For other combinations of number of exposures, $N_{exp}$, and length of exposure, $t_{exp}$, the total visit time is given by ");
	write("\\begin{equation}");
	write("T_{visit} = N_{exp} ( t_{exp} + t_{shutter}) + t_{readout} (N_{exp}-1)");
	write("\\label{eq:ExpTime}");
	write("\\end{equation}");
	write("\\clearpage");

	write("\\subsection{Describing Visits per Field}");
	write("\\vskip 0.3truecm");
	sprintf(s, "\\input{../output/%s_%d_VisitsTable.tex}", hostname, sessionID);
	write(s);
	write("\\clearpage");

	write("\\subsection{Visits Acquired in the WFD Observing Mode}");
	// We need a figure here for number of visits - Number 10 of the SRD
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_SixVisits-Num.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_SixVisits-Num.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_SixVisits-Num.png)} The number of visits acquired for each field is plotted in Aitoff projection for each filter. Only visits acquired by observing modes designed to meet the WFD number of visits are included.}", hostname, sessionID);
	write(s);
	write("\\label{fig:SixVisits}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_SixVisits.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_SixVisits.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_SixVisits.png)} The ratio of the number of visits acquired for each field to the scaled WFD spec value for that filter (see Table \\ref{tab:SRDNumberTable}) is plotted as a percentage in Aitoff projection for each filter. Only visits acquired by observing modes designed to meet the WFD number of visits are included.}", hostname, sessionID);
	write(s);
	write("\\label{fig:SixVisits}");
	write("\\end{figure}");
	write("\\clearpage");

	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_visits_allfilters.png}{\\includegraphics[width=0.95\\textwidth]{../output/%s_%d_visits_allfilters.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_visits\\_allfilters.png)} The distribution of the number of fields having a given number of visits for each filter. Only visits acquired by modes designed to meet the WFD number of visits are included. The inset box contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles for each curve.}", hostname, sessionID);
	write(s);
	write("\\label{fig:visit1}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_visits_allfilters_all.png}{\\includegraphics[width=0.95\\textwidth]{../output/%s_%d_visits_allfilters_all.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_visits\\_allfilters\\_all.png)} The distribution of the number of fields having a given number of visits irrespective of filter. Only visits acquired by modes designed to meet the WFD number of visits are included. The inset box contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles.}", hostname, sessionID);
	write(s);
	write("\\label{fig:visit2}");
	write("\\end{figure}");
	write("\\clearpage");

	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_cvisits_allfilters.png}{\\includegraphics[width=.95\\textwidth]{../output/%s_%d_cvisits_allfilters.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_cvisits\\_allfilters.png)} The cumulative distribution of Figure \\ref{fig:visit1} showing the number of fields having visits $\\ge x$ in each filter. Only visits acquired by modes designed to meet the WFD number of visits are included. The inset box contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles for each curve.}", hostname, sessionID);
	write(s);
	write("\\label{fig:cvisit1}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_cvisits_allfilters_all.png}{\\includegraphics[width=.95\\textwidth]{../output/%s_%d_cvisits_allfilters_all.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_cvisits\\_allfilters\\_all.png)} The cumulative distribution of Figure \\ref{fig:visit2} showing the number of fields having visits $\\ge x$. Only visits acquired by modes designed to meet the WFD number of visits are included. The inset box contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles for each curve.}", hostname, sessionID);
	write(s);
	write("\\label{fig:cvisit2}");
	write("\\end{figure}");
	write("\\clearpage");
	sprintf(s, "\\input{../output/%s_%d_VisitsHistogram.tex}", hostname, sessionID);
	write(s);

	write("\\subsection{Visits Acquired for All Observing Modes}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_SixVisitsAll-Num.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_SixVisitsAll-Num.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_SixVisitsAll-Num.png)} The number of visits acquired for each field is plotted in Aitoff projection for each filter. All visits acquired by all observing modes are included in this plot and are not limited only to observing modes that were designed to meet the WFD number of visits.}", hostname, sessionID);
	write(s);
	write("\\label{fig:SixVisits}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_SixVisits-All.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_SixVisits-All.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_SixVisits-All.png)} The ratio of the number of visits acquired for each field to the scaled WFD spec value for that filter is plotted as a percentage in Aitoff projection for each filter. All visits acquired by all observing modes are included in this plot and are not limited only to modes that were designed to meet the WFD number of visits (see Table \\ref{tab:SRDNumberTable}).}", hostname, sessionID);
	write(s);
	write("\\label{fig:SixVisits}");
	write("\\end{figure}");
	sprintf(s, "\\input{../output/%s_%d_VisitsHistogramAll.tex}", hostname, sessionID);
	write(s);
	write("\\clearpage");
}

void write4thSection() {
	write("\\section{Survey Depth}");
/*	write("\\subsection{Methods}"); 
	write("\\subsubsection{Calculating Sky Brightness}"); */
	write("\\subsection{Calculating Sky Brightness, Single Visit Depth and Coadded Depth}");
	write("The Operations Simulator uses two methods of calculating the sky brightness at the time of a visit: OpSimSky and ETCSky.\n");	
	write("Before each visit, the sky brightness in the V filter, VskyBright, is evaluated using the  Johnson V band calculated from the Krisciunas and Schaeffer model, with a few modifications. This model uses the Moon phase, angular distance between the field and the Moon and the field's airmass to calculate added brightness to the zero-Moon, zenith sky brightness (e.g. Krisciunas 1997, PASP, 209, 1181; Krisciunas and Schaefer 1991, PASP, 103, 1033; Benn and Ellison 1998, La Palma Technical Note 115).\n");
	write("From VskyBright there are two different methods to evaluate the sky  brightness in a particular band. One method is to take measurements of the color of the sky as a function of lunar phase, and use these to correct VskyBright to a particular filter. This is the approach used for the OpSim sky brightness, OpSimSky.\n");
	write("An alternate method, ETCSky, is to use sky brightness measurements taken at various phases of the moon in many filters and calculate empirical fits to the sky brightness in each band. This method is what has been used to create the LSST Exposure Time Calculator (ETC) and has the advantage of accounting for the fact that the night sky does not behave similarly in all bands by including the angular dependence as a function of filter bandpass.\n");
    write("Single Visit Depth is calculated using formulas from University of Washington Survey Science Group website (http://ssg.astro.washington.edu/elsst/magsfilters.shtml).\n");
    write("The Coadded Depth calculation can be found in Ivezic et al, arXiv:0805.2366[astro-ph].");
	write("The plots and tables in this document report the sky brightness from the ETCSky method. Further calculations of Single Visit Depth use the sky brightness from the ETCSky method.");
	write("\\clearpage");

	write("\\subsection{Single Visit Depth}");
	// We need median and coadded m5 values (2 graphs)
	write("\\begin{figure}[H]");
	write("\\vskip-0.4truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_median5sigma.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_median5sigma.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	write("\\vskip-0.1truecm");
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_median5sigma.png)} The median of the single visit depth ($5\\sigma$ limiting magnitude) for all visits to a given field is computed, from it the WFD spec value for the single visit depth (see Table \\ref{tab:SRDNumberTable}) is subtracted and the difference is plotted in Aitoff projection for each filter. Fields with a positive value have a median single visit depth deeper than the expected zenith value. The $5\\sigma$ limiting magnitude for each visit is computed using the sky brightness determined by the ETC algorithm. Visits acquired by all observing modes are included in this plot and are not limited to only observing modes that were designed to meet the WFD number of visits.}", hostname, sessionID);
	write(s);
	write("\\label{fig:Median5sigma}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	write("\\vskip-0.4truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_m5_allfilters.png}{\\includegraphics[width=.95\\textwidth]{../output/%s_%d_m5_allfilters.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	write("\\vskip-0.1truecm");
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_m5\\_allfilters.png)} The distribution of visits with single visit depth for each filter. Only visits acquired by observing modes designed to meet the WFD number of visits are included. The inset box contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles for each curve.}", hostname, sessionID);
	write(s);
	write("\\label{fig:hist5sigma}");
	write("\\end{figure}");
	makeTable("Limiting Magnitude");
	write("\\clearpage");

	write("\\subsection{Coadded Depth}");
	// We need median and coadded m5 values (2 graphs)
	write("\\begin{figure}[H]");
	write("\\vskip -0.1truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_coadded5sigma.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_coadded5sigma.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_coadded5sigma.png)} The difference between the coadded depth and the WFD spec coadded depth (see Table \\ref{tab:SRDNumberTable}) for each field is plotted in Aitoff projection for each filter. Fields with positive values have a coadded depth deeper than the WFD zenith value. Visits acquired by all observing modes are included in this plot and are not limited only to observing modes that were designed to meet the WFD number of visits.}", hostname, sessionID);
	write(s);
	write("\\label{fig:Coadded5sigma}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	write("\\vskip -0.1truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_coadded5sigmaWFD.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_coadded5sigmaWFD.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_coadded5sigmaWFD.png)} The difference between the coadded depth and the WFD spec coadded depth (see Table \\ref{tab:SRDNumberTable}) for each field is plotted in Aitoff projection for each filter. Fields with positive values have a coadded depth deeper than the WFD zenith value. Only visits acquired by observing modes designed to meet the WFD number of visits are included in this plot.}", hostname, sessionID);
	write(s);
	write("\\label{fig:Coadded5sigmaWFD}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	write("\\vskip-0.1truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_coadded_allfilters.png}{\\includegraphics[width=.95\\textwidth]{../output/%s_%d_coadded_allfilters.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_coadded\\_allfilters.png)} The distribution of fields with coadded depth in each filter. Visits acquired by all observing modes are included in this plot and are not limited only to observing modes that were designed to meet the WFD number of visits. The inset box contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles for each curve.}", hostname, sessionID);
	write(s);
	write("\\label{fig:coaddedallfilters}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	write("\\vskip-0.1truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_coadded_allfilters_wfd.png}{\\includegraphics[width=.95\\textwidth]{../output/%s_%d_coadded_allfilters_wfd.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_coadded\\_allfilters\\_wfd.png)} The distribution of fields with coadded depth in each filter. Only visits acquired by observing modes designed to meet the WFD number of visits are included in this plot. The inset box contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles for each curve.}", hostname, sessionID);
	write(s);
	write("\\label{fig:coaddedallfilterswfd}");
	write("\\end{figure}");
	sprintf(s, "\\input{../output/%s_%d_CoaddedTable.tex}", hostname, sessionID);
	write(s);
	write("\\clearpage");
}

void write5thSection() {
	write("\\section{Observing Conditions}");
	write("\\subsection{Filter Map}");
	// First year only and all the years, This might not look that great for a run is less than a year
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_oneyearhourglass.png}{\\includegraphics[width=\\textwidth]{../output/%s_%d_oneyearhourglass.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	write("\\vskip 0.7truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_hourglass.png}{\\includegraphics[width=\\textwidth]{../output/%s_%d_hourglass.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{A map of the time spent in each filter in hours from local midnight versus the time of observation in days. The first year of the survey is mapped in the top panel {\\it (%s\\_%d\\_oneyearhourglass.png)} and the entire survey is mapped in the bottom panel {\\it (%s\\_%d\\_hourglass.png)}. The color of the filled area indicates the filter used. The enclosing curves indicate the time of civil, nautical, and astronomical twilight. The phase of the moon is indicated by the white curve along the bottom edge of the plot (arbitrarily scaled).  }", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\label{fig:%s.%d.hourglass}", hostname, sessionID);
	write(s);
	write("\\end{figure}");
	write("\\clearpage");

	write("\\subsection{Sky Brightness}");
	write("\\begin{figure}[H]");
	write("\\vskip -0.1truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_medianskyb.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_medianskyb.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_medianskyb.png)}The difference between the median of the sky brightness for all visits to a given field and the expected median no-moon zenith sky brightness at Cerro Pachon for each field is plotted in Aitoff projection for each filter (see Table \\ref{tab:SRDNumberTable}). All visits acquired by all observing modes are included in this plot and are not limited to only observing that were designed to meet the WFD number of visits.}", hostname, sessionID);
	write(s);
	write("\\label{fig:MedianSkyb}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	write("\\vskip-0.1truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_skyb_allfilters.png}{\\includegraphics[width=.95\\textwidth]{../output/%s_%d_skyb_allfilters.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_skyb\\_allfilters.png)} The distribution of fields with sky brightness for each filter. Only visits acquired by observing modes designed to meet the WFD number of visits are included. The inset box contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles for each curve.}", hostname, sessionID);
	write(s);
	write("\\label{fig:histSkyb}");
	write("\\end{figure}");
	makeTable("Sky Brightness");
	write("\\clearpage");

	write("\\subsection{Seeing}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_medianseeing.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_medianseeing.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_medianseeing.png)} The ratio of the median seeing for all visits to a given field to the expected median zenith seeing (see Table \\ref{tab:SRDNumberTable}, but of course many fields cannot reach zenith) is calculated and is plotted in Aitoff projection for each filter. All visits acquired by all observing modes are included in this plot and are not limited to only observing modes that were designed to meet the WFD number of visits.}", hostname, sessionID);
	write(s);
	write("\\label{fig:MedianSeeing}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	write("\\vskip-0.1truecm");
	sprintf(s, "\\IfFileExists{../output/%s_%d_seeing_allfilters.png}{\\includegraphics[width=.95\\textwidth]{../output/%s_%d_seeing_allfilters.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_seeing\\_allfilters.png)} The distribution of visits with seeing for each filter. Only visits acquired by observing modes designed to meet the WFD number of visits are included. The inset box contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles for each curve. }", hostname, sessionID);
	write(s);
	write("\\label{fig:histSeeing}");
	write("\\end{figure}");
	write("\\clearpage");
	makeTable("Seeing");
	write("\\clearpage");

	write("\\subsection{Airmass}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_medianairmass.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_medianairmass.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_medianairmass.png)} The median of the airmass for the visits to each field is plotted in Aitoff projection for each filter. All visits acquired by all observing modes are included in this plot and are not limited to only observing modes that were designed to meet the WFD number of visits.}", hostname, sessionID);
	write(s);
	write("\\label{fig:MedianAirmass}");
	write("\\end{figure}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_maxairmass.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_maxairmass.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_maxairmass.png)} The maximum of the airmass for the visits to each field is plotted in Aitoff projection for each filter. All visits acquired by all observing modes are included in this plot and are not limited to only observing modes that were designed to meet the WFD number of visits.}", hostname, sessionID);
	write(s);
	write("\\label{fig:MaximumAirmass}");
	write("\\end{figure}");
	write("\\clearpage");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_airmass_allfilters.png}{\\includegraphics[width=.95\\textwidth]{../output/%s_%d_airmass_allfilters.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_airmass\\_allfilters.png)} The distribution of fields with airmass for each filter. Only visits acquired by observing modes designed to meet the WFD number of visits are included. The legend contains the values of the 25$^{th}$, 50$^{th}$ (median), and 75$^{th}$ percentiles for each curve.}", hostname, sessionID);
	write(s);
	write("\\label{fig:histAirmass}");
	write("\\end{figure}");
	write("\\clearpage");
	makeTable("Airmass");
	write("\\clearpage");
}

void write6thSection() {
	write("\\section{Science Specific Figures of Merit}");
	write("\\subsection{Near-Earth Object Science}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_revisit_griz.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_revisit_griz.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_revisit\\_griz.png)} A map of pairs of visits in any combination of g, r, i, and z filters that are separated by 15 to 60 minutes per lunation averaged over the length of the survey. Three pairs per lunation is needed to determine an orbit well enough to recover the object at a later time.}", hostname, sessionID);
	write(s);
	sprintf(s, "\\label{fig:%s_%d_revisit_griz}", hostname, sessionID);
	write(s);
	write("\\end{figure}");
	write("\\clearpage");
	write("\\vskip1.0cm");
	makeRevisitTimeTable();
	write("\\vskip1.0truecm");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_revisit_all.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_revisit_all.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	sprintf(s, "\\caption{{\\it (%s\\_%d\\_revisit\\_all.png)} A map of pairs of visits in the same filter that are separated by 15 to 60 minutes per lunation averaged over the length of the survey. Three pairs per lunation is needed to determine an orbit well enough to recover the object at a later time.}", hostname, sessionID);
	write(s);
	sprintf(s, "\\label{fig:%s_%d_revisit_all}", hostname, sessionID);
	write(s);
	write("\\end{figure}");
	write("\\clearpage");
}

void write7thSection() {
	write("\\section{Slew Statistics}");
	write("\\subsection{Slew Activity}");
	//write("\\vskip 0.3truecm");
    //write("{\\footnotesize")
    write("{\\tiny");
    write("\\begin{lstlisting}");
    addSummaryReport();
    write("\\end{lstlisting}");
    write("}");
    
	write("\\subsection{Inter-Visit Time}");
	write("\\begin{figure}[H]");
	sprintf(s, "\\IfFileExists{../output/%s_%d_slews.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_slews.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, hostname, sessionID);
	write(s);
	write("\\caption{The logarithmic distribution of slew time and slew distance, where ``slew'' means the time between completing an integration at one field and beginning an integration at the next field.}");
	sprintf(s, "\\label{fig:%s_%d_slews}", hostname, sessionID);
	write(s);
	write("\\end{figure}");

	write("\\clearpage");
}

void writeAppendixA() {
	write("\\appendix");

	int i;

	write("\\section{Visits Requested by Observing Mode}");
	for(i=0; i < proposal_list_length; i++) {
		sprintf(s, "\\subsection{%s}", proposal_list[i].propConf);
		write(s);
		write("\\begin{figure}[H]");
		sprintf(s, "\\IfFileExists{../output/%s_%d_SixVisits-Num-%d.png}{\\includegraphics[width=1.00\\textwidth]{../output/%s_%d_SixVisits-Num-%d.png}}{\\includegraphics[width=1.00\\textwidth]{../images/nodata.png}}", hostname, sessionID, proposal_list[i].propID, hostname, sessionID, proposal_list[i].propID);
		write(s);
		sprintf(s, "\\caption{{\\it (%s\\_%d\\_SixVisits-Num-%d.png)} The total number of visits acquired for each field requested by observing mode %s is plotted in Aitoff projection for each filter. }", hostname, sessionID, proposal_list[i].propID, proposal_list[i].propConf);
		write(s);
		write("\\label{fig:SixVisits}");
		write("\\end{figure}");
		
	}
	write("\\clearpage");
}

void writeAppendixB() {

	int i;


	write("\\section{Configuration File Specifications}");
	write("\\label{sec:PropSpecs}");
	write("A particular observing mode may be implemented by one or more configuration files.  In this section a  selected group of parameters from each configuration file are displayed.  While not scientifically interesting, this illustrates how the observing cadence may be directed.");

	for(i=0; i < proposal_list_length; i++) {
		int propID = proposal_list[i].propID;
		sprintf(s, "\\subsection{%s}", proposal_list[i].propConf);
		write(s);
		write("\\begin{table}[H]{\\textbf{Details}} \\\\ [1.0ex]");
		write("\\begin{tabular*}{\\textwidth}{\\tblspace lllllll}");
		write("\\hline");		
		write("\\multicolumn{1}{l}{Parameter} & \\multicolumn{6}{l}{Value} \\\\");
		write("\\hline \\hline");
		write("\\multicolumn{7}{l}{\\emph{Observing Time Details}} \\\\");
		write("\\hline");
		sprintf(s, "Visit Time	& %s & & & & & \\\\", getProposalValue("ExposureTime", propID));
		write(s);
		sprintf(s, "NVisits	 & %s & & & & & \\\\", getProposalValue("NVisits", propID));
		write(s);
		sprintf(s, "MaxNeedAfterOverflow	& %s & & & & & \\\\", getProposalValue("MaxNeedAfterOverflow", propID));
		write(s);
		write("\\hline");
		write("\\multicolumn{7}{l}{\\emph{Observing Condition Restrictions}} \\\\");
		write("\\hline");	
		sprintf(s, "MaxAirmass & %s & & & & & \\\\", getProposalValue("MaxAirmass", propID));
		write(s);
		sprintf(s, "MaxSeeing	& %s & & & & & \\\\", getProposalValue("MaxSeeing", propID));
		write(s);
		sprintf(s, "minTransparency	& %s & & & & & \\\\", getProposalValue("minTransparency", propID));
		write(s);
		sprintf(s, "TwilightBoundary	& %s & & & & & \\\\", getProposalValue("TwilightBoundary", propID));
		write(s);
		if ( proposal_list[i].nUserRegions == 0 ) {
			write("\\hline");
			write("\\multicolumn{7}{l}{\\emph{Observing Area Definitions}} \\\\");
			write("\\hline");
			sprintf(s, "taperL	& %s & & & & & \\\\", getProposalValue("taperL", propID));
			write(s);
			sprintf(s, "taperB	& %s & & & & & \\\\", getProposalValue("taperB", propID));
			write(s);
			sprintf(s, "peakL	& %s & & & & & \\\\", getProposalValue("peakL", propID));
			write(s);
			sprintf(s, "deltaLST & %s & & & & & \\\\", getProposalValue("deltaLST", propID));
			write(s);
			sprintf(s, "maxReach & %s & & & & & \\\\", getProposalValue("maxReach", propID));
			write(s);
		} 
		write("\\hline");
		write("\\multicolumn{7}{l}{\\emph{Target Ranking Parameters}} \\\\");
		write("\\hline");
		sprintf(s, "ProgressToStartBoost	& %s & & & & & \\\\", getProposalValue("ProgressToStartBoost", propID));
		write(s);
		sprintf(s, "MaxBoostToComplete	& %s & & & & & \\\\", getProposalValue("MaxBoostToComplete", propID));
		write(s);
		sprintf(s, "RelativeProposalPriority	& %s & & & & & \\\\", getProposalValue("RelativeProposalPriority", propID));
		write(s);
		sprintf(s, "MaxProximityBonus	& %s & & & & & \\\\", getProposalValue("MaxProximityBonus", propID));
		write(s);
		sprintf(s, "RankScale	& %s & & & & & \\\\", getProposalValue("RankScale", propID));
		write(s);
		sprintf(s, "AcceptSerendipity	& %s & & & & & \\\\", getProposalValue("AcceptSerendipity", propID));
		write(s);
		sprintf(s, "AcceptConsecutiveObs	& %s & & & & & \\\\", getProposalValue("AcceptConsecutiveObs", propID));
		write(s);
		write("\\hline");
		write("\\multicolumn{7}{l}{\\emph{Observing Filter Details}} \\\\");
		write("\\hline");
		// THESE VALUES MIGHT NOT BE APPLICABLE TO ALL PROPOSALS THEREFORE 
		//   WE NEED TO COME UP WITH A LOGICAL MODEL THAT HELPS US DISTINGUISH
		//   BETWEEN ALL THE PROPOSALS THAT WE HAVE.
		struct filtervalue* f = getFilterValues("Filter", propID);
		struct filtervalue* fv = getFilterValues("Filter_Visits", propID);
		struct filtervalue* fms = getFilterValues("Filter_MaxSeeing", propID);
		struct filtervalue* fmib = getFilterValues("Filter_MinBrig", propID);
		struct filtervalue* fmab = getFilterValues("Filter_MaxBrig", propID);

		int j=0;
		char s1[256];	
		
		if ( f[0].size > 0 ) {
			bzero(s, 256);
			sprintf(s, "Filter          ");
			for(j=0; j < f[0].size; j++) {
				
				sprintf(s1, "& %s ", f[j].value);
				strcat(s, s1);
			}
			strcat(s, "\\\\");
			write(s);
		}

		if ( fv[0].size > 0 ) {
			bzero(s, 256);
			sprintf(s, "Filter\\_Visits  ");
			for(j=0; j < fv[0].size; j++) {
				sprintf(s1, "& %s ", fv[j].value);
				strcat(s, s1);
			}
			strcat(s, "\\\\");
			write(s);
		}

		if ( fms[0].size > 0 ) {
			bzero(s, 256);
			sprintf(s, "Filter\\_MaxSeeing");
			for(j=0; j < fms[0].size; j++) {
				sprintf(s1, "& %s ", fms[j].value);
				strcat(s, s1);
			}
			strcat(s, "\\\\");
			write(s);
		}

		if ( fmib[0].size > 0 ) {
			bzero(s, 256);
			sprintf(s, "Filter\\_MinBrig ");
			for(j=0; j < fmib[0].size; j++) {
				sprintf(s1, "& %s ", fmib[j].value);
				strcat(s, s1);
			}
			strcat(s, "\\\\");
			write(s);
		}

		if ( fmab[0].size > 0 ) {
			bzero(s, 256);
			sprintf(s, "Filter\\_MaxBrig ");
			for(j=0; j < fmab[0].size; j++) {
				sprintf(s1, "& %s ", fmab[j].value);
				strcat(s, s1);
			}
			strcat(s, "\\\\");
			write(s);
		}
		/*
			END OF THIS
		*/
		if ( strstr(proposal_list[i].propName, "SS") != NULL ) {
			// SubSequence Proposal
			write("\\hline");
			write("\\multicolumn{7}{l}{\\emph{Sequence Specifications}}\\\\");
			write("\\hline");
			sprintf(s, "MaxNumberActiveSequences	& %s & & & & & \\\\", getProposalValue("MaxNumberActiveSequences", propID));
			write(s);
			sprintf(s, "RestartLostSequences	& %s & & & & & \\\\", getProposalValue("RestartLostSequences", propID));
			write(s);
			sprintf(s, "RestartCompleteSequences	& %s & & & & & \\\\", getProposalValue("RestartCompleteSequences", propID));
			write(s);
			sprintf(s, "MasterSubSequence	& %s & & & & & \\\\", getProposalValue("MasterSubSequence", propID));
			write(s);
			
			struct filtervalue* ssname = getFilterValues("SubSeqName", propID);
			struct filtervalue* ssfilters = getFilterValues("SubSeqFilters", propID);
			struct filtervalue* ssexposures = getFilterValues("SubSeqExposures", propID);
			struct filtervalue* ssevents = getFilterValues("SubSeqEvents", propID);
			struct filtervalue* ssmaxmissed = getFilterValues("SubSeqMaxMissed", propID);
			struct filtervalue* ssinterval = getFilterValues("SubSeqInterval", propID);
			struct filtervalue* sswstart = getFilterValues("SubSeqWindowStart", propID);
			struct filtervalue* sswmax = getFilterValues("SubSeqWindowMax", propID);
			struct filtervalue* sswend = getFilterValues("SubSeqWindowEnd", propID);

			if ( ssname[0].size > 0 ) {
				bzero(s, 256);
				sprintf(s, "SubSeqName ");
				for(j=0; j < ssname[0].size; j++) {
					sprintf(s1, "& %s ", ssname[j].value);
					strcat(s, s1);
				}
				strcat(s, "\\\\");
				write(s);
			}
			if ( ssfilters[0].size > 0 ) {
				bzero(s, 256);
				sprintf(s, "SubSeqFilters ");
				for(j=0; j < ssfilters[0].size; j++) {
					sprintf(s1, "& %s ", ssfilters[j].value);
					strcat(s, s1);
				}
				strcat(s, "\\\\");
				write(s);
			}
			if ( ssexposures[0].size > 0 ) {
				bzero(s, 256);
				sprintf(s, "SubSeqExposures ");
				for(j=0; j < ssexposures[0].size; j++) {
					sprintf(s1, "& %s ", ssexposures[j].value);
					strcat(s, s1);
				}
				strcat(s, "\\\\");
				write(s);
			}
			if ( ssevents[0].size > 0 ) {
				bzero(s, 256);
				sprintf(s, "SubSeqEvents ");
				for(j=0; j < ssevents[0].size; j++) {
					sprintf(s1, "& %s ", ssevents[j].value);
					strcat(s, s1);
				}
				strcat(s, "\\\\");
				write(s);
			}
			if ( ssmaxmissed[0].size > 0 ) {
				bzero(s, 256);
				sprintf(s, "SubSeqMaxMissed ");
				for (j=0; j < ssmaxmissed[0].size; j++) {
					sprintf(s1, "& %s ", ssmaxmissed[j].value);
					strcat(s, s1);
				}
				strcat(s, "\\\\");
				write(s);
			}
			if ( ssinterval[0].size > 0 ) {
				bzero(s, 256);
				sprintf(s, "SubSeqInterval ");
				for (j=0; j < ssinterval[0].size; j++) {
					sprintf(s1, "& %s ", ssinterval[j].value);
					strcat(s, s1);
				}
				strcat(s, "\\\\");
				write(s);
			}
			if ( sswstart[0].size > 0 ) {
				bzero(s, 256);
				sprintf(s, "SubSeqWindowStart ");
				for (j=0; j < sswstart[0].size; j++) {
					sprintf(s1, "& %s ", sswstart[j].value);
					strcat(s, s1);
				}
				strcat(s, "\\\\");
				write(s);
			}
			if ( sswmax[0].size > 0 ) {
				bzero(s, 256);
				sprintf(s, "SubSeqWindowMax ");
				for(j=0; j < sswmax[0].size; j++) {
					sprintf(s1, "& %s ", sswmax[j].value);
					strcat(s, s1);
				}
				strcat(s, "\\\\");
				write(s);
			}
			if ( sswend[0].size > 0 ) {
				bzero(s, 256);
				sprintf(s, "SubSeqWindowEnd ");
				for(j=0; j < sswend[0].size; j++) {
					sprintf(s1, "& %s ", sswend[j].value);
					strcat(s, s1);
				}
				strcat(s, "\\\\");
				write(s);
			}
		}
		write("\\hline \\hline");
		write("\\end{tabular*} \\\\");
		write("\\caption{A value of '?' indicates that that parameter was not defined or was not applicable for this observing mode.}");
		sprintf(s, "\\label{tab:PropID%d}", propID);
		write(s);
		write("\\end{table}");
		write("\\clearpage");
	}
}

void writeAppendixC() {
	write("\\section{Engineering Specifications }");
	write("\\label{sec:EngSpecs}");	
	
	write("\\begin{table}[H]{\\bf Site Characteristics} \\\\ [1.0ex]");
	write("{\\small");
	write("\\begin{tabular*}{\\textwidth}{\\tblspace lll}");
	write("\\hline");
	write("\\colhead{Characteristic} &");
	write("\\colhead{Parameter} &");
	write("\\colhead{Value} \\\\");
	write("\\hline \\hline");
	sprintf(s, "Site Information & siteConf	& %s \\\\", getConfigValue("siteConf"));
	write(s);
	sprintf(s, "Site Latitude  & latitude & %s deg \\\\", getConfigValue("latitude"));
	write(s);	
	sprintf(s, "Site Longitude  & longitude & %s deg \\\\", getConfigValue("longitude"));
	write(s); 
	sprintf(s, "Site Elevation  & height & %s m \\\\", getConfigValue("height"));
	write(s);
	sprintf(s, "Atmospheric Pressure & pressure & %s millibars \\\\", getConfigValue("pressure"));
	write(s);
	sprintf(s, "Ambient Temperature & temperature	& %s $^{\\circ}$C\\\\", getConfigValue("temperature"));
	write(s);
	sprintf(s, "Relative Humidity & relativeHumidity &	%s \\ \\\\", getConfigValue("relativeHumidity"));
	write(s);
	write("\\hline \\hline");
	write("\\end{tabular*}}"); 
	write("\\caption{A list of settings pertaining to the selected site (siteConf) which is Cerro Pachon.}");
	write("\\label{tab:Site}");
	write("\\end{table}");

	write("\\begin{table}[H]{\\bf Camera Characteristics} \\\\ [1.0ex]");
	write("{\\small");
	write("\\begin{tabular*}{\\textwidth}{\\tblspace lll}");
	write("\\hline");
	write("\\colhead{Characteristic} &");
	write("\\colhead{Parameter} &");
	write("\\colhead{Value} \\\\");
	write("\\hline \\hline");
	sprintf(s, "Field of View & fov	& %s degrees \\\\", getConfigValue("fov"));
	write(s);
	sprintf(s, "Total Readout Time (sec) & Readout\\_Time	& %s sec \\\\", getConfigValue("Readout_Time"));
	write(s);
	sprintf(s, "Telescope Seeing & telSeeing & %s arcsec \\\\", getConfigValue("telSeeing"));
	write(s);
	sprintf(s, "Optical Seeing & opticalDesSeeing & %s arcsec \\\\", getConfigValue("opticalDesSeeing"));
	write(s);
	sprintf(s, "Camera Seeing & cameraSeeing & %s arcsec \\\\", getConfigValue("cameraSeeing"));
	write(s);
	sprintf(s, "Seeing Epoch & seeingEpoch &	%s \\\\", getConfigValue("seeingEpoch"));
	write(s);
	sprintf(s, "Filter Information & Filter\\_MountTime	& %s sec \\\\", getConfigValue("Filter_MountTime"));
	write(s);
	sprintf(s, "& Filter\\_MoveTime	& %s sec \\\\", getConfigValue("Filter_MoveTime"));
	write(s);
	struct filtervalue* f = getFilterMountedValues("Filter_Mounted");
	int i;
	for(i =0; i < f[0].size; i++) {
		sprintf(s, "& Filter\\_Mounted	& %s \\\\", f[i].value);
		write(s);
	}
	sprintf(s, "& Filter\\_Pos	& %s \\\\", getConfigValue("Filter_Pos"));
	write(s);
	f = getFilterMountedValues("Filter_Removable");
	for(i =0; i < f[0].size; i++) {
		sprintf(s, "& Filter\\_Removable	& %s \\\\", f[i].value);
		write(s);
	}
	sprintf(s, "& Filter\\_Unmounted	& %s \\\\", getConfigValue("Filter_Unmounted"));
	write(s);  
	write("\\hline \\hline");
	write("\\end{tabular*}}");
	write("\\caption{A list of settings pertaining to the camera. Only 5 filters may be mounted per night as 8 hours are required to swap out the sixth.}");
	write("\\label{tab:Camera}");
	write("\\end{table}");
}

void writeEndDocument() {
	write("\\end{document}");
}

int main(int argc, char **argv) {
	if ( argc == 4 || argc == 5) {
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
		// Open tex file
		openTex();
		// Open Database Connection
		openDB(argv[2]);
		// Read Config Data
		readConfigData();
		// Read Session Data
		readSessionData();
		// Read Proposal Data
		readPropData();

		/* Write Pages */
		writeTitlePage();
		write1stSection();
		write2ndSection();
		write3rdSection();
		write4thSection();
		write5thSection();
		// write6thSection();
		write7thSection();
		writeAppendixA();
		writeAppendixB();
		// writeAppendixC();
		writeEndDocument();
		/* End Pages */

		closeTex();
		closeDB();
	} else {
		printf("Error : Number of arguments");
		exit(1);
	}
}
