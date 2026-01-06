# 🚀 Firebase Storage Uploader - Signed URLs Guide

## ✅ What's Been Added

### `storage_uploader.py` - Complete Cloud Sync Solution
- ✅ Uploads clips to Firebase Storage automatically
- ✅ Generates **Signed URLs** (secure, temporary links)
- ✅ Updates Firestore with cloud URLs
- ✅ Integrated into main workflow

---

## 🔐 Why Signed URLs?

### Security Benefits:
- ✅ **7-day expiration** - Links stop working after a week
- ✅ **Private bucket** - Videos don't need to be publicly accessible
- ✅ **Bandwidth protection** - Prevents unauthorized access
- ✅ **Privacy** - Links expire automatically

### Workflow:
1. Worker generates clips locally
2. Videos uploaded to Firebase Storage
3. Signed URLs generated (valid 7 days)
4. URLs saved to Firestore
5. Dashboard streams videos instantly from cloud

---

## 📋 How It Works

### Automatic Integration:
After a clip is edited, the system automatically:

1. **Uploads to Firebase Storage**
   ```python
   cloud_url = upload_clip_after_editing(
       edited_video_path=edited_clip_path,
       clip_id=clip_id,
       filename="clip_001.mp4",
       platform="tiktok",
       caption="Your caption here"
   )
   ```

2. **Generates Signed URL** (valid for 7 days)
   - Secure temporary link
   - Works even with private bucket
   - Expires automatically

3. **Updates Firestore**
   - Saves `video_url` (signed URL)
   - Updates `storage_path`
   - Sets status to `ready`

---

## 🎯 Usage

### In Your Workflow:
The uploader is **automatically called** after editing in `main.py`:

```python
# After editing is done...
if edited_clip_path.exists():
    cloud_url = upload_clip_after_editing(
        edited_video_path=edited_clip_path,
        clip_id=clip_id,
        filename=f"{clip_name}.mp4",
        platform='tiktok',
        caption=caption
    )
```

### Manual Upload:
You can also call it manually:

```python
from storage_uploader import upload_clip_after_editing

cloud_url = upload_clip_after_editing(
    edited_video_path=Path("clips/clip_001.mp4"),
    clip_id="abc123",
    filename="clip_001.mp4",
    platform="tiktok",
    caption="Check this out! 🔥"
)
```

---

## ⚙️ Configuration

### Environment Variables:
```env
USE_FIREBASE=true
FIREBASE_SERVICE_ACCOUNT=<your-json-string>
FIREBASE_STORAGE_BUCKET=catzuko-4afef.appspot.com
```

### Signed URL Expiration:
Default: **7 days** (Firebase maximum)

To change:
```python
cloud_url = upload_clip_after_editing(
    edited_video_path=edited_clip_path,
    clip_id=clip_id,
    filename="clip.mp4",
    expiration_days=7  # Max 7 days
)
```

---

## 🔄 Complete Workflow

### Local Worker:
1. ✅ Downloads video
2. ✅ Transcribes with Whisper
3. ✅ Finds viral clips with Ollama
4. ✅ Edits clip (cuts, crops, adds captions)
5. ✅ **Uploads to Firebase Storage** ← NEW!
6. ✅ **Generates signed URL** ← NEW!
7. ✅ **Saves URL to Firestore** ← NEW!

### Vercel Dashboard:
1. ✅ Fetches clips from Firestore
2. ✅ Gets signed URLs
3. ✅ Streams videos instantly
4. ✅ Works on your phone!

---

## 💡 Pro Tips

### Why 7 Days?
- Google Cloud/Firebase maximum for signed URLs
- Clips reviewed within 1-2 days
- Posted within a week
- Links expire automatically (security)

### Benefits:
- ✅ **No public bucket needed** - More secure
- ✅ **Bandwidth protection** - Links expire
- ✅ **Privacy** - Temporary access only
- ✅ **Works on Vercel** - No local files needed

---

## 🐛 Troubleshooting

### "Upload failed"
- Check Firebase credentials are set
- Verify `USE_FIREBASE=true`
- Check Firebase Storage bucket exists
- Check file exists locally

### "Signed URL not generated"
- Verify Firebase Admin SDK initialized
- Check bucket permissions
- Verify service account has Storage Admin role

### "Dashboard shows no videos"
- Check Firestore has `video_url` field
- Verify signed URL hasn't expired
- Check browser console for errors

---

## ✅ Verification

### Test Upload:
```python
from storage_uploader import upload_clip_after_editing
from pathlib import Path

# Test with a clip
cloud_url = upload_clip_after_editing(
    edited_video_path=Path("clips/test_clip.mp4"),
    clip_id="test123",
    filename="test_clip.mp4",
    platform="tiktok"
)

print(f"Cloud URL: {cloud_url}")
```

### Check Firestore:
1. Go to Firebase Console
2. Open Firestore Database
3. Check `clips` collection
4. Verify `video_url` field exists
5. Copy URL and test in browser

---

## 🚀 Next Steps

1. ✅ **Run your worker** - Clips will auto-upload
2. ✅ **Check Firestore** - Verify URLs are saved
3. ✅ **Open dashboard** - Videos should stream instantly
4. ✅ **Test on phone** - Works from anywhere!

---

**Your remote dashboard now works perfectly!** 🎉

Videos are uploaded to Firebase Storage with signed URLs, making them accessible from your Vercel dashboard while keeping them secure.

