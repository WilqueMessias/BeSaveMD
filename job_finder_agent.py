import os
import requests
from datetime import datetime

# Agent Configuration
TARGET_FILE = "Job_Hunt_List.md"
SEARCH_QUERY = "Python Django jobs Canada LMIA sponsorship hiring"
# Note: For real-world use, you would integrate with an API like Serper or SerpApi
# For this demonstration, we simulate the agent finding a new lead.

def find_new_jobs():
    """
    Simulates searching the web for new leads.
    In a real scenario, this would call a Search API.
    """
    # Simulated lead found
    new_leads = [
        {
            "company": "Wealthsimple",
            "title": "Senior Python Engineer",
            "email": "careers@wealthsimple.com"
        }
    ]
    return new_leads

def update_job_list(leads):
    if not os.path.exists(TARGET_FILE):
        print(f"File {TARGET_FILE} not found!")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    with open(TARGET_FILE, "a", encoding="utf-8") as f:
        for lead in leads:
            entry = f"| {today} | {lead['company']} | {lead['title']} | {lead['email']} | Found by Agent |\n"
            f.write(entry)
            print(f"✅ Added {lead['company']} to the list!")

if __name__ == "__main__":
    print("🚀 Starting Job Finder Agent...")
    leads = find_new_jobs()
    update_job_list(leads)
    print("🏁 Agent finished search.")
