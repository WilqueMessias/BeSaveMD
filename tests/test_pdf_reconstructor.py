import unittest
from unittest.mock import MagicMock, patch
import fitz # Importe fitz para poder fazer o patch corretamente
from src.services.pdf_engine import PDFReconstructor

class TestPDFReconstructor(unittest.TestCase):

    def setUp(self):
        # Mock para fitz.open e seus métodos
        self.mock_doc = MagicMock()
        self.mock_page = MagicMock()
        self.mock_doc.return_value.__enter__.return_value = self.mock_doc  # Para uso com 'with'
        self.mock_doc.__iter__.return_value = [self.mock_page]
        self.mock_doc.__len__.return_value = 1
        self.mock_doc.close = MagicMock()
        
        # Configuração padrão para page.get_text("dict")
        self.mock_page.get_text.return_value = {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {"size": 12, "font": "Helvetica", "text": "Normal text."},
                                {"size": 12, "font": "Helvetica-Bold", "text": "Bold text."}, # Exemplo de negrito
                            ]
                        }
                    ]
                }
            ]
        }

    @patch('fitz.open')
    def test_analyze_fonts(self, mock_fitz_open):
        mock_fitz_open.return_value = self.mock_doc
        
        # Cenário 1: Várias fontes, identificar a do corpo do texto
        self.mock_page.get_text.return_value = {
            "blocks": [
                {"lines": [{"spans": [{"size": 24, "font": "A", "text": "Header"}]}]},
                {"lines": [{"spans": [{"size": 12, "font": "B", "text": "Body text line 1"}]}]},
                {"lines": [{"spans": [{"size": 12, "font": "C", "text": "Body text line 2 long long"}]}]},
                {"lines": [{"spans": [{"size": 18, "font": "D", "text": "Subheader"}]}]},
            ]
        }

        reconstructor = PDFReconstructor("dummy.pdf")
        reconstructor.analyze_fonts()
        self.assertEqual(reconstructor.body_font_size, 12)
        self.assertEqual(reconstructor.font_counts[12], 26) # 16 + 10
        self.assertEqual(reconstructor.font_counts[24], 6)

    def test_is_header(self):
        reconstructor = PDFReconstructor("dummy.pdf")
        reconstructor.body_font_size = 12 # Mock body font size

        self.assertTrue(reconstructor.is_header(15)) # 15 > 12 * 1.1 = 13.2
        self.assertFalse(reconstructor.is_header(13)) # 13 < 13.2
        self.assertFalse(reconstructor.is_header(12))

    def test_get_header_level(self):
        reconstructor = PDFReconstructor("dummy.pdf")
        reconstructor.body_font_size = 12 # Mock body font size

        self.assertEqual(reconstructor.get_header_level(24), 1) # 24/12 = 2.0 > 1.8
        self.assertEqual(reconstructor.get_header_level(18), 2) # 18/12 = 1.5 > 1.4
        self.assertEqual(reconstructor.get_header_level(14), 3) # 14/12 = 1.16 > 1.1
        self.assertEqual(reconstructor.get_header_level(12), 0)

    def test_process_span(self):
        reconstructor = PDFReconstructor("dummy.pdf") # Instância dummy

        self.assertEqual(reconstructor.process_span({"text": "hello", "font": "Helvetica"}), "hello")
        self.assertEqual(reconstructor.process_span({"text": "world", "font": "Helvetica-Bold"}), "**world**")
        self.assertEqual(reconstructor.process_span({"text": "italic", "font": "Helvetica-Oblique"}), "*italic*")
        self.assertEqual(reconstructor.process_span({"text": "bolditalic", "font": "Helvetica-BoldOblique"}), "***bolditalic***")
        self.assertEqual(reconstructor.process_span({"text": " ", "font": "Helvetica"}), "") # Espaço em branco

    @patch('fitz.open')
    def test_merge_text_blocks(self, mock_fitz_open):
        mock_fitz_open.return_value = self.mock_doc
        reconstructor = PDFReconstructor("dummy.pdf")

        # Cenário 1: Blocos próximos que devem ser mesclados
        blocks_to_merge = [
            {"lines": [{"spans": [{"text": "First line."}]}], "bbox": (0, 0, 100, 10)},
            {"lines": [{"spans": [{"text": "Second line."}]}], "bbox": (0, 11, 100, 21)}, # vert_dist = 1, x_diff = 0
        ]
        merged = reconstructor._merge_text_blocks(blocks_to_merge)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["lines"][0]["spans"][0]["text"], "First line.")
        self.assertEqual(merged[0]["lines"][1]["spans"][0]["text"], "Second line.")

        # Cenário 2: Blocos distantes que não devem ser mesclados
        blocks_no_merge = [
            {"lines": [{"spans": [{"text": "First line."}]}], "bbox": (0, 0, 100, 10)},
            {"lines": [{"spans": [{"text": "Second line."}]}], "bbox": (0, 30, 100, 40)}, # vert_dist = 20
        ]
        merged = reconstructor._merge_text_blocks(blocks_no_merge)
        self.assertEqual(len(merged), 2)

    @patch('fitz.open')
    def test_format_block_to_markdown_headers(self, mock_fitz_open):
        mock_fitz_open.return_value = self.mock_doc
        reconstructor = PDFReconstructor("dummy.pdf")
        reconstructor.body_font_size = 12

        # H1
        block_h1 = {"lines": [{"spans": [{"size": 24, "font": "A", "text": "Título Principal"}]}]}
        self.assertEqual(reconstructor._format_block_to_markdown(block_h1), "# Título Principal\n")

        # H2
        block_h2 = {"lines": [{"spans": [{"size": 18, "font": "B", "text": "Subtítulo"}]}]}
        self.assertEqual(reconstructor._format_block_to_markdown(block_h2), "## Subtítulo\n")

        # Texto normal (não cabeçalho)
        block_normal = {"lines": [{"spans": [{"size": 12, "font": "C", "text": "Parágrafo normal."}]}]}
        self.assertEqual(reconstructor._format_block_to_markdown(block_normal), "Parágrafo normal.\n")

    @patch('fitz.open')
    def test_format_block_to_markdown_lists(self, mock_fitz_open):
        mock_fitz_open.return_value = self.mock_doc
        reconstructor = PDFReconstructor("dummy.pdf")
        reconstructor.body_font_size = 12

        # Lista com bullet
        block_list_bullet = {"lines": [{"spans": [{"size": 12, "font": "A", "text": "- Item 1"}]}]}
        self.assertEqual(reconstructor._format_block_to_markdown(block_list_bullet), "- Item 1\n")

        # Lista numerada
        block_list_numbered = {"lines": [{"spans": [{"size": 12, "font": "B", "text": "1. Item A"}]}]}
        self.assertEqual(reconstructor._format_block_to_markdown(block_list_numbered), "1. Item A\n")
        
    @patch('fitz.open')
    def test_detect_columns(self, mock_fitz_open):
        mock_fitz_open.return_value = self.mock_doc
        reconstructor = PDFReconstructor("dummy.pdf")
        
        # Cenário 1: Sem colunas claras (todos os blocos numa faixa X similar)
        blocks_single_column = [
            {"lines": [], "bbox": (10, 10, 100, 20)},
            {"lines": [], "bbox": (12, 30, 102, 40)},
            {"lines": [], "bbox": (15, 50, 105, 60)},
        ]
        columns = reconstructor._detect_columns(blocks_single_column)
        self.assertEqual(len(columns), 1)
        self.assertEqual(len(columns[0]), 3)

        # Cenário 2: Duas colunas claras
        blocks_two_columns = [
            {"lines": [], "bbox": (10, 10, 100, 20)}, # Coluna 1
            {"lines": [], "bbox": (200, 10, 300, 20)}, # Coluna 2
            {"lines": [], "bbox": (15, 30, 105, 40)}, # Coluna 1
            {"lines": [], "bbox": (205, 30, 305, 40)}, # Coluna 2
        ]
        columns = reconstructor._detect_columns(blocks_two_columns)
        self.assertEqual(len(columns), 2) # Pode variar dependendo da heurística e ordenação
        
        # Verificar que os blocos da primeira coluna estão agrupados, e os da segunda também
        # A ordem das colunas pode não ser garantida, mas o agrupamento sim.
        # Como a heurística é simples (agrupa por x_ref), vou verificar o número de blocos em cada "coluna" detectada.
        col_lengths = sorted([len(c) for c in columns])
        self.assertEqual(col_lengths, [2, 2]) # Duas colunas com 2 blocos cada

if __name__ == '__main__':
    unittest.main()
