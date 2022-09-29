from fpdf import FPDF


# PDF settings
ORIENTATION = "portrait"
FORMAT = "letter"
FONT_TYPE = "Arial"
FONT_SIZE = 10
ALIGN = "L"
WIDTH = 0 # Width
HEIGHT = 6 # Height
TITLES = {
    'Table': 'Table/Report',
    'Variables': 'Variables(Columns)',
    'Universe': 'Universe used',
    'Reason': 'Visualization reason',
    'Data_source': 'Complete source description'
}

def create(data):
    pdf = FPDF()
    pdf.add_page(ORIENTATION, FORMAT)
    pdf.set_font(FONT_TYPE, "B", size=FONT_SIZE+6)
    pdf.cell(WIDTH, HEIGHT, "FRONTERS DASHBOARDS", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln()
    pdf.ln()
    count = 1
    for title, tab in data.items():
        pdf.set_font(FONT_TYPE, "B", size=FONT_SIZE+4)
        pdf.cell(WIDTH, HEIGHT, title.upper(), new_x="LMARGIN", new_y="NEXT", align=ALIGN)
        pdf.ln()
        for key, value in tab.items():
            if key == 'Vis':
                pdf.set_font(FONT_TYPE, "B", size=FONT_SIZE)
                pdf.cell(WIDTH, HEIGHT, f'{count} {value}', new_x="LMARGIN", new_y="NEXT", align=ALIGN)
            else:
                pos = ("LMARGIN", "NEXT") if key in ["Description", "Image"] else ("END", "LAST")

                if key in TITLES:
                    pdf.set_font(FONT_TYPE, "B", size=FONT_SIZE)
                    pdf.cell(WIDTH, HEIGHT, f'{TITLES[key]}: ', new_x=pos[0], new_y=pos[1], align=ALIGN)

                pdf.set_font(FONT_TYPE, size=FONT_SIZE)
                pdf.cell(WIDTH, HEIGHT, value, new_x="LMARGIN", new_y="NEXT", align=ALIGN)

                pdf.ln()
        pdf.cell(WIDTH, HEIGHT, "_"*50, new_x="LMARGIN", new_y="NEXT", align=ALIGN)
        pdf.ln()
        count += 1

    pdf.output("demo.pdf")
