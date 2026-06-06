"""Phase 4+9+10: Integrated Memory Persistence - Qdrant + Thread-Local + Cross-Thread"""

from orchestration.state import ConversationState
from rag.qdrant_manager import qdrant_manager
from typing import Dict, Any
from orchestration.latency_tracker import get_tracker
import threading
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Thread-local memory storage (Phase 9)
_thread_local_memory = threading.local()
# Cross-thread shared memory (Phase 10)
_cross_thread_memory = {}
_cross_thread_lock = threading.RLock()


def memory_persistence_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 4+9+10+12+14: Unified Memory Persistence with Session-Based Routing
    
    Purpose:
    1. Qdrant Persistence: Store to persistent vector DB for historical retrieval
    2. Thread Memory: Save to thread-local memory (Phase 9)
    3. Cross-Thread Memory: Update shared memory across threads (Phase 10)
    4. User Isolation: All memory saves prefixed with user_id (Phase 12)
    5. Session Routing: Route memory saves by session_id (Phase 14)
    
    Saves conversation state to all three memory sources simultaneously.
    Each session maintains separate memory. Different sessions have different keys.
    
    Input State Fields:
    - user_input: User message
    - response: Assistant response
    - intent: Classified intent
    - sentiment: Sentiment analysis
    - customer_id: Customer identifier
    - user_id: Authenticated user ID (Phase 12)
    - session_id: Current session ID (Phase 14)
    - conversation_id: Unique conversation ID
    
    Output:
    - persistence_status: 'success' or 'partial'
    - qdrant_saved: bool - Whether Qdrant save succeeded
    - thread_memory_saved: bool - Whether thread memory saved
    - cross_thread_saved: bool - Whether cross-thread memory saved
    """
    
    tracker = get_tracker()
    tracker.start("memory_persistence")
    
    customer_id = state.get('customer_id', 'unknown')
    user_id = state.get('user_id', None)  # Phase 12: Authenticated user
    session_id = state.get('session_id', None)  # Phase 14: Session routing
    conversation_id = state.get('conversation_id', customer_id)
    current_thread = threading.get_ident()
    
    # Phase 14: Build isolation keys with session_id for memory routing
    session_prefix = f"{user_id}:{session_id}:" if user_id and session_id else f"{user_id}:" if user_id else ""
    thread_key = f"{session_prefix}context_{conversation_id}"
    cross_thread_key = f"{session_prefix}conv_{conversation_id}_{current_thread}"
    
    logger.info(f"Memory persistence - User: {user_id}, Session: {session_id}, Customer: {customer_id}, Thread: {current_thread}")
    
    conversation_text = f"User: {state.get('user_input', '')}\nAssistant: {state.get('response', '')}"
    intent = state.get('intent', 'other')
    interaction_type = intent
    
    qdrant_saved = False
    thread_memory_saved = False
    cross_thread_saved = False
    
    try:
        qdrant_manager.add_to_history(
            customer_id=customer_id,
            text=conversation_text,
            interaction_type=interaction_type
        )
        qdrant_saved = True
        logger.debug(f"Qdrant persistence successful for user {user_id}")
    except Exception as e:
        logger.error(f"Qdrant persistence error (User: {user_id}): {str(e)}")
        qdrant_saved = False
    
    try:
        thread_state_data = {
            "customer_id": customer_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "user_input": state.get('user_input', ''),
            "response": state.get('response', ''),
            "intent": intent,
            "sentiment": state.get('sentiment', ''),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Phase 12: Use user-isolated thread key
        setattr(_thread_local_memory, thread_key, {'data': thread_state_data})
        thread_memory_saved = True
        logger.debug(f"Thread memory persistence successful for user {user_id}")
    except Exception as e:
        logger.error(f"Thread memory persistence error (User: {user_id}): {str(e)}")
        thread_memory_saved = False
    
    try:
        # Phase 12: Use user-isolated cross-thread key
        cross_thread_data = {
            "customer_id": customer_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "user_input": state.get('user_input', ''),
            "response": state.get('response', ''),
            "intent": intent,
            "sentiment": state.get('sentiment', ''),
            "complaint_severity": state.get('complaint_severity', ''),
            "escalation_level": state.get('escalation_level', ''),
            "timestamp": datetime.now().isoformat(),
            "thread_id": current_thread,
        }
        
        with _cross_thread_lock:
            _cross_thread_memory[cross_thread_key] = {'data': cross_thread_data}
        
        cross_thread_saved = True
        logger.debug(f"Cross-thread memory persistence successful for user {user_id}")
    except Exception as e:
        logger.error(f"Cross-thread memory persistence error (User: {user_id}): {str(e)}")
        cross_thread_saved = False
    
    tracker.end("memory_persistence")
    
    persistence_status = "success" if (qdrant_saved and thread_memory_saved and cross_thread_saved) else "partial"
    
    return {
        "persistence_status": persistence_status,
        "qdrant_saved": qdrant_saved,
        "thread_memory_saved": thread_memory_saved,
        "cross_thread_saved": cross_thread_saved,
    }
