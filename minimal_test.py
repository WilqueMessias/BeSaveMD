from xhtml2pdf import pisa
import io

def test():
    html = "<html><body><h1>Test</h1><p>Hello World</p></body></html>"
    pdf_io = io.BytesIO()
    print("Starting...")
    pisa_status = pisa.CreatePDF(html, dest=pdf_io)
    print("Finished:", pisa_status.err)

if __name__ == "__main__":
    test()
