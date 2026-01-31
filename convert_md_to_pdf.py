import markdown
from xhtml2pdf import pisa
import sys
import argparse
from src.utils.pdf_styles import CSS_STYLE

def convert_md_to_pdf(md_file, pdf_file):
    try:
        # Read Markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()

        # Convert Markdown to HTML
        html_content = markdown.markdown(text, extensions=['extra'])

        # Combine CSS and HTML
        full_html = f"<html><head><meta charset='utf-8'>{CSS_STYLE}</head><body>{html_content}</body></html>"

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
