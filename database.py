import sqlite3

def init_db(db_path="crawler.db"):
    """Initialize SQLite database with tables for tracking seen content and comment mapping.
    
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
    
    # Table for mapping original comment IDs to generated UUIDs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comment_mapping (
            original_id TEXT,
            uuid TEXT,
            PRIMARY KEY (original_id)
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
    cursor.execute(f"INSERT OR IGNORE INTO {table} (id) VALUES (?)", (item_id,))
    conn.commit()

def save_comment_mapping(conn, original_id, uuid):
    """Save the mapping between original comment ID and generated UUID.
    
    Args:
        conn (sqlite3.Connection): Database connection.
        original_id (str): Original comment ID (e.g., cid or data-fullname).
        uuid (str): Generated UUID for the comment.
    """
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO comment_mapping (original_id, uuid) VALUES (?, ?)", (original_id, uuid))
    conn.commit()

def get_mapped_uuid(conn, original_id):
    """Get the UUID mapped to an original comment ID.
    
    Args:
        conn (sqlite3.Connection): Database connection.
        original_id (str): Original comment ID.
        
    Returns:
        str or None: Mapped UUID, or None if not found.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT uuid FROM comment_mapping WHERE original_id = ?", (original_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def close_db(conn):
    """Close the database connection.
    
    Args:
        conn (sqlite3.Connection): Database connection.
    """
    conn.close()