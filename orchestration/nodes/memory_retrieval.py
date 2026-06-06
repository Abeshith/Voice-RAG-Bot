"""Phase 4+9+10: Integrated Memory Retrieval - Qdrant + Thread-Local + Cross-Thread"""

from orchestration.state import ConversationState
from rag.qdrant_manager import QdrantManager
from typing import Dict, Any, List, Optional
import json
import threading
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Thread-local memory storage (Phase 9)
_thread_local_memory = threading.local()
# Cross-thread shared memory (Phase 10)
_cross_thread_memory = {}
_cross_thread_lock = threading.RLock()


def memory_retrieval_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 4+9+10: Unified Memory Retrieval integrating three memory layers
    
    Purpose:
    1. Qdrant Memory: Persistent multi-session customer history from vector DB
    2. Thread Memory: Current thread's conversation context (Phase 9)
    3. Cross-Thread Memory: Shared memory across concurrent threads (Phase 10)
    
    Retrieves from all three sources and enriches state with complete context.
    
    Input State Fields:
    - customer_id: str - Customer identifier for history lookup
    - conversation_id: str - Unique conversation identifier
    
    Output:
    - memory_context: str - Formatted Qdrant history
    - history_sessions: int - Number of previous sessions
    - thread_memory: dict - Current thread's memory context
    - cross_thread_memory: dict - Shared cross-thread context
    - thread_id: int - Current thread ID
    - all_memory_available: bool - Whether all memory sources accessible
    """
    
    customer_id = state.get("customer_id", "")
    conversation_id = state.get("conversation_id", customer_id)
    current_thread = threading.get_ident()
    
    qdrant_memory = {}
    thread_memory = {}
    cross_thread_memory = {}
    thread_memory_status = "unavailable"
    cross_thread_status = "unavailable"
    
    if not customer_id:
        return {
            "memory_context": "",
            "history_sessions": 0,
            "thread_memory": {},
            "cross_thread_memory": {},
            "thread_id": current_thread,
            "all_memory_available": False,
        }
    
    try:
        qdrant = QdrantManager()
        search_results = qdrant.search_history(
            query="customer interaction history",
            customer_id=customer_id,
            limit=20
        )
        
        if search_results:
            sessions = {}
            for result in search_results:
                session_id = f"session_{len(sessions)}"
                interaction_type = result.get("interaction_type", "unknown")
                text = result.get("text", "")[:200]
                
                if session_id not in sessions:
                    sessions[session_id] = {
                        "interactions": [],
                        "types": set(),
                    }
                
                sessions[session_id]["interactions"].append(text)
                sessions[session_id]["types"].add(interaction_type)
            
            memory_parts = []
            memory_parts.append(f"Customer History Summary (ID: {customer_id})")
            memory_parts.append(f"Total Interactions: {len(search_results)}")
            memory_parts.append("")
            
            for session_id, session_data in list(sessions.items())[:5]:
                types = ", ".join(session_data.get("types", set()))
                count = len(session_data.get("interactions", []))
                
                memory_parts.append(f"Session: {session_id}")
                memory_parts.append(f"  Types: {types or 'unknown'}")
                memory_parts.append(f"  Interactions: {count}")
                memory_parts.append("")
            
            qdrant_memory = {
                "memory_context": "\n".join(memory_parts),
                "history_sessions": len(sessions),
            }
    except Exception as e:
        logger.error(f"Qdrant memory retrieval error: {str(e)}")
        qdrant_memory = {
            "memory_context": "",
            "history_sessions": 0,
        }
    
    try:
        thread_ctx = getattr(_thread_local_memory, f'context_{conversation_id}', None)
        
        if thread_ctx:
            thread_memory = thread_ctx.get('data', {})
            thread_memory_status = "retrieved"
        else:
            thread_memory_status = "no_context"
    except Exception as e:
        logger.error(f"Thread memory retrieval error: {str(e)}")
        thread_memory_status = f"error: {str(e)}"
    
    try:
        with _cross_thread_lock:
            mem_key = f"conv_{conversation_id}"
            cross_mem = _cross_thread_memory.get(mem_key, {})
            
            if cross_mem:
                cross_thread_memory = cross_mem.get('data', {})
                cross_thread_status = "retrieved"
            else:
                cross_thread_status = "no_shared_memory"
            
            linked_threads = []
    except Exception as e:
        logger.error(f"Cross-thread memory retrieval error: {str(e)}")
        cross_thread_status = f"error: {str(e)}"
        linked_threads = []
    
    all_available = (
        thread_memory_status == "retrieved" and
        cross_thread_status == "retrieved"
    )
    
    return {
        "memory_context": qdrant_memory.get("memory_context", ""),
        "history_sessions": qdrant_memory.get("history_sessions", 0),
        "thread_memory": thread_memory,
        "cross_thread_memory": cross_thread_memory,
        "thread_id": current_thread,
        "thread_memory_status": thread_memory_status,
        "cross_thread_status": cross_thread_status,
        "cross_thread_links": linked_threads,
        "all_memory_available": all_available,
    }
