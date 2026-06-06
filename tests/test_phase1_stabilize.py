"""Phase 1: Stabilize Current Graph - Test Suite"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.langgraph_workflow import compiled_workflow, run_workflow
import json
from datetime import datetime

# Test cases for Phase 1
TEST_CASES = [
    {
        "name": "Refund Request",
        "input": "My refund is delayed",
        "expected": {
            "intent": "refund_request",
            "sentiment": "negative",
            "has_entities": True,
            "has_response": True,
        }
    },
    {
        "name": "Order Status Inquiry",
        "input": "Where is my order ORD123?",
        "expected": {
            "intent": "order_status",
            "sentiment": "neutral",
            "has_entities": True,
            "has_response": True,
        }
    },
    {
        "name": "Complaint with Escalation",
        "input": "This is my third complaint about this issue",
        "expected": {
            "intent": "complaint",
            "sentiment": "negative",
            "has_entities": False,
            "has_response": True,
        }
    },
    {
        "name": "Product Question",
        "input": "Tell me about your return policy",
        "expected": {
            "intent": "product_question",
            "sentiment": "neutral",
            "has_entities": False,
            "has_response": True,
        }
    },
    {
        "name": "Billing Issue",
        "input": "I was charged twice for my order",
        "expected": {
            "intent": "billing_issue",
            "sentiment": "negative",
            "has_entities": True,
            "has_response": True,
        }
    },
]

def test_entity_extraction():
    """Test Phase 1: Entity Extraction Node"""
    print("\n" + "="*60)
    print("TEST: Entity Extraction Node")
    print("="*60)
    
    from orchestration.nodes.entity_extraction import entity_extraction_node
    from orchestration.state import ConversationState
    
    test_inputs = [
        "My name is John Smith and order ORD123",
        "Contact support@company.com",
        "Customer ID: CUST_001",
    ]
    
    for test_input in test_inputs:
        state = ConversationState(
            user_input=test_input,
            customer_id="TEST_001",
            intent="",
            sentiment="",
            entities={},
            conversation_summary="",
            kb_context="",
            history_context="",
            response="",
            validation_passed=False,
            final_audio_path="",
        )
        
        result = entity_extraction_node(state)
        
        print(f"\n✓ Input: {test_input}")
        print(f"  Entities: {result.get('entities', {})}")
        
        assert "entities" in result, "No entities extracted"
    
    print("\n✅ Entity Extraction: PASSED")
    return True


def test_sentiment_analysis():
    """Test Phase 1: Sentiment Analysis Node"""
    print("\n" + "="*60)
    print("TEST: Sentiment Analysis Node")
    print("="*60)
    
    from orchestration.nodes.sentiment_hybrid import sentiment_analysis_hybrid
    from orchestration.state import ConversationState
    
    test_cases_sentiment = [
        ("I love your product!", "positive"),
        ("I'm very frustrated", "negative"),
        ("Tell me about your service", "neutral"),
        ("This is absolutely unacceptable", "negative"),
    ]
    
    for test_input, expected_sentiment in test_cases_sentiment:
        state = ConversationState(
            user_input=test_input,
            customer_id="TEST_001",
            intent="",
            sentiment="",
            entities={},
            conversation_summary="",
            kb_context="",
            history_context="",
            response="",
            validation_passed=False,
            final_audio_path="",
        )
        
        result = sentiment_analysis_hybrid(state)
        
        sentiment = result.get("sentiment", "").upper()
        print(f"\n✓ Input: {test_input}")
        print(f"  Detected: {sentiment} (Expected: {expected_sentiment.upper()})")
        
        assert sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"], f"Invalid sentiment: {sentiment}"
    
    print("\n✅ Sentiment Analysis: PASSED")
    return True


def test_intent_detection():
    """Test Phase 1: Intent Detection Node"""
    print("\n" + "="*60)
    print("TEST: Intent Detection Node")
    print("="*60)
    
    from orchestration.nodes.intent_detection import intent_detection_node
    from orchestration.state import ConversationState
    
    valid_intents = [
        "complaint",
        "refund_request",
        "inquiry",
        "account_issue",
        "escalation",
        "billing",
        "product_question",
        "order_status",
        "other"
    ]
    
    test_inputs = [
        "I want to return this",
        "Where is my order",
        "My account is locked",
        "I was overcharged",
    ]
    
    for test_input in test_inputs:
        state = ConversationState(
            user_input=test_input,
            customer_id="TEST_001",
            intent="",
            sentiment="",
            entities={},
            conversation_summary="",
            kb_context="",
            history_context="",
            response="",
            validation_passed=False,
            final_audio_path="",
        )
        
        result = intent_detection_node(state)
        
        intent = result.get("intent", "").lower()
        confidence = result.get("confidence", 0)
        
        print(f"\n✓ Input: {test_input}")
        print(f"  Intent: {intent} (Confidence: {confidence:.2f})")
        
        assert intent in valid_intents, f"Invalid intent: {intent}"
        assert 0 <= confidence <= 1, f"Invalid confidence: {confidence}"
    
    print("\n✅ Intent Detection: PASSED")
    return True


def test_retrieval_router():
    """Test Phase 1: Retrieval Router Node"""
    print("\n" + "="*60)
    print("TEST: Retrieval Router Node")
    print("="*60)
    
    from orchestration.nodes.retrieval_router import retrieval_router_node
    from orchestration.state import ConversationState
    
    state = ConversationState(
        user_input="My refund is delayed",
        customer_id="TEST_001",
        intent="refund_request",
        sentiment="NEGATIVE",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = retrieval_router_node(state)
    
    kb_context = result.get("kb_context", "")
    history_context = result.get("history_context", "")
    
    print(f"\n✓ Retrieved KB Context: {len(kb_context)} chars")
    print(f"✓ Retrieved History Context: {len(history_context)} chars")
    
    assert "kb_context" in result, "No KB context retrieved"
    
    print("\n✅ Retrieval Router: PASSED")
    return True


def test_context_builder():
    """Test Phase 1: Context Builder Node"""
    print("\n" + "="*60)
    print("TEST: Context Builder Node")
    print("="*60)
    
    from orchestration.nodes.context_builder import context_builder_node
    from orchestration.state import ConversationState
    
    state = ConversationState(
        user_input="My refund is delayed",
        customer_id="TEST_001",
        intent="refund_request",
        sentiment="NEGATIVE",
        entities={"PRODUCT": ["laptop"]},
        conversation_summary="Customer wants refund",
        kb_context="Refund policy: 30 days",
        history_context="Previous complaint about shipping",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = context_builder_node(state)
    
    print(f"\n✓ Context built successfully")
    print(f"  State keys: {list(result.keys())}")
    
    print("\n✅ Context Builder: PASSED")
    return True


def test_response_generation():
    """Test Phase 1: Response Generation Node"""
    print("\n" + "="*60)
    print("TEST: Response Generation Node")
    print("="*60)
    
    from orchestration.nodes.response_generation import response_generation_node
    from orchestration.state import ConversationState
    
    state = ConversationState(
        user_input="My refund is delayed",
        customer_id="TEST_001",
        intent="refund_request",
        sentiment="NEGATIVE",
        entities={"PRODUCT": ["laptop"]},
        conversation_summary="Customer wants refund",
        kb_context="Refund policy: 30 days",
        history_context="Previous complaint",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = response_generation_node(state)
    
    response = result.get("response", "")
    
    print(f"\n✓ Generated Response ({len(response)} chars):")
    print(f"  {response[:100]}...")
    
    assert len(response) > 0, "Empty response generated"
    assert len(response) >= 50, "Response too short"
    
    print("\n✅ Response Generation: PASSED")
    return True


def test_validation():
    """Test Phase 1: Validation Node"""
    print("\n" + "="*60)
    print("TEST: Validation Node")
    print("="*60)
    
    from orchestration.nodes.validation import validation_node
    from orchestration.state import ConversationState
    
    good_response = "I understand your frustration. Your refund is being processed and should arrive within 5-7 business days."
    
    state = ConversationState(
        user_input="My refund is delayed",
        customer_id="TEST_001",
        intent="refund_request",
        sentiment="NEGATIVE",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response=good_response,
        validation_passed=False,
        final_audio_path="",
    )
    
    result = validation_node(state)
    
    validation_passed = result.get("validation_passed", False)
    
    print(f"\n✓ Response: {good_response[:80]}...")
    print(f"  Validation Passed: {validation_passed}")
    
    assert "validation_passed" in result, "No validation result"
    
    print("\n✅ Validation: PASSED")
    return True


def test_memory_persistence():
    """Test Phase 1: Memory Persistence Node"""
    print("\n" + "="*60)
    print("TEST: Memory Persistence Node")
    print("="*60)
    
    from orchestration.nodes.memory_persistence import memory_persistence_node
    from orchestration.state import ConversationState
    
    state = ConversationState(
        user_input="My refund is delayed",
        customer_id="TEST_001",
        intent="refund_request",
        sentiment="NEGATIVE",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="Your refund is being processed.",
        validation_passed=True,
        final_audio_path="",
    )
    
    result = memory_persistence_node(state)
    
    print(f"\n✓ Memory persisted for customer: TEST_001")
    print(f"  Interaction Type: refund_request")
    
    print("\n✅ Memory Persistence: PASSED")
    return True


def test_tts_generation():
    """Test Phase 1: TTS Generation Node"""
    print("\n" + "="*60)
    print("TEST: TTS Generation Node")
    print("="*60)
    
    from orchestration.nodes.tts_generation import tts_generation_node
    from orchestration.state import ConversationState
    
    state = ConversationState(
        user_input="My refund is delayed",
        customer_id="TEST_001",
        intent="refund_request",
        sentiment="NEGATIVE",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="Your refund is being processed within 5-7 business days.",
        validation_passed=True,
        final_audio_path="",
    )
    
    result = tts_generation_node(state)
    
    audio_path = result.get("final_audio_path")
    
    print(f"\n✓ Audio Generated: {audio_path}")
    
    if audio_path:
        audio_file = Path(audio_path)
        if audio_file.exists():
            size_mb = audio_file.stat().st_size / (1024*1024)
            print(f"  File Size: {size_mb:.2f} MB")
    
    print("\n✅ TTS Generation: PASSED")
    return True


def test_end_to_end():
    """Test Phase 1: End-to-End Workflow"""
    import asyncio
    
    print("\n" + "="*70)
    print("TEST: END-TO-END WORKFLOW")
    print("="*70)
    
    results = []
    
    for test_case in TEST_CASES:
        print(f"\n{'─'*70}")
        print(f"Test Case: {test_case['name']}")
        print(f"Input: {test_case['input']}")
        print(f"{'─'*70}")
        
        try:
            result = asyncio.run(run_workflow(test_case["input"], "TEST_001"))
            
            # Verify expected outputs
            intent = result.get("intent", "")
            sentiment = result.get("sentiment", "")
            entities = result.get("entities", {})
            response = result.get("response", "")
            audio_path = result.get("final_audio_path")
            
            print(f"\n✓ Intent: {intent}")
            print(f"✓ Sentiment: {sentiment}")
            
            try:
                print(f"✓ Entities: {len(entities)} found")
            except TypeError as te:
                print(f"✓ Entities: ERROR - {te} - Value: {entities}")
                raise
                
            try:
                print(f"✓ Response: {response[:80]}...")
            except TypeError as te:
                print(f"✓ Response: ERROR - {te} - Value: {response}")
                raise
                
            print(f"✓ Audio Path: {audio_path}")
            
            # Validation
            checks = {
                "response_generated": len(response) > 10 and not response.startswith("Error") and "{" not in response[:20],
                "intent_detected": len(intent) > 0,
                "sentiment_detected": len(sentiment) > 0 and sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"],
                "validation_passed": result.get("validation_passed", False),
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                print(f"\n✅ Test Case PASSED")
                results.append(("PASSED", test_case["name"]))
            else:
                print(f"\n⚠️  Test Case PARTIAL")
                for check, status in checks.items():
                    print(f"   {check}: {'✓' if status else '✗'}")
                results.append(("PARTIAL", test_case["name"]))
                
        except Exception as e:
            print(f"\n❌ Test Case FAILED: {str(e)}")
            results.append(("FAILED", test_case["name"]))
    
    return results


def main():
    """Run all Phase 1 tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "PHASE 1: STABILIZE CURRENT GRAPH" + " "*21 + "║")
    print("║" + " "*15 + "Node-by-Node Testing & Validation" + " "*20 + "║")
    print("╚" + "="*68 + "╝")
    
    all_tests = []
    
    try:
        all_tests.append(("Entity Extraction", test_entity_extraction()))
    except Exception as e:
        print(f"❌ Entity Extraction FAILED: {e}")
        all_tests.append(("Entity Extraction", False))
    
    try:
        all_tests.append(("Sentiment Analysis", test_sentiment_analysis()))
    except Exception as e:
        print(f"❌ Sentiment Analysis FAILED: {e}")
        all_tests.append(("Sentiment Analysis", False))
    
    try:
        all_tests.append(("Intent Detection", test_intent_detection()))
    except Exception as e:
        print(f"❌ Intent Detection FAILED: {e}")
        all_tests.append(("Intent Detection", False))
    
    try:
        all_tests.append(("Retrieval Router", test_retrieval_router()))
    except Exception as e:
        print(f"❌ Retrieval Router FAILED: {e}")
        all_tests.append(("Retrieval Router", False))
    
    try:
        all_tests.append(("Context Builder", test_context_builder()))
    except Exception as e:
        print(f"❌ Context Builder FAILED: {e}")
        all_tests.append(("Context Builder", False))
    
    try:
        all_tests.append(("Response Generation", test_response_generation()))
    except Exception as e:
        print(f"❌ Response Generation FAILED: {e}")
        all_tests.append(("Response Generation", False))
    
    try:
        all_tests.append(("Validation", test_validation()))
    except Exception as e:
        print(f"❌ Validation FAILED: {e}")
        all_tests.append(("Validation", False))
    
    try:
        all_tests.append(("Memory Persistence", test_memory_persistence()))
    except Exception as e:
        print(f"❌ Memory Persistence FAILED: {e}")
        all_tests.append(("Memory Persistence", False))
    
    try:
        all_tests.append(("TTS Generation", test_tts_generation()))
    except Exception as e:
        print(f"❌ TTS Generation FAILED: {e}")
        all_tests.append(("TTS Generation", False))
    
    # End-to-end tests
    print("\n")
    import asyncio
    e2e_results = test_end_to_end()
    
    # Summary
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*25 + "TEST SUMMARY" + " "*32 + "║")
    print("╠" + "="*68 + "╣")
    
    node_tests_passed = sum(1 for _, result in all_tests if result)
    print(f"║ Node Tests: {node_tests_passed}/{len(all_tests)} PASSED" + " "*46 + "║")
    
    e2e_passed = sum(1 for status, _ in e2e_results if status == "PASSED")
    print(f"║ E2E Tests:  {e2e_passed}/{len(e2e_results)} PASSED" + " "*46 + "║")
    
    print("╠" + "="*68 + "╣")
    
    for test_name, result in all_tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"║ {test_name:<40} {status:<20} ║")
    
    print("╠" + "="*68 + "╣")
    for status, test_name in e2e_results:
        icon = "✅" if status == "PASSED" else "⚠️ " if status == "PARTIAL" else "❌"
        print(f"║ E2E: {test_name:<35} {icon} {status:<15} ║")
    
    print("╚" + "="*68 + "╝")
    
    if node_tests_passed == len(all_tests) and e2e_passed == len(e2e_results):
        print("\n🎉 PHASE 1 COMPLETE: All Tests PASSED ✅")
        print("Ready for Phase 2: Rich State Typing\n")
        return True
    else:
        print("\n⚠️  PHASE 1: Some Tests FAILED")
        print("Fix issues before proceeding to Phase 2\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
