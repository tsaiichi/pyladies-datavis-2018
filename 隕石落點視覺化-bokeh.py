import numpy as np

from bokeh.layouts import row, column
from bokeh.models import BoxSelectTool, LassoSelectTool, Spacer
from bokeh.plotting import figure, curdoc

# added
from bokeh.io import show, output_notebook, output_file
from bokeh.models import FixedTicker

import pandas as pd

data_path = "./meteorite-landings.csv"
df = pd.read_csv(data_path)
# filter 'reclong'
df = df[df['reclong']<=180]

x = df['reclong']
print(max(x), min(x))  # 178.2 -165.43333

y = df['reclat']
print(max(y), min(y))  # 81.16667 -87.36667

# norm mass to encode to circle size
mass = df['mass']
print(max(mass), min(mass))  # 60000000.0, 0.0
areas = (mass-min(mass)) / (max(mass)-min(mass))
print(max(areas), min(areas))  # 1.0, 0.0

# encode 'fall' to colors
colors = pd.factorize(df['fall'])[0]
cmap = ['#6E3D76', '#00441B']
colors = [cmap[c] for c in colors ]


output_notebook()
# tool bar
TOOLS="pan,wheel_zoom,box_select,lasso_select,reset"

# create the scatter plot
p = figure(plot_width=600, plot_height=300, min_border=10, min_border_left=50,
           toolbar_location=None, x_axis_location=None, y_axis_location=None)
p.background_fill_color = "#fafafa"
p.select(BoxSelectTool).select_every_mousemove = False
p.select(LassoSelectTool).select_every_mousemove = False

r = p.scatter(x, y, size=np.sqrt(areas)*50, color=colors, alpha=0.6)


# create the horizontal histogram
hhist, hedges = np.histogram(x, bins=20)
hzeros = np.zeros(len(hedges)-1)
hmax = max(hhist)*1.1

LINE_ARGS = dict(color="#3A5785", line_color=None)

ph = figure(tools=TOOLS, toolbar_location="above", plot_width=p.plot_width, plot_height=100,
            x_range=p.x_range, y_range=(0, hmax), min_border=10, min_border_left=50, 
            y_axis_location="right", title="Nasa Meteorite-Landings")
ph.xgrid.grid_line_color = None
ph.yaxis.ticker = FixedTicker(ticks=[0, hmax//2000*1000, hmax//1000*1000])
ph.background_fill_color = "#fafafa"

ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hhist, color="white", line_color="#3A5785")
hh1 = ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros, alpha=0.5, **LINE_ARGS)
hh2 = ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros, alpha=0.1, **LINE_ARGS)

# create the vertical histogram
vhist, vedges = np.histogram(y, bins=20)
vzeros = np.zeros(len(vedges)-1)
vmax = max(vhist)*1.1

pv = figure(toolbar_location=None, plot_width=100, plot_height=p.plot_height, x_range=(0, vmax),
            y_range=p.y_range, min_border=10, y_axis_location="right")
pv.ygrid.grid_line_color = None
pv.xaxis.major_label_orientation = np.pi/4
pv.xaxis.ticker = FixedTicker(ticks=[0, vmax//2000*1000, vmax//1000*1000])
pv.background_fill_color = "#fafafa"

pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vhist, color="white", line_color="#3A5785")
vh1 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.5, **LINE_ARGS)
vh2 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.1, **LINE_ARGS)

layout = column(row(ph, Spacer(width=100, height=100)), row(p, pv))

curdoc().add_root(layout)
curdoc().title = "Selection Histogram"

def update(attr, old, new):
    inds = np.array(new['1d']['indices'])
    if len(inds) == 0 or len(inds) == len(x):
        hhist1, hhist2 = hzeros, hzeros
        vhist1, vhist2 = vzeros, vzeros
    else:
        neg_inds = np.ones_like(x, dtype=np.bool)
        neg_inds[inds] = False
        hhist1, _ = np.histogram(x[inds], bins=hedges)
        vhist1, _ = np.histogram(y[inds], bins=vedges)
        hhist2, _ = np.histogram(x[neg_inds], bins=hedges)
        vhist2, _ = np.histogram(y[neg_inds], bins=vedges)

    hh1.data_source.data["top"]   =  hhist1
    hh2.data_source.data["top"]   = -hhist2
    vh1.data_source.data["right"] =  vhist1
    vh2.data_source.data["right"] = -vhist2

r.data_source.on_change('selected', update)

show(layout)

output_file('bokeh_vis.html')