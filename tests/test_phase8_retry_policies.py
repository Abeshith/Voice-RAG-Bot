"""Phase 8: Retry Policies - Test Suite"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.state import ConversationState
from orchestration.nodes.retry_policy import (
    RetryPolicy,
    RetryManager,
    response_generation_retry_node,
    validation_retry_routing_node
)


def test_retry_policy_exponential_backoff():
    """Test Phase 8: Exponential backoff calculation"""
    print("\n" + "="*60)
    print("TEST: Exponential Backoff Strategy")
    print("="*60)
    
    delays = []
    for attempt in range(5):
        delay = RetryPolicy.get_backoff_delay(attempt, "exponential_backoff")
        delays.append(delay)
        print(f"✓ Attempt {attempt}: {delay}s")
    
    # Verify exponential growth
    assert delays[0] == 1.0, "First attempt should be 1s"
    assert delays[1] == 2.0, "Second attempt should be 2s"
    assert delays[2] == 4.0, "Third attempt should be 4s"
    assert delays[3] == 8.0, "Fourth attempt should be 8s"
    
    print("\n✅ Exponential Backoff: PASSED")
    return True


def test_retry_policy_linear_backoff():
    """Test Phase 8: Linear backoff calculation"""
    print("\n" + "="*60)
    print("TEST: Linear Backoff Strategy")
    print("="*60)
    
    delays = []
    for attempt in range(5):
        delay = RetryPolicy.get_backoff_delay(attempt, "linear_backoff")
        delays.append(delay)
        print(f"✓ Attempt {attempt}: {delay}s")
    
    # Verify linear growth
    assert delays[0] == 0.0, "First attempt should be 0s"
    assert delays[1] == 1.0, "Second attempt should be 1s"
    assert delays[2] == 2.0, "Third attempt should be 2s"
    
    print("\n✅ Linear Backoff: PASSED")
    return True


def test_retry_policy_fixed_delay():
    """Test Phase 8: Fixed delay"""
    print("\n" + "="*60)
    print("TEST: Fixed Delay Strategy")
    print("="*60)
    
    for attempt in range(3):
        delay = RetryPolicy.get_backoff_delay(attempt, "fixed_delay")
        print(f"✓ Attempt {attempt}: {delay}s")
        assert delay == 1.0, "Fixed delay should always be 1s"
    
    print("\n✅ Fixed Delay: PASSED")
    return True


def test_should_retry_retryable_error():
    """Test Phase 8: Retry decision for retryable errors"""
    print("\n" + "="*60)
    print("TEST: Retry Decision - Retryable Errors")
    print("="*60)
    
    retryable = ["timeout", "rate_limit", "service_unavailable"]
    
    for error in retryable:
        result = RetryPolicy.should_retry(0, error, max_retries=3)
        print(f"✓ {error}: {result}")
        assert result == True, f"{error} should be retryable"
    
    print("\n✅ Retryable Errors: PASSED")
    return True


def test_should_retry_non_retryable_error():
    """Test Phase 8: Retry decision for non-retryable errors"""
    print("\n" + "="*60)
    print("TEST: Retry Decision - Non-Retryable Errors")
    print("="*60)
    
    non_retryable = ["validation_error", "permission_error", "not_found"]
    
    for error in non_retryable:
        result = RetryPolicy.should_retry(0, error, max_retries=3)
        print(f"✓ {error}: {result}")
        assert result == False, f"{error} should not be retryable"
    
    print("\n✅ Non-Retryable Errors: PASSED")
    return True


def test_should_retry_max_attempts():
    """Test Phase 8: Max retries limit"""
    print("\n" + "="*60)
    print("TEST: Retry Decision - Max Attempts Limit")
    print("="*60)
    
    max_retries = 3
    
    for attempt in range(5):
        result = RetryPolicy.should_retry(attempt, "timeout", max_retries=max_retries)
        print(f"✓ Attempt {attempt}/{max_retries}: {result}")
        
        if attempt < max_retries:
            assert result == True, f"Should retry at attempt {attempt}"
        else:
            assert result == False, f"Should not retry beyond {max_retries}"
    
    print("\n✅ Max Attempts Limit: PASSED")
    return True


def test_retry_config_normal():
    """Test Phase 8: Retry config for normal severity"""
    print("\n" + "="*60)
    print("TEST: Retry Config - Normal Severity")
    print("="*60)
    
    config = RetryPolicy.get_retry_config("normal")
    
    print(f"✓ Max Retries: {config['max_retries']}")
    print(f"✓ Strategy: {config['strategy']}")
    print(f"✓ Timeout: {config['timeout']}s")
    
    assert config["max_retries"] == 3, "Normal should allow 3 retries"
    assert config["strategy"] == "exponential_backoff", "Should use exponential"
    assert config["timeout"] == 30, "Normal timeout should be 30s"
    
    print("\n✅ Normal Config: PASSED")
    return True


def test_retry_config_critical():
    """Test Phase 8: Retry config for critical severity"""
    print("\n" + "="*60)
    print("TEST: Retry Config - Critical Severity")
    print("="*60)
    
    config = RetryPolicy.get_retry_config("critical")
    
    print(f"✓ Max Retries: {config['max_retries']}")
    print(f"✓ Strategy: {config['strategy']}")
    print(f"✓ Timeout: {config['timeout']}s")
    
    assert config["max_retries"] == 7, "Critical should allow 7 retries"
    assert config["strategy"] == "adaptive", "Should use adaptive"
    assert config["timeout"] == 60, "Critical timeout should be 60s"
    
    print("\n✅ Critical Config: PASSED")
    return True


def test_response_generation_retry_node():
    """Test Phase 8: Response generation retry node"""
    print("\n" + "="*60)
    print("TEST: Response Generation Retry Node")
    print("="*60)
    
    state = ConversationState(
        user_input="test",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        complaint_severity="HIGH",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = response_generation_retry_node(state)
    
    print(f"✓ Retry Policy: {result['retry_policy_applied']}")
    print(f"✓ Max Attempts: {result['retry_max_attempts']}")
    print(f"✓ Strategy: {result['retry_strategy']}")
    
    assert result["retry_policy_applied"] == "high", "HIGH severity complaint"
    assert result["retry_max_attempts"] == 5, "HIGH should allow 5 retries"
    
    print("\n✅ Retry Node: PASSED")
    return True


def test_validation_retry_routing_pass():
    """Test Phase 8: Validation retry routing - validation passed"""
    print("\n" + "="*60)
    print("TEST: Validation Retry Routing - Pass")
    print("="*60)
    
    state = ConversationState(
        user_input="test",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        complaint_severity="MEDIUM",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="Good response",
        validation_passed=True,
        final_audio_path="",
    )
    
    route = validation_retry_routing_node(state)
    
    print(f"✓ Route: {route}")
    assert route == "memory_persistence", "Should proceed to persistence when validated"
    
    print("\n✅ Validation Pass Routing: PASSED")
    return True


def test_validation_retry_routing_retry():
    """Test Phase 8: Validation retry routing - retry available"""
    print("\n" + "="*60)
    print("TEST: Validation Retry Routing - Retry Available")
    print("="*60)
    
    state = ConversationState(
        user_input="test",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        complaint_severity="MEDIUM",
        retry_count=1,
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="Bad response",
        validation_passed=False,
        final_audio_path="",
    )
    
    route = validation_retry_routing_node(state)
    
    print(f"✓ Route: {route}")
    assert route == "response_generation", "Should retry when validation failed and retries available"
    
    print("\n✅ Retry Available Routing: PASSED")
    return True


def test_validation_retry_routing_escalate():
    """Test Phase 8: Validation retry routing - escalate on critical"""
    print("\n" + "="*60)
    print("TEST: Validation Retry Routing - Escalate Critical")
    print("="*60)
    
    state = ConversationState(
        user_input="test",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        complaint_severity="CRITICAL",
        retry_count=7,
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="Failed response",
        validation_passed=False,
        final_audio_path="",
    )
    
    route = validation_retry_routing_node(state)
    
    print(f"✓ Route: {route}")
    assert route == "escalation", "Should escalate when critical retries exhausted"
    
    print("\n✅ Escalate Routing: PASSED")
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 8: RETRY POLICIES - TESTS")
    print("="*60)
    
    test_retry_policy_exponential_backoff()
    test_retry_policy_linear_backoff()
    test_retry_policy_fixed_delay()
    test_should_retry_retryable_error()
    test_should_retry_non_retryable_error()
    test_should_retry_max_attempts()
    test_retry_config_normal()
    test_retry_config_critical()
    test_response_generation_retry_node()
    test_validation_retry_routing_pass()
    test_validation_retry_routing_retry()
    test_validation_retry_routing_escalate()
    
    print("\n" + "="*60)
    print("PHASE 8: All retry policy tests PASSED")
    print("="*60 + "\n")
