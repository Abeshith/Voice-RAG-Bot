"""Context formatter for LLM prompts"""

from orchestration.state import ConversationState
from typing import Dict, Any
from orchestration.latency_tracker import get_tracker


def context_builder_node(state: ConversationState) -> Dict[str, Any]:
    """
    Build complete context string from all available information
    for LLM to generate response
    
    Combines:
    - User input
    - Intent & sentiment
    - KB context
    - Customer history
    - Conversation summary
    
    Returns:
        State update (no new fields added, just confirmation)
    """
    tracker = get_tracker()
    tracker.start("context_builder")
    
    # Extract components
    sentiment_label = state['sentiment']['label']
    sentiment_score = state['sentiment']['score']
    intent = state['intent']['intent']
    kb_context = state['kb_context']
    history_context = state['history_context']
    conversation_summary = state['conversation_summary']
    entities = state.get('entities', {})
    
    # Build prompt context (this will be used by response_generation node)
    # We just validate all components exist, they'll be used by next node
    
    # Prepare formatted context for logging/debugging
    formatted_context = f"""
=== UNIFIED CONTEXT ===
User Intent: {intent}
User Sentiment: {sentiment_label} (confidence: {sentiment_score:.2f})

KB Context:
{kb_context}

Customer History:
{history_context}

Conversation Summary:
{conversation_summary}

Entities Detected:
{entities}
"""
    
    tracker.end("context_builder")
    # Return minimal state update - context is already in state
    # Next node (response_generation) will use these state fields directly
    return {}
