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
from orchestration.nodes.context_builder import context_builder_node
from orchestration.nodes.response_generation import response_generation_node
from orchestration.nodes.validation import validation_node
from orchestration.nodes.memory_persistence import memory_persistence_node
from orchestration.nodes.tts_generation import tts_generation_node

logger = logging.getLogger(__name__)

def build_workflow() -> StateGraph:
    workflow = StateGraph(ConversationState)
    
    workflow.add_node("sentiment_analysis", sentiment_analysis_node)
    workflow.add_node("entity_extraction", entity_extraction_node)
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("retrieval_router", retrieval_router_node)
    workflow.add_node("context_builder", context_builder_node)
    workflow.add_node("response_generation", response_generation_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("memory_persistence", memory_persistence_node)
    workflow.add_node("tts_generation", tts_generation_node)
    
    workflow.add_edge(START, "sentiment_analysis")
    workflow.add_edge(START, "entity_extraction")
    workflow.add_edge("sentiment_analysis", "intent_detection")
    workflow.add_edge("entity_extraction", "intent_detection")
    workflow.add_edge("intent_detection", "retrieval_router")
    workflow.add_edge("retrieval_router", "context_builder")
    workflow.add_edge("context_builder", "response_generation")
    workflow.add_edge("response_generation", "validation")
    
    def should_regenerate(state: ConversationState) -> str:
        return "memory_persistence" if state.get("validation_passed", False) else "response_generation"
    
    workflow.add_conditional_edges("validation", should_regenerate, {"memory_persistence": "memory_persistence", "response_generation": "response_generation"})
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
            "response": "",
            "validation_passed": False,
            "final_audio_path": None
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
