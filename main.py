import json
import time
from reddit_crawler import crawl_reddit
from youtube_crawler import crawl_youtube


def load_config(file_path="sample.json"):
    """Load configuration from JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


def main():
    """Main function to orchestrate Reddit and YouTube crawling."""
    while True:
        print("Starting new crawling cycle...")
        config = load_config()

        # Reddit crawling
        subreddits = config.get("subreddits", [])
        single_reddit_post = config.get("single_reddit_post", "")
        if subreddits or single_reddit_post:
            print("Starting Reddit crawling...")
            try:
                crawl_reddit()
            except Exception as e:
                print(f"Error in Reddit crawling: {e}")
                time.sleep(300)  # Backoff for 5 minutes on error
        else:
            print("No Reddit sources to crawl.")

        # YouTube crawling
        youtube_channels = config.get("youtube_channels", [])
        single_youtube_video = config.get("single_youtube_video", "")
        if youtube_channels or single_youtube_video:
            print("Starting YouTube crawling...")
            try:
                crawl_youtube()
            except Exception as e:
                print(f"Error in YouTube crawling: {e}")
                time.sleep(300)  # Backoff for 5 minutes on error
        else:
            print("No YouTube sources to crawl.")

        print("Cycle complete. Sleeping for 5 minutes...")
        time.sleep(300)  # Sleep for 5 minutes between cycles


if __name__ == "__main__":
    main()