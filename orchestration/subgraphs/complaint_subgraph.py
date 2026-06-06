"""Phase 6: Complaint Subgraph - Specialized complaint handling workflow"""

from orchestration.state import ConversationState
from typing import Dict, Any, Literal
import logging

logger = logging.getLogger(__name__)


class ComplaintSeverityAssessor:
    """Assess complaint severity and determine handling strategy"""
    
    SEVERITY_LEVELS = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    @staticmethod
    def assess_severity(
        user_input: str,
        sentiment: str,
        entities: Dict[str, Any],
        history_sessions: int = 0
    ) -> Dict[str, Any]:
        """
        Assess complaint severity based on multiple factors:
        - Sentiment strength (NEGATIVE = higher)
        - Repeat complaints (history_sessions)
        - Urgent keywords (overcharged, broken, defective, etc.)
        - Customer history (pattern of issues)
        """
        
        severity = "LOW"
        escalation_urgency = 0  # 0-10 scale
        recommended_action = "standard_resolution"
        
        # Factor 1: Sentiment
        if sentiment == "NEGATIVE":
            escalation_urgency += 3
        
        # Factor 2: Urgent keywords
        urgent_keywords = [
            "overcharged", "broken", "defective", "damage", "missing",
            "lost", "scam", "fraud", "false", "faulty", "fail"
        ]
        if any(keyword in user_input.lower() for keyword in urgent_keywords):
            escalation_urgency += 4
        
        # Factor 3: Repeat complaint pattern
        if history_sessions > 3:
            escalation_urgency += 3
            recommended_action = "escalate_to_manager"
        
        # Factor 4: Third+ complaint (extremely dissatisfied)
        if history_sessions > 2:
            escalation_urgency += 2
        
        # Determine severity level
        if escalation_urgency >= 8:
            severity = "CRITICAL"
        elif escalation_urgency >= 6:
            severity = "HIGH"
        elif escalation_urgency >= 3:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        # Auto-escalate for critical issues
        if severity == "CRITICAL":
            recommended_action = "immediate_escalation"
        elif severity == "HIGH":
            recommended_action = "escalate_to_manager"
        elif severity == "MEDIUM":
            recommended_action = "offer_resolution"
        
        return {
            "severity": severity,
            "escalation_urgency": escalation_urgency,
            "recommended_action": recommended_action,
            "auto_escalate": severity in ["CRITICAL", "HIGH"],
        }


def complaint_assessment_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 6: Complaint Assessment Node
    
    Assess complaint severity and determine handling strategy
    
    Input:
    - user_input: str - Customer's complaint
    - sentiment: str - Detected sentiment
    - entities: Dict - Extracted entities
    
    Output:
    - complaint_severity: str - LOW, MEDIUM, HIGH, or CRITICAL
    - escalation_urgency: int - 0-10 scale
    - recommended_action: str - How to handle
    - auto_escalate: bool - Whether to escalate automatically
    """
    
    user_input = state.get("user_input", "")
    sentiment = state.get("sentiment", "NEUTRAL")
    entities = state.get("entities", {})
    
    # Get severity assessment
    assessment = ComplaintSeverityAssessor.assess_severity(
        user_input=user_input,
        sentiment=sentiment,
        entities=entities,
        history_sessions=0  # Would be populated from memory_context in full implementation
    )
    
    return {
        "complaint_severity": assessment["severity"],
        "escalation_urgency": assessment["escalation_urgency"],
        "complaint_action": assessment["recommended_action"],
        "auto_escalate": assessment["auto_escalate"],
    }


def complaint_resolution_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 6: Complaint Resolution Node
    
    Determine resolution options based on severity
    
    Resolution strategies by severity:
    - LOW: Standard apology + KB solution
    - MEDIUM: Apology + offered remedy (discount, replacement)
    - HIGH: Immediate escalation to agent
    - CRITICAL: Skip to manager + expedited resolution
    """
    
    severity = state.get("complaint_severity", "LOW")
    intent = state.get("intent", "complaint")
    
    resolutions = {
        "LOW": {
            "message": "apologize and offer standard resolution",
            "offer_discount": False,
            "offer_replacement": False,
            "escalate": False,
            "response_tone": "sympathetic"
        },
        "MEDIUM": {
            "message": "apologize and offer remedy (5-10% discount or replacement)",
            "offer_discount": True,
            "offer_replacement": True,
            "escalate": False,
            "response_tone": "empathetic"
        },
        "HIGH": {
            "message": "acknowledge severity and escalate to specialist",
            "offer_discount": True,
            "offer_replacement": True,
            "escalate": True,
            "response_tone": "urgent"
        },
        "CRITICAL": {
            "message": "immediate escalation to manager with priority handling",
            "offer_discount": True,
            "offer_replacement": True,
            "escalate": True,
            "response_tone": "critical"
        }
    }
    
    resolution = resolutions.get(severity, resolutions["LOW"])
    
    return {
        "resolution_strategy": resolution["message"],
        "offer_discount": resolution["offer_discount"],
        "offer_replacement": resolution["offer_replacement"],
        "needs_escalation": resolution["escalate"],
        "response_tone": resolution["response_tone"],
    }


def complaint_escalation_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 6: Complaint Escalation Node
    
    Determine if escalation is needed and prepare escalation details
    
    Output:
    - escalate_to_human: bool - Needs human agent
    - escalation_level: str - agent, supervisor, manager
    - escalation_reason: str - Why escalating
    - priority_flag: bool - High priority in queue
    """
    
    severity = state.get("complaint_severity", "LOW")
    auto_escalate = state.get("auto_escalate", False)
    
    escalation_config = {
        "LOW": {
            "escalate": False,
            "level": "none",
            "reason": "Can be resolved by bot",
            "priority": False
        },
        "MEDIUM": {
            "escalate": False,
            "level": "none",
            "reason": "Offer bot resolution first",
            "priority": False
        },
        "HIGH": {
            "escalate": True,
            "level": "agent",
            "reason": "Complex complaint requiring specialist",
            "priority": True
        },
        "CRITICAL": {
            "escalate": True,
            "level": "manager",
            "reason": "Severe issue requiring immediate management",
            "priority": True
        }
    }
    
    config = escalation_config.get(severity, escalation_config["LOW"])
    
    return {
        "escalate_to_human": config["escalate"],
        "escalation_level": config["level"],
        "escalation_reason": config["reason"],
        "priority_flag": config["priority"],
    }


def complaint_subgraph_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 6: Complaint Subgraph Orchestrator
    
    Runs all complaint-specific nodes in sequence:
    1. Assessment (severity)
    2. Resolution (strategy)
    3. Escalation (decision)
    
    This is a meta-node that orchestrates the complaint subgraph
    """
    
    # Check if this is a complaint intent
    intent = state.get("intent", "inquiry")
    if intent != "complaint":
        # Not a complaint - return empty/default values
        return {
            "complaint_severity": "",
            "escalation_urgency": 0,
            "complaint_action": "",
            "auto_escalate": False,
            "resolution_strategy": "",
            "offer_discount": False,
            "offer_replacement": False,
            "needs_escalation": False,
            "response_tone": "",
            "escalate_to_human": False,
            "escalation_level": "",
            "escalation_reason": "",
            "priority_flag": False,
        }
    
    # Run assessment
    assessment = complaint_assessment_node(state)
    
    # Update state with assessment results
    state_with_assessment = {
        **state,
        **assessment
    }
    
    # Run resolution
    resolution = complaint_resolution_node(state_with_assessment)
    
    # Update state with resolution
    state_with_resolution = {
        **state_with_assessment,
        **resolution
    }
    
    # Run escalation
    escalation = complaint_escalation_node(state_with_resolution)
    
    # Combine all outputs
    return {
        **assessment,
        **resolution,
        **escalation
    }
