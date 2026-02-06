import re
import json
import sys
import os

# Adiciona o diretório atual ao path para importação
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_engine import PDFReconstructor

class AuditEngine:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.reconstructor = PDFReconstructor(pdf_path)
        self.full_text = ""
        self.entities = {
            "monetary_values": [],
            "dates": [],
            "keywords": []
        }
        # Palavras-chave do desafio GovTech
        self.target_keywords = [
            "Fiscalização", "UST", "Evidência", "TI", "Glosa", 
            "Automação", "Subjetividade", "Inovação", "Gestão"
        ]

    def run_audit(self):
        """Executa o pipeline de auditoria simulada."""
        print(f"[*] Iniciando auditoria em: {self.pdf_path}")
        
        # 1. Extração de Texto via Engine Base
        print("[*] Extraindo texto do PDF...")
        try:
            self.reconstructor.analyze_fonts()
            raw_text_pages = []
            for page in self.reconstructor.doc:
                # Usamos extração simples para regex, sem formatação markdown
                raw_text_pages.append(page.get_text())
            self.full_text = "\n".join(raw_text_pages)
        except Exception as e:
            return {"error": str(e)}

        # 2. Extração de Entidades (Regex POC)
        print("[*] Identificando entidades...")
        self._extract_monetary()
        self._extract_dates()
        self._extract_keywords()

        # 3. Geração de Relatório
        report = {
            "document": os.path.basename(self.pdf_path),
            "status": "ANALYZED",
            "findings": {
                "total_monetary_mentions": len(self.entities["monetary_values"]),
                "total_date_mentions": len(self.entities["dates"]),
                "key_terms_found": self.entities["keywords"]
            },
            "sample_data": {
                "top_values": self.entities["monetary_values"][:5],
                "recent_dates": self.entities["dates"][:5]
            },
            "audit_verdict": self._generate_verdict()
        }
        
        return report

    def _extract_monetary(self):
        # Regex para R$ 1.000,00 ou 1.000.000,00
        pattern = r'R\$\s?[\d\.]+(?:,\d{2})?'
        matches = re.finditer(pattern, self.full_text)
        for match in matches:
            self.entities["monetary_values"].append(match.group(0))

    def _extract_dates(self):
        # Regex para DD/MM/AAAA
        pattern = r'\b\d{2}/\d{2}/\d{4}\b'
        matches = re.finditer(pattern, self.full_text)
        for match in matches:
            self.entities["dates"].append(match.group(0))

    def _extract_keywords(self):
        found = {}
        for kw in self.target_keywords:
            count = len(re.findall(r'\b' + re.escape(kw) + r'\b', self.full_text, re.IGNORECASE))
            if count > 0:
                found[kw] = count
        self.entities["keywords"] = found

    def _generate_verdict(self):
        """Simula um parecer da IA."""
        if "UST" in self.entities["keywords"] or "Fiscalização" in self.entities["keywords"]:
            return "COMPATÍVEL: Documento trata de Fiscalização/UST. Fortes indícios de relevância para o desafio."
        return "GENÉRICO: Documento com baixo alinhamento técnico aparente."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python audit_engine.py <caminho_do_pdf>")
        sys.exit(1)
        
    pdf_file = sys.argv[1]
    auditor = AuditEngine(pdf_file)
    result = auditor.run_audit()
    
    # Salva relatório JSON
    output_json = pdf_file + ".audit.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
        
    print(f"[*] Relatório salvo em: {output_json}")
    print(json.dumps(result, indent=4, ensure_ascii=False))
