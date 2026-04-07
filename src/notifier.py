import requests
from typing import List, Dict

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
