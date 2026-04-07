import re
import os
import nltk
from typing import List, Dict

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

nltk_data_path = os.path.join(os.getcwd(), 'nltk_data')
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

nltk.download('punkt', download_dir=nltk_data_path, quiet=True)

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