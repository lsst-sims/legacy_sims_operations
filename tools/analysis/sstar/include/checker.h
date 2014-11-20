
// This comes from the simulation

// galactic exclusion
#define PEAKL 10.0
#define TAPERL 0.0
#define TAPERB 90.0

// observatory site
#define LON (-70.98333)
#define LAT (-30.33333)
#define ELEV (2737.0)
#define TZ (4.0)

#define SIM_EPOCH 49353
#define SIM_STARTDAY 0.0

// size of a field
#define FIELD_RADIUS (1.75/DEG_IN_RADIAN)
#define FIELDMAX 5000

// check parameters
#define LARGE_AIRMASS 1.5
#define MOON_AVOID (1.0/DEG_IN_RADIAN)

// here below are constants
#define RRR 6378.388
#define NMAX 3000000

#define MAXPROP 50
#define MAXFILTERS 6

// grace period for times: five minutes
#define GRACE 5.0*(60.0/86400.0)

#define write_airmass(arg) fprintf(ftableairmass, "%s\n", arg);
#define write_seeing(arg) fprintf(ftableseeing, "%s\n", arg);
#define write_skyb(arg) fprintf(ftableskyb, "%s\n", arg);
#define write_5sigma(arg) fprintf(ftable5sigma, "%s\n", arg);
#define write_5sigmacoadd(arg) fprintf(ftable5sigmacoadd, "%s\n", arg);

int debug=0;
int doTimeSummary=0, doCheck=0, doPeriodSearch=0, doHourglass=0, doOpposition=0, doAirmass=0;
int doSixVisits=0, doVisits=0, doNEOrevisits=0, doSNtiming=0, doSlew=0;
int do5sigma=0, doskyb=0, doSeeing=0;
char tableName[1024];
int useMaxAirmass;
int useDesignStretch;
int sessionID;
int nIDs=0, propIDs[MAXPROP];
int numAllIDs, allPropIDs[MAXPROP];
int skipDays=0, lengthDays=0;
int ndesiredFilters;
char desiredFilters[MAXFILTERS][5];
int doHardcopy=0;
char plotfileRoot[1024], plotTitle[1024];
char hostname[80];
char identifier[80];
int identifier_length = 80;
double median_data[5000000];
int median_data_length;
char database[1024];

typedef struct {
  int obsHistID;
  double ra;
  double dec;
  double slewtime;
  double slewdist;
  double date;
  long expdate;
  double seeing;
  double vskybright;
  double filtsky;
  double m5;
  double etc_skyb;
  double etc_m5;
  int field;
  char filtername[10];
  int filter;
  int propid;
  int twilight;
} observation;

int numobs, numFields;
observation *obs;

double startMJD, endMJD;
double lat, lon, sim_epoch, sim_startday, peakL, taperL, taperB;

#define UCOLOR 13
#define GCOLOR 8
#define RCOLOR 9
#define ICOLOR 10
#define ZCOLOR 11
#define YCOLOR 12
#define DARKGRAY 14
#define LIGHTGRAY 15

#define NFILTERS 6
#define FILTLEN 5
char filtername[NFILTERS][FILTLEN] = {"u","g","r","i","z","y"};
int filtercolor[NFILTERS] = {UCOLOR, GCOLOR, RCOLOR, ICOLOR, ZCOLOR, YCOLOR};
int twilightFilters[NFILTERS], ntwilightFilters;
int pairsFilters[NFILTERS], npairsFilters; 

// first makes a two rows, three columns plot good for powerpoint
/*int hpanely[NFILTERS] = {1, 2, 1, 2, 1, 2};
int hpanelx[NFILTERS] = {1, 1, 2, 2, 3, 3};*/

int hpanelx[NFILTERS] = {1, 2, 3, 1, 2, 3};
int hpanely[NFILTERS] = {1, 1, 1, 2, 2, 2};

// second makes a three rows, two columns plot good for print
int vpanelx[NFILTERS] = {1, 2, 1, 2, 1, 2};
int vpanely[NFILTERS] = {1, 1, 2, 2, 3, 3};

#define PLOTSIZE 8.0

/*
  High Level Statistics file
*/
FILE* quickfp;

/*
  Revisit time file
*/
FILE* revisitfp;

