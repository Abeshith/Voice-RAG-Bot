"""Response quality validation"""

from orchestration.state import ConversationState
from typing import Dict, Any
import logging
from orchestration.latency_tracker import get_tracker

logger = logging.getLogger(__name__)


def validation_node(state: ConversationState) -> Dict[str, Any]:
    """
    Validate generated response against quality criteria:
    1. Length checks (not too short, not too long)
    2. Tone-sentiment consistency
    3. Basic sanity checks
    
    Returns:
        state update with validation_passed boolean
    """
    tracker = get_tracker()
    tracker.start("validation")
    
    response = state.get('response', '')
    sentiment = state.get('sentiment', {}).get('label', 'NEUTRAL')
    
    # Check 1: Response length (between 50-500 characters)
    response_length = len(response)
    length_valid = 50 <= response_length <= 500
    
    # Check 2: Tone-sentiment consistency
    tone_checks = {
        "NEGATIVE": {
            "forbidden_words": ["happy", "excellent", "amazing"],
            "required_sentiment": ["understand", "apologize", "help"]
        },
        "POSITIVE": {
            "forbidden_words": ["sorry", "problem", "issue"],
            "required_sentiment": ["great", "happy", "enjoy"]
        }
    }
    
    response_lower = response.lower()
    tone_valid = True
    
    if sentiment in tone_checks:
        checks = tone_checks[sentiment]
        # Check forbidden words aren't present
        forbidden_present = any(word in response_lower for word in checks.get("forbidden_words", []))
        tone_valid = not forbidden_present
    
    # Check 3: Response not empty
    content_valid = len(response.strip()) > 0
    
    # Overall validation
    validation_passed = length_valid and content_valid and tone_valid
    
    logger.info(f"✓ Validation: length={response_length} ({length_valid}), content={content_valid}, tone={tone_valid} -> {'PASS' if validation_passed else 'FAIL'}")
    
    tracker.end("validation")
    return {"validation_passed": validation_passed}
