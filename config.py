"""
Configuration file for Clipfarm
Edit these settings to customize your setup
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
CLIPS_DIR = BASE_DIR / "clips"
READY_TO_POST_DIR = BASE_DIR / "ready_to_post"
TIKTOK_DIR = READY_TO_POST_DIR / "tiktok"
INSTAGRAM_DIR = READY_TO_POST_DIR / "instagram"
YOUTUBE_SHORTS_DIR = READY_TO_POST_DIR / "youtube_shorts"

# Create directories if they don't exist
for dir_path in [DOWNLOADS_DIR, CLIPS_DIR, READY_TO_POST_DIR, TIKTOK_DIR, INSTAGRAM_DIR, YOUTUBE_SHORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# YouTube channel IDs to monitor (add your target channels here)
# Format: "UCxxxxxxxxxxxxxxxxxxxxxxxxxx"
YOUTUBE_CHANNELS = [
    "UCXR42GnrCHSxWjBuASCroQw",  # Your channel
]

# Video processing settings
MAX_VIDEOS_PER_CHANNEL = 3  # Process top 3 most recent videos per channel
MAX_CLIPS_PER_VIDEO = 3  # Generate top 3 clips per video
CLIP_DURATION_MIN = 30  # Minimum clip duration in seconds
CLIP_DURATION_MAX = 60  # Maximum clip duration in seconds

# Whisper settings
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
# base is recommended for CPU, small/medium for GPU

# Ollama settings
OLLAMA_MODEL = "llama3.1"  # Options: llama3.1, mistral, phi3

# Video editing settings
VERTICAL_ASPECT_RATIO = (9, 16)  # TikTok/Reels/Shorts format
CAPTION_FONT_SIZE = 70
CAPTION_COLOR = "yellow"
CAPTION_STROKE_COLOR = "black"
CAPTION_STROKE_WIDTH = 3
VIDEO_FPS = 30

# Affiliate settings
WHOP_AFFILIATE_LINK = ""  # Add your Whop affiliate link here
LINK_IN_BIO_TEXT = "Link in bio 🔗"

# Firebase settings (if using Firebase)
FIREBASE_CREDENTIALS_FILE = "firebase-key.json"  # Path to Firebase credentials
FIREBASE_STORAGE_BUCKET = "catzuko-4afef.appspot.com"  # Your Firebase Storage bucket

# Selenium settings (for automated posting - optional)
CHROME_DRIVER_PATH = ""  # Path to chromedriver.exe (leave empty to use system PATH)
HEADLESS_BROWSER = False  # Set to True to run browser in background

# Processing settings
PROCESSING_DELAY = 2  # Seconds to wait between processing clips

