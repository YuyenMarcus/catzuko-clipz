"""
Video Transcriber
Transcribes videos using OpenAI Whisper (free, runs locally)
"""
import whisper
from pathlib import Path
from typing import List, Dict, Optional

class VideoTranscriber:
    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper model
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
                       base is recommended for CPU, small/medium for GPU
        """
        print(f"Loading Whisper model: {model_name}...")
        print("(This may take a minute on first run)")
        self.model = whisper.load_model(model_name)
        self.model_name = model_name
    
    def transcribe(self, video_path: Path) -> List[Dict]:
        """
        Transcribe a video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of transcript segments, each with:
            - start: Start time in seconds
            - end: End time in seconds
            - text: Transcribed text
        """
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        print(f"Transcribing video: {video_path}")
        
        try:
            result = self.model.transcribe(str(video_path))
            
            # Return segments with timestamps
            segments = result.get('segments', [])
            
            print(f"Transcription complete. Found {len(segments)} segments.")
            
            return segments
            
        except Exception as e:
            print(f"Error transcribing video: {e}")
            raise
    
    def get_full_text(self, segments: List[Dict]) -> str:
        """Get full transcript text from segments"""
        return " ".join([seg['text'] for seg in segments])
    
    def get_segments_in_range(self, segments: List[Dict], start_time: float, end_time: float) -> List[Dict]:
        """
        Get transcript segments within a time range
        
        Args:
            segments: All transcript segments
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Segments within the time range
        """
        return [
            seg for seg in segments
            if start_time <= seg['start'] <= end_time or 
               (seg['start'] <= start_time <= seg['end'])
        ]


if __name__ == "__main__":
    # Test the transcriber
    transcriber = VideoTranscriber(model_name="base")
    
    # Test with a video (replace with actual path)
    test_video = Path("test_video.mp4")
    
    if test_video.exists():
        print(f"Testing transcription: {test_video}")
        segments = transcriber.transcribe(test_video)
        
        print(f"\nFirst 5 segments:")
        for seg in segments[:5]:
            print(f"{seg['start']:.1f}s - {seg['end']:.1f}s: {seg['text']}")
    else:
        print(f"Test video not found: {test_video}")

