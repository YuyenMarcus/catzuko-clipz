# Quick Start Guide

Get Clipfarm running in 30 minutes!

## Step 1: Install Python (5 min)

If you don't have Python:
- Download from https://www.python.org/downloads/
- **Important**: Check "Add Python to PATH" during installation
- Verify: Open terminal and run `python --version`

## Step 2: Install Dependencies (10 min)

### Install Python packages:
```bash
pip install -r requirements.txt
```

### Install FFmpeg:

**Windows:**
1. Download from https://www.gyan.dev/ffmpeg/builds/
2. Extract zip file
3. Add `ffmpeg.exe` to your PATH, or place it in project folder

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### Install Ollama:

1. Download from https://ollama.ai
2. Install and run Ollama
3. Download model:
```bash
ollama pull llama3.1
```

## Step 3: Verify Installation (2 min)

Run the setup check:
```bash
python setup.py
```

Fix any missing dependencies before continuing.

## Step 4: Configure Channels (5 min)

1. Open `config.py`
2. Find YouTube channel IDs:
   - Go to YouTube channel
   - View page source (Ctrl+U or Cmd+U)
   - Search for "channel_id"
   - Copy ID starting with "UC"
3. Add to `YOUTUBE_CHANNELS` list:
```python
YOUTUBE_CHANNELS = [
    "UC_channel_id_here",
    "UC_another_channel_id",
]
```

## Step 5: Run Your First Clip! (5 min)

```bash
python main.py
```

The script will:
- Check channels for new videos
- Download videos
- Transcribe them
- Find viral clips
- Edit and add captions
- Save to `ready_to_post/` folders

## Step 6: Review and Post (10 min)

1. Check `ready_to_post/tiktok/` folder
2. Review clips and captions (`.txt` files)
3. Upload manually to platforms
4. Copy caption from `.txt` file when posting

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "FFmpeg not found"
- Windows: Add FFmpeg to PATH or download portable version
- Mac/Linux: Use package manager

### "Ollama model not found"
```bash
ollama pull llama3.1
```

### "Out of memory"
- Use smaller models in `config.py`:
  - `WHISPER_MODEL = "tiny"` (instead of "base")
  - `OLLAMA_MODEL = "phi3"` (instead of "llama3.1")

## Next Steps

- Run daily: `python main.py` once per day
- Scale up: Add more channels, process more videos
- Optimize: Adjust clip detection keywords in `clip_finder.py`
- Automate: Set up Task Scheduler (Windows) or cron (Mac/Linux)

## Daily Routine

1. **Morning (5 min)**: Run `python main.py`
2. **Afternoon (30 min)**: Review clips, post to platforms
3. **Evening (15 min)**: Check analytics, respond to comments

**Total: ~50 minutes/day for 10-15 viral clips**

---

**Need help?** Check `README.md` for detailed documentation.

