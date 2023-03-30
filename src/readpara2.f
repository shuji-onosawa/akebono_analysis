c
c
c				/2000/05/19  Manabu YAMADA
c				/2017/11/07  Yuki Ishigaya
c
c     指定した日付のH+,O+のデータを読みこみ別のファイルに任意のデータを書き込む
c
      program main
      implicit none

      integer	iyymmdd, ihhmmss
      real	dmlt, dinv, dalt, dmlat
      real	VI(3), TEMP(3), DEN(3), ves(3)
      real	vdm, d13, d29, ytime, bx, by, bz, pt, pden, ivs, kp
      real	suns, Dst, dlat, deg, cvsa, cvpe


      character(5)  SPECIES(3)
      data SPECIES/'H+','He+','O+'/

      integer day
      integer k, id

c     select event data
      print *, "Please enter event data (yymmdd)"
      read *, day

      open(1, file='y1990.dat')
      open(2, file='parah.txt', position='append')
      open(3, file='parao.txt', position='append')

      write (2,*) day
      write (3,*) day

c     read comment line
      READ(1,*)

      do 1000 id=1,9999999
	 READ(1,*,END=1100) 
     -			 iyymmdd,ihhmmss,dmlt,dinv,dalt,dmlat
     -			,VI(1),VI(2),vdm,VI(3),TEMP(1),TEMP(2)
     -			,d13,TEMP(3),ytime,bx,by,bz,pt,pden
     -			,ivs,kp,suns, Dst,dlat,deg
     -			,DEN(1),DEN(2),d29,DEN(3)
     -			,cvsa,cvpe,ves(1),ves(2),ves(3)
	 if(iyymmdd.EQ.day)then
		 write (2,*) ihhmmss, cvsa, VI(1), TEMP(1), DEN(1)
         	 write (3,*) ihhmmss, cvsa, VI(3), TEMP(3), DEN(3)
		 endif

c       書き出すデータは以下を参照
c
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

c 	※ 全体が[]で囲まれている変数は他の値から導き出せる.
c	(学部時代 gnuplot を使うために値を書き込んだもの.
c	 プログラムのデータ読み込みの都合でまだ残しているが
c	 そのうち他の変数を記述するかも知れない…)
c	※ コメントの直後にアスタリスクが付いている変数は
c	NSSDC からダウンロードしたデータ


 1000 continue
 1100 continue

      close(2)
      close(1)
      stop
      end
