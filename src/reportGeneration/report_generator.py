from fpdf import FPDF
from fpdf.fonts import FontFace
import polars as pl
from PIL import Image

class PricingReport(FPDF):
    def header(self):
        #Logo
        self.image('assets/vijay_brand.jpg',175,5,25)
        self.set_font("Helvetica","B", 18)
        self.set_x(90)
        self.cell(30,10,'Vijay Ecommerce Pricing Report', 0,align='C')
        self.set_y(45)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0,10, 'Page' + str(self.page_no())+'/{nb}',0,align='C')

    def insert_table(self,df:pl.dataframe):
        platform = df["platform"].min()
        data = df.to_numpy()
        self.set_font('Helvetica', '', 7)
        colors = {
            "zepto":{"text":(247,53,99),
                     "bg":(57,0,103)},
            "instamart":{"text":(247,247,247),
                         "bg":(247,79,0)},
            "blinkit":{"text":(47,130,21),
                       "bg":(240,197,68)}
        }
        col_widths=(6,10,9,13,20,5,5,5,5,5)
        text_align = ("Left","Left","Left","Left","Left",
                      "Center","Center","Center","Center","Center")
        headings_style= FontFace(emphasis="BOLD",
                                 color=colors[platform]["text"],
                                 fill_color=colors[platform]["bg"])
        with self.table(col_widths=col_widths,
                        text_align=text_align,
                        headings_style=headings_style) as table:
            row = table.row()
            for col in df.columns:
                row.cell(col)
            for data_row in data:
                row = table.row()
                for datum in data_row:
                    row.cell(str(datum))


def split_tables_report(data:pl.dataframe)->pl.dataframe:
    dataframes = data.select(["platform",
                   "timestamp",
                   "search_term",
                   "brand",
                   "product_name",
                   "mrp",
                   "price",
                   "unit",
                   "ppu",
                   "discount_pct"]).partition_by(["platform","search_term"])
    for frame in dataframes:
        yield frame

def create_report(frames:list[pl.dataframe]):
    pdf = PricingReport()
    bg_image = Image.open("./assets/report_bg.jpg")
    pdf.set_page_background(bg_image)
    pdf.set_auto_page_break(auto=True)
    pdf.set_margin(15)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Helvetica', '', 12)
    for frame in frames:
        pdf.insert_table(frame)
        pdf.ln()
        pdf.ln()


    pdf.output('demo_files/test.pdf')

