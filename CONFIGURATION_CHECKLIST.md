# 🛠️ Final Configuration Checklist

**Before pushing to GitHub and deploying to Vercel, verify these settings:**

## ✅ 1. Ollama Connection

### Check:
```bash
python check_config.py
```

### Requirements:
- ✅ Ollama service must be running
- ✅ Llama 3.1 model downloaded: `ollama pull llama3.1`
- ✅ Python can connect: `import ollama` works

### How to Fix:
**Windows:**
- Ollama should run as a service automatically
- Check Task Manager for "Ollama" process
- If not running, start Ollama application

**Mac/Linux:**
```bash
ollama serve
```

**Test Connection:**
```python
import ollama
models = ollama.list()
print(models)
```

**If Dashboard Shows "Worker Error":**
- Ollama is not running or not accessible
- Check firewall settings
- Verify Ollama is listening on default port (11434)

---

## ✅ 2. FFmpeg Path (Windows)

### Check:
```bash
ffmpeg -version
```

### Requirements:
- ✅ `ffmpeg.exe` accessible from command line
- ✅ `ffprobe.exe` also available (for video info)

### How to Fix on Windows:

1. **Download FFmpeg:**
   - Go to https://www.gyan.dev/ffmpeg/builds/
   - Download "ffmpeg-release-essentials.zip"
   - Extract to `C:\ffmpeg` (or your preferred location)

2. **Add to System PATH:**
   - Press `Win + X` → System → Advanced System Settings
   - Click "Environment Variables"
   - Under "System Variables", find "Path" → Edit
   - Click "New" → Add: `C:\ffmpeg\bin` (or your ffmpeg folder)
   - Click OK on all dialogs

3. **Verify:**
   - Close and reopen terminal/Python
   - Run: `ffmpeg -version`
   - Should show version info (not "command not found")

**Alternative (Portable):**
- Place `ffmpeg.exe` in your project folder
- Update `video_editor.py` to use full path

---

## ✅ 3. Vercel/Cloud Considerations

### ⚠️ Important Limitations:

**Your videos are processed LOCALLY on your machine.**

### What WON'T Work on Vercel:
- ❌ **Live Feed videos** - Vercel has read-only filesystem
- ❌ **Video preview** - Clips stored locally, not accessible from cloud
- ❌ **Direct file access** - Can't serve videos from Vercel

### What WILL Work on Vercel:
- ✅ Status monitoring
- ✅ Analytics dashboard
- ✅ Log viewer
- ✅ Settings toggles
- ✅ Queue management
- ✅ Post history

### Solutions:

#### Option 1: Run Dashboard Locally (Recommended)
```bash
python web_dashboard.py
```
Then access at: http://localhost:5000

**Full features available!**

#### Option 2: Use Cloudflare Tunnel (Free)
1. Install Cloudflare Tunnel:
   ```bash
   # Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
   ```

2. Run tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:5000
   ```

3. Access via provided URL (e.g., `https://your-tunnel.cfargotunnel.com`)

**Benefits:**
- Free
- Secure (HTTPS)
- No router configuration needed
- Access from anywhere

#### Option 3: Use ngrok (Free Tier)
1. Sign up: https://ngrok.com/
2. Install ngrok
3. Run:
   ```bash
   ngrok http 5000
   ```
4. Access via provided URL

**Limitations:**
- Free tier has session limits
- URL changes each time

#### Option 4: Cloud Storage Integration
Store clips in cloud storage (S3, Cloudinary, etc.) and serve from there:

1. Upload clips to cloud storage after generation
2. Update dashboard to fetch videos from cloud URLs
3. Full Live Feed works on Vercel

**Example:**
```python
# After generating clip
upload_to_s3(clip_path)
clip_url = get_s3_url(clip_path)
# Store URL in database
```

---

## 🎯 Recommended Setup

### For Development:
- ✅ Run everything locally
- ✅ Dashboard: `python web_dashboard.py`
- ✅ Automation: `python automation_system.py`

### For Production:
- ✅ **Vercel**: Host dashboard UI (monitoring/control)
- ✅ **Your Server/PC**: Run automation + local dashboard (full features)
- ✅ **Cloud Storage**: Store clips for remote access (optional)

### Hybrid Approach:
1. Deploy dashboard to Vercel for monitoring
2. Run automation locally
3. Use Cloudflare Tunnel for local dashboard with full features
4. Store clips in cloud storage for universal access

---

## 🔍 Quick Verification

Run the configuration checker:

```bash
python check_config.py
```

This will verify:
- ✅ Ollama connection
- ✅ FFmpeg PATH
- ✅ Database setup
- ✅ Directory structure
- ⚠️ Vercel considerations (info only)

---

## 📝 Pre-Deployment Checklist

Before pushing to GitHub:

- [ ] Ollama running and accessible
- [ ] Llama 3.1 model downloaded
- [ ] FFmpeg in system PATH
- [ ] Database initialized (run `python check_config.py`)
- [ ] All directories created
- [ ] Tested locally: `python web_dashboard.py`
- [ ] Environment variables documented
- [ ] Vercel limitations understood

---

## 🚀 After Deployment

### If Using Vercel:
1. Set environment variables in Vercel dashboard:
   - `SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)

2. Remember:
   - Live Feed videos won't work
   - Use local dashboard or tunnel for full features

### If Using Local + Tunnel:
1. Start dashboard: `python web_dashboard.py`
2. Start tunnel: `cloudflared tunnel --url http://localhost:5000`
3. Access via tunnel URL
4. Full features available!

---

## 🆘 Troubleshooting

### "Ollama Connection Failed"
- Check Ollama is running
- Verify firewall allows connections
- Test: `ollama list`

### "FFmpeg Not Found"
- Verify PATH includes ffmpeg folder
- Restart terminal after adding to PATH
- Test: `ffmpeg -version`

### "Live Feed Not Working on Vercel"
- Expected behavior (Vercel limitation)
- Use local dashboard or tunnel
- Or implement cloud storage

---

**Run `python check_config.py` to verify everything is ready!** ✅

