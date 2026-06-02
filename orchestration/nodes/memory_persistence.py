"""Conversation storage to Qdrant customer history"""

from orchestration.state import ConversationState
from rag.qdrant_manager import qdrant_manager
from typing import Dict, Any
from orchestration.latency_tracker import get_tracker


def memory_persistence_node(state: ConversationState) -> Dict[str, Any]:
    """
    Store conversation turn to customer history collection in Qdrant
    Enables historical context retrieval for repeat customers
    
    Stores:
    - Customer ID (for filtering)
    - User input + response
    - Intent classification
    - Sentiment
    - Timestamp
    
    Returns:
        state update (minimal, side-effect is primary)
    """
    tracker = get_tracker()
    tracker.start("memory_persistence")
    
    # Combine user input and response for storage
    conversation_text = f"User: {state['user_input']}\nAssistant: {state['response']}"
    
    # Determine interaction type from intent for categorization
    intent = state['intent']['intent']
    interaction_type = intent
    
    # Store to Qdrant customer history
    qdrant_manager.add_to_history(
        customer_id=state['customer_id'],
        text=conversation_text,
        interaction_type=interaction_type
    )
    
    # Update conversation summary in memory (every 5 turns)
    # For now, just store the current exchange
    
    tracker.end("memory_persistence")
    return {}
