"""Phase 4: Memory Retrieval Node - Test Suite"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.state import ConversationState
from orchestration.nodes.memory_retrieval import memory_retrieval_node


def test_memory_retrieval_basic():
    """Test Phase 4: Memory Retrieval with existing customer"""
    print("\n" + "="*60)
    print("TEST: Memory Retrieval Node - Existing Customer")
    print("="*60)
    
    state = ConversationState(
        user_input="What about my previous issues?",
        customer_id="TEST_001",
        intent="inquiry",
        sentiment="NEUTRAL",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = memory_retrieval_node(state)
    
    memory_context = result.get("memory_context", "")
    history_sessions = result.get("history_sessions", 0)
    
    print(f"\n✓ Memory Context Length: {len(memory_context)} chars")
    print(f"✓ History Sessions Found: {history_sessions}")
    
    if memory_context:
        print(f"✓ Memory Context Preview:")
        for line in memory_context.split("\n")[:5]:
            print(f"  {line}")
    
    assert "memory_context" in result, "No memory_context in result"
    assert "history_sessions" in result, "No history_sessions in result"
    
    print("\n✅ Memory Retrieval (Existing): PASSED")
    return True


def test_memory_retrieval_no_customer():
    """Test Phase 4: Memory Retrieval with missing customer_id"""
    print("\n" + "="*60)
    print("TEST: Memory Retrieval Node - No Customer ID")
    print("="*60)
    
    state = ConversationState(
        user_input="Hello",
        customer_id="",
        intent="inquiry",
        sentiment="NEUTRAL",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = memory_retrieval_node(state)
    
    memory_context = result.get("memory_context", "")
    history_sessions = result.get("history_sessions", 0)
    
    print(f"\n✓ Memory Context: '{memory_context}'")
    print(f"✓ History Sessions: {history_sessions}")
    
    assert history_sessions == 0, "Should have 0 sessions for empty customer_id"
    
    print("\n✅ Memory Retrieval (No Customer): PASSED")
    return True


def test_memory_retrieval_new_customer():
    """Test Phase 4: Memory Retrieval with customer having no history"""
    print("\n" + "="*60)
    print("TEST: Memory Retrieval Node - New Customer")
    print("="*60)
    
    state = ConversationState(
        user_input="Hello, I'm new here",
        customer_id="NEW_CUST_999999",
        intent="inquiry",
        sentiment="NEUTRAL",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = memory_retrieval_node(state)
    
    memory_context = result.get("memory_context", "")
    history_sessions = result.get("history_sessions", 0)
    
    print(f"\n✓ Memory Context Length: {len(memory_context)}")
    print(f"✓ History Sessions: {history_sessions}")
    
    # New customer may have 0 or empty context
    assert "memory_context" in result, "No memory_context in result"
    
    print("\n✅ Memory Retrieval (New Customer): PASSED")
    return True


def test_memory_context_structure():
    """Test Phase 4: Memory Context has proper structure"""
    print("\n" + "="*60)
    print("TEST: Memory Context Structure")
    print("="*60)
    
    state = ConversationState(
        user_input="Query",
        customer_id="TEST_001",
        intent="inquiry",
        sentiment="NEUTRAL",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = memory_retrieval_node(state)
    memory_context = result.get("memory_context", "")
    
    if memory_context:
        lines = memory_context.split("\n")
        
        # Check for expected structure
        has_customer_id = "Customer History Summary" in memory_context
        has_sessions = "Total Sessions" in memory_context or "Session" in memory_context
        
        print(f"\n✓ Has Customer ID: {has_customer_id}")
        print(f"✓ Has Session Info: {has_sessions}")
        
        if has_customer_id:
            assert "TEST_001" in memory_context, "Customer ID not in context"
        
        print("\n✅ Memory Context Structure: PASSED")
    else:
        print("\n⚠️  Memory Context is empty (no history for customer)")
    
    return True


def test_memory_retrieval_response_type():
    """Test Phase 4: Memory Retrieval returns correct types"""
    print("\n" + "="*60)
    print("TEST: Memory Retrieval Response Types")
    print("="*60)
    
    state = ConversationState(
        user_input="test",
        customer_id="TEST_001",
        intent="inquiry",
        sentiment="NEUTRAL",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = memory_retrieval_node(state)
    
    memory_context = result.get("memory_context")
    history_sessions = result.get("history_sessions")
    
    print(f"\n✓ memory_context type: {type(memory_context).__name__}")
    print(f"✓ history_sessions type: {type(history_sessions).__name__}")
    
    assert isinstance(memory_context, str), f"memory_context should be str, got {type(memory_context)}"
    assert isinstance(history_sessions, int), f"history_sessions should be int, got {type(history_sessions)}"
    
    print("\n✅ Response Types: PASSED")
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 4: MEMORY RETRIEVAL NODE - TESTS")
    print("="*60)
    
    test_memory_retrieval_basic()
    test_memory_retrieval_no_customer()
    test_memory_retrieval_new_customer()
    test_memory_context_structure()
    test_memory_retrieval_response_type()
    
    print("\n" + "="*60)
    print("PHASE 4: All memory retrieval tests PASSED")
    print("="*60 + "\n")
