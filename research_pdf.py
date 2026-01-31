import fitz

def analyze_pdf_structure(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Get text blocks with detailed info
    blocks = page.get_text("dict")["blocks"]
    
    print(f"Total blocks: {len(blocks)}")
    
    # Analyze a few blocks to see what metadata we have (font, size, bbox)
    for i, block in enumerate(blocks[:5]):
        print(f"Block {i}: {block.keys()}")
        if "lines" in block:
            first_line = block["lines"][0]
            first_span = first_line["spans"][0]
            print(f"  Sample Text: {first_span['text']}")
            print(f"  Font: {first_span['font']}")
            print(f"  Size: {first_span['size']}")
            print(f"  BBox: {block['bbox']}")
            print("-" * 30)

if __name__ == "__main__":
    analyze_pdf_structure("d:/curriculo/EN_Wilque_Messias_de_Lima.pdf")
