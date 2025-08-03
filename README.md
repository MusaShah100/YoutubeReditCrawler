# 📡 YoutubeReditCrawler

## 🔍 Overview

**YoutubeReditCrawler** is a Python-based project designed to scrape and analyze **Lebanese Arabizi** comments from Reddit and YouTube. It continuously monitors content, detects Arabizi text, and stores relevant comments in a structured format for further processing or training.

---

## ✨ Features

- 🔁 Scrapes comments from Reddit (`old.reddit.com`) and YouTube
- 🧠 Detects Lebanese Arabizi comments using a custom classifier
- 💾 Stores relevant comments in a `.jsonl` file
- 🗃 Tracks processed content using an SQLite database

---

## 📦 Installation

1. Ensure **Python 3.8+** is installed.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration

Create a `sample.json` configuration file in the root directory with this structure:

```json
{
  "subreddits": ["lebanon", "beirut"],
  "youtube_videos": ["https://www.youtube.com/watch?v=aoUEXRlvmxc"],
  "single_reddit_post": "https://old.reddit.com/r/lebanon/comments/18k7z8v/what_are_your_thoughts_on_the_current_situation/",
  "single_youtube_video": "https://www.youtube.com/watch?v=aoUEXRlvmxc"
}
```

- `subreddits`: List of subreddits to crawl
- `youtube_videos`: List of YouTube video URLs
- `single_reddit_post`: (Optional) Scrape a single Reddit post
- `single_youtube_video`: (Optional) Scrape a single YouTube video

---

## ▶️ Usage

1. Ensure all required files are in the same directory:
   - `main.py`
   - `reddit_crawler.py`
   - `youtube_crawler.py`
   - `classifier.py`
   - `database.py`
   - `sample.json`
   - `requirements.txt`

2. Run the script:
   ```bash
   python main.py
   ```

3. Output:
   - `comments.jsonl` — Saved Arabizi comments
   - `crawler.db` — SQLite database tracking processed posts/videos

---

## 🧱 Project Structure

```
YoutubeReditCrawler/
├── main.py               # Entry point
├── reddit_crawler.py     # Reddit scraping logic
├── youtube_crawler.py    # YouTube scraping logic
├── classifier.py         # Lebanese Arabizi classifier
├── database.py           # SQLite database management
├── sample.json           # Configuration file
├── requirements.txt      # Dependencies
├── comments.jsonl        # Output file (generated)
└── crawler.db            # SQLite database (generated)
```

---

## 🛡 License

This project is open-source and available for anyone to use and modify.

---

## 👤 Author

**Syed Moosa Ali**
