/*
up, perp�C�I���̃J�E���g���v�Z�p�v���O�����@

SDB/SMS����thermal(0-25eV)��H+,O+�̃f�[�^��ǂݍ���
�t�@�C���ithermalh.txt, thermalo.txt)�ɏ����o��
�i�����o���I���Ă��v���O�������I�����Ȃ��ꍇ��Ctrl+Z�ŋ����I���A
5�b���x�ŏ����o���͏I���j

*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char *argv[])
{
	FILE	*file, *wfh, *wfo;
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

/*�ǂݍ��ރt�@�C��(�L�[�{�[�g����)�Ə����o���t�@�C�����J��*/
	file = fopen(argv[1], "rb");
	wfh = fopen("thermalh.txt", "w");
	wfo = fopen("thermalo.txt", "w");

/*1block�ڂ���J�n������ǂݍ��݁A�����o��*/
	for( i = 0; i <= 5; i++){
		dd = getc(file);
		day[i] = dd;
		}

	/*�`��*/
	for( h = 0; h <= 1; h++){
		dd = getc(file);
		hh[h] = dd;
		}
	/*�`��*/
	for( m = 0; m <= 1; m++){
		dd = getc(file);
		mm[m] = dd;
		}
	/*�`�b*/
	for( s = 0; s <= 1; s++){
		dd = getc(file);
		ss[s] = dd;
		}

	ihs = atoi(hh);
	ims = atoi(mm);
	iss = atoi(ss);

	/*�w�b�_�[�̎c��̏��̓X���[*/
	for( k = 0; k <= 3648; k++){ 
		dd = getc(file);
		}

/*2block�ڈȍ~�̌v���f�[�^��ǂݍ��݁A�����o��*/
	while( (icn = getc(file)) != EOF || scanf("%d", &n) != EOF ){

		/*�w�b�_�[�̏��
		ramm(�X�s�����ʓ���ram�����̊p�x)
		rama(ram�����ƃX�s�����ʂ̂Ȃ��p)
		iaper(���͐��ƃX�s�����ʂ̂Ȃ��p�H)
		mfl(�ϑ����[�h)
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
				fprintf(wfh, "%d %d %d\n",ihh,imm,isc);
				fprintf(wfo, "%d %d %d\n",ihh,imm,isc);
				}
			else if( mfl == EOF )goto OUT;

			for(j=0; j<=3; j++){
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
				if( mfl == 1 && dd != EOF ){
					for(i=0; i<=15; i++){fprintf(wfh, "%f %f %f\n", dbl[i][0], dbl[i][1], dbl[i][2]);}
					t = t + 1;
					}
				if( dd == EOF )goto OUT;
				}
			for(j=0; j<=3; j++){
				for(i=0; i<=15; i++){
					dd = getc(file);
					df = ((float)dd)/50.0;
					if( dd == EOF )goto OUT;	
					}
				if( dd == EOF )goto OUT;	
				}
			for(j=0; j<=3; j++){
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
				if( mfl == 1 && dd != EOF ){
					for(i=0; i<=15; i++){fprintf(wfo, "%f %f %f\n", dbl[i][0], dbl[i][1], dbl[i][2]);}
					t = t + 1;
					}
				else if( dd == EOF )goto OUT;	
				}

			for(k=0; k<=2; k++){
			for(i=0; i<=15; i++){
				dd = getc(file);
				df = ((float)dd)/50.0;
				if( dd == EOF )goto OUT;	
				}
				if( dd == EOF )goto OUT;	
			}
		}
	}
OUT:
	fclose(wfh);
	fclose(wfo);
	fclose(file);
	exit(0);
}
