"""
Video Editor
Edits clips: crops to vertical format, adds captions, exports ready-to-post videos
"""
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from pathlib import Path
from typing import List, Dict, Optional
import json

class VideoEditor:
    def __init__(self, output_dir: Path):
        """
        Initialize video editor
        
        Args:
            output_dir: Directory to save edited clips
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_srt_file(self, segments: List[Dict], output_path: Path):
        """
        Create SRT subtitle file from transcript segments
        
        Args:
            segments: Transcript segments with start, end, text
            output_path: Path to save SRT file
        """
        def format_timestamp(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, seg in enumerate(segments, 1):
                start = format_timestamp(seg['start'])
                end = format_timestamp(seg['end'])
                text = seg['text'].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
    
    def edit_clip(self, video_path: Path, start_time: float, end_time: float,
                  transcript_segments: List[Dict], clip_name: str,
                  caption_font_size: int = 70, caption_color: str = "yellow",
                  caption_stroke_color: str = "black", caption_stroke_width: int = 3,
                  fps: int = 30) -> Optional[Path]:
        """
        Edit a video clip: cut, crop to vertical, add captions
        
        Args:
            video_path: Path to source video
            start_time: Start time in seconds
            end_time: End time in seconds
            transcript_segments: Transcript segments for this clip
            clip_name: Name for the output file
            caption_font_size: Font size for captions
            caption_color: Caption text color
            caption_stroke_color: Caption stroke color
            caption_stroke_width: Caption stroke width
            fps: Output video FPS
            
        Returns:
            Path to edited video file, or None if editing failed
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        output_path = self.output_dir / f"{clip_name}.mp4"
        
        print(f"Editing clip: {start_time:.1f}s - {end_time:.1f}s")
        
        try:
            # 1. Load and cut clip
            video = VideoFileClip(str(video_path))
            clip = video.subclip(start_time, end_time)
            
            # 2. Crop to vertical (9:16 aspect ratio)
            w, h = clip.size
            target_w = int(h * 9 / 16)
            
            if w > target_w:
                # Crop from center
                x_center = w / 2
                clip = clip.crop(x1=x_center - target_w / 2, x2=x_center + target_w / 2)
            else:
                # Video is already narrow, crop height instead
                target_h = int(w * 16 / 9)
                y_center = h / 2
                clip = clip.crop(y1=y_center - target_h / 2, y2=y_center + target_h / 2)
            
            # 3. Create caption clips
            caption_clips = []
            
            # Adjust segment times relative to clip start
            for seg in transcript_segments:
                seg_start = seg['start'] - start_time
                seg_end = seg['end'] - start_time
                
                # Only include segments that overlap with clip
                if seg_end > 0 and seg_start < (end_time - start_time):
                    seg_start = max(0, seg_start)
                    seg_end = min(end_time - start_time, seg_end)
                    duration = seg_end - seg_start
                    
                    if duration > 0:
                        try:
                            txt = TextClip(
                                seg['text'],
                                fontsize=caption_font_size,
                                color=caption_color,
                                stroke_color=caption_stroke_color,
                                stroke_width=caption_stroke_width,
                                font='Arial-Bold',
                                method='caption',
                                size=(clip.w * 0.9, None),
                                align='center'
                            )
                            txt = txt.set_position(('center', 'bottom')).set_start(seg_start).set_duration(duration)
                            caption_clips.append(txt)
                        except Exception as e:
                            print(f"Warning: Could not create caption for segment: {e}")
                            continue
            
            # 4. Composite video with captions
            if caption_clips:
                final = CompositeVideoClip([clip] + caption_clips)
            else:
                final = clip
            
            # Set duration
            final = final.set_duration(end_time - start_time)
            
            # 5. Export
            print(f"Exporting to: {output_path}")
            final.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=fps,
                preset='medium',  # Balance between speed and quality
                threads=4,
                logger=None  # Suppress verbose output
            )
            
            # Clean up
            clip.close()
            video.close()
            final.close()
            
            print(f"Clip saved: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error editing clip: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def edit_clip_simple(self, video_path: Path, start_time: float, end_time: float,
                        clip_name: str) -> Optional[Path]:
        """
        Simple version: just cut and crop, no captions (faster)
        
        Args:
            video_path: Path to source video
            start_time: Start time in seconds
            end_time: End time in seconds
            clip_name: Name for the output file
            
        Returns:
            Path to edited video file
        """
        output_path = self.output_dir / f"{clip_name}.mp4"
        
        try:
            video = VideoFileClip(str(video_path))
            clip = video.subclip(start_time, end_time)
            
            # Crop to vertical
            w, h = clip.size
            target_w = int(h * 9 / 16)
            
            if w > target_w:
                x_center = w / 2
                clip = clip.crop(x1=x_center - target_w / 2, x2=x_center + target_w / 2)
            
            clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                logger=None
            )
            
            clip.close()
            video.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error in simple edit: {e}")
            return None


if __name__ == "__main__":
    # Test the editor
    editor = VideoEditor("test_clips")
    
    # Test with a video (replace with actual path)
    test_video = Path("test_video.mp4")
    
    if test_video.exists():
        print(f"Testing video editor: {test_video}")
        
        # Example transcript segments
        test_segments = [
            {'start': 0.0, 'end': 5.0, 'text': 'This is a test caption'},
            {'start': 5.0, 'end': 10.0, 'text': 'Another caption line'},
        ]
        
        result = editor.edit_clip(
            test_video,
            start_time=0.0,
            end_time=10.0,
            transcript_segments=test_segments,
            clip_name="test_clip"
        )
        
        if result:
            print(f"Success! Edited clip saved to: {result}")
    else:
        print(f"Test video not found: {test_video}")

