"""
Database models for Clipfarm - Firebase Firestore & Storage Integration
Uses Firebase Firestore for metadata and Firebase Storage for video files
Falls back to SQLite if Firebase is not configured
"""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Check if Firebase should be used
USE_FIREBASE = os.environ.get('USE_FIREBASE', 'false').lower() == 'true'
USE_CLOUD_DB = os.environ.get('USE_CLOUD_DB', 'false').lower() == 'true'

# Firebase configuration
FIREBASE_CREDENTIALS_PATH = (
    os.environ.get('FIREBASE_CREDENTIALS') or 
    os.environ.get('FIREBASE_CREDENTIALS_FILE', 'firebase-key.json')
)
FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET', 'catzuko-4afef.appspot.com')

# Initialize Firebase if enabled
firebase_db = None
firebase_storage = None

if USE_FIREBASE:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, storage
        import json
        import tempfile
        
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            # Check if credentials are base64 encoded (Vercel/serverless)
            if os.environ.get('FIREBASE_CREDENTIALS_BASE64'):
                import base64
                cred_json = base64.b64decode(os.environ['FIREBASE_CREDENTIALS_BASE64']).decode('utf-8')
                cred_data = json.loads(cred_json)
                
                # Create temporary file for Vercel
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(cred_data, f)
                    temp_cred_path = f.name
                
                cred = credentials.Certificate(temp_cred_path)
                storage_bucket = FIREBASE_STORAGE_BUCKET or (cred_data.get('project_id', '') + '.appspot.com')
                firebase_admin.initialize_app(cred, {
                    'storageBucket': storage_bucket
                })
            else:
                # Try multiple credential file names
                possible_paths = [
                    FIREBASE_CREDENTIALS_PATH,
                    'firebase-key.json',
                    'firebase-credentials.json'
                ]
                
                cred_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        cred_path = path
                        break
                
                if cred_path:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': FIREBASE_STORAGE_BUCKET
                    })
                else:
                    # Try default credentials (Google Cloud environments)
                    try:
                        firebase_admin.initialize_app()
                    except:
                        print("Warning: Firebase credentials not found. Falling back to SQLite.")
                        USE_FIREBASE = False
        
        if USE_FIREBASE:
            firebase_db = firestore.client()
            firebase_storage = storage.bucket()
            print("✅ Firebase initialized - Using Firestore & Storage")
    except ImportError:
        print("Warning: firebase-admin not installed. Install with: pip install firebase-admin")
        USE_FIREBASE = False
    except Exception as e:
        print(f"Warning: Firebase initialization failed: {e}. Falling back to SQLite.")
        USE_FIREBASE = False

# SQLite fallback
if not USE_FIREBASE:
    import sqlite3
    DB_PATH = Path("clipfarm.db")
    
    def get_connection():
        """Get SQLite database connection"""
        return sqlite3.connect(str(DB_PATH))


def init_db():
    """Initialize database"""
    if USE_FIREBASE:
        print("Using Firebase Firestore - no initialization needed")
        return
    
    # Initialize SQLite
    conn = get_connection()
    c = conn.cursor()
    
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
                  error_message TEXT,
                  storage_url TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  level TEXT NOT NULL,
                  component TEXT NOT NULL,
                  message TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY,
                  value TEXT NOT NULL,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  clip_id INTEGER,
                  platform TEXT NOT NULL,
                  account TEXT,
                  posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  success BOOLEAN DEFAULT 1,
                  error_message TEXT,
                  FOREIGN KEY (clip_id) REFERENCES clips(id))''')
    
    c.execute('''INSERT OR IGNORE INTO settings (key, value) VALUES 
                 ('auto_posting_enabled', '0'),
                 ('auto_posting_tiktok', '0'),
                 ('auto_posting_instagram', '0'),
                 ('auto_posting_youtube', '0')''')
    
    conn.commit()
    conn.close()
    print("SQLite database initialized")


def add_clip(filename: str, video_path: str, platform: str, caption: str = None,
             caption_path: str = None, start_time: float = None, 
             end_time: float = None, reason: str = None, storage_url: str = None):
    """
    Add a new clip - Uploads to Firebase Storage and saves metadata to Firestore
    """
    if USE_FIREBASE and firebase_db and firebase_storage:
        try:
            video_path_obj = Path(video_path)
            video_url = storage_url
            
            # Upload video to Firebase Storage if file exists
            if video_path_obj.exists() and not storage_url:
                try:
                    blob = firebase_storage.blob(f"clips/{filename}")
                    blob.upload_from_filename(str(video_path_obj))
                    blob.make_public()  # Make publicly accessible for dashboard
                    video_url = blob.public_url
                    print(f"✅ Uploaded to Firebase Storage: {video_url}")
                except Exception as e:
                    print(f"⚠️ Firebase Storage upload failed: {e}")
                    video_url = None
            
            # Save metadata to Firestore
            doc_ref = firebase_db.collection('clips').document()
            doc_ref.set({
                'filename': filename,
                'video_path': video_path,
                'video_url': video_url,  # Firebase Storage public URL
                'caption_path': caption_path,
                'status': 'pending',
                'platform': platform,
                'caption': caption,
                'start_time': start_time,
                'end_time': end_time,
                'reason': reason,
                'storage_url': video_url,  # Alias for compatibility
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            return doc_ref.id
        except Exception as e:
            print(f"Firebase add_clip failed: {e}, falling back to SQLite")
    
    # Fallback to SQLite
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO clips 
                 (filename, video_path, caption_path, status, platform, caption, start_time, end_time, reason, storage_url)
                 VALUES (?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?)''',
              (filename, video_path, caption_path, platform, caption, start_time, end_time, reason, storage_url))
    clip_id = c.lastrowid
    conn.commit()
    conn.close()
    return clip_id


def update_clip_status(clip_id, status: str, error_message: str = None):
    """Update clip status"""
    if USE_FIREBASE and firebase_db:
        try:
            doc_ref = firebase_db.collection('clips').document(str(clip_id))
            update_data = {
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            if status == 'posted':
                update_data['posted_at'] = firestore.SERVER_TIMESTAMP
            if error_message:
                update_data['error_message'] = error_message
            doc_ref.update(update_data)
            return
        except Exception as e:
            print(f"Firebase update_clip_status failed: {e}, falling back to SQLite")
    
    # SQLite fallback
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
    if USE_FIREBASE and firebase_db:
        try:
            query = firebase_db.collection('clips')
            
            if status:
                query = query.where('status', '==', status)
            if platform:
                query = query.where('platform', '==', platform)
            
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            clips = []
            for doc in docs:
                clip_data = doc.to_dict()
                clip_data['id'] = doc.id
                
                # Convert Firestore timestamps
                if 'created_at' in clip_data and clip_data['created_at']:
                    if hasattr(clip_data['created_at'], 'timestamp'):
                        clip_data['created_at'] = datetime.fromtimestamp(
                            clip_data['created_at'].timestamp()
                        ).isoformat()
                
                if 'posted_at' in clip_data and clip_data['posted_at']:
                    if hasattr(clip_data['posted_at'], 'timestamp'):
                        clip_data['posted_at'] = datetime.fromtimestamp(
                            clip_data['posted_at'].timestamp()
                        ).isoformat()
                
                # Ensure video_url is available
                if 'video_url' not in clip_data and 'storage_url' in clip_data:
                    clip_data['video_url'] = clip_data['storage_url']
                
                clips.append(clip_data)
            
            return clips
        except Exception as e:
            print(f"Firebase get_clips failed: {e}, falling back to SQLite")
    
    # SQLite fallback
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


def get_clip_by_id(clip_id):
    """Get a single clip by ID"""
    if USE_FIREBASE and firebase_db:
        try:
            doc = firebase_db.collection('clips').document(str(clip_id)).get()
            if doc.exists:
                clip_data = doc.to_dict()
                clip_data['id'] = doc.id
                return clip_data
            return None
        except Exception as e:
            print(f"Firebase get_clip_by_id failed: {e}, falling back to SQLite")
    
    # SQLite fallback
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM clips WHERE id = ?", (clip_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def add_log(level: str, component: str, message: str):
    """Add a log entry"""
    if USE_FIREBASE and firebase_db:
        try:
            firebase_db.collection('logs').add({
                'level': level,
                'component': component,
                'message': message,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            return
        except Exception as e:
            print(f"Firebase add_log failed: {e}, falling back to SQLite")
    
    # SQLite fallback
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO logs (level, component, message)
                 VALUES (?, ?, ?)''', (level, component, message))
    conn.commit()
    conn.close()


def get_logs(component: str = None, limit: int = 100) -> List[Dict]:
    """Get recent logs"""
    if USE_FIREBASE and firebase_db:
        try:
            query = firebase_db.collection('logs')
            if component:
                query = query.where('component', '==', component)
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            
            logs = []
            for doc in query.stream():
                log_data = doc.to_dict()
                log_data['id'] = doc.id
                if 'created_at' in log_data and log_data['created_at']:
                    if hasattr(log_data['created_at'], 'timestamp'):
                        log_data['created_at'] = datetime.fromtimestamp(
                            log_data['created_at'].timestamp()
                        ).isoformat()
                logs.append(log_data)
            return logs
        except Exception as e:
            print(f"Firebase get_logs failed: {e}, falling back to SQLite")
    
    # SQLite fallback
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
    if USE_FIREBASE and firebase_db:
        try:
            doc = firebase_db.collection('settings').document(key).get()
            if doc.exists:
                return doc.to_dict().get('value', default)
            return default
        except Exception as e:
            print(f"Firebase get_setting failed: {e}, falling back to SQLite")
    
    # SQLite fallback
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(key: str, value: str):
    """Set a setting value"""
    if USE_FIREBASE and firebase_db:
        try:
            firebase_db.collection('settings').document(key).set({
                'value': value,
                'updated_at': firestore.SERVER_TIMESTAMP
            }, merge=True)
            return
        except Exception as e:
            print(f"Firebase set_setting failed: {e}, falling back to SQLite")
    
    # SQLite fallback
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO settings (key, value, updated_at)
                 VALUES (?, ?, CURRENT_TIMESTAMP)''', (key, value))
    conn.commit()
    conn.close()


def get_analytics() -> Dict:
    """Get analytics summary - Real-time stats from Firestore"""
    if USE_FIREBASE and firebase_db:
        try:
            # Get counts by status
            pending_query = firebase_db.collection('clips').where('status', '==', 'pending')
            posted_query = firebase_db.collection('clips').where('status', '==', 'posted')
            failed_query = firebase_db.collection('clips').where('status', '==', 'failed')
            processing_query = firebase_db.collection('clips').where('status', '==', 'processing')
            
            pending_count = len(list(pending_query.stream()))
            posted_count = len(list(posted_query.stream()))
            failed_count = len(list(failed_query.stream()))
            processing_count = len(list(processing_query.stream()))
            
            # Count by platform
            all_clips = firebase_db.collection('clips').stream()
            platform_counts = {}
            for clip in all_clips:
                platform = clip.to_dict().get('platform', 'unknown')
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Posts today
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            posts_today_query = firebase_db.collection('posts').where('posted_at', '>=', today_start).where('success', '==', True)
            posts_today_count = len(list(posts_today_query.stream()))
            
            # Failed posts today
            failed_today_query = firebase_db.collection('posts').where('posted_at', '>=', today_start).where('success', '==', False)
            failed_today_count = len(list(failed_today_query.stream()))
            
            return {
                'pending': pending_count,
                'posted': posted_count,
                'failed': failed_count,
                'processing': processing_count,
                'platforms': platform_counts,
                'posts_today': posts_today_count,
                'failed_today': failed_today_count,
                'total_clips': pending_count + posted_count + failed_count + processing_count
            }
        except Exception as e:
            print(f"Firebase get_analytics failed: {e}, falling back to SQLite")
    
    # SQLite fallback
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT status, COUNT(*) FROM clips GROUP BY status")
    status_counts = dict(c.fetchall())
    
    c.execute("SELECT platform, COUNT(*) FROM clips GROUP BY platform")
    platform_counts = dict(c.fetchall())
    
    c.execute('''SELECT COUNT(*) FROM posts 
                 WHERE DATE(posted_at) = DATE('now') AND success = 1''')
    posts_today = c.fetchone()[0]
    
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


def record_post(clip_id, platform: str, account: str, success: bool, error_message: str = None):
    """Record a post attempt"""
    if USE_FIREBASE and firebase_db:
        try:
            firebase_db.collection('posts').add({
                'clip_id': str(clip_id),
                'platform': platform,
                'account': account,
                'success': success,
                'error_message': error_message,
                'posted_at': firestore.SERVER_TIMESTAMP
            })
            
            if success:
                update_clip_status(clip_id, 'posted')
            else:
                update_clip_status(clip_id, 'failed', error_message)
            return
        except Exception as e:
            print(f"Firebase record_post failed: {e}, falling back to SQLite")
    
    # SQLite fallback
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


def update_worker_heartbeat(worker_id: str = 'main'):
    """Update worker heartbeat (Firebase only)"""
    if USE_FIREBASE and firebase_db:
        try:
            firebase_db.collection('heartbeats').document(worker_id).set({
                'last_seen': firestore.SERVER_TIMESTAMP,
                'status': 'online'
            }, merge=True)
        except Exception as e:
            print(f"Firebase update_heartbeat failed: {e}")


def get_worker_status(worker_id: str = 'main') -> Dict:
    """Get worker status (Firebase only)"""
    if USE_FIREBASE and firebase_db:
        try:
            doc = firebase_db.collection('heartbeats').document(worker_id).get()
            if not doc.exists:
                return {'status': 'offline', 'last_seen': None}
            
            heartbeat = doc.to_dict()
            last_seen = heartbeat.get('last_seen')
            
            if last_seen:
                if hasattr(last_seen, 'timestamp'):
                    last_seen_dt = datetime.fromtimestamp(last_seen.timestamp())
                else:
                    last_seen_dt = last_seen
                
                now = datetime.now()
                is_online = (now - last_seen_dt).total_seconds() < 120
                
                return {
                    'status': 'online' if is_online else 'offline',
                    'last_seen': last_seen_dt.isoformat() if hasattr(last_seen_dt, 'isoformat') else str(last_seen_dt)
                }
            
            return {'status': 'offline', 'last_seen': None}
        except Exception as e:
            print(f"Firebase get_worker_status failed: {e}")
    
    return {'status': 'unknown', 'last_seen': None}


# Initialize database on import
init_db()
