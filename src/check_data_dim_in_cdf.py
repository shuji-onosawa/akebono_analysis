import pytplot

for date in ['0201', '0202', '0203', '0204', '0205', '0206', '0207', '0208', '0209', '0210',
             '0211', '0212', '0213', '0214', '0215', '0216', '0217', '0218', '0219', '0220',
             '0221', '0222', '0223', '0224', '0225', '0226', '0227', '0228']:

    print(date)
    cdf_name = '/Document/Make_mca_cdf/onosawa/CDF-H0/1990/ak_h0_mca_1990' + date + '_v01.cdf'
    pytplot.cdf_to_tplot(cdf_name)
