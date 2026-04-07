import json
import os
import requests
import re
import nltk
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict

from database import GitPulseDB

# Create a local folder for NLTK data so GitHub Actions can find it
nltk_data_path = os.path.join(os.getcwd(), 'nltk_data')
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

nltk.download('punkt', download_dir=nltk_data_path, quiet=True)

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

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

class NotificationProvider:
    """Handles outgoing communication to Discord."""
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        
    def send_to_discord(self, top_repos: List[Dict]):
        if not self.webhook_url:
            print("Error: No Discord Webhook URL found.")
            return
        
        message_content = "🚀 **GitPulse Daily Intelligence Update** 🚀\n"
        message_content += "--- Top Multilingual Trending Repositories Report ---\n\n"

        for repo in top_repos:
            lang_tag = f"🏷️ **[{repo['lang']}]**" # New tag
            growth = repo.get('growth', 0)

            # --- Logic: Add Growth Indicators ---
            growth = repo.get('growth', 0)
            growth_str = f"+{growth}" if growth > 0 else "New"
            
            # Visual flair for high growth
            trend_emoji = "🔹"
            if growth > 100:
                trend_emoji = "🔥 **[EXPLOSIVE]**"
            elif growth > 20:
                trend_emoji = "📈 *[Rising]*"

            message_content += f"{lang_tag}{trend_emoji} **{repo['name']}** (`{repo['label']}`)\n"
            message_content += f"📝 *{repo.get('summary', 'Processing...') }*\n"
            message_content += f"⭐ Stars: {repo['stars']} (**{growth_str}**) | 🔗 [View](<{repo['link']}>)\n\n"

        payload = {"content": message_content}

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            print("[SUCCESS] Notification sent to Discord!")
        except Exception as e:
            print(f"[ERROR] Failed to send Discord notification: {e}")

class LocalSummarizer:
    """Summarizes text locally without external NLTK dependencies."""
    def summarize(self, text: str) -> str:
        if not text or len(text) < 50:
            return "No detailed description available."
        
        try:
           #REMOVE HTML TAGS (like <img...>)
            clean = re.sub(r'<[^>]*>', '', text)
            
            #REMOVE MARKDOWN LINKS & IMAGES [text](url) or ![alt](url)
            clean = re.sub(r'!\[.*?\]\(.*?\)', '', clean)
            clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean)
            
            # REMOVE REMAINING MARKDOWN NOISE (#, *, >, `)
            clean = re.sub(r'[#*>`-]', '', clean)
            
            # REMOVE EXTRA WHITESPACE
            clean = " ".join(clean.split())
            
            # SPLIT INTO SENTENCES
            sentences = clean.split(". ")
            if len(sentences) > 0:
                # Get the first 2 sentences
                summary = ". ".join(sentences[:2]).strip()
                return (summary[:180] + '..') if len(summary) > 180 else (summary + ".")
            
            return "See README for full details."
        except Exception:
            return "Error parsing description."
        
# --- EXECUTION FLOW ---
if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("CRITICAL ERROR: No token found.")
    else:
        extractor = GitHubExtractor(GITHUB_TOKEN)
        transformer = DataTransformer()
        summarizer = LocalSummarizer()
        db = GitPulseDB() # Initialize the database connection once

        target_languages = ["python", "java", "cpp"]
        final_list = []

        for lang in target_languages:
            print(f"--- Step 1: Extracting {lang.upper()} ---")
            raw_results = extractor.get_trending_repos(language=lang)
        
            print(f"--- Step 2: Transforming {len(raw_results)} items ---")
            for repo in raw_results[:2]:
                processed_item = transformer.process(repo)
                processed_item['lang'] = lang.upper()

                print("\n--- Step 3: Deep Analysis & AI Summarization ---")
                owner = repo['owner']['login']
                readme = extractor.get_readme_content(owner, processed_item['name'])
                processed_item['summary'] = summarizer.summarize(readme)
            
                # This looks up the star count from the PREVIOUS run
                prev_stars = db.get_previous_stars(processed_item['name'])
                processed_item['growth'] = (processed_item['stars'] - prev_stars) if prev_stars else 0  
                
                final_list.append(processed_item)

        # --- STEP 5: Saving all collected languages and notify ---
        print(f"\n--- Step 5: Archiving {len(final_list)} items and Notifying ---")
        db.save_trending(final_list)

        notifier = NotificationProvider(DISCORD_WEBHOOK_URL)
        notifier.send_to_discord(final_list)