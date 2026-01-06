"""
Firebase Storage Uploader with Signed URL Generation
Uploads clips to Firebase Storage and generates signed URLs for dashboard access
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    from firebase_admin import storage, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Warning: firebase-admin not installed. Install with: pip install firebase-admin")


def upload_and_get_url(local_file_path: str, destination_blob_name: str, expiration_days: int = 7) -> Optional[str]:
    """
    Uploads a file to Firebase Storage and returns a Signed URL valid for specified days.
    
    Args:
        local_file_path: Path to local video file
        destination_blob_name: Name for the file in Firebase Storage (e.g., "clip_001.mp4")
        expiration_days: Number of days the signed URL should be valid (max 7 for Firebase)
    
    Returns:
        Signed URL string, or None if upload fails
    """
    if not FIREBASE_AVAILABLE:
        print("⚠️ Firebase not available. Skipping upload.")
        return None
    
    if not os.path.exists(local_file_path):
        print(f"⚠️ File not found: {local_file_path}")
        return None
    
    try:
        bucket = storage.bucket()
        blob = bucket.blob(f"clips/{destination_blob_name}")
        
        # 1. Upload the video
        print(f"🚀 Uploading {destination_blob_name} to Firebase Storage...")
        blob.upload_from_filename(local_file_path)
        print(f"✅ Upload complete: {destination_blob_name}")
        
        # 2. Generate a Signed URL (Maximum allowed is 7 days)
        # This link works even if the bucket is private.
        # Signed URLs are more secure than public URLs
        expiration = timedelta(days=min(expiration_days, 7))  # Cap at 7 days max
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET"
        )
        
        print(f"✅ Generated signed URL (valid for {expiration_days} days)")
        return url
        
    except Exception as e:
        print(f"❌ Error uploading to Firebase Storage: {e}")
        return None


def sync_clip_to_cloud(clip_data: dict, local_path: str, expiration_days: int = 7) -> Optional[str]:
    """
    Uploads clip to Firebase Storage and updates Firestore document with cloud URL.
    
    Args:
        clip_data: Dictionary with clip metadata (must have 'id' and 'filename')
        local_path: Path to local video file
        expiration_days: Number of days signed URL should be valid (max 7)
    
    Returns:
        Cloud URL string, or None if sync fails
    """
    if not FIREBASE_AVAILABLE:
        print("⚠️ Firebase not available. Skipping cloud sync.")
        return None
    
    try:
        db = firestore.client()
        
        # Upload and get the signed URL
        cloud_url = upload_and_get_url(local_path, clip_data.get('filename', Path(local_path).name), expiration_days)
        
        if not cloud_url:
            print("⚠️ Failed to upload to Firebase Storage")
            return None
        
        # Update Firestore so the Dashboard sees the video
        clip_id = clip_data.get('id')
        if not clip_id:
            print("⚠️ Clip ID not found in clip_data")
            return None
        
        doc_ref = db.collection('clips').document(str(clip_id))
        update_data = {
            'video_url': cloud_url,
            'storage_path': f"clips/{clip_data.get('filename', Path(local_path).name)}",
            'storage_url': cloud_url,  # Alias for compatibility
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        # Only update status if it's not already set to a final state
        current_status = clip_data.get('status', 'pending')
        if current_status not in ['posted', 'failed']:
            update_data['status'] = 'ready'  # Ready for dashboard review
        
        doc_ref.update(update_data)
        
        print(f"✅ Cloud sync complete! Video available at signed URL")
        print(f"   URL expires in {expiration_days} days")
        return cloud_url
        
    except Exception as e:
        print(f"❌ Error syncing to cloud: {e}")
        return None


def upload_clip_after_editing(edited_video_path: Path, clip_id: str, filename: str, 
                               platform: str = None, caption: str = None) -> Optional[str]:
    """
    Convenience function to upload a clip after editing is complete.
    
    Args:
        edited_video_path: Path to the edited video file
        clip_id: Firestore document ID for the clip
        filename: Filename for storage (e.g., "clip_001.mp4")
        platform: Platform name (optional)
        caption: Caption text (optional)
    
    Returns:
        Cloud URL string, or None if upload fails
    """
    if not edited_video_path.exists():
        print(f"⚠️ Edited video not found: {edited_video_path}")
        return None
    
    clip_data = {
        'id': clip_id,
        'filename': filename,
        'platform': platform,
        'caption': caption
    }
    
    return sync_clip_to_cloud(clip_data, str(edited_video_path))


# Pro-Tip: Why "7 Days"?
# Google Cloud/Firebase Signed URLs have a maximum lifespan of 7 days.
# 
# The Workflow: Your worker generates clips, you review them on your phone 
# within a day or two, and you post them.
# 
# The Benefit: If someone steals your dashboard URL, the video links will 
# stop working after a week, protecting your bandwidth and privacy.

