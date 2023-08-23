import pyspedas
import pytplot
import akebono
import pandas as pd
from calc_sza_from_geo import calc_sza_from_geo
import xarray as xr

# input
start_date = '1991-04-01'
end_date = '1991-04-02'
inv_min = 0
inv_max = 90
mlt_min = 0
mlt_max = 24
alt_min = 0
alt_max = 10000

# calc
sza_list = []
Epwr_list = []
Bpwr_list = []

# date list. format: YYYY-MM-DD
date_list = pd.date_range(start_date, end_date, freq='D').strftime('%Y-%m-%d')
for date1, date2 in zip(date_list[:-1], date_list[1:]):
    print('processing: ' + date1 + ' to ' + date2)
    try:
        akebono.orb(trange=[date1, date2])
    except Exception as e:
        print('No orbit data')
        print(e)
        continue
    akebono.vlf_mca(trange=[date1, date2], datatype='pwr')
    pytplot.tplot_names()
    # interpolate
    pyspedas.tinterpol('akb_orb_geo', 'akb_mca_Emax_pwr', newname='akb_orb_geo_intrp')
    pyspedas.tinterpol('akb_orb_inv', 'akb_mca_Emax_pwr', newname='akb_orb_inv_intrp')
    pyspedas.tinterpol('akb_orb_mlt', 'akb_mca_Emax_pwr', newname='akb_orb_mlt_intrp')
    pyspedas.tinterpol('akb_orb_alt', 'akb_mca_Emax_pwr', newname='akb_orb_alt_intrp')

    # get data and convert to xarray
    Epwr_xry = pytplot.get_data('akb_mca_Emax_pwr', xarray=True)
    Bpwr_xry = pytplot.get_data('akb_mca_Bmax_pwr', xarray=True)
    geo_xry = pytplot.get_data('akb_orb_geo_intrp', xarray=True)
    inv_xry = pytplot.get_data('akb_orb_inv_intrp', xarray=True)
    mlt_xry = pytplot.get_data('akb_orb_mlt_intrp', xarray=True)
    alt_xry = pytplot.get_data('akb_orb_alt_intrp', xarray=True)

    # make dataset
    geo_xry = geo_xry.rename_dims({'v_dim': 'v_dim1'})
    dataset = xr.merge([Epwr_xry, Bpwr_xry, geo_xry, inv_xry, mlt_xry, alt_xry])
    print(dataset)
