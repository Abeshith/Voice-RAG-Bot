"""Phase 15: Escalation State Management - Track and persist escalation state across sessions"""

from orchestration.state import ConversationState
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import logging

logger = logging.getLogger(__name__)

_cross_thread_lock = threading.RLock()
_cross_thread_memory = {}

ESCALATION_LEVELS = ["none", "low", "medium", "high", "critical"]


def escalation_state_management_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 15: Escalation State Management
    
    Tracks and persists escalation state across user sessions
    Influences response generation based on current escalation level
    
    Features:
    1. Track escalation state per user (persists across sessions)
    2. Update escalation based on sentiment/complaint severity
    3. Persist escalation state in cross-thread memory
    4. Retrieve escalation state for session
    5. Clear escalation on user request
    
    Escalation Levels:
    - none: Normal conversation
    - low: Customer slightly dissatisfied
    - medium: Clear complaint or issue
    - high: Escalation required, agent needed
    - critical: Severe issue, urgent escalation
    
    Input State Fields:
    - user_id: Authenticated user identifier
    - session_id: Current session identifier
    - sentiment: Current sentiment analysis (POSITIVE/NEGATIVE/NEUTRAL)
    - escalation_level: Current interaction escalation level
    - escalation_reason: Reason for escalation
    - escalation_ticket: Ticket ID if applicable
    - response: Generated response
    
    Output:
    - user_escalation_state: Current user escalation state level
    - escalation_state_updated: Whether state was updated
    - escalation_state_persisted: Whether state was saved
    - escalation_history_count: Count of escalations in this session
    - escalation_state_management_status: Operation status
    - escalation_influenced_response: Whether response was influenced by escalation
    - previous_escalation_level: Previous escalation level before this interaction
    """
    
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    sentiment = state.get("sentiment", "NEUTRAL")
    current_escalation_level = state.get("escalation_level", "none")
    escalation_reason = state.get("escalation_reason", "")
    trend_escalation_recommended = state.get("trend_escalation_recommended", False)
    trend_escalation_reason = state.get("trend_escalation_reason", "")
    
    if not user_id:
        return {
            "user_escalation_state": "none",
            "escalation_state_updated": False,
            "escalation_state_persisted": False,
            "escalation_history_count": 0,
            "escalation_state_management_status": "no_user",
            "escalation_influenced_response": False,
            "previous_escalation_level": "none",
        }
    
    try:
        with _cross_thread_lock:
            escalation_key = f"{user_id}:escalation_state"
            
            escalation_data = _cross_thread_memory.get(escalation_key, {
                "data": {
                    "user_id": user_id,
                    "current_level": "none",
                    "previous_level": "none",
                    "history": [],
                    "updated_at": datetime.now().isoformat(),
                    "session_id": session_id,
                }
            })
            
            escalation_info = escalation_data.get("data", {})
            previous_level = escalation_info.get("current_level", "none")
            escalation_history = escalation_info.get("history", [])
            
            new_level = previous_level
            state_updated = False
            
            if current_escalation_level in ESCALATION_LEVELS and current_escalation_level != "none":
                if ESCALATION_LEVELS.index(current_escalation_level) > ESCALATION_LEVELS.index(previous_level):
                    new_level = current_escalation_level
                    state_updated = True
            
            if trend_escalation_recommended:
                if trend_escalation_reason == "4_consecutive_negative_high_alert":
                    new_level = "high"
                    state_updated = True
                elif trend_escalation_reason == "3_consecutive_negative_medium_alert":
                    new_level = "medium"
                    state_updated = True
                elif trend_escalation_reason == "2_consecutive_negative_low_alert":
                    if previous_level in ["none", "low"]:
                        new_level = "low"
                        state_updated = True
            
            if sentiment == "NEGATIVE" and previous_level == "none" and not trend_escalation_recommended:
                new_level = "low"
                state_updated = True
            
            if state_updated or not state_updated:
                reason = escalation_reason
                if trend_escalation_recommended:
                    reason = trend_escalation_reason
                elif not reason:
                    reason = "sentiment_based"
                
                escalation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "previous_level": previous_level,
                    "new_level": new_level,
                    "reason": reason,
                    "sentiment": sentiment,
                    "trend_based": trend_escalation_recommended,
                })
            
            escalation_info["current_level"] = new_level
            escalation_info["previous_level"] = previous_level
            escalation_info["history"] = escalation_history[-50:]
            escalation_info["updated_at"] = datetime.now().isoformat()
            escalation_info["session_id"] = session_id
            
            _cross_thread_memory[escalation_key] = {
                "data": escalation_info
            }
            
            escalation_influenced_response = new_level in ["high", "critical"]
            
            logger.debug(f"Escalation state: user={user_id}, session={session_id}, level={new_level}, previous={previous_level}")
            
            return {
                "user_escalation_state": new_level,
                "escalation_state_updated": state_updated,
                "escalation_state_persisted": True,
                "escalation_history_count": len(escalation_history),
                "escalation_state_management_status": "success",
                "escalation_influenced_response": escalation_influenced_response,
                "previous_escalation_level": previous_level,
            }
        
    except Exception as e:
        logger.error(f"Escalation state management error (user_id={user_id}): {str(e)}")
        return {
            "user_escalation_state": "none",
            "escalation_state_updated": False,
            "escalation_state_persisted": False,
            "escalation_history_count": 0,
            "escalation_state_management_status": f"error: {str(e)}",
            "escalation_influenced_response": False,
            "previous_escalation_level": "none",
        }


def get_user_escalation_state(user_id: str) -> str:
    """Retrieve current escalation state for user"""
    if not user_id:
        return "none"
    
    try:
        with _cross_thread_lock:
            escalation_key = f"{user_id}:escalation_state"
            escalation_data = _cross_thread_memory.get(escalation_key, {})
            escalation_info = escalation_data.get("data", {})
            return escalation_info.get("current_level", "none")
    except Exception as e:
        logger.error(f"Error retrieving escalation state: {str(e)}")
        return "none"


def reset_user_escalation_state(user_id: str) -> bool:
    """Reset escalation state when issue is resolved"""
    if not user_id:
        return False
    
    try:
        with _cross_thread_lock:
            escalation_key = f"{user_id}:escalation_state"
            escalation_data = _cross_thread_memory.get(escalation_key, {})
            escalation_info = escalation_data.get("data", {})
            
            escalation_history = escalation_info.get("history", [])
            escalation_history.append({
                "timestamp": datetime.now().isoformat(),
                "session_id": escalation_info.get("session_id"),
                "previous_level": escalation_info.get("current_level", "none"),
                "new_level": "none",
                "reason": "manual_reset",
                "sentiment": "NEUTRAL",
            })
            
            escalation_info["current_level"] = "none"
            escalation_info["previous_level"] = "none"
            escalation_info["history"] = escalation_history[-50:]
            escalation_info["updated_at"] = datetime.now().isoformat()
            
            _cross_thread_memory[escalation_key] = {"data": escalation_info}
            logger.info(f"Escalation state reset for user: {user_id}")
            return True
    except Exception as e:
        logger.error(f"Error resetting escalation state: {str(e)}")
        return False
