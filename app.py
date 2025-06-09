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
cov_total.columns = ["s.no", "state", "total_active_cases", "new_cases_since_day_before"]

# Save Data
cov_total.to_csv('data/total_data.csv', index=False)

# Map data
borders = 'mapping/ne_50m_admin_1_states_provinces.shp'
gdf = gpd.read_file(borders)[['admin', 'adm0_a3', 'name', 'geometry']]

# Rename columns
gdf.columns = ['country', 'country_code', 'state', 'geometry']

# - Functions

def create_data(df1, map_data):
    """Create and modify data for the bokeh map"""

    # Mask data to the required year value
    df1 = gdf.merge(cov_total, how='inner', left_on='state', right_on='state')

    # Read data to json
    df_json = json.loads(df1[
        ['country', 'country_code', 'state', 'geometry', 'total_active_cases', 'new_cases_since_day_before']
        ].to_json())

    map_data = json.dumps(df_json)

    # Assign Source
    return map_data

# Data source
map_source = GeoJSONDataSource(geojson=create_data(cov_total, gdf))

# Map Geometry
color_mapper = LinearColorMapper(palette=colorcet.bgy, low=0, high=100)

color_bar = ColorBar(color_mapper = color_mapper, location = (0,0))

# Map
TOOLS = "pan,wheel_zoom,reset,hover,save"

map_all = figure(
    width=725, 
    height=500,
    title="Total active cases by states",
    tools=TOOLS, x_axis_location=None, y_axis_location=None,
    tooltips = [
        ("state", "@state"),
        ("Cases", "@total_active_cases")
    ]
)

map_all.grid.grid_line_color = None
map_all.hover.point_policy = "follow_mouse"

# Create patches (of map)
map_all.patches(
    "xs", "ys", source=map_source,
    fill_color={
        "field": 'percentage',
        "transform": color_mapper
    },
    fill_alpha=0.7, line_color="black", line_width=0.5
)

map_all.add_layout(color_bar, 'below')

layout = map_all

curdoc().add_root(layout)
curdoc().title = "Covid-19 cases map"