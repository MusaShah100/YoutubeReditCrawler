import sqlite3

def init_db(db_path="crawler.db"):
    """Initialize SQLite database with tables for tracking seen content.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        sqlite3.Connection: Database connection.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table for seen comments (Reddit and YouTube)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_comments (
            id TEXT PRIMARY KEY
        )
    """)

    # Table for seen posts/videos (Reddit post URLs, YouTube video URLs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_posts (
            id TEXT PRIMARY KEY
        )
    """)

    conn.commit()
    return conn


def is_seen(conn, table, item_id):
    """Check if an item (comment or post) has been seen.

    Args:
        conn (sqlite3.Connection): Database connection.
        table (str): Table name ('seen_comments' or 'seen_posts').
        item_id (str): ID of the item to check.

    Returns:
        bool: True if item is seen, False otherwise.
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table} WHERE id = ?", (item_id,))
    return cursor.fetchone() is not None


def mark_seen(conn, table, item_id):
    """Mark an item (comment or post) as seen.

    Args:
        conn (sqlite3.Connection): Database connection.
        table (str): Table name ('seen_comments' or 'seen_posts').
        item_id (str): ID of the item to mark.
    """
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table} (id) VALUES (?)", (item_id,))
    conn.commit()


def close_db(conn):
    """Close the database connection.

    Args:
        conn (sqlite3.Connection): Database connection.
    """
    conn.close()