# Instructions for Reddit/YouTube Web Crawler

## What This Project Does
This project scrapes comments from Reddit (via old.reddit.com) and YouTube to find Lebanese Arabizi comments. It saves relevant comments to a JSONL file and tracks processed content in an SQLite database.

## How to Install Requirements
1. Ensure Python 3.8 or higher is installed on your system.
2. Install the required libraries by running:
   ```
   pip install -r requirements.txt
   ```

## How to Fill sample.json
Create a file named `sample.json` in the project directory with the following structure:
```json
{
  "subreddits": ["lebanon", "beirut"], // List of subreddits to scrape
  "youtube_videos": ["https://www.youtube.com/watch?v=aoUEXRlvmxc"], // List of YouTube video URLs
  "single_reddit_post": "https://old.reddit.com/r/lebanon/comments/18k7z8v/what_are_your_thoughts_on_the_current_situation/", // Optional: A single Reddit post URL
  "single_youtube_video": "https://www.youtube.com/watch?v=aoUEXRlvmxc" // Optional: A single YouTube video URL
}
```
- Add subreddits relevant to your target (e.g., `lebanon`, `beirut`).
- Add YouTube video URLs (e.g., `https://www.youtube.com/watch?v=aoUEXRlvmxc`).
- Optionally, specify a single Reddit post or YouTube video URL to scrape.

## How to Run main.py
1. Ensure all project files are in the same directory: `main.py`, `reddit_crawler.py`, `youtube_crawler.py`, `database.py`, `classifier.py`, `sample.json`, `requirements.txt`.
2. Run the script using:
   ```
   python main.py
   ```
3. The script will run continuously, scraping Reddit and YouTube comments, printing progress (e.g., "Processing subreddit: lebanon", "Comments fetched: 50, Relevant comments saved: 5").
4. Check `comments.jsonl` for saved comments and `crawler.db` for the SQLite database.