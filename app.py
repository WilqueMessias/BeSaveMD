print("-- - STARTING APP ---")
from flask import Flask, render_template, request, send_file, jsonify
import io
import os
import re
import tempfile
import markdown
from xhtml2pdf import pisa
import fitz  # PyMuPDF
from src.utils.pdf_styles import CSS_STYLE
from flask_restx import Api, Namespace, Resource, reqparse, fields
from src.utils.badge_preprocessor import TECH_COLORS, tech_badge_preprocessor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- API-first: lógica de conversão reutilizada por web, Android e iOS ---

ALLOWED_EXT_MD = {".md"}
ALLOWED_EXT_PDF = {".pdf"}
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))  # 10 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

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
        from src.services.pdf_engine import PDFReconstructor
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
api = Api(app, 
          version='1.0', 
          title='Conversor MD/PDF API', 
          description='API para converter arquivos Markdown para PDF e vice-versa',
          doc='/api/docs'
)

# Modelo para respostas de erro
api_error_model = api.model('Error', {'error': fields.String(description='Mensagem de erro')})

md_pdf_ns = Namespace('md-to-pdf', description='Conversão de Markdown para PDF')
pdf_md_ns = Namespace('pdf-to-md', description='Conversão de PDF para Markdown')

api.add_namespace(md_pdf_ns)
api.add_namespace(pdf_md_ns)

# Parser para upload de arquivo Markdown
md_upload_parser = reqparse.RequestParser()
md_upload_parser.add_argument('file', 
                             type='FileStorage', 
                             location='files', 
                             required=True, 
                             help='Arquivo Markdown (.md) para conversão')

# Parser para upload de arquivo PDF
pdf_upload_parser = reqparse.RequestParser()
pdf_upload_parser.add_argument('file', 
                              type='FileStorage', 
                              location='files', 
                              required=True, 
                              help='Arquivo PDF (.pdf) para conversão')


@md_pdf_ns.route('/')
class MdToPdfConverter(Resource):
    @md_pdf_ns.doc(description='Converte um arquivo Markdown para PDF.')
    @md_pdf_ns.expect(md_upload_parser)
    @md_pdf_ns.produces(['application/pdf', 'application/json'])
    @md_pdf_ns.response(200, 'Sucesso', headers={'Content-Disposition': 'attachment; filename=*.pdf'})
    @md_pdf_ns.response(400, 'Requisição inválida', model=api_error_model)
    @md_pdf_ns.response(500, 'Erro interno do servidor', model=api_error_model)
    def post(self):
        """Converte um arquivo Markdown (.md) para PDF."""
        args = md_upload_parser.parse_args()
        file = args['file']
        
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


@pdf_md_ns.route('/')
class PdfToMdConverter(Resource):
    @pdf_md_ns.doc(description='Converte um arquivo PDF para Markdown.')
    @pdf_md_ns.expect(pdf_upload_parser)
    @pdf_md_ns.produces(['text/markdown', 'application/json'])
    @pdf_md_ns.response(200, 'Sucesso', headers={'Content-Disposition': 'attachment; filename=*.md'})
    @pdf_md_ns.response(400, 'Requisição inválida', model=api_error_model)
    @pdf_md_ns.response(500, 'Erro interno do servidor', model=api_error_model)
    def post(self):
        """Converte um arquivo PDF (.pdf) para Markdown."""
        args = pdf_upload_parser.parse_args()
        file = args['file']

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
