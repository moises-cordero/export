
from fpdf import FPDF

pdf = FPDF()

pdf.add_page("P", "letter")

font_type = "Arial"
font_size = 12
align = "L"
w = 0 # Width
h = 6 # Height

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

for _, tab in data_dict.items():
    for key, value in tab.items():
        if key=="name":
            pdf.set_font(font_type, "B", size=font_size+4)
            pdf.cell(w, h, value, new_x="LMARGIN", new_y="NEXT", align=align)
            pdf.ln()
        else:
            if key=="variables":
                value = ", ".join(value)
            pos = ("LMARGIN", "NEXT") if key in ["description", "graph"] else ("END", "LAST")
            pdf.set_font(font_type, "B", size=font_size)
            pdf.cell(w, h, f'{key.capitalize()}: ', new_x=pos[0], new_y=pos[1], align=align)
            pdf.set_font(font_type, size=font_size)
            pdf.cell(w, h, value, new_x="LMARGIN", new_y="NEXT", align=align)
        pdf.ln()
    pdf.cell(w, h, "_"*50, new_x="LMARGIN", new_y="NEXT", align=align)
    pdf.ln()

pdf.output("demo.pdf")
