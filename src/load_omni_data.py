import pyspedas
import pytplot

year = input('year')
start_day_string = [year + '-01-01', 
                    year + '-02-01',
                    year + '-03-01',
                    year + '-04-01',
                    year + '-05-01',
                    year + '-06-01',
                    year + '-07-01',
                    year + '-08-01',
                    year + '-09-01',
                    year + '-10-01',
                    year + '-11-01',
                    year + '-12-01',
                    str(int(year) + 1) + '-01-01']

for k in range(len(start_day_string)-1):
    
    trange = [start_day_string[k], start_day_string[k+1]]
    print(trange)
    pyspedas.omni.data(trange = trange, level = 'hro', datatype='1min')
    tplot_names = pytplot.tplot_names(True)
    pytplot.store_data(tplot_names, delete=True)