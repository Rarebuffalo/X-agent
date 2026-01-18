"""
Consolidated database module for X Bot Agent.
Handles all database operations with proper context management.
"""
import sqlite3
import time
import logging
from contextlib import contextmanager
from typing import Optional, List, Tuple
from config import DB_NAME, LOG_FILE

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR)

# =============================================================================
# Database Connection Management
# =============================================================================

@contextmanager
def get_db_connection():
    """Context manager for database connections with proper error handling."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logging.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize all database tables."""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Table for tracking monthly post counts (rate limiting)
        c.execute('''CREATE TABLE IF NOT EXISTS post_counts (
            id INTEGER PRIMARY KEY,
            month TEXT UNIQUE,
            count INTEGER DEFAULT 0
        )''')
        
        # Table for tracking posted tweet content (duplicate prevention)
        c.execute('''CREATE TABLE IF NOT EXISTS posted_tweets (
            id INTEGER PRIMARY KEY,
            content_hash TEXT UNIQUE,
            tweet_id TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Table for tracking processed mentions
        c.execute('''CREATE TABLE IF NOT EXISTS processed_mentions (
            id INTEGER PRIMARY KEY,
            tweet_id TEXT UNIQUE,
            author_id TEXT,
            author_username TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Table for tracking retweets
        c.execute('''CREATE TABLE IF NOT EXISTS retweet_log (
            id INTEGER PRIMARY KEY,
            original_tweet_id TEXT UNIQUE,
            retweeted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_quote_retweet BOOLEAN DEFAULT 0
        )''')
        
        conn.commit()

# =============================================================================
# Post Count Operations (Rate Limiting)
# =============================================================================

def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return time.strftime("%Y-%m")

def get_post_count() -> int:
    """Get current month's post count."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT count FROM post_counts WHERE month=?", (get_current_month(),))
        result = c.fetchone()
        return result['count'] if result else 0

def increment_post_count() -> bool:
    """Increment current month's post count. Returns True on success."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            current_month = get_current_month()
            c.execute("""
                INSERT INTO post_counts (month, count) VALUES (?, 1)
                ON CONFLICT(month) DO UPDATE SET count = count + 1
            """, (current_month,))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to increment post count: {e}")
        return False

# =============================================================================
# Posted Tweets Operations (Duplicate Prevention)
# =============================================================================

def get_content_hash(content: str) -> str:
    """Generate a simple hash for tweet content."""
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()

def has_posted_before(content: str) -> bool:
    """Check if similar content has been posted before."""
    content_hash = get_content_hash(content)
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM posted_tweets WHERE content_hash=?", (content_hash,))
        return c.fetchone() is not None

def record_posted_tweet(content: str, tweet_id: str) -> bool:
    """Record a posted tweet to prevent duplicates."""
    try:
        content_hash = get_content_hash(content)
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR IGNORE INTO posted_tweets (content_hash, tweet_id) VALUES (?, ?)",
                (content_hash, tweet_id)
            )
            conn.commit()
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to record posted tweet: {e}")
        return False

# =============================================================================
# Mention Operations
# =============================================================================

def has_processed_mention(tweet_id: str) -> bool:
    """Check if a mention has been processed before."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM processed_mentions WHERE tweet_id=?", (tweet_id,))
        return c.fetchone() is not None

def mark_mention_processed(tweet_id: str, author_id: str = None, author_username: str = None) -> bool:
    """Mark a mention as processed."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR IGNORE INTO processed_mentions (tweet_id, author_id, author_username) VALUES (?, ?, ?)",
                (tweet_id, author_id, author_username)
            )
            conn.commit()
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to mark mention as processed: {e}")
        return False

# =============================================================================
# Retweet Operations
# =============================================================================

def has_retweeted(tweet_id: str) -> bool:
    """Check if a tweet has been retweeted before."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM retweet_log WHERE original_tweet_id=?", (tweet_id,))
        return c.fetchone() is not None

def record_retweet(tweet_id: str, is_quote: bool = False) -> bool:
    """Record a retweet to prevent duplicates."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR IGNORE INTO retweet_log (original_tweet_id, is_quote_retweet) VALUES (?, ?)",
                (tweet_id, is_quote)
            )
            conn.commit()
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to record retweet: {e}")
        return False

# =============================================================================
# Statistics
# =============================================================================

def get_bot_stats() -> dict:
    """Get bot statistics."""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Current month posts
        c.execute("SELECT count FROM post_counts WHERE month=?", (get_current_month(),))
        result = c.fetchone()
        current_month_posts = result['count'] if result else 0
        
        # Total tweets ever
        c.execute("SELECT COUNT(*) as total FROM posted_tweets")
        total_tweets = c.fetchone()['total']
        
        # Total mentions processed
        c.execute("SELECT COUNT(*) as total FROM processed_mentions")
        total_mentions = c.fetchone()['total']
        
        # Total retweets
        c.execute("SELECT COUNT(*) as total FROM retweet_log")
        total_retweets = c.fetchone()['total']
        
        return {
            'current_month_posts': current_month_posts,
            'total_tweets': total_tweets,
            'total_mentions_processed': total_mentions,
            'total_retweets': total_retweets
        }
