"""
Video Downloader
Downloads videos from YouTube using yt-dlp (free, no API needed)
"""
import subprocess
import os
from pathlib import Path
from typing import Optional

class VideoDownloader:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_video(self, url: str, video_id: Optional[str] = None) -> Optional[Path]:
        """
        Download a video from YouTube
        
        Args:
            url: YouTube video URL
            video_id: Optional video ID for filename (if None, extracted from URL)
            
        Returns:
            Path to downloaded video file, or None if download failed
        """
        if video_id is None:
            # Extract video ID from URL
            if 'v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
            else:
                video_id = url.split('/')[-1]
        
        output_path = self.output_dir / f"{video_id}.mp4"
        
        # Skip if already downloaded
        if output_path.exists():
            print(f"Video already exists: {output_path}")
            return output_path
        
        print(f"Downloading video: {url}")
        
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]/best',  # Prefer mp4, fallback to best quality
            '-o', str(output_path),
            '--no-playlist',
            url
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if output_path.exists():
                print(f"Downloaded successfully: {output_path}")
                return output_path
            else:
                print(f"Download completed but file not found: {output_path}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"Error downloading video: {e}")
            print(f"Error output: {e.stderr}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def download_batch(self, urls: list, video_ids: Optional[list] = None) -> list:
        """
        Download multiple videos
        
        Args:
            urls: List of YouTube URLs
            video_ids: Optional list of video IDs (must match urls length)
            
        Returns:
            List of paths to downloaded videos (None for failed downloads)
        """
        results = []
        
        for i, url in enumerate(urls):
            video_id = video_ids[i] if video_ids and i < len(video_ids) else None
            result = self.download_video(url, video_id)
            results.append(result)
        
        return results


if __name__ == "__main__":
    # Test the downloader
    downloader = VideoDownloader("test_downloads")
    
    # Test with a short video (replace with actual URL)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example
    
    print(f"Testing download: {test_url}")
    result = downloader.download_video(test_url)
    
    if result:
        print(f"Success! Video saved to: {result}")
    else:
        print("Download failed")

