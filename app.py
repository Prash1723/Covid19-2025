from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, Legend, GeoJSONDataSource, LinearColorMapper, ColorBar, Range1d
from bokeh.models import NumeralTickFormatter, HoverTool, LabelSet, Panel, Tabs, Slider, CustomJS, TapTool, CDSView
from bokeh.models.widgets import TableColumn, DataTable, NumberFormatter, Dropdown, Select, RadioButtonGroup, TableColumn
from bokeh.palettes import Category20c
from bokeh.layouts import row, column, gridplot
from bokeh.palettes import Viridis6 as palette
from bokeh.transform import cumsum

import colorcet

import geopandas as gpd
import pycountry
import json

import warnings
warnings.filterwarnings('ignore')

cases_url = 'https://www.covid19india.org/'
active_cl = 'has-fixed-layout'
h3_table2 = 'COVID-19 Active Cases State Wise 2025 Update Today'

response = requests.get(cases_url)
soup = BeautifulSoup(response.text, 'html.parser')

tables = soup.find_all('table', attrs={'class': active_cl})

# Load data
cov_total = pd.read_html(str(tables), header=0)[0]

# Rename Columns
cov_total.columns = ["s.no", "state", "total_active_cases", "new_cases_today"]

# Rename state
state_name = {'Kerala***': 'Kerala', 'Orissa': 'Odisha'}

cov_total.state = cov_total.state.apply(lambda x: state_name.get(x, x))

# Save Data
cov_total.to_csv('data/total_data.csv', index=False)

# Map data
borders = 'mapping/in.shp'
gdf = gpd.read_file(borders)[['id', 'name', 'geometry']]

# Rename columns
gdf.columns = ['state_code', 'state', 'geometry']

# Rename state
gdf.state = gdf.state.apply(lambda x: state_name.get(x, x))

# Drop total row
cov_total.drop(index=28, axis=0, inplace=True)

# Replace - with 0 in new_cases_today
cov_total.new_cases_today.replace({'–': 0}, inplace=True)
cov_total.new_cases_today = cov_total.new_cases_today.apply(lambda x: int(x))

# - Functions

# Mask data to the required year value
df1 = gdf.merge(cov_total, how='left', left_on='state', right_on='state')

df1.fillna(0, inplace=True)

affected_state = df1.query('new_cases_today==new_cases_today.max()')['state'].values[0]

total_daily, total_active = cov_total[['new_cases_today', 'total_active_cases']].sum()
print(total_daily) 
print(total_active)

# Calculate percentages
df1['total_active_cases_perc'] = (df1['total_active_cases']*100)/total_active
df1['new_cases_today_perc'] = (df1['new_cases_today']*100)/total_daily

# Create widgets
state_select = Select(
    title="Select state",
    value=affected_state,
    options=list(set(cov_total['state'].dropna().astype(str)))
    )

# Read data to json
## India map data
df_json = json.loads(df1[[
    'state_code', 
    'state', 
    'geometry', 
    'total_active_cases', 
    'new_cases_today', 
    'total_active_cases_perc', 
    'new_cases_today_perc'
    ]].to_json())

map_data = json.dumps(df_json)

## State map data
state_json = json.loads(df1.query('state==@affected_state')[[
    'state_code', 
    'state', 
    'geometry', 
    'total_active_cases', 
    'new_cases_today', 
    'total_active_cases_perc', 
    'new_cases_today_perc'
    ]].to_json())

state_data = json.dumps(state_json)

# Data source
map_source = GeoJSONDataSource(geojson=map_data)

state_source = GeoJSONDataSource()

# Map Geometry
color_mapper1 = LinearColorMapper(palette=colorcet.bgy, low=0, high=cov_total.new_cases_today.max())
color_mapper2 = LinearColorMapper(palette=colorcet.bgy, low=0, high=cov_total.total_active_cases.max())

color_bar1 = ColorBar(color_mapper = color_mapper1, location = (0,0))
color_bar2 = ColorBar(color_mapper = color_mapper2, location = (0,0))

# Map of India
TOOLS = "pan,wheel_zoom,reset,hover,save"

map_all = figure(
    width=550, 
    height=725,
    title="Total active cases by states",
    tools=TOOLS, x_axis_location=None, y_axis_location=None,
    tooltips = [
        ("state", "@state"),
        ("Cases", "@total_active_cases"),
        ("percentage", "@total_active_cases_perc%")
    ]
)

map_all.grid.grid_line_color = None
map_all.hover.point_policy = "follow_mouse"

# Create patches (of map)
map_all.patches(
    "xs", "ys", source=map_source,
    fill_color={
        "field": 'total_active_cases',
        "transform": color_mapper2
    },
    fill_alpha=0.7, line_color="black", line_width=0.5
)

map_all.add_layout(color_bar2, 'below')

def update_state():
    """
    Update state map data
    """
    selected_state = state_select.value

    # Filter data
    data = df1[df1['state']==selected_state][[
    'state_code', 
    'state', 
    'geometry', 
    'total_active_cases', 
    'new_cases_today', 
    'total_active_cases_perc', 
    'new_cases_today_perc'
    ]].to_json()
    
    # Read and dump data into json
    state_json = json.loads(data)
    state_data = json.dumps(state_json)

    state_source.geojson = state_data

def create_state(src):
    """
    Creates the state map
    """

    map_data = src

    # State map of India
    TOOLS = "pan,wheel_zoom,reset,hover,save"

    map_state = figure(
        width=460, 
        height=460,
        title="Daily active cases by state",
        tools=TOOLS, x_axis_location=None, y_axis_location=None,
        tooltips = [
            ("state", "@state"),
            ("Cases", "@new_cases_today"),
            ("percentage", "@new_cases_today_perc%")
        ]
    )

    map_state.grid.grid_line_color = None
    map_state.hover.point_policy = "follow_mouse"

    # Create patches (of map)
    map_state.patches(
        "xs", "ys", source=map_data,
        fill_color={
            "field": 'new_cases_today',
            "transform": color_mapper1
        },
        fill_alpha=0.7, line_color="black", line_width=0.5
    )

    map_state.add_layout(color_bar1, 'below')

    return map_state

update_state()

map_state = create_state(state_source)

state_select.on_change("value", lambda attr, old, new: update_state())

layout = row(map_all, column(state_select, map_state))

curdoc().add_root(layout)
curdoc().title = "Covid-19 cases map"