- cdfのメタデータを取得する
```python
from pytplot import cdf_to_tplot
import pytplot

cdf_to_tplot('cdffilename')
gatt = get_data('valuable', metadata=True)['CDF']['VATT']
pytplot.data_quants['valuable']
```