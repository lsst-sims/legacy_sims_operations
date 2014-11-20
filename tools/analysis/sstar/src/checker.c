/*
  checker code

  Philip Pinto

*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <math.h>
#include <string.h>
#include <strings.h>
#include <mysql.h>
#include <argtable2.h>
#include <assert.h>
#include <cpgplot.h>
#include <slalib.h>
#include "checker.h"
#include "astron.h"
#include "aitoff.h"

#include "hunt.c"
#include "astron.c"
#include "util.c"
#include "plotutil.c"
#include "aitoff.c"
#include "processargs.c"
#include "mysql.c"
#include "checkobservations.c"
#include "hourglass.c"
#include "fieldsutil.c"
#include "visits.c"
#include "slewstuff.c"
#include "revisits.c"
#include "opposition.c"
#include "airmassplot.c"
#include "medianplot.c"

// set the basic parameters defined above
void setUp(void) {
  int i;

  // site
  lat = LAT / DEG_IN_RADIAN;
  lon = LON / DEG_IN_RADIAN;
  sim_epoch = SIM_EPOCH;
  sim_startday = SIM_STARTDAY;

  // exclusion zone
  peakL = PEAKL / DEG_IN_RADIAN;
  taperL = TAPERL  / DEG_IN_RADIAN;
  taperB = TAPERB  / DEG_IN_RADIAN;

  // for astron.c
  setUpSiteData(LAT,LON,ELEV,TZ);

  ntwilightFilters=2;
  twilightFilters[0] = filterToNumber("z");
  twilightFilters[1] = filterToNumber("y");
}

void setupQuickFire() {
	char fName[80];
	sprintf(fName, "../output/%s_%d_quickstats.tex", hostname, sessionID);
	quickfp = fopen(fName, "a");
}

void closeQuickFire() {
	fflush(quickfp);
	fclose(quickfp);
}

// read the database
void getData(char *host, char *user, char *passwd, char *table, char *db) {
  int i;

  // connect to db
  openLSSTdb(host, user, passwd, db);

  // print which proposals are present
  get_propIDs(allPropIDs, &numAllIDs, sessionID, table);  
  printf("table \"%s\" in db \"%s\" has proposal IDs: ",table,db);
  for(i=0; i<numAllIDs; i++) printf("%d ",allPropIDs[i]);
  printf("\n");

  // if no proposals were requested, use them all
  if(nIDs==0) {
    nIDs = numAllIDs;
    for(i=0; i<nIDs; i++) propIDs[i] = allPropIDs[i];
  }

  // get the first and last observation MJD
  get_startendMJD(&startMJD, &endMJD, sessionID, table);
  // convert to MJD's of previous local noon and following local noon
  //  for inclusiveness (inclusivity? inclusivitude?)
  startMJD = mjdPrevNoon(startMJD);
  endMJD = mjdPrevNoon(endMJD) + 1.0;
  startMJD += skipDays;
  if(lengthDays>0) 
    endMJD = startMJD + lengthDays;
  else
    lengthDays = endMJD - startMJD + 1;

  printf("using data from days %d to %d   ", skipDays, skipDays + lengthDays);
  printf("( MJD %f to %f )\n", startMJD, endMJD);

  // get the number of fields
  get_numFields(&numFields, sessionID, table);

  // read the database
  read_obsHistory(propIDs, nIDs, startMJD, endMJD, "expMJD", sessionID, table, &obs, &numobs);
  // translate filter information
  for(i=0; i<numobs; i++) obs[i].filter = filterToNumber(obs[i].filtername);
}

//  Get a unique set of observations (obs are entered once for each proposal they satisfy)
//  SELECT DISTINCT takes VERY long on mysql...
void uniqueObservations(void) {
  int i;
    int count_duplicates = 0;
  // sort observations by MJD
  qsort(obs, numobs, sizeof(observation), compareDate);

  // keep a unique set (i.e. exclude all but one visit at the same MJD)
  //    find duplicates & set first of each to a date very far
  //    in the future
  for(i=0; i<numobs-1; i++) {
    if(obs[i].expdate == obs[i+1].expdate) {
      obs[i].expdate = 1000000000.0;
        count_duplicates++;
    }      
  }

  // sort observations by MJD again to put these all at end
  qsort(obs, numobs, sizeof(observation), compareDate);

  // find where to stop
  for(i=0; i<numobs; i++) {
    if(obs[i].expdate == 1000000000.0) break;
  }
  numobs = i-1;
    
    printf("[Duplicates found] %d\n", count_duplicates);
}

int main(int argc, char **argv) {
  int i;

  // parse command line
  processArgs(argc, argv);

  // load site & survey data
  setUp();

  getData("localhost", "www", "zxcvbnm", tableName, database);
  readConfigData();
  readProposalData();

  setupQuickFire();

  printf("\nUsing proposals:"); for(i=0; i<nIDs; i++) printf(" %d", propIDs[i]); printf("\n");

  // Six Visit plot by proposal. At this point we have all proposals in 
  // one six plot thingy. Total plots n where n is no. of proposals
  if(doSixVisits) {
	// SRD only with respect to Universal
	visNumSix();
	// Against the number of requested visits per proposal per filter
	doVisNumSixByProposal();
  }

  if(doAirmass) doAirmassPlotbyProposal();

  if(doSeeing) doSeeingPlotbyProposal();

  if(doskyb) doSkybPlotbyProposal();

  if(do5sigma) dom5PlotbyProposal();

  // This unique thing should be done afterwards so that we can divide visits by proposal  
  uniqueObservations();

  if(doNEOrevisits) revisitsNEO();

  if(doSixVisits) {
	// SRD only with respect to Universal
	visNumSixAll();
  }

  if(doTimeSummary) timeSummary();

  if(doCheck) checkObservations();

  if(doOpposition) oppositionPlot();

  // At this point we have all proposals in 
  // one six plot thingy. So both average and maximum airmass for each proposal
  if(doAirmass) airmassPlot();

  if(doSeeing) seeingPlot();

  if(doskyb) skybPlot();

  if(do5sigma) m5Plot();

  if(doHourglass) {
	hourglassPlot();
	oneYearhourglassPlot();
  }

  if(doSlew) slewPlot();

  closeQuickFire();
  closeLSSTdb();
}
