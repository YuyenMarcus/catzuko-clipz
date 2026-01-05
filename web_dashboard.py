"""
Clipfarm Web Dashboard
Private web interface to monitor and control the automation system
"""
from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
from pathlib import Path
import json
from datetime import datetime
import os
import threading
import subprocess
import sys

# Vercel environment detection
IS_VERCEL = os.environ.get('VERCEL') == '1'

app = Flask(__name__, 
            static_folder='static' if not IS_VERCEL else None,
            template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Import Clipfarm components
from config import *
from main import ClipfarmPipeline
from automation_system import ContentAutomationSystem

# Global state
automation_system = None
automation_thread = None
is_running = False

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    clips_queue = load_clips_queue()
    post_history = load_post_history()
    daily_summary = load_daily_summary()
    
    # Count clips in folders
    tiktok_clips = len(list(TIKTOK_DIR.glob("*.mp4"))) if TIKTOK_DIR.exists() else 0
    instagram_clips = len(list(INSTAGRAM_DIR.glob("*.mp4"))) if INSTAGRAM_DIR.exists() else 0
    youtube_clips = len(list(YOUTUBE_SHORTS_DIR.glob("*.mp4"))) if YOUTUBE_SHORTS_DIR.exists() else 0
    
    return jsonify({
        'automation_running': is_running,
        'clips_in_queue': len(clips_queue),
        'total_clips_ready': tiktok_clips + instagram_clips + youtube_clips,
        'tiktok_clips': tiktok_clips,
        'instagram_clips': instagram_clips,
        'youtube_clips': youtube_clips,
        'posts_today': get_posts_today(post_history),
        'last_run': daily_summary.get('date') if daily_summary else None,
        'videos_processed': daily_summary.get('videos_processed', 0) if daily_summary else 0,
        'clips_generated': daily_summary.get('total_clips', 0) if daily_summary else 0
    })

@app.route('/api/clips-queue')
def get_clips_queue():
    """Get clips waiting to be posted"""
    clips_queue = load_clips_queue()
    return jsonify(clips_queue)

@app.route('/api/post-history')
def get_post_history():
    """Get posting history"""
    post_history = load_post_history()
    return jsonify(post_history)

@app.route('/api/daily-summary')
def get_daily_summary():
    """Get daily summary"""
    summary = load_daily_summary()
    return jsonify(summary if summary else {})

@app.route('/api/channels')
def get_channels():
    """Get configured channels"""
    return jsonify({
        'channels': YOUTUBE_CHANNELS,
        'max_videos_per_channel': MAX_VIDEOS_PER_CHANNEL,
        'max_clips_per_video': MAX_CLIPS_PER_VIDEO
    })

@app.route('/api/accounts')
def get_accounts():
    """Get configured accounts"""
    accounts_file = Path("accounts.json")
    if accounts_file.exists():
        with open(accounts_file, 'r') as f:
            accounts = json.load(f)
        return jsonify(accounts)
    return jsonify({'tiktok': [], 'instagram': [], 'youtube': []})

@app.route('/api/run-generation', methods=['POST'])
def run_generation():
    """Manually trigger content generation"""
    try:
        def run_in_thread():
            global is_running
            is_running = True
            try:
                pipeline = ClipfarmPipeline()
                pipeline.run_daily()
            except Exception as e:
                print(f"Error in generation: {e}")
            finally:
                is_running = False
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        
        return jsonify({'success': True, 'message': 'Content generation started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/start-automation', methods=['POST'])
def start_automation():
    """Start 24/7 automation system"""
    global automation_system, automation_thread, is_running
    
    if is_running:
        return jsonify({'success': False, 'error': 'Automation already running'}), 400
    
    try:
        enable_auto_post = request.json.get('enable_auto_post', True)
        headless = request.json.get('headless', False)
        
        def run_automation():
            global is_running
            is_running = True
            try:
                system = ContentAutomationSystem(
                    enable_auto_posting=enable_auto_post,
                    headless=headless
                )
                system.run()
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(f"Error in automation: {e}")
            finally:
                is_running = False
        
        automation_thread = threading.Thread(target=run_automation, daemon=True)
        automation_thread.start()
        
        return jsonify({'success': True, 'message': 'Automation system started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop-automation', methods=['POST'])
def stop_automation():
    """Stop automation system"""
    global is_running
    # Note: This is a simple implementation. For production, use proper process management
    is_running = False
    return jsonify({'success': True, 'message': 'Stop signal sent'})

@app.route('/api/clips/<platform>')
def get_clips(platform):
    """Get clips for a specific platform"""
    platform_dir = READY_TO_POST_DIR / platform
    
    if not platform_dir.exists():
        return jsonify([])
    
    clips = []
    for video_file in platform_dir.glob("*.mp4"):
        caption_file = video_file.with_suffix('.txt')
        caption = ""
        if caption_file.exists():
            with open(caption_file, 'r', encoding='utf-8') as f:
                caption = f.read()
        
        clips.append({
            'filename': video_file.name,
            'path': str(video_file),
            'caption': caption,
            'size': video_file.stat().st_size,
            'modified': datetime.fromtimestamp(video_file.stat().st_mtime).isoformat()
        })
    
    return jsonify(clips)

@app.route('/api/clip/<platform>/<filename>')
def get_clip_info(platform, filename):
    """Get detailed info about a specific clip"""
    platform_dir = READY_TO_POST_DIR / platform
    video_file = platform_dir / filename
    
    if not video_file.exists():
        return jsonify({'error': 'Clip not found'}), 404
    
    caption_file = video_file.with_suffix('.txt')
    caption = ""
    if caption_file.exists():
        with open(caption_file, 'r', encoding='utf-8') as f:
            caption = f.read()
    
    return jsonify({
        'filename': filename,
        'path': str(video_file),
        'caption': caption,
        'size': video_file.stat().st_size,
        'modified': datetime.fromtimestamp(video_file.stat().st_mtime).isoformat()
    })

@app.route('/api/download/<path:filepath>')
def download_clip(filepath):
    """Download a clip file"""
    # Handle both platform/filename and full path formats
    if '/' in filepath:
        parts = filepath.split('/')
        if len(parts) >= 2:
            platform = parts[-2]
            filename = parts[-1]
            platform_dir = READY_TO_POST_DIR / platform
            video_file = platform_dir / filename
        else:
            video_file = Path(filepath)
    else:
        # Try to find in any platform folder
        video_file = None
        for platform_dir in [TIKTOK_DIR, INSTAGRAM_DIR, YOUTUBE_SHORTS_DIR]:
            test_file = platform_dir / filepath
            if test_file.exists():
                video_file = test_file
                break
        
        if not video_file:
            video_file = Path(filepath)
    
    if not video_file.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(str(video_file), as_attachment=True)

@app.route('/api/delete-clip', methods=['POST'])
def delete_clip():
    """Delete a clip from queue"""
    data = request.json
    clip_path = data.get('path')
    
    if not clip_path:
        return jsonify({'success': False, 'error': 'No path provided'}), 400
    
    try:
        clip_file = Path(clip_path)
        if clip_file.exists():
            clip_file.unlink()
            
            # Also delete caption file if exists
            caption_file = clip_file.with_suffix('.txt')
            if caption_file.exists():
                caption_file.unlink()
            
            # Remove from queue
            clips_queue = load_clips_queue()
            clips_queue = [c for c in clips_queue if c.get('video_path') != clip_path]
            save_clips_queue(clips_queue)
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Helper functions
def load_clips_queue():
    """Load clips queue from file"""
    queue_file = Path("clips_queue.json")
    if queue_file.exists():
        try:
            with open(queue_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_clips_queue(clips):
    """Save clips queue to file"""
    queue_file = Path("clips_queue.json")
    with open(queue_file, 'w') as f:
        json.dump(clips, f, indent=2)

def load_post_history():
    """Load post history from file"""
    history_file = Path("post_history.json")
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def load_daily_summary():
    """Load daily summary from file"""
    summary_file = Path("daily_summary.json")
    if summary_file.exists():
        try:
            with open(summary_file, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def get_posts_today(post_history):
    """Count posts made today"""
    today = datetime.now().date().isoformat()
    count = 0
    for account_data in post_history.values():
        if today in account_data:
            count += account_data[today]
    return count

# Vercel compatibility - export app for serverless
# Vercel will automatically detect the 'app' variable

if __name__ == '__main__':
    print("\n" + "="*60)
    print("CLIPFARM WEB DASHBOARD")
    print("="*60)
    print("\nStarting web server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    # Check if running on Vercel
    import os
    if os.environ.get('VERCEL'):
        # Vercel will handle the app through the handler
        print("Running on Vercel")
    else:
        # Local development
        app.run(host='127.0.0.1', port=5000, debug=True)

