/*
SDB/SMSから全データを読み込みファイル(test.txt)に書き出す
書き出し終ってもプログラムが終了しないのでCtrl+Zで強制終了
（5秒程度で書き出しは終わる）
gcc smsread.c なんちゃら -lm デコンパイル
./なんちゃら　ほにゃらら.sms　で実行
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char *argv[])
{
	FILE	*file, *wfile;
	int	icn, iaper, mfl, dd;
	char	day[7], hh[3], mm[3], ss[3];
	int	h, m, s;
	float	ramm, rama, df;
	double	d;
	int	ihs, ims, iss;
	int	ihh, imm, isc;
	int	i, ii, j, k, n, t;
	float	saa[8] = {0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5};
	float	sab[8] = {-180, -157.5, -135, -112.5, -90, -67.5, -45, -22};
	double	dbl[16][3];

	day[6] = '\0';
	hh[2] = '\0';
	mm[2] = '\0';
	ss[2] = '\0';
	t = 0;

/*読み込むファイル(キーボート入力)と書き出すファイルを開く*/
	file = fopen(argv[1], "rb");
	wfile = fopen("test.txt", "w");

/*1block目から開始時刻を読み込み、書き出す*/
	for( i = 0; i <= 5; i++){
		dd = getc(file);
		day[i] = dd;
		printf("%c", dd);
		}

	/*～時*/
	for( h = 0; h <= 1; h++){
		dd = getc(file);
		hh[h] = dd;
		printf("%c", dd);
		}
	/*～分*/
	for( m = 0; m <= 1; m++){
		dd = getc(file);
		mm[m] = dd;
		printf("%c", dd);
		}
	/*～秒*/
	for( s = 0; s <= 1; s++){
		dd = getc(file);
		ss[s] = dd;
		printf("%c", dd);
		}

	ihs = atoi(hh);
	ims = atoi(mm);
	iss = atoi(ss);

	/*ヘッダーの残りの情報はスルー*/
	for( k = 0; k <= 108; k++){ 
		dd = getc(file);
		printf("%c", dd);
		}
	for(k = 0; k <= 3539; k++){
		dd = fscanf(file, "%d", &dd);
		}

/*2block目以降の計測データを読み込み、書き出す*/
	while( (icn = getc(file)) != EOF || scanf("%d", &n) != EOF ){

		/*ヘッダーの情報
		ramm(スピン平面内のram方向の角度)
		rama(ram方向とスピン平面のなす角)
		iaper(磁力線とスピン平面のなす角？)
		mfl(観測モード)
		*/
		for( n = 0; n <= 14; n++){
			dd = getc(file);
			ramm = (float)dd;
			dd = getc(file);
			rama = (float)dd*2.0;
			iaper = getc(file);
			mfl = getc(file);
			ihh = ihs;
			isc = iss + icn*120 + n*8;
			imm = ims + isc/60;

			if( imm >= 60 ){ ihh=ihh+imm/60; }

			imm = imm%60;
			isc = isc%60;

			if( mfl == 1 ){
				fprintf(wfile, "(Thermalmode) Time: %d %d %d / min pitch angle: %d\n",ihh,imm,isc,iaper);
				}
			if( mfl == 2 ){
				fprintf(wfile, "(Suprathermalmode) Time: %d %d %d / min pitch angle: %d\n",ihh,imm,isc,iaper);
				}
			else if( mfl == EOF )goto OUT;

			for(k=0; k<=2; k++){
			for(j=0; j<=7; j++){
				for(i=0; i<=7; i++){
					dd = getc(file); //2byte ずつ
					df = ((float)dd)/50.0;
					ii = i + 8;
					d = pow(10, (double)df);
					dbl[ii][0] = (double)t;
					dbl[ii][1] = (double)saa[i];
					dbl[ii][2] = d;
					if( dd == EOF )goto OUT;	
					}
				for(i=0; i<=7; i++){
					dd = getc(file);
					df = ((float)dd)/50.0;
					d = pow(10, (double)df);   //number fluxを(coun/cc)対数から整数値に戻してる
					dbl[i][0] = (double)t;
					dbl[i][1] = (double)sab[i];
					dbl[i][2] = d;
					if(dd == EOF )goto OUT;
					}
				if( mfl == 1 && dd != EOF ){
					for(i=0; i<=15; i++){fprintf(wfile, "%5.1f\t%6.1f\t%f\n", dbl[i][0], dbl[i][1], dbl[i][2]);}
					t = t + 1;
					}
				if( mfl == 1 && dd != EOF ){fprintf(wfile, "\n");}
				else if( dd == EOF )goto OUT;	
				}
				if( dd == EOF )goto OUT;	
			}

			for(k=0; k<=3; k++){
				for(i=0; i<=7; i++){
					dd = getc(file);
					df = ((float)dd)/50.0;
					ii = i + 8;
					d = pow(10, (double)df);
					dbl[ii][0] = (double)t;
					dbl[ii][1] = (double)saa[i];
					dbl[ii][2] = d;
					if( dd == EOF )goto OUT;	
					}
				for(i=0; i<=7; i++){
					dd = getc(file);
					df = ((float)dd)/50.0;
					d = pow(10, (double)df);
					dbl[i][0] = (double)t;
					dbl[i][1] = (double)sab[i];
					dbl[i][2] = d;
					if(dd == EOF )goto OUT;
					}
				if( mfl == 2 && dd != EOF ){
					for(i=0; i<=15; i++){fprintf(wfile, "%5.1f\t%6.1f\t%f\n", dbl[i][0], dbl[i][1], dbl[i][2]);}
					t = t + 1;
					}
				if( mfl == 2 && dd != EOF ){fprintf(wfile, "\n");}
				else if( dd == EOF )goto OUT;	
				}

			if( dd == EOF )goto OUT;	
			}
			
		}
OUT:
	fclose(wfile);
	fclose(file);
	exit(0);
}
