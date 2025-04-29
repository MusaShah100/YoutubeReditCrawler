import json
import time
import uuid
import requests
from bs4 import BeautifulSoup
from youtube_comment_downloader import YoutubeCommentDownloader
from classifier import is_relevant
from database import init_db, is_seen, mark_seen, close_db
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def load_config(file_path="sample.json"):
    """Load configuration from JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


def save_comment(comment_data, file_path="comments.jsonl"):
    """Save comment to JSONL file."""
    with open(file_path, "a") as f:
        json.dump(comment_data, f)
        f.write("\n")


def get_video_ids_from_channel(channel_identifier, headers):
    """Fetch video IDs from a YouTube channel page or ID.

    Args:
        channel_identifier (str): Channel URL or ID.
        headers (dict): HTTP headers for requests.

    Returns:
        list: List of video URLs.
    """
    video_urls = []
    if channel_identifier.startswith("http"):
        channel_url = channel_identifier
    else:
        channel_url = f"https://www.youtube.com/channel/{channel_identifier}/videos"

    try:
        response = requests.get(channel_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find video links
        video_links = soup.find_all("a", class_="yt-simple-endpoint style-scope ytd-grid-video-renderer")
        for link in video_links:
            href = link.get("href", "")
            if href.startswith("/watch?v="):
                video_urls.append(f"https://www.youtube.com{href}")

        return video_urls[:10]  # Limit to 10 videos to avoid overloading
    except requests.RequestException as e:
        print(f"Error fetching channel {channel_identifier}: {e}")
        return []


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: print(f"Retrying video fetch (attempt {retry_state.attempt_number})...")
)
def fetch_comments_with_timeout(downloader, video_url, timeout=30):
    """Fetch comments with a timeout to prevent hanging.

    Args:
        downloader: YoutubeCommentDownloader instance.
        video_url (str): URL of the YouTube video.
        timeout (int): Timeout in seconds for fetching comments.

    Returns:
        iterator: Comments iterator from youtube-comment-downloader.
    """
    # youtube-comment-downloader doesn't support direct timeout, so we rely on tenacity for retries
    return downloader.get_comments_from_url(video_url)


def scrape_comments(video_url, conn, downloader):
    """Scrape comments from a YouTube video.

    Args:
        video_url (str): URL of the YouTube video.
        conn: SQLite connection.
        downloader: YoutubeCommentDownloader instance.

    Returns:
        tuple: (comments_fetched, comments_saved).
    """
    comments_fetched = 0
    comments_saved = 0
    print(f"Processing video: {video_url}")

    # Check if video is seen
    if is_seen(conn, "seen_posts", video_url):
        print("Video already processed.")
        return comments_fetched, comments_saved

    try:
        comments = fetch_comments_with_timeout(downloader, video_url)
        for comment in comments:
            comment_id = comment.get("cid", str(uuid.uuid4()))
            if is_seen(conn, "seen_comments", comment_id):
                continue

            text = comment.get("text", "")
            author = comment.get("author", "unknown")
            is_reply = comment.get("parent", None) is not None
            parent_id = comment.get("parent", None)

            comments_fetched += 1

            # Classify and save if relevant
            if text and is_relevant(text):
                comment_data = {
                    "id": str(uuid.uuid4()),
                    "text": text,
                    "author": author,
                    "url": video_url,
                    "is_reply": is_reply,
                    "parent_id": parent_id if is_reply and is_seen(conn, "seen_comments", parent_id) else None
                }
                save_comment(comment_data)
                comments_saved += 1

            mark_seen(conn, "seen_comments", comment_id)
            time.sleep(1)  # Rate limiting

        # Mark video as seen
        mark_seen(conn, "seen_posts", video_url)

    except Exception as e:
        print(f"Failed to fetch comments for {video_url} after retries: {e}")
        # Skip this video and continue with the next
        return comments_fetched, comments_saved

    print(f"Comments fetched: {comments_fetched}, Relevant comments saved: {comments_saved}")
    return comments_fetched, comments_saved


def crawl_youtube():
    """Main function to crawl YouTube comments."""
    config = load_config()
    youtube_channels = config.get("youtube_channels", [])
    single_video = config.get("single_youtube_video", "")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    downloader = YoutubeCommentDownloader()

    conn = init_db()
    total_fetched = 0
    total_saved = 0

    try:
        # Process single video if provided
        if single_video:
            fetched, saved = scrape_comments(single_video, conn, downloader)
            total_fetched += fetched
            total_saved += saved

        # Process channels
        for channel in youtube_channels:
            print(f"Processing channel: {channel}")
            video_urls = get_video_ids_from_channel(channel, headers)
            for video_url in video_urls:
                fetched, saved = scrape_comments(video_url, conn, downloader)
                total_fetched += fetched
                total_saved += saved
                time.sleep(2)  # Rate limiting between videos

    except Exception as e:
        print(f"Error in crawl_youtube: {e}")
    finally:
        close_db(conn)

    print(f"Total comments fetched: {total_fetched}, Total relevant comments saved: {total_saved}")


if __name__ == "__main__":
    crawl_youtube()