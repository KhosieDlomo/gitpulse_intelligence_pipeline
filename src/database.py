import sqlite3
from datetime import datetime

class GitPulseDB:
    def __init__(self, db_name="data/gitpulse.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS repo_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT,
            stars INTEGER,
            label TEXT,
            language TEXT,
            summary TEXT,
            captured_at TIMESTAMP
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def save_trending(self, repo_list):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO repo_history (repo_name, stars, label, language, summary, captured_at) VALUES (?, ?, ?, ?, ?, ?)"
        data = [(r['name'], r['stars'], r['label'], r.get('lang', 'Unknown'), r.get('summary', ''), now) for r in repo_list]
        self.conn.executemany(query, data)
        self.conn.commit()

    def get_previous_stars(self, repo_name):
        """Fetches the most recent star count for a specific repo."""
        query = """
        SELECT stars FROM repo_history 
        WHERE repo_name = ? 
        ORDER BY captured_at DESC LIMIT 1
        """
        cursor = self.conn.execute(query, (repo_name,))
        result = cursor.fetchone()
        return result[0] if result else None