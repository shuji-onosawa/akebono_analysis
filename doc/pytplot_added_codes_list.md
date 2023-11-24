# logs of changes by myself in files in pytplot module
## MPLPlotter/tplot.py
* adjust positions of added x-axes

before
```python
    # set up the new x-axis
    axis_delta = axis_delta - num_panels*0.1
    new_xaxis = this_axis.secondary_xaxis(location=axis_delta)
    xaxis_ticks = this_axis.get_xticks().tolist()
    xaxis_ticks_dt = [np.datetime64(mpl.dates.num2date(tick_val).isoformat()) for tick_val in xaxis_ticks]
    # xaxis_ticks_unix = [tick_val.timestamp() for tick_val in xaxis_ticks_dt]
    xaxis_labels = get_var_label_ticks(label_data, xaxis_ticks_dt)
    new_xaxis.set_xticks(xaxis_ticks_dt)
    new_xaxis.set_xticklabels(xaxis_labels)
    ytitle = pytplot.data_quants[label].attrs['plot_options']['yaxis_opt']['axis_label']
    new_xaxis.set_xlabel(ytitle)

fig.subplots_adjust(bottom=0.05+len(var_label)*0.1)

```
after
```python
    # set up the new x-axis
    axis_delta = axis_delta - num_panels*0.03
    new_xaxis = this_axis.secondary_xaxis(location=axis_delta)
    xaxis_ticks = this_axis.get_xticks().tolist()
    xaxis_ticks_dt = [np.datetime64(mpl.dates.num2date(tick_val).isoformat()) for tick_val in xaxis_ticks]
    # xaxis_ticks_unix = [tick_val.timestamp() for tick_val in xaxis_ticks_dt]
    xaxis_labels = get_var_label_ticks(label_data, xaxis_ticks_dt)
    new_xaxis.set_xticks(xaxis_ticks_dt)
    new_xaxis.set_xticklabels(xaxis_labels)
    ytitle = pytplot.data_quants[label].attrs['plot_options']['yaxis_opt']['axis_label']
    new_xaxis.set_xlabel(ytitle)

# fig.subplots_adjust(bottom=0.05+len(var_label)*0.1)
```
* apply horizontal bars
```python
    # apply any vertical an horizontal bars
    if pytplot.data_quants[variable].attrs['plot_options'].get('time_bar') is not None:
        time_bars = pytplot.data_quants[variable].attrs['plot_options']['time_bar']

        for time_bar in time_bars:
            if time_bar['dimension'] == 'height':
                this_axis.axvline(x=datetime.fromtimestamp(time_bar['location'], tz=timezone.utc),
                    color=np.array(time_bar.get('line_color'))/256.0, lw=time_bar.get('line_width'))
            if time_bar['dimension'] == 'width':
                this_axis.axhline(y=time_bar['location'],
                    color=np.array(time_bar.get('line_color'))/256.0, lw=time_bar.get('line_width'))
```
* Silence the warning of transfrom non-nanosecond to nanosecond
プロットしたいデータはnanosecondだけど追加x軸に指定したいデータ(軌道データとか)がnon-nanosecondの時に出る警告を消す
```python
def get_var_label_ticks(var_xr, times):
    out_ticks = []
    for time in times:
        out_ticks.append('{:.2f}'.format(var_xr.interp(coords={'time': time}, kwargs={'fill_value': 'extrapolate', 'bounds_error': False}).values))
    return out_ticks
```
->
```python
def get_var_label_ticks(var_xr, times):
    out_ticks = []
    for time in times:
        time_ns = np.datetime64(time, 'ns')  # Convert to nanosecond precision
        interpolated_value = var_xr.interp(coords={'time': time_ns}, kwargs={'fill_value': 'extrapolate', 'bounds_error': False}).values
        out_ticks.append('{:.2f}'.format(interpolated_value))
    return out_ticks
```

## options.py
```python
    if(value == 6 or value == 'none'):
        pytplot.data_quants[i].attrs['plot_options']['line_opt']['visible'] = False

if option == 'char_size':
pytplot.data_quants[i].attrs['plot_options']['extras']['char_size'] = value
```

->
```python
    if(value == 6 or value == 'none'):
        pytplot.data_quants[i].attrs['plot_options']['line_opt']['visible'] = False

if option == 'marker':
    pytplot.data_quants[i].attrs['plot_options']['line_opt']['marker'] = value

if option == 'char_size':
pytplot.data_quants[i].attrs['plot_options']['extras']['char_size'] = value
```
