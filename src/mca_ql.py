import load
import pytplot
from datetime import datetime, timedelta


def next_day(date_string):
    date_format = '%Y-%m-%d'
    date = datetime.strptime(date_string, date_format)
    next_date = date + timedelta(days=1)
    return next_date.strftime(date_format)


date = '1990-02-17'
load.mca(trange=[date, next_day(date)], spec_type='amp') 

pytplot.tlimit([date + ' 3:45:00', date + ' 3:55:00'])
pytplot.tplot(['Emax_amp', 'Bmax_amp'], xsize=10, ysize=10)
