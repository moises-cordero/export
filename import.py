import pandas as pd
from bs4 import BeautifulSoup

url = "tables.html"
title_tag = "h3"

html = open(url,'r').read()
segments = html.split("<hr>")
tables_dict = {}
for s in segments[1:]:
    soup = BeautifulSoup(s, 'html.parser')
    try:
        title = soup.find(title_tag).find("div").text.strip()
        pd_table = pd.read_html(s)[0]
        table = pd_table.values.tolist()
        columns = list(pd_table.columns)
        tables_dict[title] = {"table": table,
                              "columns": columns,
                        }
    except AttributeError as e:
        raise ValueError("No title found in this section") from e
    except ValueError as e:
        raise ValueError("No table found in this section") from e
print(tables_dict)
print()
