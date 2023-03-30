/*
SDB/SMS����thermal(0-25eV)��O+�̃f�[�^��ǂݍ���
gnuplot��(sms.plt)�ŃJ���[�R���^������悤�Ƀt�@�C��(smsploto.txt)�ɏ����o��
�����o���I���Ă��v���O�������I�����Ȃ��̂�Ctrl+Z�ŋ����I��
�i5�b���x�ŏ����o���͏I���j
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

/*�ǂݍ��ރt�@�C��(�L�[�{�[�g����)�Ə����o���t�@�C�����J��*/
	file = fopen(argv[1], "rb");
	wfile = fopen("smsploto.txt", "w");

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
				fprintf(wfile, "Time: %d %d %d / min pitch angle: %d\n",ihh,imm,isc,iaper);
				}
			else if( mfl == EOF )goto OUT;

/*��������thermal�f�[�^�ǂݍ��� *1 */
			/*H,He��ǂݔ�΂� *2 */
			for(k=0; k<=1; k++){
			for(j=0; j<=7; j++){
				for(i=0; i<=15; i++){
					dd = getc(file);
					df = ((float)dd)/50.0;
					if( dd == EOF )goto OUT;	
					}
				if( dd == EOF )goto OUT;	
				}
				if( dd == EOF )goto OUT;	
				}
			/*��������O+�ǂݍ��݁A�����o�� *3 */
			for(j=0; j<=7; j++){
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
					for(i=0; i<=15; i++){fprintf(wfile, "%5.1f\t%6.1f\t%f\n", dbl[i][0], dbl[i][1], dbl[i][2]);}
					t = t + 1;
					}
				if( mfl == 1 && dd != EOF ){fprintf(wfile, "\n");}
				else if( dd == EOF )goto OUT;	
				}
			/*�����܂�*/
/*�����܂�
*3������ǂ݂����ǂݔ�΂��Ă��鏑���o�������C�I����̈ʒu�Ɉړ�����Ƃ��̃C�I����̏����o���v���O������
��j*2�̑O�Ɉړ�����ƁAH+�̏����o��*/

/*��������suprathermal�f�[�^�̓ǂݔ�΂�*/
			for(k=0; k<=2; k++){
			for(i=0; i<=15; i++){
				dd = getc(file);
				df = ((float)dd)/50.0;
				if( dd == EOF )goto OUT;	
				}
				if( dd == EOF )goto OUT;	
			}
/*�����܂�*/
		}
	}
OUT:
	fclose(wfile);
	fclose(file);
	exit(0);
}
