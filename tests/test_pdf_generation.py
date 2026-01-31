import unittest
import io
from xhtml2pdf import pisa
from src.utils.pdf_styles import CSS_STYLE

class TestPdfGeneration(unittest.TestCase):

    def test_basic_pdf_creation(self):
        html_content = "<h1>Test</h1><p>Hello World</p>"
        full_html = f"<html><head><meta charset='utf-8'>{CSS_STYLE}</head><body>{html_content}</body></html>"
        
        pdf_io = io.BytesIO()
        pisa_status = pisa.CreatePDF(full_html, dest=pdf_io)
        
        self.assertFalse(pisa_status.err, f"Erro ao gerar PDF: {pisa_status.err}")
        self.assertGreater(pdf_io.tell(), 0, "O PDF gerado está vazio.")

if __name__ == "__main__":
    unittest.main()
