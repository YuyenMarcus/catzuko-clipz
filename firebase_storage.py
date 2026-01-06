"""
Firebase Storage Integration
Uploads video clips to Firebase Storage
"""
import os
from pathlib import Path
from typing import Optional

# Storage configuration
USE_FIREBASE_STORAGE = os.environ.get('USE_FIREBASE_STORAGE', 'false').lower() == 'true'
FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET', '')

class FirebaseStorage:
    """Firebase Storage integration"""
    
    def __init__(self):
        try:
            import firebase_admin
            from firebase_admin import storage
            
            if not firebase_admin._apps:
                raise ValueError("Firebase Admin not initialized. Initialize Firebase first.")
            
            self.bucket = storage.bucket(FIREBASE_STORAGE_BUCKET) if FIREBASE_STORAGE_BUCKET else None
            
            if not self.bucket:
                raise ValueError("FIREBASE_STORAGE_BUCKET not configured")
                
        except ImportError:
            raise ImportError("firebase-admin required. Install with: pip install firebase-admin")
    
    def upload_clip(self, local_path: Path, remote_path: str = None) -> Optional[str]:
        """
        Upload a clip to Firebase Storage
        
        Args:
            local_path: Path to local video file
            remote_path: Remote path in bucket (defaults to filename)
            
        Returns:
            Public URL of uploaded file, or None if failed
        """
        if not local_path.exists():
            print(f"File not found: {local_path}")
            return None
        
        if remote_path is None:
            remote_path = f"clips/{local_path.name}"
        
        try:
            # Upload to Firebase Storage
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(str(local_path))
            
            # Make publicly accessible
            blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            print(f"Uploaded to Firebase Storage: {public_url}")
            return public_url
            
        except Exception as e:
            print(f"Error uploading to Firebase Storage: {e}")
            return None


class CloudStorageAdapter:
    """Storage adapter supporting Firebase and Supabase"""
    
    def __init__(self):
        self.storage = None
        
        if USE_FIREBASE_STORAGE:
            try:
                self.storage = FirebaseStorage()
                print("Using Firebase Storage")
                self.storage_type = 'firebase'
            except Exception as e:
                print(f"Failed to initialize Firebase Storage: {e}")
                print("Falling back to Supabase Storage or local only")
                USE_FIREBASE_STORAGE = False
        
        if not USE_FIREBASE_STORAGE:
            # Try Supabase Storage
            USE_CLOUD_STORAGE = os.environ.get('USE_CLOUD_STORAGE', 'false').lower() == 'true'
            if USE_CLOUD_STORAGE:
                try:
                    from cloud_storage import SupabaseStorage
                    self.storage = SupabaseStorage()
                    print("Using Supabase Storage")
                    self.storage_type = 'supabase'
                except Exception as e:
                    print(f"Failed to initialize Supabase Storage: {e}")
                    print("Clips will be stored locally only")
                    self.storage = None
            else:
                self.storage = None
                print("Cloud storage disabled. Clips stored locally only.")
    
    def upload_clip(self, local_path: Path, remote_path: str = None) -> Optional[str]:
        """
        Upload a clip to cloud storage
        
        Args:
            local_path: Path to local video file
            remote_path: Remote path (optional)
            
        Returns:
            Public URL if successful, None otherwise
        """
        if not self.storage:
            return None
        
        return self.storage.upload_clip(local_path, remote_path)


# Global storage instance
cloud_storage = CloudStorageAdapter()

def upload_clip(local_path: Path, remote_path: str = None) -> Optional[str]:
    """Upload a clip to cloud storage"""
    return cloud_storage.upload_clip(local_path, remote_path)

