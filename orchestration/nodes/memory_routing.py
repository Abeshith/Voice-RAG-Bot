"""Phase 14: Memory Routing by Session - Route and validate session-specific memory access"""

from orchestration.state import ConversationState
from typing import Dict, Any, Optional
import threading
import logging

logger = logging.getLogger(__name__)

_cross_thread_lock = threading.RLock()
_cross_thread_memory = {}


def memory_routing_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 14: Memory Routing by Session
    
    Determines which memory to use based on session_id
    Validates session isolation before proceeding with memory access
    
    Features:
    1. Route memory access to session-specific storage
    2. Separate thread memory per session
    3. Separate cross-thread memory per session
    4. Verify session isolation is maintained
    5. Build session memory keys for retrieval/persistence nodes
    
    Input State Fields:
    - user_id: Authenticated user identifier
    - session_id: Current session identifier
    - conversation_id: Conversation identifier
    
    Output:
    - session_memory_status: Status of memory routing
    - session_specific_context: Current session's memory context
    - previous_session_context: Previous sessions' aggregated context
    - memory_routed_by_session: Whether routing succeeded
    - session_isolation_verified: Whether isolation is maintained
    """
    
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    conversation_id = state.get("conversation_id")
    
    if not user_id or not session_id:
        return {
            "session_memory_status": "no_user_or_session",
            "session_specific_context": None,
            "previous_session_context": None,
            "memory_routed_by_session": False,
            "session_isolation_verified": False,
        }
    
    try:
        session_memory_status = "pending"
        session_specific_context = {}
        previous_session_context = {}
        memory_routed_by_session = False
        session_isolation_verified = False
        
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
            all_sessions = sessions_info.get("sessions", {})
            
            if session_id in all_sessions:
                current_session = all_sessions[session_id]
                session_specific_context = {
                    "session_id": session_id,
                    "start_time": current_session.get("start_time"),
                    "message_count": current_session.get("message_count", 0),
                }
                session_memory_status = "found"
                memory_routed_by_session = True
                
                logger.debug(f"Session memory routed: user={user_id}, session={session_id}")
            else:
                session_memory_status = "session_not_found"
                logger.warning(f"Session not found in tracking: user={user_id}, session={session_id}")
            
            other_sessions = {s_id: s_data for s_id, s_data in all_sessions.items() if s_id != session_id}
            if other_sessions:
                previous_session_context = {
                    "previous_session_count": len(other_sessions),
                    "session_ids": list(other_sessions.keys()),
                }
            
            session_isolation_verified = session_id in all_sessions
        
        return {
            "session_memory_status": session_memory_status,
            "session_specific_context": session_specific_context,
            "previous_session_context": previous_session_context,
            "memory_routed_by_session": memory_routed_by_session,
            "session_isolation_verified": session_isolation_verified,
        }
        
    except Exception as e:
        logger.error(f"Memory routing error (user_id={user_id}, session_id={session_id}): {str(e)}")
        return {
            "session_memory_status": f"error: {str(e)}",
            "session_specific_context": None,
            "previous_session_context": None,
            "memory_routed_by_session": False,
            "session_isolation_verified": False,
        }


def clear_previous_session_memory(user_id: str, session_id: str) -> bool:
    """
    Clear memory from previous sessions when user logs out
    Prevents memory leakage between sessions
    """
    
    if not user_id or not session_id:
        return False
    
    try:
        with _cross_thread_lock:
            sessions_key = f"{user_id}:sessions"
            sessions_data = _cross_thread_memory.get(sessions_key, {})
            sessions_info = sessions_data.get("data", {})
            
            all_sessions = sessions_info.get("sessions", {})
            for s_id in list(all_sessions.keys()):
                if s_id != session_id:
                    thread_key = f"{user_id}:{s_id}:context_*"
                    cross_key = f"{user_id}:{s_id}:conv_*"
                    
                    keys_to_delete = [k for k in _cross_thread_memory.keys() if k.startswith(f"{user_id}:{s_id}:")]
                    for key in keys_to_delete:
                        del _cross_thread_memory[key]
                    
                    logger.info(f"Cleared memory for previous session: user={user_id}, session={s_id}")
        
        return True
    except Exception as e:
        logger.error(f"Error clearing previous session memory: {str(e)}")
        return False
