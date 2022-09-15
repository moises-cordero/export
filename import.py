import pandas as pd
from bs4 import BeautifulSoup

url = "tables.html"

soup = BeautifulSoup(open(url,'r').read(), 'html.parser')
for h3 in soup.find_all('h3'):
    title = h3.text.strip()
    pd_table = pd.read_html(str(h3.parent))[0]
    columns = list(pd_table.columns)
    table = pd_table.values.tolist()
