from bs4 import BeautifulSoup
from fpdf import FPDF
import pandas as pd
import spreadsheet

# HTML settings
URL = "tables.html"
TITLE_TAG = "h3"
TABS_TABLE = "List of Pages"
TABS_COLUMN = "DisplayName"

# PDF settings
ORIENTATION = "portrait"
FORMAT = "letter"
FONT_TYPE = "Arial"
FONT_SIZE = 12
ALIGN = "L"
WIDTH = 0 # Width
HEIGHT = 6 # Height

def extract_from_html():
    # Get data from the HMTL file
    html = open(URL,'r', encoding='utf-8').read()
    segments = html.split("<hr>")
    tables_dict = {}
    for s in segments[1:]:
        soup = BeautifulSoup(s, 'html.parser')
        try:
            title = soup.find(TITLE_TAG).find("div").text.strip()
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

    index = tables_dict[TABS_TABLE]["columns"].index(TABS_COLUMN)
    spreadsheet.update([v[index] for v in tables_dict[TABS_TABLE]["table"]])
    return tables_dict

def create_pdf(tables_dict):
    # fields = {"description": "Name",
    #         "table": "Position",
    #         "variables": ""
    #         }

    t = "Table #2"
    t = tables_dict["Table #2"]
    data = []
    for n,row in enumerate(t["table"]):
        data[n] = {"name": ""
                }
        table1_id = row[t["columns"].index("id_table1")]

    data_dict = {
        0: {
            "name": "Tab #1",
            "description": "This is the description of tab #2",
            "table": "Table of Tab #1",
            "variables": ["var1.1", "var1.2", "var1.3"],
            "graph": ""
        },
        1: {
            "name": "Tab #2",
            "description": "This is the description of tab #2",
            "table": "Table of Tab #2",
            "variables": ["var2.1", "var2.2", "var2.3"],
            "graph": ""
        },
    }

    pdf = FPDF()
    pdf.add_page(ORIENTATION, FORMAT)
    for _, tab in data_dict.items():
        for key, value in tab.items():
            if key=="name":
                pdf.set_font(FONT_TYPE, "B", size=FONT_SIZE+4)
                pdf.cell(WIDTH, HEIGHT, value, new_x="LMARGIN", new_y="NEXT", align=ALIGN)
                pdf.ln()
            else:
                if key=="variables":
                    value = ", ".join(value)
                pos = ("LMARGIN", "NEXT") if key in ["description", "graph"] else ("END", "LAST")
                pdf.set_font(FONT_TYPE, "B", size=FONT_SIZE)
                pdf.cell(WIDTH, HEIGHT, f'{key.capitalize()}: ', new_x=pos[0], new_y=pos[1], align=ALIGN)
                pdf.set_font(FONT_TYPE, size=FONT_SIZE)
                pdf.cell(WIDTH, HEIGHT, value, new_x="LMARGIN", new_y="NEXT", align=ALIGN)
            pdf.ln()
        pdf.cell(WIDTH, HEIGHT, "_"*50, new_x="LMARGIN", new_y="NEXT", align=ALIGN)
        pdf.ln()

    pdf.output("demo.pdf")

def main():
    tables_dict = extract_from_html()

if __name__ == '__main__':
    main()