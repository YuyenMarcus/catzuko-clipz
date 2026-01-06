"""
Cloud Storage Integration
Uploads video clips to cloud storage (Supabase Storage or Cloudflare R2)
"""
import os
from pathlib import Path
from typing import Optional
import json

# Storage configuration
USE_CLOUD_STORAGE = os.environ.get('USE_CLOUD_STORAGE', 'false').lower() == 'true'
STORAGE_PROVIDER = os.environ.get('STORAGE_PROVIDER', 'supabase')  # 'supabase' or 'cloudflare_r2'

class SupabaseStorage:
    """Supabase Storage integration"""
    
    def __init__(self):
        try:
            from supabase import create_client
            SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
            SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
            
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY required for Supabase Storage")
            
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.bucket_name = os.environ.get('SUPABASE_STORAGE_BUCKET', 'clips')
        except ImportError:
            raise ImportError("supabase-py required. Install with: pip install supabase")
    
    def upload_clip(self, local_path: Path, remote_path: str = None) -> Optional[str]:
        """
        Upload a clip to Supabase Storage
        
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
            remote_path = local_path.name
        
        try:
            # Read file
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            # Upload to Supabase Storage
            result = self.client.storage.from_(self.bucket_name).upload(
                remote_path,
                file_data,
                file_options={"content-type": "video/mp4", "upsert": "true"}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(remote_path)
            
            print(f"Uploaded to Supabase: {public_url}")
            return public_url
            
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
            return None


class CloudflareR2Storage:
    """Cloudflare R2 Storage integration"""
    
    def __init__(self):
        try:
            import boto3
            from botocore.config import Config
            
            self.account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '')
            self.access_key_id = os.environ.get('CLOUDFLARE_R2_ACCESS_KEY_ID', '')
            self.secret_access_key = os.environ.get('CLOUDFLARE_R2_SECRET_ACCESS_KEY', '')
            self.bucket_name = os.environ.get('CLOUDFLARE_R2_BUCKET', 'clips')
            self.public_url = os.environ.get('CLOUDFLARE_R2_PUBLIC_URL', '')
            
            if not all([self.account_id, self.access_key_id, self.secret_access_key]):
                raise ValueError("Cloudflare R2 credentials required")
            
            # Configure S3 client for R2
            self.s3_client = boto3.client(
                's3',
                endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                config=Config(signature_version='s3v4')
            )
            
        except ImportError:
            raise ImportError("boto3 required. Install with: pip install boto3")
    
    def upload_clip(self, local_path: Path, remote_path: str = None) -> Optional[str]:
        """
        Upload a clip to Cloudflare R2
        
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
            remote_path = local_path.name
        
        try:
            # Upload to R2
            self.s3_client.upload_file(
                str(local_path),
                self.bucket_name,
                remote_path,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
            
            # Construct public URL
            if self.public_url:
                public_url = f"{self.public_url.rstrip('/')}/{remote_path}"
            else:
                public_url = f"https://{self.bucket_name}.r2.dev/{remote_path}"
            
            print(f"Uploaded to Cloudflare R2: {public_url}")
            return public_url
            
        except Exception as e:
            print(f"Error uploading to R2: {e}")
            return None


class CloudStorage:
    """Cloud storage adapter supporting Firebase and Supabase"""
    
    def __init__(self):
        self.storage = None
        
        # Check Firebase first (if enabled)
        USE_FIREBASE_STORAGE = os.environ.get('USE_FIREBASE_STORAGE', 'false').lower() == 'true'
        
        if USE_FIREBASE_STORAGE:
            try:
                from firebase_storage import FirebaseStorage
                self.storage = FirebaseStorage()
                print("Using Firebase Storage")
            except Exception as e:
                print(f"Failed to initialize Firebase Storage: {e}")
                USE_FIREBASE_STORAGE = False
        
        if not USE_FIREBASE_STORAGE and USE_CLOUD_STORAGE:
            try:
                if STORAGE_PROVIDER == 'supabase':
                    self.storage = SupabaseStorage()
                    print("Using Supabase Storage")
                elif STORAGE_PROVIDER == 'cloudflare_r2':
                    self.storage = CloudflareR2Storage()
                    print("Using Cloudflare R2 Storage")
                else:
                    print(f"Unknown storage provider: {STORAGE_PROVIDER}")
            except Exception as e:
                print(f"Failed to initialize cloud storage: {e}")
                print("Clips will be stored locally only")
                self.storage = None
    
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
cloud_storage = CloudStorage()

def upload_clip(local_path: Path, remote_path: str = None) -> Optional[str]:
    """Upload a clip to cloud storage"""
    return cloud_storage.upload_clip(local_path, remote_path)

