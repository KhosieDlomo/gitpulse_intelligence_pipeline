import requests
import base64
from datetime import datetime, timedelta
from typing import List, Dict

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
