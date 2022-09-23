import pandas as pd
from bs4 import BeautifulSoup

url = "tables.html"
title_tag = "<h3>"

html = open(url,'r').read()
segments = html.split(title_tag)
tables_dict = {}
for s in segments[2:]:
    soup = BeautifulSoup(s, 'html.parser')
    title = soup.find("div").text.strip()
    pd_table = pd.read_html(s)[0]
    table = pd_table.values.tolist()
    columns = list(pd_table.columns)
    tables_dict[title] = {"table": table,
                          "columns": columns,
                    }

print(tables_dict)