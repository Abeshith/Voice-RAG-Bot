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
    Phase 4+9+10: Unified Memory Persistence integrating three memory layers
    
    Purpose:
    1. Qdrant Persistence: Store to persistent vector DB for historical retrieval
    2. Thread Memory: Save to thread-local memory (Phase 9)
    3. Cross-Thread Memory: Update shared memory across threads (Phase 10)
    
    Saves conversation state to all three memory sources simultaneously.
    
    Input State Fields:
    - user_input: User message
    - response: Assistant response
    - intent: Classified intent
    - sentiment: Sentiment analysis
    - customer_id: Customer identifier
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
    conversation_id = state.get('conversation_id', customer_id)
    current_thread = threading.get_ident()
    
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
    except Exception as e:
        logger.error(f"Qdrant persistence error: {str(e)}")
        qdrant_saved = False
    
    try:
        thread_state_data = {
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "user_input": state.get('user_input', ''),
            "response": state.get('response', ''),
            "intent": intent,
            "sentiment": state.get('sentiment', ''),
            "timestamp": datetime.now().isoformat(),
        }
        
        setattr(_thread_local_memory, f'context_{conversation_id}', {'data': thread_state_data})
        thread_memory_saved = True
    except Exception as e:
        logger.error(f"Thread memory persistence error: {str(e)}")
        thread_memory_saved = False
    
    try:
        mem_key = f"conv_{conversation_id}_{current_thread}"
        
        cross_thread_data = {
            "customer_id": customer_id,
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
            _cross_thread_memory[mem_key] = {'data': cross_thread_data}
        
        cross_thread_saved = True
    except Exception as e:
        logger.error(f"Cross-thread memory persistence error: {str(e)}")
        cross_thread_saved = False
    
    tracker.end("memory_persistence")
    
    persistence_status = "success" if (qdrant_saved and thread_memory_saved and cross_thread_saved) else "partial"
    
    return {
        "persistence_status": persistence_status,
        "qdrant_saved": qdrant_saved,
        "thread_memory_saved": thread_memory_saved,
        "cross_thread_saved": cross_thread_saved,
    }
