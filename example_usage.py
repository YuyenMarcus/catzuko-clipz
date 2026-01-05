"""
Example usage of Clipfarm components
Demonstrates how to use each component individually
"""
from pathlib import Path
from config import DOWNLOADS_DIR, CLIPS_DIR

# Example 1: Monitor YouTube channels
print("Example 1: Monitoring YouTube Channels")
print("-" * 50)
from youtube_monitor import YouTubeMonitor

monitor = YouTubeMonitor()
# Replace with actual channel ID
# channel_id = "UCX6OQ3DkcsbYNE6H8uQQuVA"  # Example: MrBeast
# videos = monitor.get_channel_videos(channel_id, max_results=5)
# for video in videos:
#     print(f"  - {video['title']}")

# Example 2: Download a video
print("\nExample 2: Downloading Videos")
print("-" * 50)
from video_downloader import VideoDownloader

downloader = VideoDownloader(DOWNLOADS_DIR)
# video_url = "https://www.youtube.com/watch?v=VIDEO_ID"
# video_path = downloader.download_video(video_url)
# print(f"  Downloaded to: {video_path}")

# Example 3: Transcribe a video
print("\nExample 3: Transcribing Videos")
print("-" * 50)
from transcriber import VideoTranscriber

transcriber = VideoTranscriber(model_name="base")
# video_path = Path("downloads/video.mp4")
# if video_path.exists():
#     segments = transcriber.transcribe(video_path)
#     print(f"  Transcribed {len(segments)} segments")
#     print(f"  First segment: {segments[0]['text']}")

# Example 4: Find viral clips
print("\nExample 4: Finding Viral Clips")
print("-" * 50)
from clip_finder import ClipFinder

clip_finder = ClipFinder(model_name="llama3.1")
# Example transcript segments
example_segments = [
    {'start': 0.0, 'end': 5.0, 'text': 'Welcome to the channel'},
    {'start': 5.0, 'end': 15.0, 'text': 'Today I\'m going to reveal the secret to making a million dollars'},
    {'start': 15.0, 'end': 45.0, 'text': 'Nobody tells you this, but if you want to get rich, you need to stop doing what everyone else is doing'},
    {'start': 45.0, 'end': 60.0, 'text': 'This changed everything for me'},
]
clips = clip_finder.find_clips(example_segments, max_clips=2, min_duration=30, max_duration=60)
print(f"  Found {len(clips)} clips:")
for clip in clips:
    print(f"    - {clip['start']:.1f}s to {clip['end']:.1f}s: {clip['reason']}")

# Example 5: Edit a clip
print("\nExample 5: Editing Clips")
print("-" * 50)
from video_editor import VideoEditor

editor = VideoEditor(CLIPS_DIR)
# video_path = Path("downloads/video.mp4")
# if video_path.exists():
#     clip_path = editor.edit_clip(
#         video_path,
#         start_time=5.0,
#         end_time=45.0,
#         transcript_segments=example_segments[1:3],
#         clip_name="example_clip"
#     )
#     print(f"  Edited clip saved to: {clip_path}")

# Example 6: Generate captions
print("\nExample 6: Generating Captions")
print("-" * 50)
from caption_generator import CaptionGenerator

caption_gen = CaptionGenerator(model_name="llama3.1")
caption = caption_gen.generate_caption(example_segments[1:3], use_ai=True)
print(f"  Generated caption:\n  {caption}")

print("\n" + "=" * 50)
print("To use these examples:")
print("1. Uncomment the code sections")
print("2. Replace placeholder values with actual data")
print("3. Run: python example_usage.py")

