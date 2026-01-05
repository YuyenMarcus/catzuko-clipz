"""
Clipfarm - Main Workflow
Automated content clipping system that generates viral clips from YouTube videos
"""
import time
from datetime import datetime
from pathlib import Path
import json

from config import *
from youtube_monitor import YouTubeMonitor
from video_downloader import VideoDownloader
from transcriber import VideoTranscriber
from clip_finder import ClipFinder
from video_editor import VideoEditor
from caption_generator import CaptionGenerator

class ClipfarmPipeline:
    def __init__(self):
        """Initialize the complete pipeline"""
        print("Initializing Clipfarm Pipeline...")
        
        # Initialize components
        self.monitor = YouTubeMonitor(cache_file="processed_videos.json")
        self.downloader = VideoDownloader(DOWNLOADS_DIR)
        self.transcriber = VideoTranscriber(model_name=WHISPER_MODEL)
        self.clip_finder = ClipFinder(model_name=OLLAMA_MODEL)
        self.editor = VideoEditor(CLIPS_DIR)
        self.caption_generator = CaptionGenerator(model_name=OLLAMA_MODEL)
        
        print("Pipeline initialized!")
    
    def process_video(self, video_url: str, video_id: str, video_title: str) -> dict:
        """
        Process a single video: download, transcribe, find clips, edit, generate captions
        
        Args:
            video_url: YouTube video URL
            video_id: Video ID
            video_title: Video title
            
        Returns:
            Dictionary with processing results
        """
        print(f"\n{'='*60}")
        print(f"Processing: {video_title}")
        print(f"URL: {video_url}")
        print(f"{'='*60}\n")
        
        results = {
            'video_id': video_id,
            'video_title': video_title,
            'video_url': video_url,
            'clips': []
        }
        
        try:
            # Step 1: Download video
            print("Step 1: Downloading video...")
            video_path = self.downloader.download_video(video_url, video_id)
            
            if not video_path or not video_path.exists():
                print(f"Failed to download video: {video_url}")
                return results
            
            # Step 2: Transcribe
            print("\nStep 2: Transcribing video...")
            transcript_segments = self.transcriber.transcribe(video_path)
            
            if not transcript_segments:
                print("No transcript segments found")
                return results
            
            print(f"Transcribed {len(transcript_segments)} segments")
            
            # Step 3: Find viral clips
            print("\nStep 3: Finding viral clips...")
            clips = self.clip_finder.find_clips(
                transcript_segments,
                use_ai=True,
                max_clips=MAX_CLIPS_PER_VIDEO,
                min_duration=CLIP_DURATION_MIN,
                max_duration=CLIP_DURATION_MAX
            )
            
            print(f"Found {len(clips)} potential clips")
            
            if not clips:
                print("No viral clips found in this video")
                return results
            
            # Step 4: Edit clips and generate captions
            print("\nStep 4: Editing clips and generating captions...")
            
            for i, clip in enumerate(clips, 1):
                print(f"\n  Processing clip {i}/{len(clips)}...")
                print(f"    Time: {clip['start']:.1f}s - {clip['end']:.1f}s")
                print(f"    Reason: {clip['reason']}")
                
                # Get transcript segments for this clip
                clip_segments = self.transcriber.get_segments_in_range(
                    transcript_segments,
                    clip['start'],
                    clip['end']
                )
                
                # Create clip name
                clip_name = f"{video_id}_clip_{i}_{int(clip['start'])}s"
                
                # Edit clip
                edited_clip_path = self.editor.edit_clip(
                    video_path,
                    clip['start'],
                    clip['end'],
                    clip_segments,
                    clip_name,
                    caption_font_size=CAPTION_FONT_SIZE,
                    caption_color=CAPTION_COLOR,
                    caption_stroke_color=CAPTION_STROKE_COLOR,
                    caption_stroke_width=CAPTION_STROKE_WIDTH,
                    fps=VIDEO_FPS
                )
                
                if not edited_clip_path:
                    print(f"    Failed to edit clip {i}")
                    continue
                
                # Generate caption
                print(f"    Generating caption...")
                caption = self.caption_generator.generate_caption(
                    clip_segments,
                    use_ai=True,
                    link_in_bio=LINK_IN_BIO_TEXT
                )
                
                # Save caption to file
                caption_path = edited_clip_path.with_suffix('.txt')
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(caption)
                
                # Copy to platform-specific folders
                self._organize_clip(edited_clip_path, caption_path, clip_name)
                
                # Add to results
                results['clips'].append({
                    'clip_name': clip_name,
                    'start_time': clip['start'],
                    'end_time': clip['end'],
                    'reason': clip['reason'],
                    'video_path': str(edited_clip_path),
                    'caption_path': str(caption_path),
                    'caption': caption
                })
                
                print(f"    ✓ Clip saved: {edited_clip_path.name}")
                time.sleep(PROCESSING_DELAY)
            
            print(f"\n✓ Successfully processed {len(results['clips'])} clips from this video")
            
        except Exception as e:
            print(f"\n✗ Error processing video: {e}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def _organize_clip(self, video_path: Path, caption_path: Path, clip_name: str):
        """
        Copy clip and caption to platform-specific folders
        
        Args:
            video_path: Path to edited video
            caption_path: Path to caption file
            clip_name: Name of the clip
        """
        # Copy to all platform folders
        for platform_dir in [TIKTOK_DIR, INSTAGRAM_DIR, YOUTUBE_SHORTS_DIR]:
            # Copy video
            dest_video = platform_dir / video_path.name
            if not dest_video.exists():
                import shutil
                shutil.copy2(video_path, dest_video)
            
            # Copy caption
            dest_caption = platform_dir / caption_path.name
            if not dest_caption.exists():
                import shutil
                shutil.copy2(caption_path, dest_caption)
    
    def run_daily(self):
        """
        Run the complete daily workflow:
        1. Check channels for new videos
        2. Process new videos
        3. Generate clips ready for posting
        """
        print(f"\n{'='*60}")
        print(f"Clipfarm Daily Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        if not YOUTUBE_CHANNELS:
            print("⚠️  No YouTube channels configured!")
            print("   Add channel IDs to config.py -> YOUTUBE_CHANNELS")
            return
        
        # Check for new videos
        print(f"Checking {len(YOUTUBE_CHANNELS)} channels for new videos...")
        new_videos = self.monitor.check_channels(
            YOUTUBE_CHANNELS,
            max_per_channel=MAX_VIDEOS_PER_CHANNEL
        )
        
        if not new_videos:
            print("No new videos found. All videos have been processed.")
            return
        
        print(f"\nFound {len(new_videos)} new videos to process\n")
        
        # Process each video
        all_results = []
        for video in new_videos:
            result = self.process_video(
                video['url'],
                video['video_id'],
                video['title']
            )
            
            # Mark as processed
            self.monitor.mark_as_processed(video['video_id'])
            
            all_results.append(result)
            
            print(f"\n{'='*60}\n")
            time.sleep(PROCESSING_DELAY)
        
        # Summary
        print(f"\n{'='*60}")
        print("DAILY RUN COMPLETE")
        print(f"{'='*60}")
        
        total_clips = sum(len(r['clips']) for r in all_results)
        print(f"Videos processed: {len(all_results)}")
        print(f"Total clips generated: {total_clips}")
        print(f"\nClips ready for posting:")
        print(f"  TikTok: {TIKTOK_DIR}")
        print(f"  Instagram: {INSTAGRAM_DIR}")
        print(f"  YouTube Shorts: {YOUTUBE_SHORTS_DIR}")
        print(f"\nNext steps:")
        print(f"  1. Review clips in ready_to_post/ folders")
        print(f"  2. Upload clips manually or use automation")
        print(f"  3. Copy captions from .txt files when posting")
        
        # Save results summary
        summary_path = Path("daily_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                'date': datetime.now().isoformat(),
                'videos_processed': len(all_results),
                'total_clips': total_clips,
                'results': all_results
            }, f, indent=2)
        
        print(f"\nSummary saved to: {summary_path}")


def main():
    """Main entry point - runs daily content generation"""
    pipeline = ClipfarmPipeline()
    pipeline.run_daily()


if __name__ == "__main__":
    main()

