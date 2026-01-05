# Clipfarm - Automated Content Clipping System

A completely free, automated system that monitors YouTube channels, downloads videos, transcribes them, identifies viral-worthy clips, edits them with captions, and organizes them ready for posting to TikTok, Instagram, and YouTube Shorts.

**Goal**: Generate 10-15 viral clips per day that drive traffic to your Whop affiliate links, creating passive income.

## 🎯 Features

- ✅ **Free** - No APIs, no servers, no subscriptions ($0 cost)
- ✅ **Automated** - Monitors YouTube channels for new uploads
- ✅ **AI-Powered** - Uses local AI (Whisper + Ollama) for transcription and clip detection
- ✅ **Professional Editing** - Auto-crops to vertical format, adds captions
- ✅ **Viral Optimization** - Identifies viral moments and generates engaging captions
- ✅ **Multi-Platform Ready** - Organizes clips for TikTok, Instagram, YouTube Shorts

## 🛠️ Tech Stack (All Free)

- **Python 3** - Core language
- **yt-dlp** - YouTube video downloader
- **Whisper** - OpenAI's free local transcription model
- **FFmpeg/MoviePy** - Video editing
- **Ollama** - Free local LLMs (replaces Claude/GPT)
- **Selenium** - Browser automation (optional, for posting)

## 📋 Prerequisites

- Python 3.8 or higher
- Windows/Mac/Linux
- 8GB+ RAM (16GB recommended)
- 100GB+ free disk space
- Internet connection

## 🎛️ Web Dashboard

**NEW!** Access a private web dashboard to monitor and control your system:

```bash
python web_dashboard.py
```

Then open: **http://localhost:5000**

Features:
- Real-time status monitoring
- View clips queue and ready clips
- Posting history and analytics
- Manual controls (generate clips, start/stop automation)
- Browse clips by platform
- Download and manage clips

See `DASHBOARD_README.md` for full dashboard documentation.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install FFmpeg
# Windows: Download from https://ffmpeg.org/download.html
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# Install Ollama
# Download from https://ollama.ai
# After installation, run:
ollama pull llama3.1
```

### 2. Configure Channels

Edit `config.py` and add your target YouTube channel IDs:

```python
YOUTUBE_CHANNELS = [
    "UC_channel_id_1",  # Example: Iman Gadzhi
    "UC_channel_id_2",  # Example: Alex Hormozi
]
```

**How to find channel IDs:**
- Go to the YouTube channel
- View page source (Ctrl+U)
- Search for "channel_id"
- Copy the ID that starts with "UC"

### 3. Run the Pipeline

```bash
python main.py
```

This will:
1. Check all configured channels for new videos
2. Download new videos
3. Transcribe them using Whisper
4. Find viral clips using Ollama
5. Edit clips (vertical format + captions)
6. Generate captions
7. Organize clips in `ready_to_post/` folders

## 📁 Project Structure

```
Clipfarm/
├── main.py                 # Main workflow orchestrator
├── config.py              # Configuration settings
├── youtube_monitor.py     # YouTube channel monitoring
├── video_downloader.py    # Video downloading (yt-dlp)
├── transcriber.py         # Video transcription (Whisper)
├── clip_finder.py         # Viral clip detection (Ollama)
├── video_editor.py        # Video editing (MoviePy)
├── caption_generator.py   # Caption generation (Ollama)
├── requirements.txt       # Python dependencies
├── downloads/             # Downloaded videos
├── clips/                 # Edited clips
└── ready_to_post/         # Clips ready for posting
    ├── tiktok/
    ├── instagram/
    └── youtube_shorts/
```

## ⚙️ Configuration

Edit `config.py` to customize:

- **Channels**: Add YouTube channel IDs to monitor
- **Processing**: Max videos per channel, max clips per video
- **Whisper Model**: `tiny`, `base` (recommended), `small`, `medium`, `large`
- **Ollama Model**: `llama3.1` (recommended), `mistral`, `phi3`
- **Video Settings**: Aspect ratio, caption style, FPS
- **Affiliate Links**: Add your Whop affiliate link

## 📊 Daily Workflow

1. **Run Script** (5 minutes)
   ```bash
   python main.py
   ```

2. **Review Clips** (15 minutes)
   - Check `ready_to_post/` folders
   - Review generated clips and captions
   - Select best clips to post

3. **Post to Platforms** (30 minutes)
   - Upload clips manually to TikTok, Instagram, YouTube Shorts
   - Copy captions from `.txt` files
   - Add your affiliate link in bio

**Total Time**: ~50 minutes/day

## 🎬 Expected Output

- **3-5 channels** monitored
- **3 new videos** processed per day
- **9-15 clips** generated (3 per video)
- **5-10 clips** posted per day across platforms

## 🔧 Advanced Usage

### Manual Video Processing

```python
from main import ClipfarmPipeline

pipeline = ClipfarmPipeline()

# Process a specific video
result = pipeline.process_video(
    video_url="https://www.youtube.com/watch?v=VIDEO_ID",
    video_id="VIDEO_ID",
    video_title="Video Title"
)
```

### Custom Clip Detection

Edit `clip_finder.py` to customize what makes a clip "viral":
- Add keywords
- Adjust AI prompts
- Modify duration ranges

### Automated Posting (Optional)

The system includes Selenium-based posting automation (see `config.py`). However, manual posting is recommended for:
- Better platform compliance
- More control over timing
- Avoiding account flags

## 💰 Monetization Setup

1. **Sign up for Whop affiliate program** (free)
2. **Get affiliate links** for products/courses
3. **Create Linktree** (free tier) with affiliate links
4. **Add to bio**: "Link in bio 🔗"
5. **Match content to offers** (trading clips → trading course, etc.)

## 🐛 Troubleshooting

### "Ollama model not found"
```bash
ollama pull llama3.1
```

### "FFmpeg not found"
- Windows: Add FFmpeg to PATH or download from ffmpeg.org
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### "Whisper model download failed"
- Check internet connection
- Try smaller model: `tiny` or `base`
- Download manually from OpenAI

### "Video download failed"
- Check internet connection
- Verify video URL is accessible
- Update yt-dlp: `pip install --upgrade yt-dlp`

### "Out of memory"
- Use smaller Whisper model (`tiny` or `base`)
- Use smaller Ollama model (`phi3`)
- Process fewer videos at once

## 📈 Scaling Plan

**Week 1-2**: Get pipeline working, generate first 50 clips
**Week 3-4**: Start posting consistently, build audience
**Month 2**: Ramp to 10 clips/day across 3 platforms
**Month 3**: Optimize what works, double down

## 🆓 Cost Breakdown

| Item | Cost |
|------|------|
| Python | $0 |
| yt-dlp | $0 |
| Whisper | $0 |
| Ollama/Llama | $0 |
| FFmpeg | $0 |
| Selenium | $0 |
| Whop affiliate | $0 |
| **TOTAL** | **$0** |

## ⚠️ Limitations

- No fully hands-off automation (manual posting recommended)
- Slower processing (local AI vs cloud APIs)
- Limited to your computer's speed
- Can't run 24/7 (unless you leave computer on)

## 📝 License

Free to use for personal and commercial purposes.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error messages in console output
3. Verify all dependencies are installed correctly

---

**Built with ❤️ for creators who want to automate their content workflow without breaking the bank.**

