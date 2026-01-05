"""
Database models for Clipfarm
SQLite database to sync dashboard with automation system
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path("clipfarm.db")

def get_connection():
    """Get database connection"""
    return sqlite3.connect(str(DB_PATH))

def init_db():
    """Initialize database with all tables"""
    conn = get_connection()
    c = conn.cursor()
    
    # Clips table
    c.execute('''CREATE TABLE IF NOT EXISTS clips 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT NOT NULL,
                  video_path TEXT NOT NULL,
                  caption_path TEXT,
                  status TEXT NOT NULL DEFAULT 'pending',
                  platform TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  caption TEXT,
                  start_time REAL,
                  end_time REAL,
                  reason TEXT,
                  posted_at DATETIME,
                  error_message TEXT)''')
    
    # Logs table for worker activity
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  level TEXT NOT NULL,
                  component TEXT NOT NULL,
                  message TEXT NOT NULL)''')
    
    # Settings table for dashboard toggles
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY,
                  value TEXT NOT NULL,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Posts table for tracking posted clips
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  clip_id INTEGER,
                  platform TEXT NOT NULL,
                  account TEXT,
                  posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  success BOOLEAN DEFAULT 1,
                  error_message TEXT,
                  FOREIGN KEY (clip_id) REFERENCES clips(id))''')
    
    # Initialize default settings
    c.execute('''INSERT OR IGNORE INTO settings (key, value) VALUES 
                 ('auto_posting_enabled', '0'),
                 ('auto_posting_tiktok', '0'),
                 ('auto_posting_instagram', '0'),
                 ('auto_posting_youtube', '0')''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def add_clip(filename: str, video_path: str, platform: str, caption: str = None,
             caption_path: str = None, start_time: float = None, 
             end_time: float = None, reason: str = None) -> int:
    """Add a new clip to database"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''INSERT INTO clips 
                 (filename, video_path, caption_path, status, platform, caption, start_time, end_time, reason)
                 VALUES (?, ?, ?, 'pending', ?, ?, ?, ?, ?)''',
              (filename, video_path, caption_path, platform, caption, start_time, end_time, reason))
    
    clip_id = c.lastrowid
    conn.commit()
    conn.close()
    return clip_id

def update_clip_status(clip_id: int, status: str, error_message: str = None):
    """Update clip status"""
    conn = get_connection()
    c = conn.cursor()
    
    if status == 'posted':
        c.execute('''UPDATE clips SET status = ?, posted_at = CURRENT_TIMESTAMP, error_message = ?
                     WHERE id = ?''', (status, error_message, clip_id))
    else:
        c.execute('''UPDATE clips SET status = ?, error_message = ? WHERE id = ?''',
                  (status, error_message, clip_id))
    
    conn.commit()
    conn.close()

def get_clips(status: str = None, platform: str = None, limit: int = 100) -> List[Dict]:
    """Get clips with optional filters"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = "SELECT * FROM clips WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_clip_by_id(clip_id: int) -> Optional[Dict]:
    """Get a single clip by ID"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM clips WHERE id = ?", (clip_id,))
    row = c.fetchone()
    conn.close()
    
    return dict(row) if row else None

def add_log(level: str, component: str, message: str):
    """Add a log entry"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''INSERT INTO logs (level, component, message)
                 VALUES (?, ?, ?)''', (level, component, message))
    
    conn.commit()
    conn.close()

def get_logs(component: str = None, limit: int = 100) -> List[Dict]:
    """Get recent logs"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if component:
        c.execute('''SELECT * FROM logs WHERE component = ?
                     ORDER BY timestamp DESC LIMIT ?''', (component, limit))
    else:
        c.execute('''SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_setting(key: str, default: str = None) -> str:
    """Get a setting value"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    
    return row[0] if row else default

def set_setting(key: str, value: str):
    """Set a setting value"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''INSERT OR REPLACE INTO settings (key, value, updated_at)
                 VALUES (?, ?, CURRENT_TIMESTAMP)''', (key, value))
    
    conn.commit()
    conn.close()

def get_analytics() -> Dict:
    """Get analytics summary"""
    conn = get_connection()
    c = conn.cursor()
    
    # Count by status
    c.execute("SELECT status, COUNT(*) FROM clips GROUP BY status")
    status_counts = dict(c.fetchall())
    
    # Count by platform
    c.execute("SELECT platform, COUNT(*) FROM clips GROUP BY platform")
    platform_counts = dict(c.fetchall())
    
    # Total posts today
    c.execute('''SELECT COUNT(*) FROM posts 
                 WHERE DATE(posted_at) = DATE('now') AND success = 1''')
    posts_today = c.fetchone()[0]
    
    # Failed posts today
    c.execute('''SELECT COUNT(*) FROM posts 
                 WHERE DATE(posted_at) = DATE('now') AND success = 0''')
    failed_today = c.fetchone()[0]
    
    conn.close()
    
    return {
        'pending': status_counts.get('pending', 0),
        'posted': status_counts.get('posted', 0),
        'failed': status_counts.get('failed', 0),
        'processing': status_counts.get('processing', 0),
        'platforms': platform_counts,
        'posts_today': posts_today,
        'failed_today': failed_today,
        'total_clips': sum(status_counts.values())
    }

def record_post(clip_id: int, platform: str, account: str, success: bool, error_message: str = None):
    """Record a post attempt"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''INSERT INTO posts (clip_id, platform, account, success, error_message)
                 VALUES (?, ?, ?, ?, ?)''',
              (clip_id, platform, account, 1 if success else 0, error_message))
    
    if success:
        update_clip_status(clip_id, 'posted')
    else:
        update_clip_status(clip_id, 'failed', error_message)
    
    conn.commit()
    conn.close()

# Initialize database on import
init_db()

