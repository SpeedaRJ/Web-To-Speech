import textwrap

from fpdf import FPDF

PDF_HOME = "./pdf"


class PDFWriter:

    def __init__(self) -> None:
        self.a4_width_mm = 210
        self.pt_to_mm = 0.35
        self.fontsize_title_pt = 16
        self.fontsize_body_pt = 12
        self.margin_bottom_mm = 10
        self.character_width_mm = 7 * self.pt_to_mm
        self.width_text = self.a4_width_mm / self.character_width_mm
        self.pdf = FPDF(orientation='P', unit='mm', format='A4')
        self.pdf.set_font(family='Courier')
        self.pdf.set_auto_page_break(True, margin=self.margin_bottom_mm)
        self.filename = ""

    def add_page(self, title: str, content: str) -> None:
        self.pdf.add_page()
        self.pdf.set_font(family='Courier',
                          size=self.fontsize_title_pt, style='B')
        self.pdf.cell(200, self.fontsize_title_pt, txt=title, ln=1, align='C')
        self.pdf.set_font(family='Courier',
                          size=self.fontsize_body_pt, style='')
        content_split = textwrap.wrap(content, width=int(
            self.width_text - self.width_text * 0.2))
        for line in content_split:
            if len(line) == 0:
                self.pdf.ln()
            else:
                self.pdf.cell(200, self.fontsize_body_pt,
                              line, ln=2, align='C')

    def save(self, path: str = '') -> str:
        self.pdf.output(f"{path if path else PDF_HOME}\\{self.filename}.pdf")
        return self.filename

    def create_filename(self, title: str) -> str:
        self.filename = f"{title.replace(' ', '_').lower()}"
        return self.filename
