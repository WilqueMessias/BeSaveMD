import fitz
from collections import Counter
import re

class PDFReconstructor:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.font_counts = Counter()
        self.body_font_size = 0
        self.body_font_name = ""

    def analyze_fonts(self):
        """Pass 1: Collect font statistics to identify body text."""
        for page in self.doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Round size to avoid floating point noise (e.g., 10.999 -> 11)
                        size = round(span["size"])
                        self.font_counts[size] += len(span["text"].strip())
        
        # The most common font size by character count is likely the body text
        if self.font_counts:
            self.body_font_size = self.font_counts.most_common(1)[0][0]
        
    def is_header(self, size):
        """Determine if a font size represents a header."""
        # Simple heuristic: significantly larger than body text
        return size > self.body_font_size * 1.1

    def get_header_level(self, size):
        """Map font size to H1, H2, H3..."""
        ratio = size / self.body_font_size
        if ratio > 1.8: return 1
        if ratio > 1.4: return 2
        if ratio > 1.1: return 3
        return 0

    def process_span(self, span):
        """Process text styling within a span."""
        text = span["text"]
        font = span["font"].lower()
        
        if not text.strip():
            return ""

        # Detect Bold/Italic
        is_bold = "bold" in font or "black" in font
        is_italic = "italic" in font or "oblique" in font
        
        if is_bold and is_italic:
            text = f"***{text}***"
        elif is_bold:
            text = f"**{text}**"
        elif is_italic:
            text = f"*{text}*"
            
        return text

    def convert(self):
        """Main conversion loop."""
        try:
            self.analyze_fonts()
            markdown_output = []
            
            for page_num, page in enumerate(self.doc):
                markdown_output.append(self._process_page(page, page_num == 0))
                
            return "\n".join(markdown_output)
        finally:
            self.doc.close()

    def _process_page(self, page, is_first_page):
        """Process a single page to extract markdown."""
        page_markdown_output = []
        blocks = page.get_text("dict")["blocks"]
        
        # Sort blocks by Y then X to handle reading order better
        blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))

        # Separar cabeçalhos dos blocos de conteúdo
        header_blocks = []
        content_blocks = []
        for block in blocks:
            # Assumimos que o primeiro span de cada linha pode representar o tamanho da fonte do bloco
            if "lines" in block and block["lines"]:
                first_span_size = round(block["lines"][0]["spans"][0]["size"])
                if self.is_header(first_span_size):
                    header_blocks.append(block)
                else:
                    content_blocks.append(block)
        
        # Processar cabeçalhos primeiro
        for block in header_blocks:
            formatted_block = self._format_block_to_markdown(block)
            if formatted_block:
                page_markdown_output.append(formatted_block)

        # Processar blocos de conteúdo em colunas
        columns = self._detect_columns(content_blocks)
        for col_blocks in columns:
            merged_blocks = self._merge_text_blocks(col_blocks)
            for block in merged_blocks:
                formatted_block = self._format_block_to_markdown(block)
                if formatted_block:
                    page_markdown_output.append(formatted_block)
        
        if not is_first_page:
            # Adiciona o separador de página apenas se não for a primeira página
            # E se houver algum conteúdo na página (além de apenas cabeçalhos)
            if any(formatted_block for formatted_block in page_markdown_output if formatted_block.strip() != '' and not formatted_block.startswith('#')):
                page_markdown_output.append("\n---\n") # Separador de página
                
        return "\n".join(page_markdown_output)

    def _detect_columns(self, blocks):
        """Heuristic to detect columns and group blocks accordingly."""
        if not blocks: return []
        
        # Simple column detection: group blocks by approximate X-coordinate of their left edge
        # This assumes relatively clear column separation
        x_coords = sorted(list(set(round(b["bbox"][0], -1) for b in blocks if "bbox" in b)))
        
        if len(x_coords) < 2: # No clear columns, treat as single column
            return [blocks]

        columns = []
        processed_blocks = set()
        
        # Iterate through blocks and assign them to columns based on their x_coordinate
        # This could be improved for overlapping blocks or more complex layouts
        for x_ref in x_coords:
            current_column_blocks = []
            for b in blocks:
                if b["bbox"][0] >= x_ref - 5 and b["bbox"][0] <= x_ref + 5 and b["bbox"] not in processed_blocks:
                    current_column_blocks.append(b)
                    processed_blocks.add(b["bbox"])
            if current_column_blocks:
                # Sort blocks within a column by Y-coordinate for correct reading order
                current_column_blocks.sort(key=lambda b: b["bbox"][1])
                columns.append(current_column_blocks)
        
        # Adiciona quaisquer blocos restantes (que podem ser cabeçalhos que abrangem colunas, ou ruído)
        # Ao invés de inseri-los no topo, vamos deixá-los na ordem original se não foram processados
        # No entanto, a lógica de `_process_page` já separa cabeçalhos, então isso se aplica mais a blocos de "ruído"
        remaining_blocks = [b for b in blocks if b["bbox"] not in processed_blocks]
        if remaining_blocks:
            remaining_blocks.sort(key=lambda b: b["bbox"][1])
            # Se a coluna principal tiver uma grande quantidade de blocos, adicionar os restantes no final
            # Caso contrário, pode indicar um layout mais complexo e os restantes devem ser tratados com cuidado
            # Por enquanto, a melhor abordagem é deixar o _process_page lidar com a prioridade dos cabeçalhos.
            # Se houverem blocos restantes, tratá-los como uma coluna extra no final para não perder conteúdo.
            if columns:
                columns.append(remaining_blocks)
            else:
                columns = [remaining_blocks]


        return columns

    def _merge_text_blocks(self, blocks):
        """Merge text blocks that are logically close together."""
        if not blocks: return []

        merged_blocks = []
        current_block = None

        for b in blocks:
            if "lines" not in b: continue

            if not current_block:
                current_block = b
                merged_blocks.append(current_block) # Add first block to merged list
                continue

            # Heuristic: Merge if blocks are very close vertically and have similar X
            # Also consider if current block ends with hyphen for word wrap
            vert_dist = b["bbox"][1] - current_block["bbox"][3]
            x_diff = abs(b["bbox"][0] - current_block["bbox"][0])
            
            # Check if previous block ends with a hyphen and next starts shortly after
            last_line_text = "".join([s["text"] for s in current_block["lines"][-1]["spans"]]).strip()
            ends_with_hyphen = last_line_text.endswith('-')
            
            # Ajustar a heurística de fusão para ser mais tolerante com espaçamentos
            # `vert_dist < 10` (era 5) para permitir um pouco mais de espaçamento entre linhas do mesmo parágrafo
            # `x_diff < 20` (era 10) para permitir um pequeno desalinhamento horizontal
            if (vert_dist < 10 and x_diff < 20) or (ends_with_hyphen and vert_dist < 15): # Relax vert_dist for hyphenated words
                current_block["lines"].extend(b["lines"])
                # Update bbox to encompass merged blocks
                current_block["bbox"] = (
                    min(current_block["bbox"][0], b["bbox"][0]),
                    min(current_block["bbox"][1], b["bbox"][1]),
                    max(current_block["bbox"][2], b["bbox"][2]),
                    max(current_block["bbox"][3], b["bbox"][3])
                )
            else:
                current_block = b
                merged_blocks.append(current_block)
        
        return merged_blocks

    def _format_block_to_markdown(self, block):
        """Format a single merged block into Markdown."""
        block_text_lines = []
        
        first_span = block["lines"][0]["spans"][0]
        block_size = round(first_span["size"])
        
        header_level = self.get_header_level(block_size)
        prefix = ""
        
        # Heuristic: Detect bullet points from position or chars
        # Improved list detection to also check for numbered lists
        first_line_raw_text = "".join([s["text"] for s in block["lines"][0]["spans"]]).strip()
        list_match = re.match(r'^(\s*[-*>]|\s*\d+\.|\s*\u2022)\s*(.*)', first_line_raw_text)

        if header_level > 0:
            prefix = "#" * header_level + " "
        elif list_match:
            list_indent = list_match.group(1)
            # Determine if it's a numbered list
            if re.match(r'^\s*\d+\.', list_indent):
                prefix = "1. " # Markdown auto-numbers
            else:
                prefix = "- "
            # The block text will be the content after the bullet/number
            first_line_raw_text = list_match.group(2).strip()
            block_text_lines.append(first_line_raw_text)
        
        for i, line in enumerate(block["lines"]):
            if list_match and i == 0: # First line already processed for list prefix
                continue
            line_text = ""
            for span in line["spans"]:
                line_text += self.process_span(span)
            block_text_lines.append(line_text.strip())
        
        block_text = "\n".join(block_text_lines).strip() # Alterado para usar \n

        if prefix:
            return f"{prefix}{block_text}\n\n" # Duas quebras de linha
        elif block_text:
            return f"{block_text}\n\n" # Duas quebras de linha
        return ""

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Converte PDF em Markdown.")
    p.add_argument("input_pdf", help="Arquivo .pdf de entrada")
    p.add_argument("output_md", nargs="?", default=None, help="Arquivo .md de saída (opcional)")
    a = p.parse_args()
    out = a.output_md or a.input_pdf.rsplit(".", 1)[0] + ".md"
    converter = PDFReconstructor(a.input_pdf)
    md = converter.convert()
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Saída: {out}")
