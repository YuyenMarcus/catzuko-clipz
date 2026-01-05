"""
Caption Generator
Generates viral captions for clips using Ollama (free local LLM)
"""
import ollama
import random
from typing import List, Dict

class CaptionGenerator:
    def __init__(self, model_name: str = "llama3.1"):
        """
        Initialize caption generator
        
        Args:
            model_name: Ollama model name
        """
        self.model_name = model_name
    
    def get_clip_text(self, segments: List[Dict]) -> str:
        """Extract text from transcript segments"""
        return " ".join([seg['text'] for seg in segments])
    
    def generate_caption_ai(self, clip_text: str, link_in_bio: str = "Link in bio 🔗") -> str:
        """
        Generate viral caption using AI
        
        Args:
            clip_text: Text from the clip transcript
            link_in_bio: Text to include for affiliate link
            
        Returns:
            Generated caption text
        """
        prompt = f"""Create a viral TikTok/Instagram Reels caption for this video clip:

"{clip_text}"

Requirements:
- Hook in first 5-8 words that grabs attention
- 50-100 characters total (keep it short and punchy)
- Include call to action: "{link_in_bio}"
- Add 5-8 relevant hashtags at the end
- Make it engaging and click-worthy
- Use emojis sparingly (1-2 max)

Return ONLY the caption text, nothing else."""
        
        try:
            print(f"Generating caption with {self.model_name}...")
            response = ollama.generate(model=self.model_name, prompt=prompt)
            
            caption = response.get('response', '').strip()
            
            # Clean up the response (remove quotes if present)
            caption = caption.strip('"').strip("'")
            
            return caption
            
        except Exception as e:
            print(f"Error generating AI caption: {e}")
            return self.generate_caption_template(clip_text, link_in_bio)
    
    def generate_caption_template(self, clip_text: str, link_in_bio: str = "Link in bio 🔗") -> str:
        """
        Generate caption using templates (fallback method)
        
        Args:
            clip_text: Text from the clip transcript
            link_in_bio: Text to include for affiliate link
            
        Returns:
            Generated caption text
        """
        # Extract key topics from clip text
        text_lower = clip_text.lower()
        
        # Detect topic
        topic = "making money"
        if any(word in text_lower for word in ['secret', 'hidden', 'nobody']):
            topic = "secrets"
        elif any(word in text_lower for word in ['mistake', 'wrong', 'stop']):
            topic = "mistakes"
        elif any(word in text_lower for word in ['rich', 'wealthy', 'million']):
            topic = "wealth"
        elif any(word in text_lower for word in ['business', 'entrepreneur']):
            topic = "business"
        
        # Hook templates
        hooks = [
            f"The truth about {topic}",
            f"How I went from broke to {topic}",
            f"Stop doing this if you want {topic}",
            f"This changed everything for me",
            f"If you're struggling with {topic}, watch this",
            f"Nobody tells you this about {topic}",
            f"The {topic} secret they don't want you to know",
            f"This is why most people fail at {topic}",
        ]
        
        hook = random.choice(hooks)
        
        # Hashtags
        hashtags = [
            "#makemoneyonline", "#sidehustle", "#business", 
            "#entrepreneur", "#wealthy", "#success", 
            "#moneytips", "#passiveincome"
        ]
        
        caption = f"{hook} 💰\n\n{link_in_bio}\n\n{' '.join(hashtags[:6])}"
        
        return caption
    
    def generate_caption(self, segments: List[Dict], use_ai: bool = True, 
                        link_in_bio: str = "Link in bio 🔗") -> str:
        """
        Main method to generate caption
        
        Args:
            segments: Transcript segments for the clip
            use_ai: Whether to use AI (falls back to template if fails)
            link_in_bio: Text for affiliate link
            
        Returns:
            Generated caption
        """
        clip_text = self.get_clip_text(segments)
        
        if use_ai:
            try:
                return self.generate_caption_ai(clip_text, link_in_bio)
            except Exception as e:
                print(f"AI caption generation failed: {e}")
                print("Using template method...")
        
        return self.generate_caption_template(clip_text, link_in_bio)


if __name__ == "__main__":
    # Test the caption generator
    generator = CaptionGenerator(model_name="llama3.1")
    
    # Example transcript segments
    test_segments = [
        {'start': 0.0, 'end': 5.0, 'text': 'The secret to making a million dollars'},
        {'start': 5.0, 'end': 10.0, 'text': 'is something nobody tells you'},
    ]
    
    print("Testing caption generator...")
    caption = generator.generate_caption(test_segments, use_ai=True)
    
    print(f"\nGenerated caption:\n{caption}")

