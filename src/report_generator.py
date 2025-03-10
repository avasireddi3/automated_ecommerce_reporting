from fpdf import FPDF

class PricingReport(FPDF):
    def header(self):
        #Logo
        self.image('assets/vijay_brand.jpg',175,5,25)
        self.set_font("Helvetica","B", 15)
        self.set_x(90)
        self.cell(30,10,'Vijay Ecommerce Pricing Report', 0,align='C')

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0,10, 'Page' + str(self.page_no())+'/{nb}',0,align='C')

pdf = PricingReport()
pdf.set_auto_page_break(auto=True)
pdf.set_margin(15)
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_font('Helvetica', '', 12)
pdf.set_y(20)
page_no = pdf.get_page_label()
for i in range(1, 41):
    print(i,pdf.get_page_label())
    if pdf.get_page_label()!=page_no:
        pdf.set_y(40)
        page_no = pdf.get_page_label()
    pdf.cell(0, 10, 'Printing line number ' + str(i), 0)
    pdf.ln()

pdf.output('test.pdf')

