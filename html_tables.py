from bs4 import BeautifulSoup
import pandas as pd

# HTML settings
URL = "tables.html"
TITLE_TAG = "h3"
TABS_TABLE = "List of Pages"
TABS_COLUMN = "DisplayName"
LAST_TABLE = "List of all Columns/Fields/Measures/Expressions Used in Visuals"
VIS_PREFIX = "Visuals in"
VIS_NAME_COLUMN = "Visual Type"

# Get data from the HMTL file
def extract_data():
    data = {}
    html = open(URL,'r', encoding='utf-8').read()
    segments = html.split(f'<{TITLE_TAG}>')
    index = None
    for index, s in enumerate(segments):
        if f'<div>{TABS_TABLE}:</div></{TITLE_TAG}>' in s:
            break
    for s in segments[index:]:
        soup = BeautifulSoup(f'<{TITLE_TAG}>'+s, 'html.parser')
        try:
            title = soup.find(TITLE_TAG).find("div").text.strip().replace(":","")
            pd_table = pd.read_html(s)[0]
            table = pd_table.values.tolist()
            data[title] = table
            if title == LAST_TABLE:
                break
        except AttributeError as e:
            raise ValueError("No title found in this section") from e
        except ValueError as e:
            raise ValueError("No table found in this section") from e

    col_index = data[TABS_TABLE][0].index(TABS_COLUMN)
    tabs = [v[col_index] for v in data[TABS_TABLE][1:]]
    return tabs, data
