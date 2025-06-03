from bs4 import BeautifulSoup
import requests
import pandas as pd

cases_url = 'https://www.covid19india.org/'
active_cl = 'has-fixed-layout'
h3_table2 = 'COVID-19 Active Cases State Wise 2025 Update Today'

response = requests.get(cases_url)
soup = BeautifulSoup(response.text, 'html.parser')

tables = soup.find_all('table', attrs={'class': active_cl})

# Load data
cov_total = pd.read_html(str(tables), header=0)[0]
cov_active = pd.read_html(str(tables), header=0)[1]

cov_total.to_csv('data/total_data.csv', index=False)

cov_active.to_csv('data/daily_data.csv', index=False)