c
c
c				/2000/05/19  Manabu YAMADA
      program main

      REAL*4     VI(3),TEMP(3),DEN(3),ves(3)

      CHARACTER (5)  SPECIES(3)
      data SPECIES/'H+','He+','O+'/


      open(1,file='y1990.dat')
c     read comment line
      READ(1,*) 

      do 1000 id=1,9999999
	 READ(1,*,END=1100) 
     -			 iyymmdd,ihhmmss,dmlt,dinv,dalt,dmlat
     -			,VI(1),VI(2),vdm,VI(3),TEMP(1),TEMP(2)
     -			,d13,TEMP(3),ytime,bx,by,bz,stemp,sden
     -			,ivs,kp,suns, Dst,dlat,deg
     -			,DEN(1),DEN(2),d29,DEN(3)
     -			,cvsa,cvpe,ves(1),ves(2),ves(3)

c	iyymmdd	: year month day
c	ihhmmss : hour minute sec
c	dmlt	: magnetic local time
c	dinv	: invariant latitude (deg)
c	dalt 	: altitude (km)
c		   dalt > 0 : northern
c		   dalt < 0 : southern
c	dmlat	: magnetic latitude (deg)
c	VI(3)	: ion velocity (km/sec)
c		 upward : northern > 0, southern < 0
c	(vdm	:)
c	TEMP(3)	: ion temperature (log(K))
c	(tdm	:)
c	[ytime	: ]
c*	bx, by, bz : (nT)
c*	stemp	: plasma temperature (K)
c*	sden	: ploton density (cm-3)
c*	ivs	: bulk speed (km/sec)
c*	kp	: Kp index * 10	ex. 57 = 6-, 60 = 6, 63 = 6+
c*	suns	: sunspot number
c*	Dst	: Dst index (Gammas)
c	[dlat	: 90 - invlat] 
c	[deg	: mlt/24*360]
c	DEN(3)	: ion density (log(ions/m**3))
c	(ddm	:)
c	cvsa	: satellite potential (V)
c	cvpe	: perpndicular velocity (km/s)
c	ves()	: satellite velocity in the satellite coordinate (km/s)

c 	�� ���Τ�[]�ǰϤޤ�Ƥ����ѿ���¾���ͤ���Ƴ���Ф���.
c	(�������� gnuplot ��Ȥ�������ͤ�񤭹�������.
c	 �ץ����Υǡ����ɤ߹��ߤ��Թ�Ǥޤ��Ĥ��Ƥ��뤬
c	 ���Τ���¾���ѿ��򵭽Ҥ��뤫���Τ�ʤ���)
c	�� �����Ȥ�ľ��˥������ꥹ�����դ��Ƥ����ѿ���
c	NSSDC �����������ɤ����ǡ���


 1000 continue
 1100 continue

      stop
      end
