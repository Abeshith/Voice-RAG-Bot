import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.state_reducer import FieldReducer, StateReducerManager


def test_merge_intent():
    assert FieldReducer.merge_intent("", "refund_request") == "refund_request"
    assert FieldReducer.merge_intent("complaint", "") == "complaint"
    assert FieldReducer.merge_intent("other", "inquiry") == "inquiry"
    assert FieldReducer.merge_intent("refund_request", "inquiry") == "inquiry"
    print("✓ Intent merge works")


def test_merge_sentiment():
    assert FieldReducer.merge_sentiment("", "NEGATIVE") == "NEGATIVE"
    assert FieldReducer.merge_sentiment("POSITIVE", "") == "POSITIVE"
    assert FieldReducer.merge_sentiment("NEUTRAL", "NEGATIVE") == "NEGATIVE"
    assert FieldReducer.merge_sentiment("POSITIVE", "NEGATIVE") == "POSITIVE"
    print("✓ Sentiment merge works")


def test_merge_entities():
    entities1 = {"PER": ["John"], "LOC": ["NYC"]}
    entities2 = {"PER": ["Jane"], "ORG": ["ACME"]}
    
    merged = FieldReducer.merge_entities(entities1, entities2)
    assert "John" in merged["PER"] or "Jane" in merged["PER"]
    assert "ACME" in merged["ORG"]
    print("✓ Entities merge works")
    
    assert FieldReducer.merge_entities({}, entities1) == entities1
    assert FieldReducer.merge_entities(entities1, {}) == entities1


def test_merge_response():
    resp1 = "Short response"
    resp2 = "Much longer response with more details"
    
    assert FieldReducer.merge_response(resp1, resp2) == resp2
    assert FieldReducer.merge_response("", resp1) == resp1
    print("✓ Response merge works")


def test_state_reducer_manager_apply_updates():
    base_state = {
        "user_input": "test",
        "customer_id": "CUST_001",
        "intent": "other",
        "sentiment": "NEUTRAL",
        "response": ""
    }
    
    update1 = {"intent": "complaint", "sentiment": "NEGATIVE"}
    update2 = {"response": "We understand your issue"}
    
    result = StateReducerManager.apply_updates(base_state, update1, update2)
    
    assert result["intent"] == "complaint"
    assert result["sentiment"] == "NEGATIVE"
    assert result["response"] == "We understand your issue"
    print("✓ Apply updates works")


def test_state_reducer_manager_merge_parallel():
    output1 = {
        "intent": "complaint",
        "entities": {"PER": ["John"]}
    }
    output2 = {
        "sentiment": "NEGATIVE",
        "entities": {"ORG": ["ACME"]}
    }
    
    merged = StateReducerManager.merge_parallel_outputs([output1, output2])
    
    assert merged["intent"] == "complaint"
    assert merged["sentiment"] == "NEGATIVE"
    assert "PER" in merged["entities"]
    assert "ORG" in merged["entities"]
    print("✓ Merge parallel outputs works")


def test_state_reducer_manager_validate():
    valid_state = {
        "user_input": "test",
        "customer_id": "CUST_001",
        "intent": "inquiry",
        "sentiment": "NEUTRAL",
        "response": "Hello"
    }
    
    assert StateReducerManager.validate_state(valid_state) == True
    print("✓ State validation works")
    
    invalid_state = {
        "user_input": "test",
        "customer_id": "CUST_001",
        "intent": 123,
        "sentiment": "NEUTRAL",
        "response": "Hello"
    }
    
    assert StateReducerManager.validate_state(invalid_state) == False
    print("✓ Invalid state rejected")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 3: STATE REDUCERS - MERGE STRATEGY TESTS")
    print("="*60 + "\n")
    
    test_merge_intent()
    test_merge_sentiment()
    test_merge_entities()
    test_merge_response()
    test_state_reducer_manager_apply_updates()
    test_state_reducer_manager_merge_parallel()
    test_state_reducer_manager_validate()
    
    print("\n" + "="*60)
    print("PHASE 3: All reducer tests PASSED")
    print("="*60 + "\n")
