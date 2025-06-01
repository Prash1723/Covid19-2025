from bs4 import BeautifulSoup
import requests
import pandas as pd

cases_url = 'https://www.covid19india.org/'
active_cl = 'has-fixed-layout'

response = requests.get(cases_url)
soup = BeautifulSoup(response.text, 'html.parser')

active_table = soup.find('table', attrs={'class': active_cl})

# Load data
cov = pd.read_html(str(active_table), header=0)[0]

print(cov)
