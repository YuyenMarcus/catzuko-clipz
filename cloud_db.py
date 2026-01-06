"""
Cloud Database - Supabase PostgreSQL Integration
Replaces local SQLite for cloud sync between Vercel dashboard and local worker
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
import json

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: supabase-py not installed. Install with: pip install supabase")

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
USE_CLOUD_DB = os.environ.get('USE_CLOUD_DB', 'false').lower() == 'true'

class CloudDatabase:
    """Cloud database interface using Supabase"""
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase-py package required. Install with: pip install supabase")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables required")
        
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize tables in Supabase (run SQL migrations)"""
        # Note: Tables should be created via Supabase dashboard SQL editor
        # This is a fallback check
        pass
    
    # Clips operations
    def add_clip(self, filename: str, video_path: str, platform: str, caption: str = None,
                 caption_path: str = None, start_time: float = None, 
                 end_time: float = None, reason: str = None, storage_url: str = None) -> int:
        """Add a new clip to database"""
        data = {
            'filename': filename,
            'video_path': video_path,
            'caption_path': caption_path,
            'status': 'pending',
            'platform': platform,
            'caption': caption,
            'start_time': start_time,
            'end_time': end_time,
            'reason': reason,
            'storage_url': storage_url,
            'created_at': datetime.now().isoformat()
        }
        
        result = self.client.table('clips').insert(data).execute()
        return result.data[0]['id'] if result.data else None
    
    def update_clip_status(self, clip_id: int, status: str, error_message: str = None):
        """Update clip status"""
        update_data = {
            'status': status,
            'error_message': error_message
        }
        
        if status == 'posted':
            update_data['posted_at'] = datetime.now().isoformat()
        
        self.client.table('clips').update(update_data).eq('id', clip_id).execute()
    
    def get_clips(self, status: str = None, platform: str = None, limit: int = 100) -> List[Dict]:
        """Get clips with optional filters"""
        query = self.client.table('clips').select('*')
        
        if status:
            query = query.eq('status', status)
        
        if platform:
            query = query.eq('platform', platform)
        
        query = query.order('created_at', desc=True).limit(limit)
        result = query.execute()
        
        return result.data if result.data else []
    
    def get_clip_by_id(self, clip_id: int) -> Optional[Dict]:
        """Get a single clip by ID"""
        result = self.client.table('clips').select('*').eq('id', clip_id).execute()
        return result.data[0] if result.data else None
    
    # Logs operations
    def add_log(self, level: str, component: str, message: str):
        """Add a log entry"""
        data = {
            'level': level,
            'component': component,
            'message': message,
            'created_at': datetime.now().isoformat()
        }
        
        self.client.table('logs').insert(data).execute()
    
    def get_logs(self, component: str = None, limit: int = 100) -> List[Dict]:
        """Get recent logs"""
        query = self.client.table('logs').select('*')
        
        if component:
            query = query.eq('component', component)
        
        query = query.order('created_at', desc=True).limit(limit)
        result = query.execute()
        
        return result.data if result.data else []
    
    # Settings operations
    def get_setting(self, key: str, default: str = None) -> str:
        """Get a setting value"""
        result = self.client.table('settings').select('value').eq('key', key).execute()
        return result.data[0]['value'] if result.data else default
    
    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        data = {
            'key': key,
            'value': value,
            'updated_at': datetime.now().isoformat()
        }
        
        # Upsert
        self.client.table('settings').upsert(data).execute()
    
    # Analytics
    def get_analytics(self) -> Dict:
        """Get analytics summary"""
        # Get counts by status
        pending = self.client.table('clips').select('id', count='exact').eq('status', 'pending').execute()
        posted = self.client.table('clips').select('id', count='exact').eq('status', 'posted').execute()
        failed = self.client.table('clips').select('id', count='exact').eq('status', 'failed').execute()
        
        # Posts today
        today = datetime.now().date().isoformat()
        posts_today = self.client.table('posts').select('id', count='exact').gte('posted_at', today).eq('success', True).execute()
        
        return {
            'pending': pending.count if hasattr(pending, 'count') else len(pending.data) if pending.data else 0,
            'posted': posted.count if hasattr(posted, 'count') else len(posted.data) if posted.data else 0,
            'failed': failed.count if hasattr(failed, 'count') else len(failed.data) if failed.data else 0,
            'posts_today': posts_today.count if hasattr(posts_today, 'count') else len(posts_today.data) if posts_today.data else 0,
            'total_clips': (pending.count or 0) + (posted.count or 0) + (failed.count or 0)
        }
    
    # Posts operations
    def record_post(self, clip_id: int, platform: str, account: str, success: bool, error_message: str = None):
        """Record a post attempt"""
        data = {
            'clip_id': clip_id,
            'platform': platform,
            'account': account,
            'success': success,
            'error_message': error_message,
            'posted_at': datetime.now().isoformat()
        }
        
        self.client.table('posts').insert(data).execute()
        
        if success:
            self.update_clip_status(clip_id, 'posted')
        else:
            self.update_clip_status(clip_id, 'failed', error_message)
    
    # Heartbeat operations
    def update_heartbeat(self, worker_id: str = 'main'):
        """Update worker heartbeat"""
        data = {
            'worker_id': worker_id,
            'last_seen': datetime.now().isoformat(),
            'status': 'online'
        }
        
        self.client.table('heartbeats').upsert(data).execute()
    
    def get_worker_status(self, worker_id: str = 'main') -> Dict:
        """Get worker status"""
        result = self.client.table('heartbeats').select('*').eq('worker_id', worker_id).execute()
        
        if not result.data:
            return {'status': 'offline', 'last_seen': None}
        
        heartbeat = result.data[0]
        last_seen = datetime.fromisoformat(heartbeat['last_seen'])
        now = datetime.now()
        
        # Consider offline if no heartbeat in last 2 minutes
        is_online = (now - last_seen).total_seconds() < 120
        
        return {
            'status': 'online' if is_online else 'offline',
            'last_seen': heartbeat['last_seen']
        }


class DatabaseAdapter:
    """Adapter that switches between local SQLite, Supabase, and Firebase"""
    
    def __init__(self):
        # Check Firebase first (if enabled)
        self.use_firebase = os.environ.get('USE_FIREBASE', 'false').lower() == 'true'
        self.use_cloud = USE_CLOUD_DB and SUPABASE_AVAILABLE and not self.use_firebase
        
        if self.use_cloud:
            try:
                self.db = CloudDatabase()
                print("Using Supabase cloud database")
            except Exception as e:
                print(f"Failed to connect to Supabase: {e}")
                print("Falling back to local SQLite")
                self.use_cloud = False
        
        if not self.use_cloud:
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
    
    def add_clip(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.add_clip(*args, **kwargs)
        return self.local_funcs['add_clip'](*args, **kwargs)
    
    def update_clip_status(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.update_clip_status(*args, **kwargs)
        return self.local_funcs['update_clip_status'](*args, **kwargs)
    
    def get_clips(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.get_clips(*args, **kwargs)
        return self.local_funcs['get_clips'](*args, **kwargs)
    
    def get_clip_by_id(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.get_clip_by_id(*args, **kwargs)
        return self.local_funcs['get_clip_by_id'](*args, **kwargs)
    
    def add_log(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.add_log(*args, **kwargs)
        return self.local_funcs['add_log'](*args, **kwargs)
    
    def get_logs(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.get_logs(*args, **kwargs)
        return self.local_funcs['get_logs'](*args, **kwargs)
    
    def get_setting(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.get_setting(*args, **kwargs)
        return self.local_funcs['get_setting'](*args, **kwargs)
    
    def set_setting(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.set_setting(*args, **kwargs)
        return self.local_funcs['set_setting'](*args, **kwargs)
    
    def get_analytics(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.get_analytics(*args, **kwargs)
        return self.local_funcs['get_analytics'](*args, **kwargs)
    
    def record_post(self, *args, **kwargs):
        if self.use_cloud:
            return self.db.record_post(*args, **kwargs)
        return self.local_funcs['record_post'](*args, **kwargs)
    
    def update_heartbeat(self, worker_id: str = 'main'):
        """Update worker heartbeat (cloud only)"""
        if self.use_cloud:
            return self.db.update_heartbeat(worker_id)
    
    def get_worker_status(self, worker_id: str = 'main'):
        """Get worker status (cloud only)"""
        if self.use_cloud:
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

