# 🔥 Firebase Setup Guide

Migrate from Supabase to Firebase for better Google ecosystem integration and scalability.

## 🎯 Why Firebase?

- ✅ **Google Integration** - Seamless with Google services
- ✅ **Highly Scalable** - Handles millions of documents
- ✅ **Real-time Updates** - Live data synchronization
- ✅ **Free Tier** - Generous free limits
- ✅ **Firebase Storage** - Built-in video hosting

---

## 📋 Step 1: Create Firebase Project

1. Go to https://console.firebase.google.com
2. Click **"Add Project"**
3. Enter project name (e.g., `clipfarm`)
4. Enable Google Analytics (optional)
5. Create project

---

## 📋 Step 2: Enable Services

### Enable Firestore Database:
1. Go to **Firestore Database**
2. Click **"Create Database"**
3. Start in **Production mode** (or Test mode for development)
4. Choose location (closest to you)
5. Enable

### Enable Firebase Storage:
1. Go to **Storage**
2. Click **"Get Started"**
3. Start in **Production mode**
4. Use same location as Firestore
5. Enable

---

## 📋 Step 3: Get Service Account Credentials

1. Go to **Project Settings** (gear icon)
2. **Service Accounts** tab
3. Click **"Generate New Private Key"**
4. Download JSON file
5. Save as `firebase-credentials.json` in project root

**⚠️ Important:** Never commit this file to git! (already in .gitignore)

---

## 📋 Step 4: Configure Storage Rules

Go to **Storage** → **Rules** tab, update to:

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

For development, you can use:
```javascript
allow read, write: if true;  // Public access (development only)
```

---

## 📋 Step 5: Set Environment Variables

### Local Worker (.env):
```env
USE_FIREBASE=true
FIREBASE_CREDENTIALS=firebase-credentials.json
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
USE_FIREBASE_STORAGE=true
```

### Vercel Dashboard:
Go to Vercel Dashboard → Settings → Environment Variables:

```
USE_FIREBASE=true
FIREBASE_CREDENTIALS=<base64-encoded-json>
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
SECRET_KEY=your-secret-key-here
```

**For Vercel:** Encode credentials JSON as base64:
```bash
# On Mac/Linux:
base64 firebase-credentials.json

# On Windows (PowerShell):
[Convert]::ToBase64String([IO.File]::ReadAllBytes("firebase-credentials.json"))
```

Then decode in code (see `firebase_db.py` for Vercel handling).

---

## 📋 Step 6: Install Dependencies

```bash
pip install firebase-admin
```

---

## 📋 Step 7: Test Connection

```python
from firebase_db import db
print("Database type:", db.db_type)
print("Using:", "Firebase" if db.use_firebase else "Supabase" if db.use_cloud else "SQLite")
```

---

## 🔄 Migration from Supabase

### Option A: Fresh Start (Recommended)
- Start using Firebase
- Old Supabase data stays
- New clips go to Firebase

### Option B: Migrate Data
```python
# Run once to migrate from Supabase to Firebase
from cloud_db import CloudDatabase as SupabaseDB
from firebase_db import FirebaseDatabase

supabase = SupabaseDB()
firebase = FirebaseDatabase()

# Migrate clips
clips = supabase.get_clips(limit=1000)
for clip in clips:
    firebase.add_clip(**{k: v for k, v in clip.items() if k != 'id'})
```

---

## 💰 Firebase Free Tier Limits

**Firestore:**
- ✅ 1GB storage
- ✅ 50K reads/day
- ✅ 20K writes/day
- ✅ 20K deletes/day

**Storage:**
- ✅ 5GB storage
- ✅ 1GB downloads/day
- ✅ Unlimited uploads

**For Scale:**
- Blaze Plan (pay-as-you-go) starts at $0.06/GB storage
- Very affordable for video hosting

---

## 🎯 What This Enables

### 1. Real-time Sync
- Dashboard updates instantly
- Worker status updates live
- No polling needed

### 2. Scalability
- Handles millions of clips
- Automatic scaling
- No server management

### 3. Google Integration
- Works with Google Cloud services
- Easy to add Google Analytics
- Integrate with other Google tools

### 4. Firebase Storage
- Built-in CDN
- Automatic optimization
- Public URLs for videos

---

## 🐛 Troubleshooting

### "Credentials not found"
- Verify `firebase-credentials.json` exists
- Check `FIREBASE_CREDENTIALS` path is correct
- For Vercel: Use base64-encoded credentials

### "Permission denied"
- Check Firestore rules allow read/write
- Verify Storage rules allow public read
- Check service account has correct permissions

### "Storage bucket not found"
- Verify bucket name matches project ID
- Check Storage is enabled in Firebase console
- Format: `your-project-id.appspot.com`

---

## ✅ Verification Checklist

- [ ] Firebase project created
- [ ] Firestore Database enabled
- [ ] Firebase Storage enabled
- [ ] Service account credentials downloaded
- [ ] Storage rules configured
- [ ] Environment variables set
- [ ] firebase-admin installed
- [ ] Test connection successful

---

## 🚀 Next Steps

1. **Set up Firebase** (see above)
2. **Configure environment variables**
3. **Test connection**
4. **Deploy to Vercel**
5. **Start worker**: `python automation_system.py`

---

**Your system is now Firebase-powered!** 🔥

