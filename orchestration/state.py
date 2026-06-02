"""  
LangGraph State Definition - Central State Management for Voice RAG Bot Workflow
Defines all data flowing through the orchestration pipeline
"""

from typing import TypedDict, List, Optional, Dict, Any


class ConversationState(TypedDict):
    """
    Complete state passed through LangGraph nodes
    
    Fields:
    - user_input: Original text from voice input (after STT)
    - customer_id: Unique customer identifier for history tracking
    - intent: Intent detection result with confidence score
    - sentiment: Sentiment analysis result with label and confidence
    - entities: Extracted entities from user input (optional)
    - conversation_summary: LLM-generated summary of conversation
    - kb_context: Retrieved context from knowledge base
    - history_context: Retrieved context from customer history (persistent memory)
    - response: Final LLM-generated response text
    - validation_passed: Boolean flag for response validation
    - final_audio_path: Path to generated TTS audio file
    """
    
    # Input & Context
    user_input: str
    customer_id: str
    
    # NLP Analysis Results
    intent: Dict[str, Any]  # {"intent": "...", "confidence": float}
    sentiment: Dict[str, Any]  # {"label": "POSITIVE|NEGATIVE|NEUTRAL", "score": float}
    entities: Optional[Dict[str, Any]]  # {"entity_type": [...], ...}
    
    # Memory Management
    conversation_summary: str  # LLM-generated summary
    
    # RAG Contexts
    kb_context: str  # Knowledge base retrieval results
    history_context: str  # Customer history retrieval results
    
    # Response Generation
    response: str  # Final LLM-generated response
    
    # Validation & Output
    validation_passed: bool
    final_audio_path: Optional[str]


class ConversationStateOptional(TypedDict, total=False):
    """
    Optional version of ConversationState for partial updates
    Allows nodes to update only the fields they produce
    """
    
    user_input: str
    customer_id: str
    intent: Dict[str, Any]
    sentiment: Dict[str, Any]
    entities: Optional[Dict[str, Any]]
    conversation_summary: str
    kb_context: str
    history_context: str
    response: str
    validation_passed: bool
    final_audio_path: Optional[str]
