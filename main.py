import os
import requests
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

class GitHubExtractor:
    """Handles API communication.
       Demonstrates how to interact with GitHub's API to fetch repository data.
    """
    def __init__(self, token: str):
        self.url = "https://api.github.com/search/repositories"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    def get_trending_repos(self, language: str = "python")->List[Dict]:
        # Logic: Find repos created in the last 7 days with high stars
        query = f"q=language:{language}+created:>2026-03-29&sort=stars&order=desc"
        try:
            response = requests.get(f"{self.url}?{query}", headers=self.headers)
            response.raise_for_status() # Formal Logic: Check for success (200 OK)
            return response.json().get('items', [])
        except Exception as e:
            print(f"Extraction Error: {e}")
            return []

class DataTransformer:
    """
    Prepares data for the database.
    Demonstrates: AI Techniques (Categorization Logic).
    """
    def process(self, raw_data: List[Dict]) -> List[Dict]:
        cleaned = []
        for repo in raw_data:
            # Filtering Logic: Only keep repos with descriptions
            if repo.get('description'):
                cleaned.append({
                    "name": repo['name'],
                    "stars": repo['stargazers_count'],
                    "link": repo['html_url'],
                    "label": self._ai_label(repo['description'])
                })
        return cleaned

    def _ai_label(self, description: str) -> str:
        # Placeholder: This is where your AI Module techniques go later!
        return "General"

# --- EXECUTION FLOW ---
if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("CRITICAL ERROR: No token found. Check your .env file.")
    else:
        extractor = GitHubExtractor(GITHUB_TOKEN)
        transformer = DataTransformer()

        print("--- Step 1: Extracting ---")
        raw_results = extractor.get_trending_repos()
        
        print(f"--- Step 2: Transforming {len(raw_results)} items ---")
        final_list = transformer.process(raw_results)

        for item in final_list[:5]: # Show top 5
            print(f"Found: {item['name']} | Stars: {item['stars']} | Label: {item['label']}")