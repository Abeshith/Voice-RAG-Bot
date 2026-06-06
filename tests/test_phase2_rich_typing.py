import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.state import (
    ConversationState, ConversationStateEnhanced, 
    StateValidator, validate_intent, validate_sentiment
)


def test_validate_intent():
    assert validate_intent("complaint") == True
    assert validate_intent("refund_request") == True
    assert validate_intent("inquiry") == True
    assert validate_intent("invalid_intent") == False
    print("✓ Intent validation works")


def test_validate_sentiment():
    assert validate_sentiment("POSITIVE") == True
    assert validate_sentiment("NEGATIVE") == True
    assert validate_sentiment("NEUTRAL") == True
    assert validate_sentiment("INVALID") == False
    print("✓ Sentiment validation works")


def test_base_state_validation():
    valid_state = {
        "user_input": "test",
        "customer_id": "CUST_001",
        "intent": "inquiry",
        "sentiment": "NEUTRAL",
        "entities": {},
        "conversation_summary": "",
        "kb_context": "",
        "history_context": "",
        "response": "",
        "validation_passed": True,
        "final_audio_path": None
    }
    assert StateValidator.validate_base_state(valid_state) == True
    print("✓ Base state validation works")
    
    invalid_state = {
        "user_input": 123,
        "customer_id": "CUST_001",
        "intent": "bad_intent",
        "sentiment": "NEUTRAL"
    }
    assert StateValidator.validate_base_state(invalid_state) == False
    print("✓ Invalid base state rejected")


def test_enhanced_state_validation():
    enhanced_state = {
        "user_input": "test",
        "customer_id": "CUST_001",
        "intent": "complaint",
        "sentiment": "NEGATIVE",
        "intent_confidence": 0.95,
        "sentiment_confidence": 0.87,
        "retry_count": 0,
        "validation_attempts": 1
    }
    assert StateValidator.validate_enhanced(enhanced_state) == True
    print("✓ Enhanced state validation works")
    
    invalid_enhanced = enhanced_state.copy()
    invalid_enhanced["intent_confidence"] = 1.5
    assert StateValidator.validate_enhanced(invalid_enhanced) == False
    print("✓ Invalid confidence rejected")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 2: RICH STATE TYPING - VALIDATION TESTS")
    print("="*60 + "\n")
    
    test_validate_intent()
    test_validate_sentiment()
    test_base_state_validation()
    test_enhanced_state_validation()
    
    print("\n" + "="*60)
    print("PHASE 2: All validation tests PASSED")
    print("="*60 + "\n")
