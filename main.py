import json
import os
import requests
from datetime import datetime, timedelta
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
    def _get_start_date(self, days_back: int = 7) -> str:
        """
        Calculates the date 'n' days ago in YYYY-MM-DD format.
        """
        target_date = datetime.now() - timedelta(days=days_back)
        return target_date.strftime("%Y-%m-%d")
    
    def get_trending_repos(self, language: str = "python")->List[Dict]:
        # Logic: Find repos created in the last 7 days with high stars
        date_str = self._get_start_date()
        query = f"q=language:{language}+created:>{date_str}&sort=stars&order=desc"
        try:
            print(f"DEBUG: Searching for {language} repos created since {date_str}...")
            response = requests.get(f"{self.url}?{query}", headers=self.headers)
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            print(f"Extraction Error: {e}")
            return []
        
    def get_readme_content(self, owner: str, repo_name: str) -> str:
        """
        Fetches the README file for a specific repository.
        """
        url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            # GitHub returns READMEs as Base64 encoded strings
            import base64
            content_base64 = response.json().get('content', '')
            return base64.b64decode(content_base64).decode('utf-8')
        except Exception:
            return "" # Return empty string if no README exists

class DataTransformer:
    """
    Prepares data for the database.
    Demonstrates: AI Techniques (Categorization Logic).
    """
    def process(self, raw_data: List[Dict], readme_content: str ="") -> Dict:
        fulltext = (raw_data.get('description') or "") + " " + readme_content

        return{"name": raw_data['name'],
               "stars": raw_data['stargazers_count'],
               "link": raw_data['html_url'],
               "label": self._ai_label(fulltext.lower())
        }    

    def _ai_label(self, text: str) -> str:
        # Define 'Weights' for our Formal Logic
        scores = {
            "AI/ML": text.count("ai") + text.count("model") + text.count("inference"),
            "Automation": text.count("automate") + text.count("workflow") + text.count("ci/cd"),
            "Web Dev": text.count("http") + text.count("api") + text.count("frontend")
        }
        
        # Logic: Pick the category with the highest 'Score'
        best_category = max(scores, key=scores.get)
        
        # Fallback: If no keywords found, it's General
        return best_category if scores[best_category] > 0 else "General"

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
        
        final_list = []
        for repo in raw_results:
            processed_item = transformer.process(repo)
            final_list.append(processed_item)

        print("\n--- Step 3: Deep Analysis (READMEs) ---")
        for item in final_list[:5]: # Limit to top 5 for demo
            original_repo = next(r for r in raw_results if r['name'] == item['name'])
            owner = original_repo['owner']['login']
            
            readme = extractor.get_readme_content(owner, item['name'])
            print(f"Analyzing {item['name']}... (README Length: {len(readme)} characters)")
            
            enriched_data = transformer.process(original_repo, readme)
            item['label'] = enriched_data['label'] 
            
            print(f"   Updated Label: {item['label']}")

        # Final Summary
        print("\n--- FINAL RESULTS (Top 5) ---")
        for item in final_list[:5]:
            print(f"Repo: {item['name']} | Stars: {item['stars']} | Final Label: {item['label']}")

        # --- Step 4: Storage Layer (Data Persistence) ---
        output_file = "trending_repos.json"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                # Save the top 5 with their enriched labels
                json.dump(final_list[:5], f, indent=4)
            print(f"\n[SUCCESS] Data persisted to {output_file}")
        except Exception as e:
            print(f"\n[STORAGE ERROR] Could not save file: {e}")