"""
Firebase Database - Firestore Integration
Replaces Supabase/SQLite for cloud sync between Vercel dashboard and local worker
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
import json

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Warning: firebase-admin not installed. Install with: pip install firebase-admin")

# Firebase configuration
USE_FIREBASE = os.environ.get('USE_FIREBASE', 'false').lower() == 'true'
# Try multiple possible credential file names
FIREBASE_CREDENTIALS_PATH = (
    os.environ.get('FIREBASE_CREDENTIALS') or 
    os.environ.get('FIREBASE_CREDENTIALS_FILE', 'firebase-key.json')
)
FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET', 'catzuko-4afef.appspot.com')

class FirebaseDatabase:
    """Firebase Firestore database interface"""
    
    def __init__(self):
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin package required. Install with: pip install firebase-admin")
        
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
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
            
            # Check if credentials are base64 encoded (Vercel/serverless)
            if os.environ.get('FIREBASE_CREDENTIALS_BASE64'):
                import base64
                import json
                import tempfile
                
                cred_json = base64.b64decode(os.environ['FIREBASE_CREDENTIALS_BASE64']).decode('utf-8')
                cred_data = json.loads(cred_json)
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(cred_data, f)
                    temp_cred_path = f.name
                
                cred = credentials.Certificate(temp_cred_path)
                storage_bucket = FIREBASE_STORAGE_BUCKET or (cred_data.get('project_id', '') + '.appspot.com')
                firebase_admin.initialize_app(cred, {
                    'storageBucket': storage_bucket
                })
            elif cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': FIREBASE_STORAGE_BUCKET
                })
            else:
                # Try using default credentials (for Google Cloud environments)
                try:
                    firebase_admin.initialize_app()
                except:
                    raise ValueError(f"Firebase credentials not found. Tried: {possible_paths}. Set FIREBASE_CREDENTIALS or FIREBASE_CREDENTIALS_BASE64 environment variable.")
        
        self.db = firestore.client()
        self._init_collections()
    
    def _init_collections(self):
        """Initialize collections if needed"""
        # Firestore creates collections automatically on first write
        # No explicit initialization needed
        pass
    
    # Clips operations
    def add_clip(self, filename: str, video_path: str, platform: str, caption: str = None,
                 caption_path: str = None, start_time: float = None, 
                 end_time: float = None, reason: str = None, storage_url: str = None) -> str:
        """
        Add a new clip to database
        Uploads video to Firebase Storage and saves metadata to Firestore
        """
        from pathlib import Path
        from firebase_admin import storage
        
        video_path_obj = Path(video_path)
        video_url = storage_url
        
        # Upload video to Firebase Storage if file exists and not already uploaded
        if video_path_obj.exists() and not storage_url:
            try:
                bucket = storage.bucket()
                # Upload to clips/{filename}
                blob = bucket.blob(f"clips/{filename}")
                blob.upload_from_filename(str(video_path_obj))
                blob.make_public()  # Make publicly accessible for dashboard streaming
                video_url = blob.public_url
                print(f"Uploaded to Firebase Storage: {video_url}")
            except Exception as e:
                print(f"Firebase Storage upload failed: {e}")
                # Continue without storage URL
        
        # Save metadata to Firestore
        doc_ref = self.db.collection('clips').document()
        
        data = {
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
        }
        
        doc_ref.set(data)
        return doc_ref.id
    
    def update_clip_status(self, clip_id: str, status: str, error_message: str = None):
        """Update clip status"""
        doc_ref = self.db.collection('clips').document(clip_id)
        
        update_data = {
            'status': status,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        if status == 'posted':
            update_data['posted_at'] = firestore.SERVER_TIMESTAMP
        
        if error_message:
            update_data['error_message'] = error_message
        
        doc_ref.update(update_data)
    
    def get_clips(self, status: str = None, platform: str = None, limit: int = 100) -> List[Dict]:
        """Get clips with optional filters - returns clips with Firebase Storage URLs"""
        query = self.db.collection('clips')
        
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
            # Convert Firestore timestamps to ISO strings
            if 'created_at' in clip_data:
                if hasattr(clip_data['created_at'], 'isoformat'):
                    clip_data['created_at'] = clip_data['created_at'].isoformat()
                elif hasattr(clip_data['created_at'], 'timestamp'):
                    clip_data['created_at'] = datetime.fromtimestamp(clip_data['created_at'].timestamp()).isoformat()
            
            if 'posted_at' in clip_data and clip_data['posted_at']:
                if hasattr(clip_data['posted_at'], 'isoformat'):
                    clip_data['posted_at'] = clip_data['posted_at'].isoformat()
                elif hasattr(clip_data['posted_at'], 'timestamp'):
                    clip_data['posted_at'] = datetime.fromtimestamp(clip_data['posted_at'].timestamp()).isoformat()
            
            # Ensure video_url is available (from Firebase Storage)
            if 'video_url' not in clip_data and 'storage_url' in clip_data:
                clip_data['video_url'] = clip_data['storage_url']
            
            clips.append(clip_data)
        
        return clips
    
    def get_clip_by_id(self, clip_id: str) -> Optional[Dict]:
        """Get a single clip by ID"""
        doc = self.db.collection('clips').document(clip_id).get()
        
        if doc.exists:
            clip_data = doc.to_dict()
            clip_data['id'] = doc.id
            return clip_data
        return None
    
    # Logs operations
    def add_log(self, level: str, component: str, message: str):
        """Add a log entry"""
        self.db.collection('logs').add({
            'level': level,
            'component': component,
            'message': message,
            'created_at': firestore.SERVER_TIMESTAMP
        })
    
    def get_logs(self, component: str = None, limit: int = 100) -> List[Dict]:
        """Get recent logs"""
        query = self.db.collection('logs')
        
        if component:
            query = query.where('component', '==', component)
        
        query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        
        logs = []
        for doc in docs:
            log_data = doc.to_dict()
            log_data['id'] = doc.id
            if 'created_at' in log_data and hasattr(log_data['created_at'], 'isoformat'):
                log_data['created_at'] = log_data['created_at'].isoformat()
            logs.append(log_data)
        
        return logs
    
    # Settings operations
    def get_setting(self, key: str, default: str = None) -> str:
        """Get a setting value"""
        doc = self.db.collection('settings').document(key).get()
        
        if doc.exists:
            return doc.to_dict().get('value', default)
        return default
    
    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        self.db.collection('settings').document(key).set({
            'value': value,
            'updated_at': firestore.SERVER_TIMESTAMP
        }, merge=True)
    
    # Analytics
    def get_analytics(self) -> Dict:
        """Get analytics summary - fetches real-time stats from Firestore"""
        # Get counts by status
        pending_query = self.db.collection('clips').where('status', '==', 'pending')
        posted_query = self.db.collection('clips').where('status', '==', 'posted')
        failed_query = self.db.collection('clips').where('status', '==', 'failed')
        processing_query = self.db.collection('clips').where('status', '==', 'processing')
        
        # Note: Firestore doesn't have count() in free tier, so we fetch and count
        # For better performance with large datasets, consider using aggregation queries (requires Blaze plan)
        pending_count = len(list(pending_query.stream()))
        posted_count = len(list(posted_query.stream()))
        failed_count = len(list(failed_query.stream()))
        processing_count = len(list(processing_query.stream()))
        
        # Count by platform
        all_clips = self.db.collection('clips').stream()
        platform_counts = {}
        for clip in all_clips:
            platform = clip.to_dict().get('platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Posts today
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        posts_today_query = self.db.collection('posts').where('posted_at', '>=', today_start).where('success', '==', True)
        posts_today_count = len(list(posts_today_query.stream()))
        
        # Failed posts today
        failed_today_query = self.db.collection('posts').where('posted_at', '>=', today_start).where('success', '==', False)
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
    
    # Posts operations
    def record_post(self, clip_id: str, platform: str, account: str, success: bool, error_message: str = None):
        """Record a post attempt"""
        self.db.collection('posts').add({
            'clip_id': clip_id,
            'platform': platform,
            'account': account,
            'success': success,
            'error_message': error_message,
            'posted_at': firestore.SERVER_TIMESTAMP
        })
        
        if success:
            self.update_clip_status(clip_id, 'posted')
        else:
            self.update_clip_status(clip_id, 'failed', error_message)
    
    # Heartbeat operations
    def update_heartbeat(self, worker_id: str = 'main'):
        """Update worker heartbeat"""
        self.db.collection('heartbeats').document(worker_id).set({
            'last_seen': firestore.SERVER_TIMESTAMP,
            'status': 'online'
        }, merge=True)
    
    def get_worker_status(self, worker_id: str = 'main') -> Dict:
        """Get worker status"""
        doc = self.db.collection('heartbeats').document(worker_id).get()
        
        if not doc.exists:
            return {'status': 'offline', 'last_seen': None}
        
        heartbeat = doc.to_dict()
        last_seen = heartbeat.get('last_seen')
        
        if last_seen:
            if hasattr(last_seen, 'timestamp'):
                # Firestore timestamp
                last_seen_dt = datetime.fromtimestamp(last_seen.timestamp())
            else:
                last_seen_dt = last_seen
            
            now = datetime.now()
            # Consider offline if no heartbeat in last 2 minutes
            is_online = (now - last_seen_dt).total_seconds() < 120
            
            return {
                'status': 'online' if is_online else 'offline',
                'last_seen': last_seen_dt.isoformat() if hasattr(last_seen_dt, 'isoformat') else str(last_seen_dt)
            }
        
        return {'status': 'offline', 'last_seen': None}


class DatabaseAdapter:
    """Adapter that switches between local SQLite, Supabase, and Firebase"""
    
    def __init__(self):
        # Priority: Firebase > Supabase > Local SQLite
        self.use_firebase = USE_FIREBASE and FIREBASE_AVAILABLE
        self.use_cloud = os.environ.get('USE_CLOUD_DB', 'false').lower() == 'true'
        
        if self.use_firebase:
            try:
                self.db = FirebaseDatabase()
                print("Using Firebase Firestore database")
                self.db_type = 'firebase'
            except Exception as e:
                print(f"Failed to connect to Firebase: {e}")
                print("Falling back to Supabase or local SQLite")
                self.use_firebase = False
        
        if not self.use_firebase and self.use_cloud:
            # Try Supabase
            try:
                from cloud_db import CloudDatabase
                self.db = CloudDatabase()
                print("Using Supabase cloud database")
                self.db_type = 'supabase'
            except Exception as e:
                print(f"Failed to connect to Supabase: {e}")
                print("Falling back to local SQLite")
                self.use_cloud = False
        
        if not self.use_firebase and not self.use_cloud:
            # Fallback to local SQLite
            from models import (
                add_clip as local_add_clip,
                update_clip_status as local_update_clip_status,
                get_clips as local_get_clips,
                get_clip_by_id as local_get_clip_by_id,
                add_log as local_add_log,
                get_logs as local_get_logs,
                get_setting as local_get_setting,
                set_setting as local_set_setting,
                get_analytics as local_get_analytics,
                record_post as local_record_post
            )
            
            self.local_funcs = {
                'add_clip': local_add_clip,
                'update_clip_status': local_update_clip_status,
                'get_clips': local_get_clips,
                'get_clip_by_id': local_get_clip_by_id,
                'add_log': local_add_log,
                'get_logs': local_get_logs,
                'get_setting': local_get_setting,
                'set_setting': local_set_setting,
                'get_analytics': local_get_analytics,
                'record_post': local_record_post
            }
            print("Using local SQLite database")
            self.db_type = 'sqlite'
    
    def add_clip(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.add_clip(*args, **kwargs)
        return self.local_funcs['add_clip'](*args, **kwargs)
    
    def update_clip_status(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.update_clip_status(*args, **kwargs)
        return self.local_funcs['update_clip_status'](*args, **kwargs)
    
    def get_clips(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.get_clips(*args, **kwargs)
        return self.local_funcs['get_clips'](*args, **kwargs)
    
    def get_clip_by_id(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.get_clip_by_id(*args, **kwargs)
        return self.local_funcs['get_clip_by_id'](*args, **kwargs)
    
    def add_log(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.add_log(*args, **kwargs)
        return self.local_funcs['add_log'](*args, **kwargs)
    
    def get_logs(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.get_logs(*args, **kwargs)
        return self.local_funcs['get_logs'](*args, **kwargs)
    
    def get_setting(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.get_setting(*args, **kwargs)
        return self.local_funcs['get_setting'](*args, **kwargs)
    
    def set_setting(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.set_setting(*args, **kwargs)
        return self.local_funcs['set_setting'](*args, **kwargs)
    
    def get_analytics(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.get_analytics(*args, **kwargs)
        return self.local_funcs['get_analytics'](*args, **kwargs)
    
    def record_post(self, *args, **kwargs):
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.record_post(*args, **kwargs)
        return self.local_funcs['record_post'](*args, **kwargs)
    
    def update_heartbeat(self, worker_id: str = 'main'):
        """Update worker heartbeat (cloud only)"""
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.update_heartbeat(worker_id)
    
    def get_worker_status(self, worker_id: str = 'main'):
        """Get worker status (cloud only)"""
        if self.use_firebase or (hasattr(self, 'db') and self.db_type in ['firebase', 'supabase']):
            return self.db.get_worker_status(worker_id)
        return {'status': 'unknown', 'last_seen': None}


# Global database instance
db = DatabaseAdapter()

# Export functions for compatibility
def add_clip(*args, **kwargs):
    return db.add_clip(*args, **kwargs)

def update_clip_status(*args, **kwargs):
    return db.update_clip_status(*args, **kwargs)

def get_clips(*args, **kwargs):
    return db.get_clips(*args, **kwargs)

def get_clip_by_id(*args, **kwargs):
    return db.get_clip_by_id(*args, **kwargs)

def add_log(*args, **kwargs):
    return db.add_log(*args, **kwargs)

def get_logs(*args, **kwargs):
    return db.get_logs(*args, **kwargs)

def get_setting(*args, **kwargs):
    return db.get_setting(*args, **kwargs)

def set_setting(*args, **kwargs):
    return db.set_setting(*args, **kwargs)

def get_analytics(*args, **kwargs):
    return db.get_analytics(*args, **kwargs)

def record_post(*args, **kwargs):
    return db.record_post(*args, **kwargs)

def update_heartbeat(*args, **kwargs):
    return db.update_heartbeat(*args, **kwargs)

def get_worker_status(*args, **kwargs):
    return db.get_worker_status(*args, **kwargs)

