# logs of changes by myself in files in pytplot module
## MPLPlotter>tplot.py
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

options.py
    if(value == 6 or value == 'none'):
        pytplot.data_quants[i].attrs['plot_options']['line_opt']['visible'] = False

if option == 'char_size':
pytplot.data_quants[i].attrs['plot_options']['extras']['char_size'] = value
->
    if(value == 6 or value == 'none'):
        pytplot.data_quants[i].attrs['plot_options']['line_opt']['visible'] = False

if option == 'marker':
    pytplot.data_quants[i].attrs['plot_options']['line_opt']['marker'] = value

if option == 'char_size':
pytplot.data_quants[i].attrs['plot_options']['extras']['char_size'] = value
