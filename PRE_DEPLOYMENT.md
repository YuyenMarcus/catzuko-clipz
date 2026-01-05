# 🚀 Pre-Deployment Checklist

**Run this BEFORE pushing to GitHub and deploying to Vercel:**

## ✅ Quick Check

```bash
python check_config.py
```

This will verify:
- ✅ Ollama connection (must be running)
- ✅ FFmpeg PATH (Windows: add to System PATH)
- ✅ Database setup
- ⚠️ Vercel considerations

---

## 📋 Detailed Checklist

### 1. Ollama Connection ✅

**Status:** Check with `python check_config.py`

**Requirements:**
- Ollama service running
- Llama 3.1 model downloaded: `ollama pull llama3.1`
- Python can connect

**If Failed:**
- **Windows:** Check Task Manager for "Ollama" process
- **Mac/Linux:** Run `ollama serve` in terminal
- Test: `import ollama; ollama.list()`

---

### 2. FFmpeg Path ✅

**Status:** Check with `python check_config.py`

**Requirements:**
- `ffmpeg.exe` accessible from command line
- `ffprobe.exe` also available

**If Failed (Windows):**
1. Download: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add to System PATH:
   - Win+X → System → Advanced System Settings
   - Environment Variables → Path → Edit → New
   - Add: `C:\ffmpeg\bin`
4. Restart terminal
5. Verify: `ffmpeg -version`

---

### 3. Vercel Considerations ⚠️

**Important:** Videos are processed LOCALLY.

**What WON'T work on Vercel:**
- ❌ Live Feed videos (read-only filesystem)
- ❌ Video preview

**What WILL work on Vercel:**
- ✅ Status monitoring
- ✅ Analytics
- ✅ Log viewer
- ✅ Settings toggles
- ✅ Queue management

**Solutions:**
1. **Run locally:** `python web_dashboard.py` (full features)
2. **Use Cloudflare Tunnel:** `cloudflared tunnel --url http://localhost:5000`
3. **Use ngrok:** `ngrok http 5000`

---

## 🎯 Ready to Deploy?

Once `check_config.py` shows:
- ✅ Ollama: PASS
- ✅ FFmpeg: PASS
- ✅ Database: PASS

**Then you can:**
1. Push to GitHub: `git push -u origin main`
2. Deploy to Vercel: Import from GitHub
3. Set environment variables in Vercel

---

## 📝 Post-Deployment

### Environment Variables (Vercel):
```
SECRET_KEY=your-secret-key-here
```

Generate: `python -c "import secrets; print(secrets.token_hex(32))"`

### Remember:
- Live Feed videos need local dashboard or tunnel
- Automation runs locally
- Vercel dashboard is for monitoring only

---

**Run `python check_config.py` now to verify everything!** ✅

