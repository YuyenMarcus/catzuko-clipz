# 🔥 Firebase + Vercel Deployment Guide

Complete guide for deploying your Firebase-powered Clipfarm dashboard to Vercel.

## ✅ What's Been Updated

### `models.py` - Complete Firebase Rewrite
- ✅ Uses Firebase Firestore for all metadata (clips, logs, settings, posts)
- ✅ Automatically uploads videos to Firebase Storage
- ✅ Makes videos publicly accessible for dashboard streaming
- ✅ Falls back to SQLite if Firebase not configured
- ✅ All functions work with Firebase or SQLite

### `web_dashboard.py` - Vercel-Ready
- ✅ Fetches data from Firebase Firestore
- ✅ Uses Firebase Storage URLs for video streaming
- ✅ Works on Vercel's serverless environment
- ✅ No local file system dependencies

---

## 🚀 Vercel Deployment Steps

### 1. Set Environment Variables

Go to Vercel Dashboard → Your Project → Settings → Environment Variables:

```
USE_FIREBASE=true
FIREBASE_CREDENTIALS_BASE64=<base64-encoded-json>
FIREBASE_STORAGE_BUCKET=catzuko-4afef.appspot.com
SECRET_KEY=<your-secret-key>
```

### 2. Encode Firebase Credentials

**Windows (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("firebase-key.json"))
```

**Mac/Linux:**
```bash
base64 firebase-key.json
```

Copy the output and paste as `FIREBASE_CREDENTIALS_BASE64` value.

### 3. Generate Secret Key

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy output and set as `SECRET_KEY`.

### 4. Deploy to Vercel

**Option A: GitHub Integration**
1. Push code to GitHub (already done)
2. Go to Vercel Dashboard
3. Import project from GitHub
4. Vercel auto-detects Python
5. Click Deploy

**Option B: Vercel CLI**
```bash
npm install -g vercel
vercel login
vercel
```

---

## 📋 How It Works

### Video Upload Flow:
1. **Clip generated locally** → `add_clip()` called
2. **Uploads to Firebase Storage** → `clips/{filename}.mp4`
3. **Makes public** → Gets public URL
4. **Saves to Firestore** → Metadata with `video_url`
5. **Dashboard fetches** → Uses Firebase Storage URL

### Dashboard Flow:
1. **Dashboard loads** → Fetches clips from Firestore
2. **Gets Firebase Storage URLs** → `video_url` field
3. **Streams videos** → Direct from Firebase Storage
4. **No local files needed** → Works on Vercel!

---

## ✅ Features Enabled

### Real-time Sync
- ✅ Dashboard updates instantly
- ✅ Worker status shows live
- ✅ Analytics update in real-time

### Video Streaming
- ✅ Videos stream from Firebase Storage
- ✅ Works on Vercel (no local filesystem)
- ✅ Public URLs for easy access

### Scalability
- ✅ Handles millions of clips
- ✅ Automatic scaling
- ✅ No server management

---

## 🧪 Testing Locally

Before deploying, test Firebase connection:

```python
from models import add_clip, get_clips

# Test adding a clip (will upload to Firebase Storage)
clip_id = add_clip(
    filename="test.mp4",
    video_path="clips/test.mp4",
    platform="tiktok",
    caption="Test clip"
)

# Test fetching clips
clips = get_clips(status='pending')
print(f"Found {len(clips)} pending clips")
```

---

## 🐛 Troubleshooting

### "Firebase credentials not found"
- Verify `FIREBASE_CREDENTIALS_BASE64` is set in Vercel
- Check base64 encoding is correct
- Ensure credentials JSON is valid

### "Videos not loading"
- Check Firebase Storage rules allow public read
- Verify `video_url` is set in Firestore
- Check browser console for CORS errors

### "Dashboard shows no clips"
- Verify Firestore has data
- Check `USE_FIREBASE=true` is set
- Check Vercel function logs

---

## 📊 Firebase Storage Rules

Update Firebase Storage rules for public access:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /clips/{allPaths=**} {
      allow read: if true;  // Public read
      allow write: if request.auth != null;  // Authenticated write
    }
  }
}
```

---

## 🎯 Next Steps

1. ✅ Set environment variables in Vercel
2. ✅ Deploy dashboard
3. ✅ Test video streaming
4. ✅ Start local worker
5. ✅ Check dashboard shows clips

---

**Your Firebase-powered dashboard is ready for Vercel!** 🔥

