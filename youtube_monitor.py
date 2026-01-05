"""
YouTube Channel Monitor
Monitors YouTube channels for new uploads using RSS feeds (free, no API needed)
"""
import feedparser
import time
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import json

class YouTubeMonitor:
    def __init__(self, cache_file: str = "processed_videos.json"):
        self.cache_file = Path(cache_file)
        self.processed_videos = self._load_cache()
    
    def _load_cache(self) -> set:
        """Load list of already processed video IDs"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_videos', []))
            except:
                return set()
        return set()
    
    def _save_cache(self):
        """Save processed video IDs to cache"""
        with open(self.cache_file, 'w') as f:
            json.dump({'processed_videos': list(self.processed_videos)}, f, indent=2)
    
    def get_channel_videos(self, channel_id: str, max_results: int = 10) -> List[Dict]:
        """
        Get latest videos from a YouTube channel using RSS feed
        
        Args:
            channel_id: YouTube channel ID (starts with UC)
            max_results: Maximum number of videos to return
            
        Returns:
            List of video dictionaries with 'url', 'title', 'published', 'video_id'
        """
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
        try:
            feed = feedparser.parse(feed_url)
            
            videos = []
            for entry in feed.entries[:max_results]:
                video_id = entry.yt_videoid if hasattr(entry, 'yt_videoid') else entry.link.split('v=')[-1].split('&')[0]
                
                videos.append({
                    'url': entry.link,
                    'title': entry.title,
                    'published': entry.published,
                    'video_id': video_id,
                    'description': entry.get('summary', '')[:200]  # First 200 chars
                })
            
            return videos
        except Exception as e:
            print(f"Error fetching videos for channel {channel_id}: {e}")
            return []
    
    def get_new_videos(self, channel_id: str, max_results: int = 10) -> List[Dict]:
        """
        Get only new videos that haven't been processed yet
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to check
            
        Returns:
            List of new video dictionaries
        """
        all_videos = self.get_channel_videos(channel_id, max_results)
        new_videos = [v for v in all_videos if v['video_id'] not in self.processed_videos]
        return new_videos
    
    def mark_as_processed(self, video_id: str):
        """Mark a video as processed"""
        self.processed_videos.add(video_id)
        self._save_cache()
    
    def check_channels(self, channel_ids: List[str], max_per_channel: int = 3) -> List[Dict]:
        """
        Check multiple channels for new videos
        
        Args:
            channel_ids: List of channel IDs to check
            max_per_channel: Maximum new videos to return per channel
            
        Returns:
            List of all new videos from all channels
        """
        all_new_videos = []
        
        for channel_id in channel_ids:
            print(f"Checking channel {channel_id}...")
            new_videos = self.get_new_videos(channel_id, max_per_channel * 2)
            
            for video in new_videos[:max_per_channel]:
                video['channel_id'] = channel_id
                all_new_videos.append(video)
            
            time.sleep(1)  # Be nice to YouTube's servers
        
        return all_new_videos


if __name__ == "__main__":
    # Test the monitor
    monitor = YouTubeMonitor()
    
    # Test with a channel (replace with actual channel ID)
    test_channel = "UCX6OQ3DkcsbYNE6H8uQQuVA"  # MrBeast example
    
    print(f"Fetching videos from channel {test_channel}...")
    videos = monitor.get_channel_videos(test_channel, max_results=5)
    
    for video in videos:
        print(f"\nTitle: {video['title']}")
        print(f"URL: {video['url']}")
        print(f"Published: {video['published']}")

