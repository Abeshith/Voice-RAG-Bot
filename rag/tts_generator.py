"""
Text-to-Speech Generator - Converts bot responses to audio
Uses gTTS with professional customer support voice
"""

from gtts import gTTS
from pathlib import Path
from datetime import datetime
import json


class TTSGenerator:
    """Generates audio files for bot responses"""
    
    def __init__(self, output_dir: str = "data/audio_output"):
        """Initialize TTS generator
        
        Args:
            output_dir: Directory to save audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_audio(self, text: str, customer_id: str, session_id: str) -> str:
        """
        Generate audio file from text
        
        Args:
            text: Response text to convert to speech
            customer_id: Customer ID for file organization
            session_id: Session ID for context
        
        Returns:
            Path to generated audio file
        """
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bot_response_{customer_id}_{session_id[:8]}_{timestamp}.mp3"
            filepath = self.output_dir / filename
            
            # Generate speech with gTTS
            # Using slower speech rate (slow=True) for clarity
            # Language: English (US) for professional tone
            tts = gTTS(
                text=text,
                lang='en',
                slow=True,  # Slower speech for clarity
                tld='com'   # Top-level domain for better quality
            )
            
            # Save to file
            tts.save(str(filepath))
            
            print(f"[TTS] Generated audio: {filename} ({len(text)} chars)")
            return str(filepath)
            
        except Exception as e:
            print(f"[TTS ERROR] Failed to generate audio: {str(e)}")
            return ""
    
    def generate_greeting(self, customer_id: str) -> str:
        """Generate audio for greeting message"""
        greeting_text = "Hello! How can I help you today?"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"greeting_{customer_id}_{timestamp}.mp3"
        filepath = self.output_dir / filename
        
        try:
            tts = gTTS(
                text=greeting_text,
                lang='en',
                slow=True,
                tld='com'
            )
            tts.save(str(filepath))
            print(f"[TTS] Generated greeting: {filename}")
            return str(filepath)
        except Exception as e:
            print(f"[TTS ERROR] Failed to generate greeting: {str(e)}")
            return ""


# Global TTS generator instance
_tts_generator = None


def get_tts_generator() -> TTSGenerator:
    """Get or create global TTS generator"""
    global _tts_generator
    if _tts_generator is None:
        _tts_generator = TTSGenerator()
    return _tts_generator
