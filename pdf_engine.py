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
            
            for page in self.doc:
                blocks = page.get_text("dict")["blocks"]
                
                # Sort blocks by Y then X to handle reading order better
                blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
                
                merged_blocks = []
                current_block = None
                
                for b in blocks:
                    if "lines" not in b: continue
                    
                    if not current_block:
                        current_block = b
                        continue
                    
                    # Heuristic: Merge if blocks are very close vertically and have similar X
                    vert_dist = b["bbox"][1] - current_block["bbox"][3]
                    x_diff = abs(b["bbox"][0] - current_block["bbox"][0])
                    
                    if vert_dist < 5 and x_diff < 10:
                        current_block["lines"].extend(b["lines"])
                        current_block["bbox"] = (
                            min(current_block["bbox"][0], b["bbox"][0]),
                            current_block["bbox"][1],
                            max(current_block["bbox"][2], b["bbox"][2]),
                            b["bbox"][3]
                        )
                    else:
                        merged_blocks.append(current_block)
                        current_block = b
                
                if current_block:
                    merged_blocks.append(current_block)

                for block in merged_blocks:
                    block_text = ""
                    first_span = block["lines"][0]["spans"][0]
                    block_size = round(first_span["size"])
                    
                    header_level = self.get_header_level(block_size)
                    prefix = ""
                    
                    if header_level > 0:
                        prefix = "#" * header_level + " "
                    
                    # Heuristic: Detect bullet points from position or chars
                    raw_text = "".join([s["text"] for line in block["lines"] for s in line["spans"]])
                    if re.match(r'^[\s•\-*>]', raw_text.strip()):
                        prefix = "- "
                        # Strip the original bullet char if it's there
                        raw_text = re.sub(r'^[\s•\-*>]', '', raw_text.strip()).strip()

                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            line_text += self.process_span(span)
                        block_text += line_text + " "
                    
                    block_text = block_text.strip()
                    if prefix == "- ":
                        # Re-strip bullet char from formatted text just in case
                        block_text = re.sub(r'^\s*[•\-*]\s*', '', block_text).strip()

                    if prefix:
                        markdown_output.append(f"{prefix}{block_text}\n")
                    else:
                        markdown_output.append(f"{block_text}\n")
                
                markdown_output.append("\n---\n")
                
            return "\n".join(markdown_output)
        finally:
            self.doc.close()

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
