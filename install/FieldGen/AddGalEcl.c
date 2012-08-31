#include "slalib.h"
#include <stdio.h>

int main(int argc, char **argv)
{
  double ra, dec, l, b, mjd, el, eb; 
  double deg_to_rad = M_PI/180.0;
  int ok;

  int iy = 04;
  int im = 12;
  int id = 1;
  slaCaldj (iy, im, id, &mjd, &ok);
  fprintf(stderr,"mjd = %lf\n", mjd);
  while (scanf("%lf %lf %ld", &ra, &dec, &id) == 3) {
    ra *= deg_to_rad;
    dec *= deg_to_rad;
    slaEqgal(ra, dec, &l, &b);
    slaEqecl(ra, dec, mjd, &el, &eb);
    printf("%ld %lf %lf %lf %lf %lf %lf\n", id, ra/deg_to_rad, dec/deg_to_rad, l/deg_to_rad, b/deg_to_rad, el/deg_to_rad, eb/deg_to_rad);
  }
}
    
