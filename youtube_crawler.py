import json
import time
import uuid
from youtube_comment_downloader import YoutubeCommentDownloader
from classifier import is_relevant
from database import init_db, is_seen, mark_seen, save_comment_mapping, get_mapped_uuid, close_db
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
    print(f"Attempting to fetch comments from {video_url}")
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
            original_id = comment.get("cid", str(uuid.uuid4()))
            if is_seen(conn, "seen_comments", original_id):
                continue

            text = comment.get("text", "")
            author = comment.get("author", "unknown")
            is_reply = comment.get("parent", None) is not None

            # Generate parent_id if it's a reply and parent is saved
            parent_id = None
            if is_reply:
                parent_original_id = comment.get("parent", None)
                if parent_original_id:
                    parent_uuid = get_mapped_uuid(conn, parent_original_id)
                    if parent_uuid and is_seen(conn, "seen_comments", parent_uuid):
                        parent_id = parent_uuid

            comments_fetched += 1

            # Classify and save if relevant
            if text and is_relevant(text):
                new_uuid = str(uuid.uuid4())
                comment_data = {
                    "id": new_uuid,
                    "text": text,
                    "author": author,
                    "url": video_url,
                    "is_reply": is_reply,
                    "parent_id": parent_id
                }
                save_comment(comment_data)
                mark_seen(conn, "seen_comments", new_uuid)
                save_comment_mapping(conn, original_id, new_uuid)
                comments_saved += 1
                print(f"Saved comment: {text[:20]}... (id: {new_uuid})")
            else:
                mark_seen(conn, "seen_comments", original_id)
                save_comment_mapping(conn, original_id, original_id)  # Map even if not saved

            time.sleep(1)  # Rate limiting

        # Mark video as seen
        mark_seen(conn, "seen_posts", video_url)

    except Exception as e:
        print(f"Failed to fetch comments for {video_url} after retries: {e}")
        return comments_fetched, comments_saved

    print(f"Comments fetched: {comments_fetched}, Relevant comments saved: {comments_saved}")
    return comments_fetched, comments_saved


def crawl_youtube():
    config = load_config()
    youtube_videos = config.get("youtube_videos", [])
    single_video = config.get("single_youtube_video", "")
    downloader = YoutubeCommentDownloader()

    conn = init_db()
    total_fetched = 0
    total_saved = 0

    try:
        # Process single video if provided
        if single_video:
            print(f"Processing single video: {single_video}")
            fetched, saved = scrape_comments(single_video, conn, downloader)
            total_fetched += fetched
            total_saved += saved

        # Process list of videos
        for video_url in youtube_videos:
            print(f"Processing video: {video_url}")
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