import markdown
from xhtml2pdf import pisa
import io
import re

def strip_emojis(text):
    return text.encode('ascii', 'ignore').decode('ascii')

def test_conversion():
    try:
        with open('EN_Wilque_Messias_de_Lima.md', 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"File length: {len(text)}")
        
        # Strip some problematic chars for xhtml2pdf if needed
        text = strip_emojis(text)
        
        html = markdown.markdown(text, extensions=['extra', 'codehilite'])
        full_html = f"<html><head><meta charset='utf-8'></head><body>{html}</body></html>"
        
        print("Starting PDF generation...")
        pdf_io = io.BytesIO()
        pisa_status = pisa.CreatePDF(full_html, dest=pdf_io, encoding='utf-8')
        
        if pisa_status.err:
            print(f"Error during conversion: {pisa_status.err}")
        else:
            print("Conversion successful!")
            with open('test_output.pdf', 'wb') as f:
                f.write(pdf_io.getvalue())
            print("Output saved to test_output.pdf")
            
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_conversion()
