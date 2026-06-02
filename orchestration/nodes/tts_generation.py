"""Text-to-speech generation using gTTS"""

from gtts import gTTS
from orchestration.state import ConversationState
from typing import Dict, Any
import os
import logging
from pathlib import Path
from orchestration.latency_tracker import get_tracker

logger = logging.getLogger(__name__)


def tts_generation_node(state: ConversationState) -> Dict[str, Any]:
    """
    Convert response text to speech using gTTS
    Saves audio file and returns path
    
    Returns:
        state update with final_audio_path field
    """
    tracker = get_tracker()
    tracker.start("tts_generation")
    
    response_text = state.get('response', '')
    
    # Validate response text exists
    if not response_text or len(response_text.strip()) == 0:
        logger.warning("⚠️ TTS: No response text to convert to speech")
        tracker.end("tts_generation")
        return {"final_audio_path": None}
    
    # Create output directory if doesn't exist
    audio_dir = Path("data/audio_output")
    try:
        audio_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"❌ TTS: Failed to create audio directory: {e}")
        tracker.end("tts_generation")
        return {"final_audio_path": None}
    
    # Generate unique filename
    customer_id = state.get('customer_id', 'UNKNOWN')
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
    audio_filename = f"bot_response_{customer_id}_{timestamp}.mp3"
    audio_path = audio_dir / audio_filename
    
    try:
        logger.info(f"📢 TTS: Generating audio for: '{response_text[:50]}...'")
        
        # Generate TTS
        tts = gTTS(text=response_text, lang='en', slow=False)
        tts.save(str(audio_path))
        
        # Verify file was created
        if audio_path.exists():
            file_size = audio_path.stat().st_size
            logger.info(f"✅ TTS: Audio generated successfully ({file_size} bytes) -> {audio_path}")
            final_audio_path = str(audio_path)
        else:
            logger.error(f"❌ TTS: File created but not found at {audio_path}")
            final_audio_path = None
            
    except Exception as e:
        logger.error(f"❌ TTS generation failed: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        final_audio_path = None
    
    tracker.end("tts_generation")
    return {"final_audio_path": final_audio_path}
