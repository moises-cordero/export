from fpdf import FPDF


# PDF settings
ORIENTATION = "portrait"
FORMAT = "letter"
FONT_TYPE = "Arial"
FONT_SIZE = 12
ALIGN = "L"
WIDTH = 0 # Width
HEIGHT = 6 # Height

def create(data):
    # fields = {"description": "Name",
    #         "table": "Position",
    #         "variables": ""
    #         }

    # t = "Table #2"
    # t = data["Table #2"]
    # data_list = []
    # for n,row in enumerate(t["table"]):
    #     data_list[n] = {"name": ""
    #             }
    #     table1_id = row[t["columns"].index("id_table1")]


    pdf = FPDF()
    pdf.add_page(ORIENTATION, FORMAT)
    for _, tab in data.items():
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


if __name__ == '__main__':
    data = {
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
    create(data)