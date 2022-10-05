from bs4 import BeautifulSoup
import pandas as pd

# HTML settings
URL = "tables.html"
TITLE_TAG = "h3"
TAB_TABLE = "List of Pages"
TAB_NAME_COLUMN = "DisplayName"
TAB_ID_COLUMN = "PageIndex"
VIS_TABLE_PREFIX = "Visuals in"
VIS_NAME_COLUMN = "Title"
VIS_REASON_COLUMN = "Visual Type"
VIS_ID_COLUNM = "VisualIndex"
LAST_TABLE = "List of all Columns/Fields/Measures/Expressions Used in Visuals"
LAST_TABLE_TABLE_COLUMN = "Table Name"
LAST_TABLE_VARIABLE_COLUMN = "Name"
LAST_TABLE_FORMULA_COLUMN = "Expression"

# Get data from the HMTL file
def extract_data():
    with open(URL,'r', encoding='utf-8') as file:
        data = {}
        html = file.read()
        segments = html.split(f'<{TITLE_TAG}>')
        index = None
        for index, s in enumerate(segments):
            if f'<div>{TAB_TABLE}:</div></{TITLE_TAG}>' in s:
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
            except AttributeError as ex:
                raise ValueError("No title found in this section") from ex
            except ValueError as ex:
                raise ValueError("No table found in this section") from ex

        col_index = data[TAB_TABLE][0].index(TAB_NAME_COLUMN)
        tabs = [v[col_index] for v in data[TAB_TABLE][1:]]
        return tabs, data
