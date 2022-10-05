from fpdf import FPDF


# PDF settings
FILE_NAME = "demo.pdf"
ORIENTATION = "portrait"
FORMAT = "letter"
FONT_TYPE = "Arial"
FONT_SIZE = 10
ALIGN = "L"
WIDTH = 0 # Width
HEIGHT = 6 # Height
TITLES = {
    'Table': 'Table / Report',
    'Variables': 'Variables(Columns)',
    'Universe': 'Universe used',
    'Reason': 'Visualization reason',
    'Data_source': 'Complete source description'
}

def get_data(raw_data):
    data = {}
    for row in raw_data:
        if row['tab'] not in data:
            data[row['tab']] = {}
            for key, value in row.items():
                if key == 'Variables':
                    data[row['tab']]['Variables'] = [row['Variables']]
                elif key not in ['Formula', 'tab']:
                    data[row['tab']][key] = value
        else:
            data[row['tab']]['Variables'].append(row['Variables'])
    for _, d in data.items():
        d['Variables'] = ", ".join(d['Variables'])
    return data

def create(data):
    data = get_data(data)
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
                pdf.cell(WIDTH, HEIGHT, f'{count} {value}', new_x="LMARGIN",
                         new_y="NEXT", align=ALIGN
                         )
            else:
                pos = ("LMARGIN", "NEXT") if key in ["Description", "Image", "Data_source"] \
                                          else ("END", "LAST")

                if key in TITLES:
                    pdf.set_font(FONT_TYPE, "B", size=FONT_SIZE)
                    pdf.cell(WIDTH, HEIGHT, f'{TITLES[key]}: ', new_x=pos[0],
                             new_y=pos[1], align=ALIGN
                             )

                pdf.set_font(FONT_TYPE, size=FONT_SIZE)
                pdf.cell(WIDTH, HEIGHT, value, new_x="LMARGIN", new_y="NEXT", align=ALIGN)

                pdf.ln()
        pdf.cell(WIDTH, HEIGHT, "_"*50, new_x="LMARGIN", new_y="NEXT", align=ALIGN)
        pdf.ln()
        count += 1

    pdf.output(FILE_NAME)
