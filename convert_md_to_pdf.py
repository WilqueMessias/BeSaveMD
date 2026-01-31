import markdown
from xhtml2pdf import pisa
import sys
import argparse

# Custom CSS for the PDF
css = """
<style>
    @page {
        size: A4;
        margin: 1cm;
    }
    body {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.5;
        color: #333;
    }
    h1 {
        font-size: 24pt;
        color: #2c3e50;
        margin-bottom: 0.2cm;
        text-align: center;
    }
    h2 {
        font-size: 16pt;
        color: #2980b9;
        border-bottom: 2px solid #2980b9;
        padding-bottom: 5px;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    h3 {
        font-size: 13pt;
        color: #34495e;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    p {
        margin: 5px 0;
    }
    a {
        text-decoration: none;
        color: #2980b9;
    }
    ul {
        margin: 5px 0;
        padding-left: 20px;
    }
    li {
        margin-bottom: 3px;
    }
    .header {
        text-align: center;
        margin-bottom: 20px;
    }
    br {
        display: block;
        margin: 5px 0;
    }
    /* Center div support */
    div[align="center"] {
        text-align: center;
    }
</style>
"""

def convert_md_to_pdf(md_file, pdf_file):
    try:
        # Read Markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()

        # Convert Markdown to HTML
        html_content = markdown.markdown(text, extensions=['extra'])

        # Combine CSS and HTML
        full_html = f"<html><head><meta charset='utf-8'>{css}</head><body>{html_content}</body></html>"

        # Generate PDF
        with open(pdf_file, "wb") as f:
            pisa_status = pisa.CreatePDF(
                full_html, dest=f, encoding='utf-8'
            )

        if pisa_status.err:
            print(f"Error creating PDF: {pisa_status.err}")
            sys.exit(1)
        
        print(f"Successfully created: {pdf_file}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converte Markdown em PDF.")
    parser.add_argument("input_md", help="Arquivo .md de entrada")
    parser.add_argument("output_pdf", nargs="?", default=None, help="Arquivo .pdf de saída (opcional)")
    args = parser.parse_args()
    output_pdf = args.output_pdf or args.input_md.rsplit(".", 1)[0] + ".pdf"
    convert_md_to_pdf(args.input_md, output_pdf)
    print(f"Saída: {output_pdf}")
