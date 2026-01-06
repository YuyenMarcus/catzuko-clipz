"""
Clipfarm Web Dashboard
Private web interface to monitor and control the automation system
Vercel Serverless Function Entry Point
"""
import sys
from pathlib import Path

# Add project root to path so imports work from api/ directory
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
import json
from datetime import datetime
import os
import threading
import subprocess

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

# Initialize Firebase first (if enabled) - this handles Vercel environment variables
# Import models.py which handles Firebase/Supabase/SQLite automatically
from models import (
    add_clip, update_clip_status, get_clips, get_clip_by_id,
    add_log, get_logs, get_setting, set_setting,
    get_analytics, record_post, update_worker_heartbeat, get_worker_status,
    initialize_firebase  # Re-export for explicit initialization if needed
)

# Ensure Firebase is initialized (models.py does this on import, but we can verify)
if os.environ.get('USE_FIREBASE', 'false').lower() == 'true':
    try:
        initialize_firebase()
    except:
        pass  # Already initialized in models.py

from account_health import get_account_health, update_cookie_date
import sqlite3

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
    analytics = get_analytics()
    worker_status = get_worker_status('main')
    
    return jsonify({
        'automation_running': is_running,
        'worker_status': worker_status['status'],
        'worker_last_seen': worker_status.get('last_seen'),
        'pending': analytics['pending'],
        'posted': analytics['posted'],
        'failed': analytics['failed'],
        'posts_today': analytics['posts_today'],
        'total_clips': analytics['total_clips']
    })

@app.route('/api/analytics')
def get_analytics_endpoint():
    """
    Get analytics summary from Firebase Firestore or SQLite
    Real-time stats including pending, posted, failed counts
    """
    try:
        analytics = get_analytics()
        return jsonify(analytics)
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def get_logs_endpoint():
    """
    Get recent logs from Firebase Firestore or SQLite
    Supports filtering by component (yt-dlp, Ollama, Editor, Poster, Dashboard)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        component = request.args.get('component', None)
        logs = get_logs(component=component, limit=limit)
        return jsonify(logs)
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings')
def get_settings():
    """Get all settings"""
    return jsonify({
        'auto_posting_enabled': get_setting('auto_posting_enabled', '0'),
        'auto_posting_tiktok': get_setting('auto_posting_tiktok', '0'),
        'auto_posting_instagram': get_setting('auto_posting_instagram', '0'),
        'auto_posting_youtube': get_setting('auto_posting_youtube', '0')
    })

@app.route('/api/settings/<key>', methods=['POST'])
def update_setting(key):
    """Update a setting"""
    data = request.json
    value = data.get('value', '0')
    set_setting(key, value)
    add_log('info', 'dashboard', f'Setting {key} updated to {value}')
    return jsonify({'success': True})

@app.route('/api/manual-post', methods=['POST'])
def manual_post():
    """Manually post a clip"""
    data = request.json
    platform = data.get('platform')
    filename = data.get('filename')
    
    if not platform or not filename:
        return jsonify({'success': False, 'error': 'Missing platform or filename'}), 400
    
    try:
        # Find clip in database
        clips = get_clips(platform=platform, status='pending')
        clip = next((c for c in clips if filename in c['filename']), None)
        
        if not clip:
            return jsonify({'success': False, 'error': 'Clip not found'}), 404
        
        # Post using auto_poster
        from auto_poster import SafeAutoPoster
        import accounts
        
        poster = SafeAutoPoster()
        account_configs = accounts.get_accounts()
        
        if platform not in account_configs or not account_configs[platform]:
            return jsonify({'success': False, 'error': f'No accounts configured for {platform}'}), 400
        
        account = account_configs[platform][0]
        video_path = Path(clip['video_path'])
        caption = clip.get('caption', '')
        
        success = poster.post_with_safety(platform, video_path, caption, account)
        
        if success:
            record_post(clip['id'], platform, account['username'], True)
            add_log('info', 'dashboard', f'Manually posted {filename} to {platform}')
            return jsonify({'success': True})
        else:
            record_post(clip['id'], platform, account['username'], False, 'Manual post failed')
            return jsonify({'success': False, 'error': 'Posting failed'}), 500
            
    except Exception as e:
        add_log('error', 'dashboard', f'Manual post error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/video/<platform>/<filename>')
def serve_video(platform, filename):
    """
    Serve video file for live feed preview
    Uses Firebase Storage URL if available, otherwise falls back to local file
    """
    # Try to get clip from database (Firebase or SQLite)
    try:
        # Try to find clip by filename
        clips = get_clips(platform=platform, limit=100)
        clip = next((c for c in clips if c.get('filename') == filename), None)
        
        if clip:
            # Use Firebase Storage URL if available
            video_url = clip.get('video_url') or clip.get('storage_url')
            if video_url:
                # Redirect to Firebase Storage public URL
                return redirect(video_url)
    except Exception as e:
        print(f"Error fetching clip from database: {e}")
    
    # Fallback to local file (for development or if Firebase Storage not available)
    try:
        platform_dir = READY_TO_POST_DIR / platform
        video_file = platform_dir / filename
        
        if video_file.exists():
            return send_file(str(video_file), mimetype='video/mp4')
    except Exception as e:
        print(f"Error serving local file: {e}")
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/worker-status')
def get_worker_status_endpoint():
    """Get worker heartbeat status"""
    status = get_worker_status('main')
    return jsonify(status)

@app.route('/api/account-health')
def get_account_health_endpoint():
    """Get account health status"""
    health = get_account_health()
    return jsonify(health)

@app.route('/api/upload-cookie', methods=['POST'])
def upload_cookie():
    """Upload new cookie file"""
    from account_health import health_tracker
    
    platform = request.form.get('platform')
    account = request.form.get('account')
    
    if 'cookie_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['cookie_file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        cookie_data = file.read()
        success = health_tracker.upload_cookie(platform, account, cookie_data)
        
        if success:
            update_cookie_date(platform, account)
            add_log('info', 'dashboard', f'Cookie updated for {platform}/{account}')
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to save cookie'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clips-queue')
def get_clips_queue():
    """
    Get clips waiting to be posted from Firebase Firestore or SQLite
    Returns clips with Firebase Storage URLs if available
    """
    try:
        clips = get_clips(status='pending', limit=100)
        
        # Ensure all clips have video_url for dashboard display
        for clip in clips:
            if 'video_url' not in clip:
                clip['video_url'] = clip.get('storage_url') or clip.get('video_path')
        
        return jsonify(clips)
    except Exception as e:
        print(f"Error fetching clips queue: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/post-history')
def get_post_history_endpoint():
    """
    Get posting history from Firebase Firestore or SQLite
    Returns clips with Firebase Storage URLs
    """
    try:
        posted_clips = get_clips(status='posted', limit=100)
        
        # Ensure all clips have video_url
        for clip in posted_clips:
            if 'video_url' not in clip:
                clip['video_url'] = clip.get('storage_url') or clip.get('video_path')
        
        return jsonify(posted_clips)
    except Exception as e:
        print(f"Error fetching post history: {e}")
        return jsonify({'error': str(e)}), 500

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
            except Exception as e:
                print(f"Error in automation: {e}")
            finally:
                is_running = False
        
        automation_thread = threading.Thread(target=run_automation, daemon=True)
        automation_thread.start()
        
        return jsonify({'success': True, 'message': 'Automation started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop-automation', methods=['POST'])
def stop_automation():
    """Stop 24/7 automation system"""
    global automation_system, automation_thread, is_running
    
    is_running = False
    
    if automation_thread and automation_thread.is_alive():
        # Note: Can't forcefully stop thread, but flag will stop it on next check
        pass
    
    return jsonify({'success': True, 'message': 'Automation stopped'})

@app.route('/api/clips/<platform>')
def get_clips_endpoint(platform):
    """Get clips for a specific platform"""
    try:
        clips = get_clips(platform=platform, status='pending', limit=100)
        
        # Format for display
        result = {
            'platform': platform,
            'count': len(clips),
            'clips': clips
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            # Also delete caption if exists
            caption_file = clip_file.with_suffix('.txt')
            if caption_file.exists():
                caption_file.unlink()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def load_daily_summary():
    """Load daily summary from file"""
    summary_file = Path("daily_summary.json")
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# Database logging handler
import logging

class DatabaseLogHandler(logging.Handler):
    """Log handler that writes to database"""
    def emit(self, record):
        try:
            level = record.levelname.lower()
            component = getattr(record, 'component', 'system')
            message = self.format(record)
            add_log(level, component, message)
        except:
            pass

# Setup logging to database
logging.basicConfig(level=logging.INFO)
db_handler = DatabaseLogHandler()
logging.getLogger().addHandler(db_handler)

# Vercel compatibility - export app for serverless
# Vercel will automatically detect the 'app' variable

if __name__ == '__main__':
    print("\n" + "="*60)
    print("CLIPFARM WEB DASHBOARD")
    print("="*60)
    print("\nStarting web server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    # Local development only - debug mode disabled for production
    app.run(host='127.0.0.1', port=5000, debug=False)
