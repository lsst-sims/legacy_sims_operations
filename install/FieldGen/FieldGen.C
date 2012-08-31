#ifndef lint
static char RcsId[] = "$Id$";
#endif

// Module:	FieldGen.C
// Purpose: 	Populate sphere with LSST Fields given FOV, overlap
// Public:	
// Copyright:	2004, LSST Corp
//		This software may not be distributed to others without
//		permission of the author.
// Author:	Roberta A. Allsman, NOAO
//		robyn@noao.edu
// Modified:	$Log$
// Modified:	Revision 1.8  2005/09/16 18:31:04  robyn
// Modified:	Fix bug with extra params on output
// Modified:	
// Modified:	Revision 1.7  2005/03/09 15:25:51  robyn
// Modified:	Fix a bug where the initial field center was incorrect.
// Modified:	
// Modified:	Revision 1.6  2004/10/10 19:02:21  robyn
// Modified:	Algorithm for WL galactic bulge exclusion zone redone to more accurately
// Modified:	    shape the galactic bulge
// Modified:	Algorithm for WL moon avoidance zone converted to analytic calculation based
// Modified:	    on phase of the moon.
// Modified:	Ensured consistency of naming of filter 'Y'
// Modified:	Default log file based on session id : lsst.log<sessionid>
// Modified:	    'report' tool updated to handle default log filename.
// Modified:	All parameters fils are being loaded at the head of the log file.
// Modified:	Calculation of the FieldDB ingest files corrected.
// Modified:	
// Modified:	Revision 1.1  2004/08/10 21:29:36  robyn
// Modified:	Install Lsst Field Generation - preliminary version
// Modified:	
//
//

#include <stdlib.h>
#include <iostream.h>
#include "string.h"
#include "math.h"
#include "unistd.h"

#undef DEBUG

//========================================================================
// Support Routines 
//========================================================================
//--------------------------------------------------------------------------
//-----------------------------	print_help	----------------------------
void print_help()
{
cerr << "\n---------------------------------------------------------------\n";
cerr << "FieldGen   Create LSST Field centers given the FOV.\n";
cerr << "FieldGen  -f <fov> -o <overlap> -h \n"
     << "    -f <fov> : field of view extrapolated as side of square inscribed within a circle.\n"
     << "                Default is 3.0; units are degrees. \n"
     << "    -o <overlap> : overlap between adjacent Fields calculated as (fov - overlap/2).\n"
     << "                Default is 0 (or minimal); units are arcminutes.\n"
     << "    -h  : print this message \n"
     << " "
     << " Examples: \n"
     << "      FieldGen  -f 4. \n"
     << "      FieldGen  -f 3. -o 120.	# give same result as above. \n"
     << "      FieldGen  \n";
}

//---------------------------------------------------------------------------


//========================================================================
// Application 
//========================================================================
main(int argc, char **argv)
{

int c;
extern char *optarg;
extern int optind;
char *fov_str= (char *)0;
char *overlap_str= (char *)0;
float overlap = 0.;

static double pi2 = 2.0*M_PI;
// M_PI_2 = pi/2


while((c = getopt(argc,argv,"f:o:h")) != -1)
	switch (c){
	case 'f':
		fov_str = optarg;
		break;
	case 'o':
		overlap_str = optarg;
		overlap = atof(overlap_str);
		break;
	case 'h':
		// issue help print
		print_help();
		exit(0);
	default:
		print_help();
                exit(1);
	}


float a, delta, dalpha, alpha;
float fov, fov_rad;

if ( fov_str == (char *) 0) fov = 3.;
else fov = atof(fov_str);
#ifdef DEBUG
cout << "Fov: " << fov << "\n";
#endif

if ( overlap > 0. )  fov = fov -  (overlap / 120 );
#ifdef DEBUG
cout << "Fov - overlap: " << fov << "\n";
#endif

fov_rad = fov * M_PI / 180;
#ifdef DEBUG
cout << "Fov_rad: " << fov_rad << "\n";
#endif

int id = 1;
int even_odd = 1;
cout << 0 << " " << 90 <<  " " << id  << "\n";
id++;

float q;
q = sqrt(2)/2*fov_rad;
for ( delta = M_PI_2 - q; delta > -M_PI_2; delta -=q) {
// Spherical trig to calculate dalpha

  float s, a, b, c;
  a = b = M_PI/2 - fabs(delta);
  c = sqrt(2)/2*fov_rad;
  s = (a + b + c)/2;
  dalpha = 2 * asin(sqrt(sin(s - a)*sin(s - b)/(sin(a)*sin(b))));
  float alpha0 = (even_odd == 1 ? 0 : dalpha / 2);
  for( alpha = alpha0; alpha < pi2 + alpha0 - dalpha/2; alpha += dalpha) {
    cout << (180./M_PI) * alpha << " " << (180./M_PI) * delta << " " << id << "\n";
 		id++;
		}
  even_odd *= -1;
}
exit(0);
}
