"""LangGraph Workflow - 9-node orchestration pipeline"""

from langgraph.graph import StateGraph, END, START
from orchestration.state import ConversationState
from typing import Any, Dict
import logging
from orchestration.latency_tracker import get_tracker, reset_tracker

# Import all nodes
from orchestration.nodes.sentiment_hybrid import sentiment_analysis_hybrid as sentiment_analysis_node
from orchestration.nodes.entity_extraction import entity_extraction_node
from orchestration.nodes.intent_detection import intent_detection_node
from orchestration.nodes.retrieval_router import retrieval_router_node
from orchestration.nodes.memory_retrieval import memory_retrieval_node
from orchestration.nodes.context_builder import context_builder_node
from orchestration.nodes.response_generation import response_generation_node
from orchestration.nodes.validation import validation_node
from orchestration.nodes.memory_persistence import memory_persistence_node
from orchestration.nodes.tts_generation import tts_generation_node
from orchestration.nodes.escalation import escalation_node

# Import subgraphs
from orchestration.subgraphs.complaint_subgraph import complaint_subgraph_node

logger = logging.getLogger(__name__)

def build_workflow() -> StateGraph:
    workflow = StateGraph(ConversationState)
    
    workflow.add_node("sentiment_analysis", sentiment_analysis_node)
    workflow.add_node("entity_extraction", entity_extraction_node)
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("complaint_subgraph", complaint_subgraph_node)
    workflow.add_node("retrieval_router", retrieval_router_node)
    workflow.add_node("memory_retrieval", memory_retrieval_node)
    workflow.add_node("context_builder", context_builder_node)
    workflow.add_node("response_generation", response_generation_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("escalation", escalation_node)
    workflow.add_node("memory_persistence", memory_persistence_node)
    workflow.add_node("tts_generation", tts_generation_node)
    
    workflow.add_edge(START, "sentiment_analysis")
    workflow.add_edge(START, "entity_extraction")
    workflow.add_edge("sentiment_analysis", "intent_detection")
    workflow.add_edge("entity_extraction", "intent_detection")
    
    # Conditional routing based on intent
    def route_by_intent(state: ConversationState) -> str:
        intent = state.get("intent", "inquiry")
        if intent in ["complaint", "escalation"]:
            return "complaint_subgraph"
        else:
            return "retrieval_router"
    
    workflow.add_conditional_edges(
        "intent_detection",
        route_by_intent,
        {"complaint_subgraph": "complaint_subgraph", "retrieval_router": "retrieval_router"}
    )
    
    # Both paths merge at memory_retrieval for context enrichment
    workflow.add_edge("complaint_subgraph", "memory_retrieval")
    workflow.add_edge("retrieval_router", "memory_retrieval")
    workflow.add_edge("memory_retrieval", "context_builder")
    workflow.add_edge("context_builder", "response_generation")
    workflow.add_edge("response_generation", "validation")
    
    def should_regenerate(state: ConversationState) -> str:
        """
        Validation routing with escalation decision
        
        Routes based on:
        - validation_passed: Response quality check
        - retry_count: Retry attempts made
        - escalation_level: Whether escalation needed
        """
        validation_passed = state.get("validation_passed", False)
        escalation_level = state.get("escalation_level", "none")
        
        # If needs escalation, route there
        if escalation_level != "none" and escalation_level != "":
            return "escalation"
        
        # If validation passed, proceed to persistence
        if validation_passed:
            return "memory_persistence"
        
        # Otherwise retry response generation
        return "response_generation"
    
    workflow.add_conditional_edges(
        "validation",
        should_regenerate,
        {
            "memory_persistence": "memory_persistence",
            "response_generation": "response_generation",
            "escalation": "escalation"
        }
    )
    
    # Escalation routes to persistence (logs escalation, then continues)
    workflow.add_edge("escalation", "memory_persistence")
    workflow.add_edge("memory_persistence", "tts_generation")
    workflow.add_edge("tts_generation", END)
    
    return workflow


# Compile the workflow
workflow = build_workflow()
compiled_workflow = workflow.compile()


async def run_workflow(user_input: str, customer_id: str) -> Dict[str, Any]:
    """
    Execute the complete workflow
    
    Args:
        user_input: Text from STT (user's speech converted to text)
        customer_id: Unique customer identifier
        
    Returns:
        Complete state with response, audio path, and metadata
    """
    
    try:
        # Reset and start tracking
        reset_tracker()
        tracker = get_tracker()
        tracker.start_total()
        tracker.start("workflow_orchestration")
        
        # Initialize state
        initial_state: ConversationState = {
            "user_input": user_input,
            "customer_id": customer_id,
            "intent": {"intent": "unknown", "confidence": 0.0},
            "sentiment": {"label": "NEUTRAL", "score": 0.5},
            "entities": None,
            "conversation_summary": "",
            "kb_context": "",
            "history_context": "",
            "memory_context": "",
            "response": "",
            "validation_passed": False,
            "final_audio_path": None,
            # Phase 6: Complaint Subgraph
            "complaint_severity": "",
            "escalation_urgency": 0,
            "complaint_action": "",
            "auto_escalate": False,
            "resolution_strategy": "",
            "offer_discount": False,
            "offer_replacement": False,
            "needs_escalation": False,
            "response_tone": "",
            "escalate_to_human": False,
            "escalation_level": "",
            "escalation_reason": "",
            "priority_flag": False,
            # Phase 8: Retry Policies
            "retry_count": 0,
            "retry_policy_applied": "normal",
            "retry_max_attempts": 3,
            "retry_strategy": "exponential_backoff",
            "retry_success": True,
            "retry_attempts": [],
            # Phase 8: Escalation
            "escalation_ticket": "",
            "escalation_message": "",
            "requires_callback": False,
            # Phase 9: Thread-Scoped Memory
            "thread_memory": {},
            "thread_id": 0,
            "thread_memory_status": "pending",
            # Phase 10: Cross-Thread Memory
            "cross_thread_memory": {},
            "cross_thread_status": "pending",
            "cross_thread_links": [],
            "all_memory_available": False,
            # Phase 4+9+10: Persistence Status
            "persistence_status": "pending",
            "qdrant_saved": False,
            "thread_memory_saved": False,
            "cross_thread_saved": False,
        }
        
        # Run workflow
        final_state = await compiled_workflow.ainvoke(initial_state)
        
        tracker.end("workflow_orchestration")
        
        # Save and print results
        latency_results = tracker.save_to_file()
        tracker.print_summary()
        
        # Convert to regular dict and add latency info
        result_dict = dict(final_state)
        result_dict["latency_metrics"] = latency_results
        
        logger.info(f"Total workflow time: {latency_results['total_time_ms']} ms")
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def get_workflow_graph():
    return compiled_workflow.get_graph().draw_mermaid()
