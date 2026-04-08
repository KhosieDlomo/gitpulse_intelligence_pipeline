![GitPulse Nightly Sync](https://github.com/KhosieDlomo/gitpulse_intelligence_pipeline/actions/workflows/daily_pulse.yml/badge.svg)

# 🚀 GitPulse Intelligence Pipeline

An automated intelligence system that monitors GitHub trending repositories, analyzes project sentiment/impact using NLTK, and delivers daily reports to Discord.

## 🛠️ Tech Stack
* **Language:** Python 3.11 (Logic-based filtering & NLTK)
* **Database:** SQLite (Persistent star-tracking & historical data)
* **Infrastructure:** Docker & Docker Compose (Containerized services)
* **Automation:** GitHub Actions (CI/CD Nightly Sync)
* **UI:** Streamlit (Intelligence Dashboard)

## 🏗️ System Architecture
1. **The Pipeline:** A Python service that scrapes GitHub's trending API and applies formal logic to filter "high-impact" projects.
2. **The Intelligence:** Natural Language Toolkit (NLTK) analyzes repo descriptions for technical complexity.
3. **The Storage:** A Docker-volume-mapped SQLite database tracks star growth over time.
4. **The Cloud:** A GitHub Action triggers every morning at 10:00 AM (SAST) to sync data and alert the team via Discord.

## 🤖 Automation & CI/CD
The project features a fully automated data lifecycle managed via **GitHub Actions** (`daily_pulse.yml`):

* **Scheduled Execution:** Triggered automatically every day at 10:00 AM SAST (08:00 UTC).
* **Environment Parity:** Runs in a standardized Ubuntu container to ensure "it works on my machine" translates to the cloud.
* **State Persistence:** The workflow performs a "Self-Commit" of the SQLite database back to the repository, maintaining a historical record of star growth without manual intervention.
* **Notification Loop:** Real-time system status and failure alerts are piped directly to a Discord webhook.

## 🚀 One-Command Setup
Ensure you have Docker installed, then run:
```bash
docker compose up -d