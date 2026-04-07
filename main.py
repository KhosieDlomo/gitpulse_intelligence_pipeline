import os
import requests
import nltk
from dotenv import load_dotenv

from src.extractor import GitHubExtractor
from src.transformer import DataTransformer, LocalSummarizer
from src.notifier import NotificationProvider
from src.database import GitPulseDB


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

        
# --- EXECUTION FLOW ---
if __name__ == "__main__":
    notifier = NotificationProvider(DISCORD_WEBHOOK_URL)
    try:
        if not GITHUB_TOKEN or not DISCORD_WEBHOOK_URL:
            raise ValueError("Missing Token or Webhook Variables")
        
        print("🚀 System Check Passed. Starting GitPulse...")
        extractor = GitHubExtractor(GITHUB_TOKEN)
        transformer = DataTransformer()
        summarizer = LocalSummarizer()
        db = GitPulseDB()

        target_languages = ["python", "java", "cpp"]
        final_list = []

        for lang in target_languages:
            try:
                print(f"--- Processing {lang.upper()} ---")
                raw_results = extractor.get_trending_repos(language=lang)

                for repo in raw_results[:2]:
                    try:
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
                    except Exception as repo_err:
                        print(f"⚠️Error! Skipping repo {repo['name']}: {repo_err}")

            except Exception as lang_err:
                print(f"❌ Error ine {lang} loop: {lang_err}")
            
        # ---FINAL STEPS ---
        if final_list:
            db.save_trending(final_list)
            notifier.send_to_discord(final_list)
        else:
            print("⚠️ Pipeline finished but no new data was found.")
    
    except Exception as global_err:
        error_msg = f"🚨 **GITPULSE SYSTEM FAILURE** 🚨\nDetails: `{str(global_err)}`"
        print(error_msg)
        requests.post(DISCORD_WEBHOOK_URL, json={"content": error_msg})