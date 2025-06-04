from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt
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
cov_active = pd.read_html(str(tables), header=0)[1]

# Rename Columns
cov_total.columns = ["s.no", "state", "total_active_cases", "new_cases_since_day_before"]

# Save Data
cov_total.to_csv('data/total_data.csv', index=False)
cov_active.to_csv('data/daily_data.csv', index=False)

cov_total.plot(kind='barh', y="total_active_cases", x="state", width=0.9)
plt.xlabel('Total Active Cases')
plt.ylabel('State & UTs')
plt.show()