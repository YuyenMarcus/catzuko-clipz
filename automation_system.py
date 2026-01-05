"""
Complete Automation System - Runs 24/7 with scheduling and auto-posting
This is the FULL automation version that handles everything
"""
import time
import random
import json
import schedule
from datetime import datetime
from pathlib import Path
import shutil

from config import *
from main import ClipfarmPipeline
from auto_poster import SafeAutoPoster


class ContentAutomationSystem:
    """Complete automation system that runs 24/7"""
    
    def __init__(self, enable_auto_posting: bool = True, headless: bool = False):
        """
        Initialize automation system
        
        Args:
            enable_auto_posting: Enable automatic posting (requires account setup)
            headless: Run browser in headless mode for 24/7 operation
        """
        print("Initializing Content Automation System...")
        
        # Initialize pipeline
        self.pipeline = ClipfarmPipeline()
        
        # Initialize auto-poster if enabled
        self.enable_auto_posting = enable_auto_posting
        if enable_auto_posting:
            self.poster = SafeAutoPoster(headless=headless)
            self.accounts = self._load_accounts()
        else:
            self.poster = None
            self.accounts = None
        
        # Clips queue
        self.clips_queue_file = Path("clips_queue.json")
        self.clips_queue = self._load_clips_queue()
        
        print("Automation system initialized!")
        if enable_auto_posting:
            print(f"Auto-posting enabled with {sum(len(accs) for accs in self.accounts.values())} accounts")
        else:
            print("Auto-posting disabled - clips will be saved to ready_to_post/ folders")
    
    def _load_accounts(self) -> dict:
        """Load account configurations"""
        accounts_file = Path("accounts.json")
        
        if not accounts_file.exists():
            print("⚠️  accounts.json not found. Creating template...")
            template = {
                "tiktok": [{"username": "account1", "cookies_file": "cookies/tiktok_account1.pkl"}],
                "instagram": [{"username": "account1", "cookies_file": "cookies/instagram_account1.pkl"}],
                "youtube": [{"username": "account1", "cookies_file": "cookies/youtube_account1.pkl"}]
            }
            with open(accounts_file, 'w') as f:
                json.dump(template, f, indent=2)
            print("   Please edit accounts.json and run setup_accounts.py to configure accounts")
            return template
        
        with open(accounts_file, 'r') as f:
            return json.load(f)
    
    def _load_clips_queue(self) -> list:
        """Load clips waiting to be posted"""
        if self.clips_queue_file.exists():
            try:
                with open(self.clips_queue_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_clips_queue(self):
        """Save clips queue to file"""
        with open(self.clips_queue_file, 'w') as f:
            json.dump(self.clips_queue, f, indent=2)
    
    def daily_content_generation(self):
        """
        Generate clips once per day
        This is scheduled to run daily
        """
        print(f"\n{'='*60}")
        print(f"DAILY CONTENT GENERATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        try:
            # Run the pipeline
            self.pipeline.run_daily()
            
            # Load newly generated clips from platform folders
            new_clips = []
            
            for platform in ['tiktok', 'instagram', 'youtube']:
                platform_dir = READY_TO_POST_DIR / platform
                
                if platform_dir.exists():
                    # Find all video files
                    video_files = list(platform_dir.glob("*.mp4"))
                    
                    for video_file in video_files:
                        # Find corresponding caption file
                        caption_file = video_file.with_suffix('.txt')
                        
                        if caption_file.exists():
                            with open(caption_file, 'r', encoding='utf-8') as f:
                                caption = f.read()
                        else:
                            caption = "Check out this clip! 🔥"
                        
                        # Check if already in queue
                        if not any(c['video_path'] == str(video_file) for c in self.clips_queue):
                            new_clips.append({
                                'video_path': str(video_file),
                                'caption': caption,
                                'platform': platform,
                                'added_at': datetime.now().isoformat()
                            })
            
            # Add new clips to queue
            self.clips_queue.extend(new_clips)
            self._save_clips_queue()
            
            print(f"\n✓ Added {len(new_clips)} new clips to posting queue")
            print(f"  Total clips in queue: {len(self.clips_queue)}")
            
        except Exception as e:
            print(f"\n✗ Error in daily content generation: {e}")
            import traceback
            traceback.print_exc()
    
    def hourly_posting(self):
        """
        Post clips throughout the day
        This is scheduled to run every 2-4 hours
        """
        if not self.enable_auto_posting:
            print("Auto-posting is disabled. Skipping hourly posting.")
            return
        
        if not self.clips_queue:
            print("No clips in queue to post")
            return
        
        print(f"\n{'='*60}")
        print(f"HOURLY POSTING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Take 1 clip from queue
        clip = self.clips_queue.pop(0)
        video_path = Path(clip['video_path'])
        caption = clip['caption']
        platform = clip.get('platform', 'tiktok')
        
        if not video_path.exists():
            print(f"Video file not found: {video_path}")
            self._save_clips_queue()
            return
        
        # Select account for this platform
        if platform not in self.accounts or not self.accounts[platform]:
            print(f"No accounts configured for {platform}")
            self.clips_queue.append(clip)  # Put back in queue
            self._save_clips_queue()
            return
        
        account = random.choice(self.accounts[platform])
        cookies_file = Path(account['cookies_file'])
        
        if not cookies_file.exists():
            print(f"Cookies file not found: {cookies_file}")
            print(f"Please run setup_accounts.py to setup this account")
            self.clips_queue.append(clip)  # Put back in queue
            self._save_clips_queue()
            return
        
        # Post with safety checks
        print(f"Posting to {platform} via {account['username']}...")
        print(f"Video: {video_path.name}")
        print(f"Caption: {caption[:50]}...")
        
        success = self.poster.post_with_safety(
            platform,
            video_path,
            caption,
            account
        )
        
        if success:
            print(f"✓ Successfully posted and removed from queue")
        else:
            print(f"✗ Failed to post. Clip will be retried later.")
            # Put back at end of queue
            self.clips_queue.append(clip)
        
        self._save_clips_queue()
    
    def run(self):
        """
        Start the automation system with scheduling
        Runs 24/7 until stopped
        """
        print(f"\n{'='*60}")
        print("CONTENT AUTOMATION SYSTEM STARTED")
        print(f"{'='*60}")
        print(f"\nSchedule:")
        print(f"  - Daily content generation: 2:00 AM")
        print(f"  - Hourly posting: Every 2-4 hours (randomized)")
        
        if self.enable_auto_posting:
            print(f"\nAuto-posting: ENABLED")
            print(f"  Accounts configured:")
            for platform, accounts in self.accounts.items():
                print(f"    {platform}: {len(accounts)} account(s)")
        else:
            print(f"\nAuto-posting: DISABLED")
            print(f"  Clips will be saved to ready_to_post/ folders")
        
        print(f"\nPress Ctrl+C to stop\n")
        
        # Schedule daily content generation at 2 AM
        schedule.every().day.at("02:00").do(self.daily_content_generation)
        
        # Schedule hourly posting (randomized between 2-4 hours)
        def schedule_next_posting():
            """Schedule next posting with random delay"""
            delay_hours = random.uniform(2, 4)
            schedule.clear('posting')  # Clear previous posting schedule
            schedule.every(delay_hours).hours.do(post_and_reschedule).tag('posting')
            print(f"Next posting scheduled in {delay_hours:.1f} hours")
        
        def post_and_reschedule():
            """Post and schedule next one"""
            self.hourly_posting()
            schedule_next_posting()
        
        # Start first posting schedule
        schedule_next_posting()
        
        # Run first post immediately if there are clips in queue
        if self.clips_queue and self.enable_auto_posting:
            print("Found clips in queue. Starting first post in 2 minutes...")
            schedule.every(2).minutes.do(post_and_reschedule).tag('posting')
        
        # Main loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\nStopping automation system...")
            print("Saving state...")
            self._save_clips_queue()
            print("Done!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clipfarm Automation System')
    parser.add_argument('--no-auto-post', action='store_true', 
                       help='Disable auto-posting (clips saved to folders only)')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode (for 24/7 operation)')
    parser.add_argument('--run-once', action='store_true',
                       help='Run content generation once and exit (no scheduling)')
    
    args = parser.parse_args()
    
    # Initialize system
    system = ContentAutomationSystem(
        enable_auto_posting=not args.no_auto_post,
        headless=args.headless
    )
    
    if args.run_once:
        # Just generate content once
        print("Running content generation once...")
        system.daily_content_generation()
        print("\nDone! Check ready_to_post/ folders for clips.")
    else:
        # Run full automation with scheduling
        system.run()


if __name__ == "__main__":
    main()

