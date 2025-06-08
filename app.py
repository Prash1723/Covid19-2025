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
gdf = gpd.read_file(borders) #[['ADMIN', 'ADM0_A3', 'geometry']]


print(gdf)
# Rename columns
#gdf.columns = ['country', 'country_code', 'geometry']

# - Functions

def create_data(attr, old, new):
    """Create and modify data for the bokeh map"""

    # Mask data to the required year value
    chosen_year = year_slider.value
    df1 = geo_df1[geo_df1['year']==str(chosen_year)].copy()
    df2 = gen_df1.query('country.isin(@continents)')[gen_df1['year']==str(chosen_year)].copy()

    # Read data to json
    df_json = json.loads(df1[['country', 'country_code', 'geometry', 'technology', 'unit', 'year', 'percentage']].to_json())

    map_data = json.dumps(df_json)

    # Assign Source
    map_source.geojson = map_data
    bar_sc.data = df2

# Total Active Cases chart
cov_total.plot(kind='barh', y="total_active_cases", x="state", width=0.9)
plt.xlabel('Total Active Cases')
plt.ylabel('State & UTs')
plt.show()