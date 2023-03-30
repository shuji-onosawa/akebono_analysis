#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char *argv[])
{
  FILE	*fsms, *fperp, *fup;
  int	i, j, k, h, m, s, sh, sm, eh, em, time, stime, etime, t;       
  float	no, sa, ct, ang, perp[5] = {0}, up[5] = {0};
   
  fsms = fopen(argv[1], "r");
  fperp = fopen("smscperp.txt", "w");
  fup = fopen("smscup.txt", "w");

  printf("Start time (hh mm)");
  scanf("%d %d", &sh, &sm);
  printf("End time (hh mm)");
  scanf("%d %d", &eh, &em);
  stime = sh*60+sm;
  etime = eh*60+em;

  for( k = 0; k <= 9999; k++){
   fscanf(fsms, "%d %d %d", &h, &m, &s);
   time = h*60+m;
   t = h*10000+m*100+s;

   for( i = 0; i <= 3; i++){
     for( j = 0; j <= 15; j++){
	fscanf(fsms, "%f %f %f", &no, &sa, &ct); 
	if( j == 0 ){
	 up[i] = ct;
	 perp[i] = 0.0;
	 }
	if( j == 1 || j == 14 || j == 15 ){
	 up[i] = up[i] + ct;
	 }
	if( j == 3 || j == 4 || j == 11 || j== 12 ){
	 perp[i] =perp[i] + ct;
	 }
	}
     }

   perp[4] = perp[0]+perp[1]+perp[2]+perp[3];
   up[4] = up[0]+up[1]+up[2]+up[3];

   if( time >= stime && time <= etime ){
     fprintf(fperp, "%d %f %f %f %f %f\n", t, perp[0], perp[1], perp[2], perp[3], perp[4]);  
     fprintf(fup, "%d %f %f %f %f %f\n", t, up[0], up[1], up[2], up[3], up[4]);
     }

   perp[4] = 0.0;
   up[4] = 0.0;

   if( time > etime )break;
   }

  fclose(fperp);
  fclose(fup);
  fclose(fsms);
  exit(0);
}
