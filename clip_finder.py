"""
Viral Clip Finder
Identifies viral-worthy clips from transcripts using Ollama (free local LLM)
"""
import ollama
import json
import re
from typing import List, Dict, Optional

class ClipFinder:
    def __init__(self, model_name: str = "llama3.1"):
        """
        Initialize clip finder
        
        Args:
            model_name: Ollama model name (llama3.1, mistral, phi3)
        """
        self.model_name = model_name
        self._verify_model()
    
    def _verify_model(self):
        """Verify that the Ollama model is available"""
        try:
            # Try to list models to verify Ollama is running
            models = ollama.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            if self.model_name not in model_names:
                print(f"Warning: Model {self.model_name} not found.")
                print(f"Available models: {model_names}")
                print(f"Run: ollama pull {self.model_name}")
        except Exception as e:
            print(f"Warning: Could not verify Ollama model: {e}")
            print(f"Make sure Ollama is running. Download from https://ollama.ai")
    
    def format_transcript_for_analysis(self, segments: List[Dict]) -> str:
        """Format transcript segments into readable text for AI analysis"""
        lines = []
        for seg in segments:
            start_min = int(seg['start'] // 60)
            start_sec = int(seg['start'] % 60)
            end_min = int(seg['end'] // 60)
            end_sec = int(seg['end'] % 60)
            
            lines.append(f"[{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}] {seg['text']}")
        
        return "\n".join(lines)
    
    def find_clips_ai(self, segments: List[Dict], max_clips: int = 5, 
                      min_duration: int = 30, max_duration: int = 60) -> List[Dict]:
        """
        Find viral clips using AI analysis
        
        Args:
            segments: Transcript segments
            max_clips: Maximum number of clips to find
            min_duration: Minimum clip duration in seconds
            max_duration: Maximum clip duration in seconds
            
        Returns:
            List of clip dictionaries with start, end, and reason
        """
        transcript_text = self.format_transcript_for_analysis(segments)
        
        prompt = f"""Analyze this video transcript and identify the {max_clips} most viral-worthy clips (30-60 seconds each).

Look for:
- Controversial statements or hot takes
- Money/success/wealth mentions
- Actionable advice or tips
- Emotional peaks or dramatic moments
- Bold claims or surprising facts
- Personal stories or transformations
- "Nobody tells you" moments
- Secrets or hidden information

Transcript:
{transcript_text}

Return ONLY a valid JSON array with this exact format:
[
  {{"start": 45.2, "end": 78.5, "reason": "Bold money claim about making $10k/month"}},
  {{"start": 120.0, "end": 165.3, "reason": "Controversial take on traditional education"}}
]

Each clip must be between {min_duration} and {max_duration} seconds long.
Return exactly {max_clips} clips, or fewer if the video doesn't have enough good moments.
"""
        
        try:
            print(f"Analyzing transcript with {self.model_name}...")
            response = ollama.generate(model=self.model_name, prompt=prompt)
            
            response_text = response.get('response', '')
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                json_text = response_text
            
            clips = json.loads(json_text)
            
            # Validate and filter clips
            valid_clips = []
            for clip in clips:
                start = float(clip.get('start', 0))
                end = float(clip.get('end', 0))
                duration = end - start
                
                if min_duration <= duration <= max_duration:
                    valid_clips.append({
                        'start': start,
                        'end': end,
                        'duration': duration,
                        'reason': clip.get('reason', 'Viral moment')
                    })
            
            # Sort by start time and limit
            valid_clips.sort(key=lambda x: x['start'])
            return valid_clips[:max_clips]
            
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response as JSON: {e}")
            print(f"Response was: {response_text[:500]}")
            return self.find_clips_keyword(segments, max_clips, min_duration, max_duration)
        except Exception as e:
            print(f"Error using AI to find clips: {e}")
            print("Falling back to keyword-based method...")
            return self.find_clips_keyword(segments, max_clips, min_duration, max_duration)
    
    def find_clips_keyword(self, segments: List[Dict], max_clips: int = 5,
                          min_duration: int = 30, max_duration: int = 60) -> List[Dict]:
        """
        Find clips using keyword matching (fallback method)
        
        Args:
            segments: Transcript segments
            max_clips: Maximum number of clips to find
            min_duration: Minimum clip duration in seconds
            max_duration: Maximum clip duration in seconds
            
        Returns:
            List of clip dictionaries
        """
        viral_keywords = [
            'million', 'secret', 'mistake', 'truth', 'broke', 'rich', 
            'nobody tells you', 'nobody talks about', 'hidden', 'secret',
            'stop doing', 'this changed', 'if you want to', 'how i made',
            'passive income', 'side hustle', 'make money', 'earn money',
            'quit your job', 'fired', 'failed', 'success', 'wealthy',
            'the truth about', 'what they don\'t tell you', 'insider',
            'exposed', 'revealed', 'shocking', 'unbelievable'
        ]
        
        clips = []
        
        for segment in segments:
            text_lower = segment['text'].lower()
            
            # Check if segment contains viral keywords
            if any(keyword in text_lower for keyword in viral_keywords):
                # Extract 30-60 seconds around this moment
                center_time = (segment['start'] + segment['end']) / 2
                start = max(0, center_time - (max_duration / 2))
                end = center_time + (max_duration / 2)
                
                # Adjust to fit within video bounds
                video_end = max(seg['end'] for seg in segments)
                if end > video_end:
                    end = video_end
                    start = max(0, end - max_duration)
                
                duration = end - start
                
                if min_duration <= duration <= max_duration:
                    clips.append({
                        'start': start,
                        'end': end,
                        'duration': duration,
                        'reason': f"Keyword match: {[k for k in viral_keywords if k in text_lower][0]}"
                    })
        
        # Remove overlapping clips
        clips = self._remove_overlaps(clips)
        
        # Sort by start time and limit
        clips.sort(key=lambda x: x['start'])
        return clips[:max_clips]
    
    def _remove_overlaps(self, clips: List[Dict], overlap_threshold: float = 10.0) -> List[Dict]:
        """Remove overlapping clips, keeping the ones with better reasons"""
        if not clips:
            return []
        
        # Sort by start time
        clips = sorted(clips, key=lambda x: x['start'])
        
        non_overlapping = [clips[0]]
        
        for clip in clips[1:]:
            last_clip = non_overlapping[-1]
            
            # Check if clips overlap significantly
            if clip['start'] < last_clip['end'] - overlap_threshold:
                # Keep the clip with longer duration or better reason
                if clip['duration'] > last_clip['duration']:
                    non_overlapping[-1] = clip
            else:
                non_overlapping.append(clip)
        
        return non_overlapping
    
    def find_clips(self, segments: List[Dict], use_ai: bool = True, **kwargs) -> List[Dict]:
        """
        Main method to find clips (tries AI first, falls back to keywords)
        
        Args:
            segments: Transcript segments
            use_ai: Whether to try AI first
            **kwargs: Additional arguments passed to find_clips methods
            
        Returns:
            List of clip dictionaries
        """
        if use_ai:
            try:
                return self.find_clips_ai(segments, **kwargs)
            except Exception as e:
                print(f"AI method failed: {e}")
                print("Using keyword-based method...")
        
        return self.find_clips_keyword(segments, **kwargs)


if __name__ == "__main__":
    # Test the clip finder
    finder = ClipFinder(model_name="llama3.1")
    
    # Example transcript segments
    test_segments = [
        {'start': 0.0, 'end': 5.0, 'text': 'Welcome to the channel'},
        {'start': 5.0, 'end': 15.0, 'text': 'Today I\'m going to reveal the secret to making a million dollars'},
        {'start': 15.0, 'end': 45.0, 'text': 'Nobody tells you this, but if you want to get rich, you need to stop doing what everyone else is doing'},
        {'start': 45.0, 'end': 60.0, 'text': 'This changed everything for me'},
    ]
    
    print("Testing clip finder...")
    clips = finder.find_clips(test_segments, max_clips=3, min_duration=30, max_duration=60)
    
    print(f"\nFound {len(clips)} clips:")
    for i, clip in enumerate(clips, 1):
        print(f"\nClip {i}:")
        print(f"  Time: {clip['start']:.1f}s - {clip['end']:.1f}s ({clip['duration']:.1f}s)")
        print(f"  Reason: {clip['reason']}")

