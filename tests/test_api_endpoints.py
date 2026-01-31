import unittest
import io
import json
from werkzeug.datastructures import FileStorage
from app import app # Importa a instância da aplicação Flask

# Mocking das funções _md_to_pdf_bytes e _pdf_to_md_bytes para evitar dependências externas em testes unitários
# Em um cenário de integração real, você pode querer testar as funções reais,
# mas para testar apenas a API, o mock é suficiente.
from unittest.mock import patch

class ApiIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app._md_to_pdf_bytes')
    def test_api_convert_success(self, mock_md_to_pdf_bytes):
        mock_md_to_pdf_bytes.return_value = b"mocked pdf content"
        
        data = {
            'file': (io.BytesIO(b"# Test Markdown"), 'test.md')
        }
        response = self.app.post('/api/md-to-pdf/', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')
        self.assertIn('attachment; filename=test.pdf', response.headers['Content-Disposition'])
        self.assertEqual(response.data, b"mocked pdf content")

    def test_api_convert_no_file(self):
        response = self.app.post('/api/md-to-pdf/', content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"error": "No file part"})

    def test_api_convert_wrong_extension(self):
        data = {
            'file': (io.BytesIO(b"Some text"), 'test.txt')
        }
        response = self.app.post('/api/md-to-pdf/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"error": "Arquivo deve ser .md"})

    @patch('app._pdf_to_md_bytes')
    def test_api_convert_to_md_success(self, mock_pdf_to_md_bytes):
        mock_pdf_to_md_bytes.return_value = "mocked markdown content"
        
        # Criar um PDF de exemplo (bytes)
        pdf_content = b"%PDF-1.4\n..."
        data = {
            'file': (io.BytesIO(pdf_content), 'document.pdf')
        }
        response = self.app.post('/api/pdf-to-md/', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/markdown')
        self.assertIn('attachment; filename=document.md', response.headers['Content-Disposition'])
        self.assertEqual(response.data, b"mocked markdown content")

    def test_api_convert_to_md_no_file(self):
        response = self.app.post('/api/pdf-to-md/', content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"error": "No file part"})

    def test_api_convert_to_md_wrong_extension(self):
        data = {
            'file': (io.BytesIO(b"some image data"), 'image.jpg')
        }
        response = self.app.post('/api/pdf-to-md/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"error": "Arquivo deve ser .pdf"})

if __name__ == '__main__':
    unittest.main()
