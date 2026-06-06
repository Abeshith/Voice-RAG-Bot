"""Phase 6: Complaint Subgraph - Test Suite"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.state import ConversationState
from orchestration.subgraphs.complaint_subgraph import (
    ComplaintSeverityAssessor,
    complaint_assessment_node,
    complaint_resolution_node,
    complaint_escalation_node,
    complaint_subgraph_node
)


def test_severity_assessment_low():
    """Test Phase 6: Low severity complaint"""
    print("\n" + "="*60)
    print("TEST: Severity Assessment - Low")
    print("="*60)
    
    assessment = ComplaintSeverityAssessor.assess_severity(
        user_input="The delivery was slightly late",
        sentiment="NEUTRAL",
        entities={},
        history_sessions=0
    )
    
    print(f"\n✓ Severity: {assessment['severity']}")
    print(f"✓ Urgency: {assessment['escalation_urgency']}/10")
    print(f"✓ Auto-escalate: {assessment['auto_escalate']}")
    
    assert assessment["severity"] == "LOW", "Should be LOW severity"
    assert assessment["auto_escalate"] == False, "Should not auto-escalate"
    
    print("\n✅ Low Severity: PASSED")
    return True


def test_severity_assessment_medium():
    """Test Phase 6: Medium severity complaint"""
    print("\n" + "="*60)
    print("TEST: Severity Assessment - Medium")
    print("="*60)
    
    assessment = ComplaintSeverityAssessor.assess_severity(
        user_input="The item arrived broken and I'm frustrated",
        sentiment="NEGATIVE",
        entities={},
        history_sessions=1
    )
    
    print(f"\n✓ Severity: {assessment['severity']}")
    print(f"✓ Urgency: {assessment['escalation_urgency']}/10")
    print(f"✓ Action: {assessment['recommended_action']}")
    
    assert assessment["severity"] in ["MEDIUM", "HIGH"], "Should be MEDIUM or higher"
    
    print("\n✅ Medium Severity: PASSED")
    return True


def test_severity_assessment_critical():
    """Test Phase 6: Critical severity complaint"""
    print("\n" + "="*60)
    print("TEST: Severity Assessment - Critical")
    print("="*60)
    
    assessment = ComplaintSeverityAssessor.assess_severity(
        user_input="This is a SCAM! I was overcharged and the item is defective",
        sentiment="NEGATIVE",
        entities={},
        history_sessions=5
    )
    
    print(f"\n✓ Severity: {assessment['severity']}")
    print(f"✓ Urgency: {assessment['escalation_urgency']}/10")
    print(f"✓ Auto-escalate: {assessment['auto_escalate']}")
    
    assert assessment["severity"] == "CRITICAL", "Should be CRITICAL"
    assert assessment["auto_escalate"] == True, "Should auto-escalate"
    
    print("\n✅ Critical Severity: PASSED")
    return True


def test_complaint_assessment_node():
    """Test Phase 6: Complaint Assessment Node"""
    print("\n" + "="*60)
    print("TEST: Complaint Assessment Node")
    print("="*60)
    
    state = ConversationState(
        user_input="My order is broken and this is my second complaint",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = complaint_assessment_node(state)
    
    print(f"\n✓ Severity: {result['complaint_severity']}")
    print(f"✓ Urgency: {result['escalation_urgency']}")
    print(f"✓ Action: {result['complaint_action']}")
    print(f"✓ Auto-escalate: {result['auto_escalate']}")
    
    assert "complaint_severity" in result, "Should have complaint_severity"
    assert result["complaint_severity"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"], "Invalid severity"
    
    print("\n✅ Complaint Assessment: PASSED")
    return True


def test_complaint_resolution_low():
    """Test Phase 6: Complaint Resolution - Low Severity"""
    print("\n" + "="*60)
    print("TEST: Complaint Resolution - Low Severity")
    print("="*60)
    
    state = ConversationState(
        user_input="test",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        complaint_severity="LOW",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = complaint_resolution_node(state)
    
    print(f"\n✓ Strategy: {result['resolution_strategy']}")
    print(f"✓ Offer Discount: {result['offer_discount']}")
    print(f"✓ Offer Replacement: {result['offer_replacement']}")
    print(f"✓ Escalate: {result['needs_escalation']}")
    
    assert result["offer_discount"] == False, "LOW severity should not offer discount"
    assert result["needs_escalation"] == False, "LOW should not escalate"
    
    print("\n✅ Low Resolution: PASSED")
    return True


def test_complaint_resolution_critical():
    """Test Phase 6: Complaint Resolution - Critical Severity"""
    print("\n" + "="*60)
    print("TEST: Complaint Resolution - Critical Severity")
    print("="*60)
    
    state = ConversationState(
        user_input="test",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        complaint_severity="CRITICAL",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = complaint_resolution_node(state)
    
    print(f"\n✓ Strategy: {result['resolution_strategy']}")
    print(f"✓ Offer Discount: {result['offer_discount']}")
    print(f"✓ Escalate: {result['needs_escalation']}")
    print(f"✓ Tone: {result['response_tone']}")
    
    assert result["offer_discount"] == True, "CRITICAL should offer discount"
    assert result["needs_escalation"] == True, "CRITICAL should escalate"
    assert result["response_tone"] == "critical", "CRITICAL should have critical tone"
    
    print("\n✅ Critical Resolution: PASSED")
    return True


def test_complaint_escalation_low():
    """Test Phase 6: Complaint Escalation - Low Severity"""
    print("\n" + "="*60)
    print("TEST: Complaint Escalation - Low Severity")
    print("="*60)
    
    state = ConversationState(
        user_input="test",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        complaint_severity="LOW",
        auto_escalate=False,
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = complaint_escalation_node(state)
    
    print(f"\n✓ Escalate: {result['escalate_to_human']}")
    print(f"✓ Level: {result['escalation_level']}")
    print(f"✓ Priority: {result['priority_flag']}")
    
    assert result["escalate_to_human"] == False, "LOW should not escalate"
    
    print("\n✅ Low Escalation: PASSED")
    return True


def test_complaint_escalation_critical():
    """Test Phase 6: Complaint Escalation - Critical Severity"""
    print("\n" + "="*60)
    print("TEST: Complaint Escalation - Critical Severity")
    print("="*60)
    
    state = ConversationState(
        user_input="test",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        complaint_severity="CRITICAL",
        auto_escalate=True,
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = complaint_escalation_node(state)
    
    print(f"\n✓ Escalate: {result['escalate_to_human']}")
    print(f"✓ Level: {result['escalation_level']}")
    print(f"✓ Priority: {result['priority_flag']}")
    
    assert result["escalate_to_human"] == True, "CRITICAL should escalate"
    assert result["escalation_level"] == "manager", "CRITICAL should go to manager"
    assert result["priority_flag"] == True, "CRITICAL should be priority"
    
    print("\n✅ Critical Escalation: PASSED")
    return True


def test_complaint_subgraph_full():
    """Test Phase 6: Full Complaint Subgraph"""
    print("\n" + "="*60)
    print("TEST: Full Complaint Subgraph")
    print("="*60)
    
    state = ConversationState(
        user_input="This is my third complaint about this broken product",
        customer_id="TEST_001",
        intent="complaint",
        sentiment="NEGATIVE",
        entities={},
        conversation_summary="",
        kb_context="",
        history_context="",
        response="",
        validation_passed=False,
        final_audio_path="",
    )
    
    result = complaint_subgraph_node(state)
    
    print(f"\n✓ Severity: {result['complaint_severity']}")
    print(f"✓ Action: {result['complaint_action']}")
    print(f"✓ Strategy: {result['resolution_strategy']}")
    print(f"✓ Escalate: {result['escalate_to_human']}")
    
    assert "complaint_severity" in result, "Missing severity"
    assert "resolution_strategy" in result, "Missing resolution"
    assert "escalate_to_human" in result, "Missing escalation"
    
    print("\n✅ Full Subgraph: PASSED")
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 6: COMPLAINT SUBGRAPH - TESTS")
    print("="*60)
    
    test_severity_assessment_low()
    test_severity_assessment_medium()
    test_severity_assessment_critical()
    test_complaint_assessment_node()
    test_complaint_resolution_low()
    test_complaint_resolution_critical()
    test_complaint_escalation_low()
    test_complaint_escalation_critical()
    test_complaint_subgraph_full()
    
    print("\n" + "="*60)
    print("PHASE 6: All complaint subgraph tests PASSED")
    print("="*60 + "\n")
