pro akb_load_elfw

fn=dialog_pickfile(path='C:\Users\石ヶ谷\data\exosd\vlf_elf\', filter=['*.cdf'])

;----- Print PI info and rules of the road -----;
if(file_test(fn[0])) then begin
  gatt = cdf_var_atts(fn[0])
  print, '**************************************************************************************'
  ;print, gatt.project
  print, gatt.Logical_source_description
  print, ''
  print, 'PI: ', gatt.PI_name
  print, 'Affiliations: ', gatt.PI_affiliation
  print, ''
  print_str_maxlet, gatt.TEXT
  print, '**************************************************************************************'
endif

cdf2tplot, file=fn

h=30.0
l=0.05

gep=-2.15
ged=20.0
gbd=20.0 ;search coil->20dB, loop antenna->25dB

z0=377.0

u=1.26*10^(-6.0)

calc, '"E"="dE_wav_narrow"/(h*gep*ged)' ;mV/m
calc, '"Bx"="dBx_wav_narrow"*u/(z0*l*gbd*10^(-9))' ;nT
calc, '"By"="dBy_wav_narrow"*u/(z0*l*gbd*10^(-9))' ;nT
calc, '"Bz"="dBz_wav_narrow"*u/(z0*l*gbd*10^(-9))' ;nT

window, 0, xsize=1000, ysize=600 & erase

options, "E", 'ytitle', 'E'
options, "E", 'ysubtitle', '[mV/m]'
options, "Bx", 'ytitle', 'Bx'
options, "Bx", 'ysubtitle', '[nT]'
options, "By", 'ytitle', 'By'
options, "By", 'ysubtitle', '[nT]'
options, "Bz", 'ytitle', 'Bz'
options, "Bz", 'ysubtitle', '[nT]'

ylim, "E", -1.1, 1.1, 0
ylim, "Bx", -5000, 5000, 0
ylim, "By", -5000, 5000, 0
ylim, "Bz", -5000, 5000, 0

tplot, ["E","Bx","By","Bz"]

end