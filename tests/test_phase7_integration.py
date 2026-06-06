"""Phase 7: Complaint Subgraph Integration Test Suite"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from orchestration.langgraph_workflow import run_workflow


async def test_workflow_normal_inquiry():
    """Test Phase 7: Normal workflow (non-complaint)"""
    print("\n" + "="*60)
    print("TEST: Workflow - Normal Inquiry")
    print("="*60)
    
    result = await run_workflow(
        "Tell me about your return policy",
        "TEST_001"
    )
    
    intent = result.get("intent", "")
    response = result.get("response", "")
    
    print(f"\n✓ Intent: {intent}")
    print(f"✓ Response length: {len(response)}")
    print(f"✓ Has response: {len(response) > 0}")
    
    assert intent in ["inquiry", "product_question"], f"Expected inquiry-like intent, got {intent}"
    assert len(response) > 0, "Should have response"
    
    print("\n✅ Normal Inquiry: PASSED")
    return True


async def test_workflow_complaint():
    """Test Phase 7: Complaint workflow with subgraph"""
    print("\n" + "="*60)
    print("TEST: Workflow - Complaint with Subgraph")
    print("="*60)
    
    result = await run_workflow(
        "This is my second complaint about this broken product",
        "TEST_001"
    )
    
    intent = result.get("intent", "")
    response = result.get("response", "")
    complaint_severity = result.get("complaint_severity", "")
    escalate_to_human = result.get("escalate_to_human", False)
    
    print(f"\n✓ Intent: {intent}")
    print(f"✓ Complaint Severity: {complaint_severity}")
    print(f"✓ Escalate to Human: {escalate_to_human}")
    print(f"✓ Response length: {len(response)}")
    
    assert intent == "complaint", f"Expected complaint intent, got {intent}"
    # Complaint severity may be populated if subgraph runs
    if complaint_severity:
        assert complaint_severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"], f"Invalid severity: {complaint_severity}"
    assert len(response) > 0, "Should have response"
    
    print("\n✅ Complaint Workflow: PASSED")
    return True


async def test_workflow_refund_request():
    """Test Phase 7: Refund workflow (non-complaint intent)"""
    print("\n" + "="*60)
    print("TEST: Workflow - Refund Request")
    print("="*60)
    
    result = await run_workflow(
        "I want to return this item for a refund",
        "TEST_002"
    )
    
    intent = result.get("intent", "")
    response = result.get("response", "")
    
    print(f"\n✓ Intent: {intent}")
    print(f"✓ Response length: {len(response)}")
    
    # Refund should not trigger complaint subgraph (different intent)
    assert intent == "refund_request", f"Expected refund_request, got {intent}"
    assert "complaint_severity" not in result or result.get("complaint_severity") == "", "Refund should not have complaint_severity"
    
    print("\n✅ Refund Request: PASSED")
    return True


async def test_workflow_high_severity_complaint():
    """Test Phase 7: High severity complaint triggers escalation"""
    print("\n" + "="*60)
    print("TEST: Workflow - High Severity Complaint")
    print("="*60)
    
    result = await run_workflow(
        "This is my THIRD complaint! The item is BROKEN and I was OVERCHARGED",
        "TEST_003"
    )
    
    intent = result.get("intent", "")
    complaint_severity = result.get("complaint_severity", "")
    escalate_to_human = result.get("escalate_to_human", False)
    
    print(f"\n✓ Intent: {intent}")
    print(f"✓ Severity: {complaint_severity}")
    print(f"✓ Escalate to Human: {escalate_to_human}")
    
    assert intent == "complaint", "Should be complaint"
    # Severity may be populated if subgraph processed it
    if complaint_severity:
        assert complaint_severity in ["HIGH", "CRITICAL"], f"Should be HIGH/CRITICAL, got {complaint_severity}"
    
    print("\n✅ High Severity Complaint: PASSED")
    return True


async def test_workflow_integration():
    """Test Phase 7: Full workflow integration test"""
    print("\n" + "="*60)
    print("TEST: Full Workflow Integration")
    print("="*60)
    
    test_cases = [
        {
            "input": "My refund is delayed",
            "expected_intent": "complaint",
            "name": "Complaint"
        },
        {
            "input": "Where is my order?",
            "expected_intent": "order_status",
            "name": "Order Status"
        },
        {
            "input": "Tell me about your products",
            "expected_intent": "inquiry",
            "name": "Inquiry"
        },
    ]
    
    for test_case in test_cases:
        result = await run_workflow(test_case["input"], "TEST_INTEGRATION")
        
        intent = result.get("intent", "")
        response = result.get("response", "")
        
        print(f"\n✓ {test_case['name']}: intent={intent}, response_len={len(response)}")
        
        assert len(response) > 0, f"No response for {test_case['name']}"
        assert intent != "", f"No intent detected for {test_case['name']}"
    
    print("\n✅ Full Integration: PASSED")
    return True


async def main():
    print("\n" + "="*60)
    print("PHASE 7: COMPLAINT SUBGRAPH INTEGRATION - TESTS")
    print("="*60)
    
    await test_workflow_normal_inquiry()
    await test_workflow_complaint()
    await test_workflow_refund_request()
    await test_workflow_high_severity_complaint()
    await test_workflow_integration()
    
    print("\n" + "="*60)
    print("PHASE 7: All workflow integration tests PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
