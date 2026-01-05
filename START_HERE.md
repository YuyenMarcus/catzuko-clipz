# 🚀 CLIPFARM - START HERE

Your channel ID `UCXR42GnrCHSxWjBuASCroQw` is already configured!

## 🎛️ WEB DASHBOARD (NEW!)

Access a private web interface to monitor and control everything:

```bash
python web_dashboard.py
```

Then open: **http://localhost:5000**

See all clips, status, history, and controls in one place!

---

## ⚡ QUICK START (3 Steps)

### Step 1: Install Dependencies (5 minutes)

```bash
pip install -r requirements.txt
```

**Also install:**
- **FFmpeg**: Download from https://ffmpeg.org/download.html (Windows) or `brew install ffmpeg` (Mac)
- **Ollama**: Download from https://ollama.ai, then run: `ollama pull llama3.1`

### Step 2: Setup Accounts (One-Time, 10 minutes)

**For AUTO-POSTING (optional but recommended):**

```bash
python setup_accounts.py
```

This will:
- Open browser windows for TikTok, Instagram, YouTube
- You login manually once
- Saves cookies for automatic posting later

**If you skip this**, clips will still be generated and saved to `ready_to_post/` folders for manual posting.

### Step 3: Run!

**Option A: Full Automation (24/7 with auto-posting)**
```bash
python automation_system.py
```
or double-click: `run_automation.bat`

**Option B: Generate Clips Only (no auto-posting)**
```bash
python main.py
```
or double-click: `run_daily.bat`

**Option C: Generate Once and Exit**
```bash
python automation_system.py --run-once --no-auto-post
```

---

## 📋 WHAT HAPPENS

### Daily Content Generation (Runs at 2 AM or manually):
1. ✅ Checks your YouTube channel for new videos
2. ✅ Downloads new videos automatically
3. ✅ Transcribes using Whisper AI
4. ✅ Finds 3-5 viral clips per video using Ollama
5. ✅ Edits clips (vertical format + captions)
6. ✅ Generates viral captions
7. ✅ Saves to `ready_to_post/` folders

### Auto-Posting (If enabled):
- Posts clips every 2-4 hours throughout the day
- Maximum 5 posts per day per account (safety limit)
- Random delays to mimic human behavior
- Rotates through your accounts

---

## 📁 FOLDER STRUCTURE

```
Clipfarm/
├── downloads/          # Downloaded YouTube videos
├── clips/              # Edited clips (before organization)
├── ready_to_post/      # Final clips ready for posting
│   ├── tiktok/
│   ├── instagram/
│   └── youtube_shorts/
├── cookies/            # Saved login sessions (after setup_accounts.py)
└── clips_queue.json    # Queue of clips waiting to be posted
```

---

## ⚙️ CONFIGURATION

Your channel is already set in `config.py`:
- Channel ID: `UCXR42GnrCHSxWjBuASCroQw`

**To add more channels**, edit `config.py`:
```python
YOUTUBE_CHANNELS = [
    "UCXR42GnrCHSxWjBuASCroQw",  # Your channel
    "UC_another_channel_id",      # Add more here
]
```

**To customize accounts**, edit `accounts.json`:
```json
{
  "tiktok": [{"username": "account1", "cookies_file": "cookies/tiktok_account1.pkl"}],
  "instagram": [{"username": "account1", "cookies_file": "cookies/instagram_account1.pkl"}],
  "youtube": [{"username": "account1", "cookies_file": "cookies/youtube_account1.pkl"}]
}
```

---

## 🎯 EXPECTED OUTPUT

**Per Day:**
- 3-5 new videos processed (from your channel)
- 9-15 clips generated (3 per video)
- 5-10 clips posted automatically (if auto-posting enabled)

**Per Week:**
- 50-100 clips generated
- 35-70 clips posted

---

## 🛠️ TROUBLESHOOTING

### "Module not found"
```bash
pip install -r requirements.txt
```

### "FFmpeg not found"
- Windows: Download from https://ffmpeg.org/download.html, add to PATH
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### "Ollama model not found"
```bash
ollama pull llama3.1
```

### "Cookies file not found" (when auto-posting)
Run `python setup_accounts.py` to setup accounts

### "Out of memory"
Edit `config.py`:
- `WHISPER_MODEL = "tiny"` (instead of "base")
- `OLLAMA_MODEL = "phi3"` (instead of "llama3.1")

---

## 📊 MONITORING

**Check status:**
- `clips_queue.json` - See clips waiting to be posted
- `post_history.json` - See posting history
- `daily_summary.json` - See daily generation summary
- `processed_videos.json` - See which videos have been processed

---

## 🔄 RUNNING 24/7

**On Your Computer:**
- Just leave it running
- Set computer to never sleep
- Use `--headless` flag for background operation

**On Cloud (Free Options):**
- Oracle Cloud (always free tier)
- Google Cloud ($300 free credit)
- AWS (free tier for 12 months)

---

## 💰 MONETIZATION

1. **Add Whop affiliate links** to your bio
2. **Link in captions** drives traffic
3. **Match content to offers** (trading clips → trading course)

---

## ✅ VERIFY INSTALLATION

Run this to check everything:
```bash
python setup.py
```

All items should show `[OK]` before running the main system.

---

## 🎉 YOU'RE READY!

Your system is configured and ready to generate viral clips automatically!

**Next Steps:**
1. Install dependencies (if not done)
2. Setup accounts (optional, for auto-posting)
3. Run: `python automation_system.py`

**Questions?** Check `README.md` for detailed documentation.

