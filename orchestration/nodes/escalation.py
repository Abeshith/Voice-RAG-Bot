"""Phase 8: Escalation Node - Hand off to human agents"""

from orchestration.state import ConversationState
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def escalation_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 8: Escalation Node
    
    Handle customer escalation to human agents
    
    Escalation triggers:
    - complaint_severity == "CRITICAL"
    - escalation_level in ["manager", "supervisor"]
    - Retry attempts exhausted for important issues
    
    Actions:
    - Log escalation with full context
    - Flag for human review
    - Create ticket for agent
    - Prepare handoff message
    
    Output:
    - escalation_ticket: str - Ticket ID for tracking
    - escalation_message: str - Message for human agent
    - requires_callback: bool - Whether customer needs callback
    - priority: str - HIGH or CRITICAL
    """
    
    severity = state.get("complaint_severity", "")
    escalation_level = state.get("escalation_level", "none")
    escalation_reason = state.get("escalation_reason", "No reason provided")
    customer_id = state.get("customer_id", "UNKNOWN")
    user_input = state.get("user_input", "")
    sentiment = state.get("sentiment", "NEUTRAL")
    
    # Skip if not escalating
    if escalation_level == "none":
        return {
            "escalation_ticket": "",
            "escalation_message": "",
            "requires_callback": False,
            "priority": "NORMAL",
        }
    
    try:
        # Generate ticket ID
        ticket_id = f"ESC_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine priority and callback needs
        priority = "CRITICAL" if severity == "CRITICAL" else "HIGH"
        requires_callback = severity in ["CRITICAL", "HIGH"]
        
        # Build escalation message for human agent
        message_parts = []
        message_parts.append(f"🎯 ESCALATION TICKET: {ticket_id}")
        message_parts.append(f"Customer ID: {customer_id}")
        message_parts.append(f"Priority: {priority}")
        message_parts.append(f"Escalation Level: {escalation_level}")
        message_parts.append(f"Complaint Severity: {severity}")
        message_parts.append(f"Sentiment: {sentiment}")
        message_parts.append("")
        message_parts.append("📋 Customer Issue:")
        message_parts.append(f"{user_input}")
        message_parts.append("")
        message_parts.append("📝 Reason for Escalation:")
        message_parts.append(escalation_reason)
        message_parts.append("")
        
        # Add offer details if complaint-related
        if state.get("offer_discount"):
            message_parts.append("💳 Authorized Offers:")
            message_parts.append("  ✓ Discount available (5-20% depending on severity)")
        if state.get("offer_replacement"):
            message_parts.append("  ✓ Product replacement available")
        
        message_parts.append("")
        message_parts.append(f"⏱️ Timestamp: {datetime.now().isoformat()}")
        
        escalation_message = "\n".join(message_parts)
        
        logger.warning(f"ESCALATION: {ticket_id} - {escalation_level} - {customer_id}")
        
        return {
            "escalation_ticket": ticket_id,
            "escalation_message": escalation_message,
            "requires_callback": requires_callback,
            "priority": priority,
        }
        
    except Exception as e:
        logger.error(f"Escalation error: {str(e)}")
        return {
            "escalation_ticket": "",
            "escalation_message": f"Error during escalation: {str(e)[:100]}",
            "requires_callback": True,
            "priority": "HIGH",
        }
