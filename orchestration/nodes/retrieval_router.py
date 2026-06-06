"""Dual RAG routing - knowledge base + customer history"""

from orchestration.state import ConversationState
from rag.qdrant_manager import qdrant_manager
from typing import Dict, Any
from orchestration.latency_tracker import get_tracker


def retrieval_router_node(state: ConversationState) -> Dict[str, Any]:
    """
    Dual RAG retrieval strategy:
    1. Always search knowledge base for relevant policies/docs
    2. For specific intents (complaint, refund, escalation), also search customer history
    
    Returns:
        state update with kb_context and history_context
    """
    tracker = get_tracker()
    tracker.start("retrieval_router")
    
    user_input = state.get('user_input', '')
    customer_id = state.get('customer_id', '')
    intent = state.get('intent', 'other')
    sentiment = state.get('sentiment', 'NEUTRAL')
    
    # Always retrieve from knowledge base
    kb_results = qdrant_manager.search_kb(user_input, limit=3)
    kb_context = "\n".join([
        f"- [{r['source']}] {r['text']} (relevance: {r['score']:.2f})"
        for r in kb_results
    ])
    
    # Conditionally retrieve from customer history
    history_context = ""
    history_intents = ["complaint", "refund_request", "escalation", "billing_inquiry", "billing"]
    
    if intent in history_intents or sentiment == "NEGATIVE":
        history_results = qdrant_manager.search_history(
            user_input,
            customer_id,
            limit=3
        )
        history_context = "\n".join([
            f"- [{r['interaction_type']}] {r['text']} (relevance: {r['score']:.2f})"
            for r in history_results
        ])
    
    tracker.end("retrieval_router")
    return {
        "kb_context": kb_context if kb_results else "No relevant policies found.",
        "history_context": history_context if history_context else "No customer history available."
    }
