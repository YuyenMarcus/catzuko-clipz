# ☁️ Cloud Sync Setup Guide

This guide will help you migrate from local SQLite to Supabase (PostgreSQL) for cloud sync between your Vercel dashboard and local worker.

## 🎯 Why Cloud Sync?

- ✅ **Remote Control**: Turn automation ON/OFF from your phone (Vercel dashboard)
- ✅ **Worker Status**: See if your PC is running (green/red dot)
- ✅ **Cloud Storage**: Videos accessible from anywhere
- ✅ **No 24/7 Server**: Your PC doesn't need to be on all the time

---

## 📋 Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Sign up (free tier available)
3. Create a new project
4. Note your:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **API Key** (anon/public key)

---

## 📋 Step 2: Run Database Migration

1. Go to Supabase Dashboard → SQL Editor
2. Copy contents of `supabase_migration.sql`
3. Paste and run in SQL Editor
4. Verify tables created: `clips`, `logs`, `settings`, `posts`, `heartbeats`

---

## 📋 Step 3: Create Storage Bucket

1. Go to Supabase Dashboard → Storage
2. Create new bucket: `clips`
3. Set to **Public** (for video access)
4. Note bucket name

---

## 📋 Step 4: Set Environment Variables

### On Your Local PC (Worker):

Create `.env` file:
```env
USE_CLOUD_DB=true
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_STORAGE_BUCKET=clips
USE_CLOUD_STORAGE=true
STORAGE_PROVIDER=supabase
```

### On Vercel (Dashboard):

Go to Vercel Dashboard → Project → Settings → Environment Variables:

```
USE_CLOUD_DB=true
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here
SECRET_KEY=your-secret-key-here
```

---

## 📋 Step 5: Install Dependencies

```bash
pip install supabase
```

---

## 📋 Step 6: Test Connection

```python
from cloud_db import db
print("Database type:", "Cloud" if db.use_cloud else "Local")
```

---

## ✅ What This Enables

### 1. Remote Control
- Toggle auto-posting ON/OFF from Vercel dashboard
- Settings sync to your local worker
- Worker checks cloud settings on startup

### 2. Worker Status Monitor
- Green dot = Worker online (heartbeat < 2 min old)
- Red dot = Worker offline (no heartbeat)
- Shows in dashboard header

### 3. Cloud Video Storage
- Clips automatically upload to Supabase Storage
- Videos accessible from Vercel dashboard
- Live Feed works on cloud!

### 4. Account Health Tracking
- See cookie expiration dates
- Upload new cookies via dashboard
- Alerts when cookies expire soon

### 5. Affiliate Link Rotation
- Rotates through multiple Whop links
- Avoids spam detection
- Configurable weights

---

## 🔄 Migration Process

### Option A: Fresh Start (Recommended)
1. Start using cloud database
2. Old local data stays in SQLite
3. New clips go to Supabase

### Option B: Migrate Existing Data
```python
# Run once to migrate
from models import get_clips as local_get_clips
from cloud_db import CloudDatabase

cloud_db = CloudDatabase()
local_clips = local_get_clips()

for clip in local_clips:
    cloud_db.add_clip(**clip)
```

---

## 🐛 Troubleshooting

### "Failed to connect to Supabase"
- Check SUPABASE_URL and SUPABASE_KEY
- Verify project is active
- Check network/firewall

### "Storage upload failed"
- Verify bucket exists and is public
- Check bucket name matches
- Verify file permissions

### "Worker status shows offline"
- Check heartbeat is running: `update_heartbeat()`
- Verify cloud database connection
- Check worker is actually running

---

## 💰 Cost Estimate

**Supabase Free Tier:**
- ✅ 500MB database
- ✅ 1GB storage
- ✅ 2GB bandwidth/month
- ✅ Unlimited API requests

**For 1000 clips (~50GB):**
- Upgrade to Pro: $25/month
- Or use Cloudflare R2 (cheaper)

---

## 🚀 Next Steps

1. ✅ Set up Supabase project
2. ✅ Run migration SQL
3. ✅ Create storage bucket
4. ✅ Set environment variables
5. ✅ Test connection
6. ✅ Deploy!

**Your system is now cloud-enabled!** 🎉

