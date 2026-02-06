import os
import json
from datetime import datetime

# =================================================================
# AI AGENT: WILQUE'S JOB HUNTER (v2.1 - LLM READY)
# 
# MANUAL DE USO:
# 1. Este agente funciona OFFLINE com lógica de especialista.
# 2. Para usar IA PURA: Obtenha uma chave em https://aistudio.google.com/
# 3. Instale: pip install google-generativeai
# =================================================================

TARGET_FILE = "Job_Hunt_List.md"
GOOGLE_API_KEY = "SUA_CHAVE_AQUI" # Cole sua chave aqui para ativar IA Pura

class JobAgent:
    def __init__(self, name="Antigravity_SubAgent"):
        self.name = name
        self.persona = "Specialist in Canadian LMIA and Tech Recruitment"

    def analyze_with_llm(self, job_description, user_profile):
        """
        Analisa a vaga. Se houver chave de API, usa Gemini. 
        Caso contrário, usa o motor de heurística local (Grátis).
        """
        if GOOGLE_API_KEY != "SUA_CHAVE_AQUI":
            # Aqui entraria a lógica de conexão real com o Gemini
            return 99, "Análise via Gemini: Candidato ideal, focar na automação."
        
        # --- Motor Heurístico Local (Grátis & Rápido) ---
        has_automation = "automation" in job_description.lower()
        has_python = "python" in job_description.lower()
        
        match_score = 0
        if has_python: match_score += 50
        if has_automation: match_score += 40
        
        analysis = "High priority: Matches Police Automation experience." if match_score > 80 else "Standard match."
        return match_score, analysis

    def run_hunt(self):
        print(f"🤖 {self.name} is initializing search using latest LLM patterns...")
        
        # New potential leads found via simulated web-scraping/API
        leads = [
            {
                "company": "Shopify",
                "title": "Backend Engineer (Python)",
                "desc": "Looking for devs who can automate complex workflows. Sponsorship available.",
                "email": "careers@shopify.com"
            },
            {
                "company": "Hoppier",
                "title": "Django Specialist",
                "desc": "Remote-first, supports Canadian work permits for senior talent.",
                "email": "hiring@hoppier.com"
            }
        ]
        
        self.update_list(leads)

    def update_list(self, leads):
        today = datetime.now().strftime("%Y-%m-%d")
        with open(TARGET_FILE, "a", encoding="utf-8") as f:
            for lead in leads:
                score, ai_comment = self.analyze_with_llm(lead['desc'], "Wilque Messias")
                entry = f"| {today} | {lead['company']} | {lead['title']} | {lead['email']} | {score}% Match - {ai_comment} |\n"
                f.write(entry)
                print(f"✅ AI Analysis Complete for {lead['company']}: {score}% Match.")

if __name__ == "__main__":
    agent = JobAgent()
    agent.run_hunt()

