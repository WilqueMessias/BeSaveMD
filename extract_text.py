import pypdf
import sys

pdf_path = "d:/curriculo/EN_Wilque_Messias_de_Lima.pdf"
output_path = "d:/curriculo/pdf_content.txt"

try:
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print("Extraction successful")
except ImportError:
    print("Error: pypdf not installed")
    sys.exit(1)
except Exception as e:
    print(f"Error reading PDF: {e}")
    sys.exit(1)
