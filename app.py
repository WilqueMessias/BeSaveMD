print("--- STARTING APP ---")
from flask import Flask, render_template, request, send_file, jsonify
import io
import os
import re
import tempfile
import markdown
from xhtml2pdf import pisa
import fitz  # PyMuPDF

app = Flask(__name__)

# --- API-first: lógica de conversão reutilizada por web, Android e iOS ---

ALLOWED_EXT_MD = {".md"}
ALLOWED_EXT_PDF = {".pdf"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Custom CSS for the PDF (Same as before)
CSS_STYLE = """
<style>
    @page {
        size: A4;
        margin: 1.5cm;
    }
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 10pt;
        line-height: 1.6;
        color: #1a1a1a;
    }
    h1 {
        font-size: 28pt;
        font-weight: bold;
        color: #000;
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    h2 {
        font-size: 14pt;
        color: #000;
        border-bottom: 1px solid #ddd;
        padding-bottom: 4px;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    h3 {
        font-size: 11pt;
        color: #333;
        margin-top: 12px;
        margin-bottom: 4px;
        font-weight: bold;
    }
    .about-section {
        background-color: #f9f9f9;
        padding: 10px 15px;
        border-left: 4px solid #333;
        margin-bottom: 20px;
        font-style: italic;
    }
    p {
        margin: 6px 0;
    }
    a {
        text-decoration: none;
        color: #000;
        border-bottom: 1px solid #ccc;
    }
    ul {
        margin: 5px 0;
        padding-left: 20px;
    }
    li {
        margin-bottom: 4px;
    }
    img {
        height: 14px;
        vertical-align: middle;
    }
    div[align="center"] {
        text-align: center;
        margin-bottom: 30px;
    }
</style>
"""

TECH_COLORS = {
    "python": "3776AB", "javascript": "F7DF1E", "typescript": "3178C6",
    "django": "092E20", "flask": "000000", "react": "61DAFB",
    "sql": "4479A1", "postgresql": "4169E1", "sqlite": "003B57",
    "docker": "2496ED", "node.js": "339933", "git": "F05032",
    "github": "181717", "gitlab": "FC6D26"
}

def tech_badge_preprocessor(text):
    """Heuristic: Find technology keywords and replace with badges if they belong to a skill list."""
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        # If line looks like a tech category (starts with - **Category**)
        if re.match(r'^\s*-\s+\*\*(.+)\*\*:', line):
            header, content = line.split(':', 1)
            techs = [t.strip() for t in content.replace(',', ' ').split()]
            badges = []
            for t in techs:
                clean_t = t.lower().strip('.,')
                if clean_t in TECH_COLORS:
                    color = TECH_COLORS[clean_t]
                    badges.append(f'![{t}](https://img.shields.io/badge/{t}-{color}?style=flat-square&logo={clean_t}&logoColor=white)')
                else:
                    badges.append(f'`{t}`')
            processed_lines.append(f"{header}: {' '.join(badges)}")
        else:
            processed_lines.append(line)
            
    return '\n'.join(processed_lines)


def _md_to_pdf_bytes(md_content: str, source_filename: str) -> bytes:
    """Converte Markdown em bytes de PDF. Usado por web e API."""
    text = tech_badge_preprocessor(md_content)
    html_content = markdown.markdown(text, extensions=['extra', 'codehilite'])
    html_content = re.sub(
        r'<(h[12])>(.*?(?:About Me|Sobre M[íi]).*?)</\1>',
        r'<div class="about-section"><\1>\2</\1>',
        html_content,
        flags=re.IGNORECASE
    )
    html_content = html_content.replace('<h2>', '</div><h2>')
    if html_content.startswith('</div>'):
        html_content = html_content[6:]
    full_html = f"<html><head><meta charset='utf-8'>{CSS_STYLE}</head><body>{html_content}</body></html>"
    pdf_io = io.BytesIO()
    pisa_status = pisa.CreatePDF(full_html, dest=pdf_io, encoding='utf-8')
    if pisa_status.err:
        raise RuntimeError(f"Erro ao gerar PDF: {pisa_status.err}")
    return pdf_io.getvalue()


def _pdf_to_md_bytes(pdf_bytes: bytes, source_filename: str) -> str:
    """Converte bytes de PDF em Markdown. Usado por web e API."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    try:
        from pdf_engine import PDFReconstructor
        converter = PDFReconstructor(tmp_path)
        return converter.convert()
    finally:
        os.unlink(tmp_path)


def _validate_ext(filename: str, allowed: set) -> bool:
    ext = os.path.splitext(filename or "")[1].lower()
    return ext in allowed


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if not file or file.filename == '':
        return 'No selected file', 400
    if not _validate_ext(file.filename, ALLOWED_EXT_MD):
        return 'Arquivo deve ser .md', 400
    try:
        text = file.read().decode('utf-8')
        pdf_bytes = _md_to_pdf_bytes(text, file.filename)
        out_name = f"{os.path.splitext(file.filename)[0]}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=out_name,
            mimetype='application/pdf'
        )
    except Exception as e:
        return str(e), 500

@app.route('/convert-to-md', methods=['POST'])
def convert_to_md():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if not file or file.filename == '':
        return 'No selected file', 400
    if not _validate_ext(file.filename, ALLOWED_EXT_PDF):
        return 'Arquivo deve ser .pdf', 400
    try:
        pdf_bytes = file.read()
        md_content = _pdf_to_md_bytes(pdf_bytes, file.filename)
        out_name = f"{os.path.splitext(file.filename)[0]}.md"
        return send_file(
            io.BytesIO(md_content.encode('utf-8')),
            as_attachment=True,
            download_name=out_name,
            mimetype='text/markdown'
        )
    except Exception as e:
        return str(e), 500


# --- API: mesmo contrato para web, Android e iOS ---

@app.route('/api/convert', methods=['POST'])
def api_convert():
    """POST multipart 'file' (.md) → 200 + PDF binary ou 4xx/5xx + JSON {error}."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not _validate_ext(file.filename, ALLOWED_EXT_MD):
        return jsonify({"error": "Arquivo deve ser .md"}), 400
    try:
        text = file.read().decode('utf-8')
        pdf_bytes = _md_to_pdf_bytes(text, file.filename)
        out_name = f"{os.path.splitext(file.filename)[0]}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=out_name,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/convert-to-md', methods=['POST'])
def api_convert_to_md():
    """POST multipart 'file' (.pdf) → 200 + MD binary ou 4xx/5xx + JSON {error}."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not _validate_ext(file.filename, ALLOWED_EXT_PDF):
        return jsonify({"error": "Arquivo deve ser .pdf"}), 400
    try:
        pdf_bytes = file.read()
        md_content = _pdf_to_md_bytes(pdf_bytes, file.filename)
        out_name = f"{os.path.splitext(file.filename)[0]}.md"
        return send_file(
            io.BytesIO(md_content.encode('utf-8')),
            as_attachment=True,
            download_name=out_name,
            mimetype='text/markdown'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5050)
