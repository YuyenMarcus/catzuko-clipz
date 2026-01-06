# 🔥 Vercel + Firebase Setup Guide

Complete guide for deploying your Firebase-powered Clipfarm dashboard to Vercel using environment variables.

## 🔐 The Secret Key Strategy

Vercel cannot read your local `firebase-key.json` file. Instead, you'll store it as an environment variable.

---

## 📋 Step 1: Prepare Firebase Credentials

### Option A: JSON String Method (Recommended)

1. **Open `firebase-key.json`** on your computer
2. **Copy the entire contents** (everything inside the `{ }`)
3. **Go to Vercel** → Your Project → Settings → Environment Variables
4. **Create new variable:**
   - **Name:** `FIREBASE_SERVICE_ACCOUNT`
   - **Value:** Paste the entire JSON content
   - **Environment:** Production, Preview, Development (select all)
5. **Save**

### Option B: Base64 Encoding (Alternative)

If you prefer base64 encoding:

**Windows (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("firebase-key.json"))
```

**Mac/Linux:**
```bash
base64 firebase-key.json
```

Then set as `FIREBASE_CREDENTIALS_BASE64` in Vercel.

---

## 📋 Step 2: Set All Environment Variables

Go to Vercel Dashboard → Your Project → Settings → Environment Variables:

### Required:
```
USE_FIREBASE=true
FIREBASE_SERVICE_ACCOUNT=<paste-json-here>
FIREBASE_STORAGE_BUCKET=catzuko-4afef.appspot.com
SECRET_KEY=<your-secret-key>
```

### Generate Secret Key:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📊 Firestore Data Structure

Your data is stored in Firestore Collections:

### Collection: `clips`
One document per video clip:
```json
{
  "filename": "clip_001.mp4",
  "video_url": "https://firebasestorage.googleapis.com/...",
  "status": "pending",
  "platform": "tiktok",
  "caption": "Check this out! 🔥",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Collection: `logs`
Stores activity logs from your local worker:
```json
{
  "level": "INFO",
  "component": "yt-dlp",
  "message": "Downloaded video successfully",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Collection: `settings`
Stores dashboard toggles:
```json
{
  "auto_posting_enabled": "1",
  "auto_posting_tiktok": "1",
  "auto_posting_instagram": "0",
  "auto_posting_youtube": "1"
}
```

### Collection: `posts`
Tracks posted clips:
```json
{
  "clip_id": "abc123",
  "platform": "tiktok",
  "account": "account1",
  "success": true,
  "posted_at": "2024-01-01T12:00:00Z"
}
```

### Collection: `heartbeats`
Worker status monitoring:
```json
{
  "last_seen": "2024-01-01T12:00:00Z",
  "status": "online"
}
```

---

## 🚀 Deployment Workflow

### 1. Local Sync
Run your worker script locally:
```bash
python automation_system.py
```

This will:
- ✅ Upload `.mp4` clips to Firebase Storage
- ✅ Save metadata to Firestore
- ✅ Make videos publicly accessible

### 2. GitHub Push
Push your code (without the `.json` key!):
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin master
```

**✅ Verify:** `firebase-key.json` is in `.gitignore` and NOT committed.

### 3. Vercel Deploy

**Option A: Automatic (GitHub Integration)**
1. Go to Vercel Dashboard
2. Import project from GitHub
3. Vercel auto-detects Python
4. Environment variables are already set
5. Click **Deploy**

**Option B: Manual (Vercel CLI)**
```bash
npm install -g vercel
vercel login
vercel
```

### 4. Live Check

Visit your Vercel URL:
```
https://your-project.vercel.app
```

You should see:
- ✅ Clips uploaded from your local machine
- ✅ Firebase Storage URLs working
- ✅ Real-time data sync
- ✅ Dashboard fully functional

---

## 🧪 Testing Firebase Connection

### Test Locally:
```python
from models import initialize_firebase, firebase_db

initialize_firebase()
if firebase_db:
    print("✅ Firebase connected!")
    clips = firebase_db.collection('clips').limit(5).stream()
    for clip in clips:
        print(f"Clip: {clip.id}")
else:
    print("❌ Firebase not initialized")
```

### Test on Vercel:
1. Deploy to Vercel
2. Check Vercel Function Logs
3. Should see: `✅ Firebase initialized from Vercel environment variable`

---

## 🐛 Troubleshooting

### "Firebase credentials not found"
- ✅ Verify `FIREBASE_SERVICE_ACCOUNT` is set in Vercel
- ✅ Check JSON is valid (no extra quotes or escaping)
- ✅ Ensure environment is set for Production/Preview/Development

### "Videos not loading"
- ✅ Check Firebase Storage rules allow public read
- ✅ Verify `video_url` is set in Firestore documents
- ✅ Check browser console for CORS errors

### "Dashboard shows no clips"
- ✅ Verify Firestore has data (check Firebase Console)
- ✅ Check `USE_FIREBASE=true` is set
- ✅ Check Vercel function logs for errors

---

## 📋 Firebase Storage Rules

Update Firebase Storage rules for public access:

Go to Firebase Console → Storage → Rules:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /clips/{allPaths=**} {
      allow read: if true;  // Public read access
      allow write: if request.auth != null;  // Authenticated write
    }
  }
}
```

---

## ✅ Verification Checklist

- [ ] `firebase-key.json` is in `.gitignore`
- [ ] `FIREBASE_SERVICE_ACCOUNT` set in Vercel
- [ ] `USE_FIREBASE=true` set in Vercel
- [ ] `FIREBASE_STORAGE_BUCKET` set in Vercel
- [ ] `SECRET_KEY` generated and set
- [ ] Firebase Storage rules updated
- [ ] Code pushed to GitHub
- [ ] Vercel deployment successful
- [ ] Dashboard loads at Vercel URL
- [ ] Clips visible from local worker

---

## 🎯 Next Steps

1. ✅ Set environment variables in Vercel
2. ✅ Deploy dashboard
3. ✅ Test video streaming
4. ✅ Start local worker
5. ✅ Verify clips appear in dashboard

---

**Your Firebase-powered dashboard is ready for Vercel!** 🔥

The system automatically detects Vercel environment and uses `FIREBASE_SERVICE_ACCOUNT` to authenticate, while locally it uses `firebase-key.json`.

