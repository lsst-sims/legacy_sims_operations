void hunt(double *xx,int n, double x, int *jlo)
{
  int jm,jhi,inc;
  int ascnd;
                                                                                
  ascnd=(xx[n-1] >= xx[0]);
  if(ascnd) {
    if (x<xx[0]) {*jlo = -1; return;}
    if (x>xx[n-1]) {*jlo = n; return;}
  }
  else {
    if (x>xx[0]) {*jlo = -1; return;}
    if (x<xx[n-1]) {*jlo = n; return;}
  }

  if (*jlo < 0 || *jlo >= n) {
    *jlo=0;
    jhi=n+1;
  }
  else {
    inc=1;
    if (x >= xx[*jlo] == ascnd) {
      if (*jlo == n-1) return;
      jhi=(*jlo)+1;
      while (x >= xx[jhi] == ascnd) {
        *jlo=jhi;
        inc += inc;
        jhi=(*jlo)+inc;
        if (jhi >= n) {
          jhi=n+1;
          break;
        }
      }
    }
    else {
      if (*jlo == 0) {
        *jlo=0;
        return;
      }
      jhi=(*jlo)--;
      while (x < xx[*jlo] == ascnd) {
        jhi=(*jlo);
        inc <<= 1;
        if (inc > jhi) {
          *jlo=0;
          break;
        }
        else *jlo=jhi-inc;
      }
    }
  }
  while (jhi-(*jlo) != 1) {
    jm=(jhi+(*jlo)) >> 1;
    if (x >= xx[jm] == ascnd)
      *jlo=jm;
    else
      jhi=jm;
  }
  if (x == xx[n-1]) *jlo=n-1;
  if (x == xx[0]) *jlo=0;
}
                                                                                



#if 0
#define N 100
#include <stdio.h>

int main(void)
{

  int i;
  double x[N], xx;


  for(i=0; i<N; i++) x[i] = (double) (i)/(double)(N-1);
  for(i=0; i<N; i++) printf("%d %f\n", i, x[i]);
  while(xx>-10) {
    scanf("%lf",&xx);
    hunt(x, N, xx, &i);
    printf("%d  %f  %f  %f\n",i, x[i], xx, x[i+1]);
  }


  for(i=0; i<N; i++) x[i] = (double) (N-i-1)/(double)(N-1);
  for(i=0; i<N; i++) printf("%d %f\n", i, x[i]);
  while(xx>-10) {
    scanf("%lf",&xx);
    hunt(x, N, xx, &i);
    printf("%d  %f  %f  %f\n",i, x[i], xx, x[i+1]);
  }
}
#endif
