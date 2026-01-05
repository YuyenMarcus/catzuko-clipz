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
from models import *
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
    
    return jsonify({
        'automation_running': is_running,
        'pending': analytics['pending'],
        'posted': analytics['posted'],
        'failed': analytics['failed'],
        'posts_today': analytics['posts_today'],
        'total_clips': analytics['total_clips']
    })

@app.route('/api/analytics')
def get_analytics_endpoint():
    """Get analytics data"""
    analytics = get_analytics()
    return jsonify(analytics)

@app.route('/api/logs')
def get_logs_endpoint():
    """Get logs"""
    limit = request.args.get('limit', 50, type=int)
    component = request.args.get('component', None)
    logs = get_logs(component=component, limit=limit)
    return jsonify(logs)

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
    """Serve video file for live feed preview"""
    platform_dir = READY_TO_POST_DIR / platform
    video_file = platform_dir / filename
    
    if not video_file.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(str(video_file), mimetype='video/mp4')

@app.route('/api/clips-queue')
def get_clips_queue():
    """Get clips waiting to be posted (from database)"""
    clips = get_clips(status='pending', limit=100)
    return jsonify(clips)

@app.route('/api/post-history')
def get_post_history_endpoint():
    """Get posting history (from database)"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''SELECT p.*, c.filename, c.platform 
                 FROM posts p 
                 LEFT JOIN clips c ON p.clip_id = c.id 
                 ORDER BY p.posted_at DESC LIMIT 100''')
    rows = c.fetchall()
    conn.close()
    
    # Format for display
    history = {}
    for row in rows:
        account = row['account'] or 'unknown'
        date = row['posted_at'][:10] if row['posted_at'] else 'unknown'
        
        if account not in history:
            history[account] = {}
        if date not in history[account]:
            history[account][date] = 0
        history[account][date] += 1
    
    return jsonify(history)

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
def get_clips_endpoint(platform):
    """Get clips for a specific platform (from database)"""
    clips = get_clips(platform=platform, status='pending', limit=100)
    
    # Enhance with file info
    result = []
    for clip in clips:
        video_path = Path(clip['video_path'])
        if video_path.exists():
            result.append({
                'id': clip['id'],
                'filename': clip['filename'],
                'path': clip['video_path'],
                'caption': clip.get('caption', ''),
                'size': video_path.stat().st_size,
                'modified': clip['timestamp'],
                'platform': clip['platform'],
                'status': clip['status']
            })
    
    return jsonify(result)

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

# Logging wrapper to add logs to database
import logging
class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            add_log(
                level=record.levelname.lower(),
                component=record.name,
                message=self.format(record)
            )
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
    
    # Check if running on Vercel
    import os
    if os.environ.get('VERCEL'):
        # Vercel will handle the app through the handler
        print("Running on Vercel")
    else:
        # Local development
        app.run(host='127.0.0.1', port=5000, debug=True)

