from bs4 import BeautifulSoup
import requests
import pandas as pd

cases_url = 'https://www.covid19india.org/'
active_cl = 'has-fixed-layout'
h3_table2 = 'COVID-19 Active Cases State Wise 2025 Update Today'

response = requests.get(cases_url)
soup = BeautifulSoup(response.text, 'html.parser')

total_table = soup.find_all('table', attrs={'class': active_cl})
# active_table = soup.find('table', attrs={'class': active_cl})[1]

# Load data
cov_daily = pd.read_html(str(total_table), header=0)[0]
cov_active = pd.read_html(str(total_table), header=0)[1]

print(cov_active)