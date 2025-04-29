import json
import time
import uuid
import requests
from bs4 import BeautifulSoup
from classifier import is_relevant
from database import init_db, is_seen, mark_seen, close_db

def load_config(file_path="sample.json"):
    with open(file_path, "r") as f:
        return json.load(f)

def save_comment(comment_data, file_path="comments.jsonl"):
    with open(file_path, "a") as f:
        json.dump(comment_data, f)
        f.write("\n")

def scrape_comments(post_url, conn, headers):
    comments_fetched = 0
    comments_saved = 0
    print(f"Processing post: {post_url}")

    # Check if post is seen
    if is_seen(conn, "seen_posts", post_url):
        print("Post already processed.")
        return comments_fetched, comments_saved

    try:
        response = requests.get(post_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find comment section
        comment_area = soup.find("div", class_="commentarea")
        if not comment_area:
            print("No comments found.")
            return comments_fetched, comments_saved

        # Process comments
        comments = comment_area.find_all("div", class_="entry", recursive=True)
        for comment in comments:
            comment_id = comment.get("data-fullname", str(uuid.uuid4()))
            if is_seen(conn, "seen_comments", comment_id):
                continue

            # Extract comment text
            text_tag = comment.find("div", class_="md")
            text = text_tag.get_text(strip=True) if text_tag else ""

            # Extract author
            author_tag = comment.find("a", class_="author")
            author = author_tag.get_text(strip=True) if author_tag else "unknown"

            # Determine if it's a reply
            parent = comment.find_parent("div", class_="child")
            is_reply = bool(parent and parent.find_parent("div", class_="comment"))

            # Generate parent_id if it's a reply and parent is saved
            parent_id = None
            if is_reply:
                parent_comment = comment.find_parent("div", class_="comment")
                parent_id = parent_comment.get("data-fullname", None) if parent_comment else None

            comments_fetched += 1

            # Classify and save if relevant
            if text and is_relevant(text):
                comment_data = {
                    "id": str(uuid.uuid4()),
                    "text": text,
                    "author": author,
                    "url": post_url,
                    "is_reply": is_reply,
                    "parent_id": parent_id
                }
                save_comment(comment_data)
                comments_saved += 1

            mark_seen(conn, "seen_comments", comment_id)
            time.sleep(1)  # Rate limiting

        # Mark post as seen
        mark_seen(conn, "seen_posts", post_url)

    except requests.RequestException as e:
        print(f"Error fetching {post_url}: {e}")
        time.sleep(5)  # Backoff

    print(f"Comments fetched: {comments_fetched}, Relevant comments saved: {comments_saved}")
    return comments_fetched, comments_saved

def crawl_reddit():
    config = load_config()
    subreddits = config.get("subreddits", [])
    single_post = config.get("single_reddit_post", "")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    conn = init_db()
    total_fetched = 0
    total_saved = 0

    try:
        # Process single post if provided
        if single_post:
            fetched, saved = scrape_comments(single_post, conn, headers)
            total_fetched += fetched
            total_saved += saved

        # Process subreddits
        for subreddit in subreddits:
            print(f"Processing subreddit: {subreddit}")
            subreddit_url = f"https://old.reddit.com/r/{subreddit}/new/"
            try:
                response = requests.get(subreddit_url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # Find posts
                posts = soup.find_all("div", class_="thing")
                for post in posts:
                    post_link = post.find("a", class_="title")
                    if post_link:
                        post_url = post_link["href"]
                        if not post_url.startswith("http"):
                            post_url = f"https://old.reddit.com{post_url}"
                        fetched, saved = scrape_comments(post_url, conn, headers)
                        total_fetched += fetched
                        total_saved += saved
                        time.sleep(2)  # Rate limiting between posts

            except requests.RequestException as e:
                print(f"Error fetching subreddit {subreddit}: {e}")
                time.sleep(5)  # Backoff

        print(f"Total comments fetched: {total_fetched}, Total relevant comments saved: {total_saved}")

    finally:
        close_db(conn)

if __name__ == "__main__":
    crawl_reddit()