"""Phase 13: Session Tracking & Linking - Track and link multiple sessions per user"""

from orchestration.state import ConversationState
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading
import logging

logger = logging.getLogger(__name__)

_cross_thread_lock = threading.RLock()
_cross_thread_memory = {}


def session_tracking_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 13: Session Tracking & Linking
    
    Tracks session lifecycle and links sessions to user accounts
    
    Features:
    1. Track session start/end times
    2. Store session metadata in cross-thread memory
    3. Link sessions by user_id for history
    4. Count total sessions per user
    5. Maintain active sessions list
    
    Input State Fields:
    - user_id: Authenticated user identifier
    - session_id: Current session identifier
    - user_input: Current user input
    - response: Current response
    
    Output:
    - session_start_time: Session start timestamp
    - session_end_time: Session end timestamp
    - session_duration_seconds: Duration calculation
    - active_sessions: List of active sessions for user
    - session_count: Total sessions for user
    - session_linked: Whether linked successfully
    - session_tracking_status: Operation status
    """
    
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    customer_id = state.get("customer_id")
    
    if not user_id or not session_id:
        return {
            "session_start_time": None,
            "session_end_time": None,
            "session_duration_seconds": 0,
            "active_sessions": [],
            "session_count": 0,
            "session_linked": False,
            "session_tracking_status": "no_user_or_session",
        }
    
    session_tracking_status = "pending"
    session_start_time = None
    session_end_time = None
    session_duration_seconds = 0
    active_sessions = []
    session_count = 0
    session_linked = False
    
    try:
        with _cross_thread_lock:
            sessions_key = f"{user_id}:sessions"
            
            sessions_data = _cross_thread_memory.get(sessions_key, {
                "data": {
                    "user_id": user_id,
                    "sessions": {},
                    "active_sessions": [],
                    "session_count": 0,
                }
            })
            
            sessions_info = sessions_data.get("data", {})
            
            current_time = datetime.now().isoformat()
            
            if session_id not in sessions_info.get("sessions", {}):
                sessions_info["sessions"][session_id] = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "customer_id": customer_id,
                    "start_time": current_time,
                    "end_time": None,
                    "duration_seconds": 0,
                    "message_count": 1,
                    "created_at": current_time,
                }
                
                if session_id not in sessions_info.get("active_sessions", []):
                    sessions_info["active_sessions"].append(session_id)
                
                sessions_info["session_count"] = len(sessions_info.get("sessions", {}))
                
                session_start_time = current_time
                session_linked = True
                session_tracking_status = "created"
                
                logger.info(f"New session created: user_id={user_id}, session_id={session_id}")
            else:
                existing_session = sessions_info["sessions"][session_id]
                session_start_time = existing_session.get("start_time")
                
                existing_session["message_count"] = existing_session.get("message_count", 0) + 1
                
                session_linked = True
                session_tracking_status = "updated"
                
                logger.debug(f"Session updated: user_id={user_id}, session_id={session_id}, messages={existing_session['message_count']}")
            
            active_sessions = sessions_info.get("active_sessions", [])
            session_count = sessions_info.get("session_count", 0)
            
            _cross_thread_memory[sessions_key] = sessions_data
            
    except Exception as e:
        logger.error(f"Session tracking error (user_id={user_id}): {str(e)}")
        session_tracking_status = f"error: {str(e)}"
        session_linked = False
    
    return {
        "session_start_time": session_start_time,
        "session_end_time": session_end_time,
        "session_duration_seconds": session_duration_seconds,
        "active_sessions": active_sessions,
        "session_count": session_count,
        "session_linked": session_linked,
        "session_tracking_status": session_tracking_status,
    }


def end_session_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 13: End Session Tracking
    
    Called when user logs out or session expires
    Marks session as ended and calculates duration
    """
    
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    session_start_time = state.get("session_start_time")
    
    if not user_id or not session_id:
        return {"session_tracking_status": "no_user_or_session"}
    
    try:
        with _cross_thread_lock:
            sessions_key = f"{user_id}:sessions"
            sessions_data = _cross_thread_memory.get(sessions_key, {})
            sessions_info = sessions_data.get("data", {})
            
            if session_id in sessions_info.get("sessions", {}):
                current_time = datetime.now().isoformat()
                session_record = sessions_info["sessions"][session_id]
                
                session_record["end_time"] = current_time
                
                if session_start_time:
                    try:
                        start = datetime.fromisoformat(session_start_time)
                        end = datetime.fromisoformat(current_time)
                        duration = int((end - start).total_seconds())
                        session_record["duration_seconds"] = max(0, duration)
                    except Exception:
                        session_record["duration_seconds"] = 0
                
                if session_id in sessions_info.get("active_sessions", []):
                    sessions_info["active_sessions"].remove(session_id)
                
                _cross_thread_memory[sessions_key] = sessions_data
                
                logger.info(f"Session ended: user_id={user_id}, session_id={session_id}, duration={session_record['duration_seconds']}s")
                
                return {"session_tracking_status": "ended"}
            
    except Exception as e:
        logger.error(f"Session end error (user_id={user_id}): {str(e)}")
    
    return {"session_tracking_status": "error"}
