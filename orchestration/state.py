"""  
LangGraph State Definition - Central State Management for Voice RAG Bot Workflow
Defines all data flowing through the orchestration pipeline
"""

from typing import TypedDict, List, Optional, Dict, Any, Literal


VALID_INTENTS = Literal[
    "complaint",
    "refund_request", 
    "inquiry",
    "account_issue",
    "escalation",
    "billing",
    "product_question",
    "order_status",
    "other"
]

VALID_SENTIMENTS = Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]


def validate_intent(intent: str) -> bool:
    valid = {
        "complaint", "refund_request", "inquiry", "account_issue",
        "escalation", "billing", "product_question", "order_status", "other"
    }
    return intent in valid


def validate_sentiment(sentiment: str) -> bool:
    return sentiment in {"POSITIVE", "NEGATIVE", "NEUTRAL"}


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
    user_id: Optional[str]  # Phase 11: Authenticated user ID
    session_id: Optional[str]  # Phase 11: Unique session identifier
    
    # NLP Analysis Results
    intent: str
    sentiment: str
    entities: Optional[Dict[str, Any]]
    
    # Memory Management
    conversation_summary: str  # LLM-generated summary
    
    # RAG Contexts
    kb_context: str  # Knowledge base retrieval results
    history_context: str  # Customer history retrieval results
    memory_context: str  # Multi-session customer memory (Phase 4)
    
    # Response Generation
    response: str  # Final LLM-generated response
    
    # Validation & Output
    validation_passed: bool
    final_audio_path: Optional[str]
    
    # Phase 6: Complaint Subgraph Fields (Optional)
    complaint_severity: Optional[str]  # LOW, MEDIUM, HIGH, CRITICAL
    escalation_urgency: int  # 0-10 scale
    complaint_action: Optional[str]  # Recommended action
    auto_escalate: bool  # Auto-escalate flag
    resolution_strategy: Optional[str]  # Resolution approach
    offer_discount: bool  # Whether to offer discount
    offer_replacement: bool  # Whether to offer replacement
    needs_escalation: bool  # Needs escalation flag
    response_tone: Optional[str]  # Response tone (sympathetic, urgent, etc.)
    escalate_to_human: bool  # Human escalation needed
    escalation_level: Optional[str]  # agent, supervisor, manager
    escalation_reason: Optional[str]  # Why escalating
    priority_flag: bool  # High priority flag
    
    # Phase 8: Retry Policies
    retry_count: int  # Number of retries attempted
    retry_policy_applied: str  # Policy used (normal, high, critical, low)
    retry_max_attempts: int  # Max retries allowed
    retry_strategy: str  # exponential_backoff, linear, fixed, adaptive
    retry_success: bool  # Whether retries were successful
    retry_attempts: list  # History of retry attempts
    
    # Phase 8: Escalation
    escalation_ticket: str  # Ticket ID for escalation
    escalation_message: str  # Message for human agent
    requires_callback: bool  # Whether customer needs callback
    
    # Phase 9: Thread-Scoped Memory
    thread_memory: Dict[str, Any]  # Current thread's conversation memory
    thread_id: int  # Current thread ID
    thread_memory_status: str  # Status of thread memory retrieval
    
    # Phase 10: Cross-Thread Memory
    cross_thread_memory: Dict[str, Any]  # Shared memory across threads
    cross_thread_status: str  # Status of cross-thread memory retrieval
    cross_thread_links: list  # List of linked thread IDs
    all_memory_available: bool  # Whether all memory sources accessible
    
    # Phase 4+9+10: Persistence Status
    persistence_status: str  # 'success' or 'partial'
    qdrant_saved: bool  # Whether Qdrant save succeeded
    thread_memory_saved: bool  # Whether thread memory saved
    cross_thread_saved: bool  # Whether cross-thread memory saved
    
    # Phase 13: Session Linking & Tracking
    session_start_time: Optional[str]  # ISO format session start timestamp
    session_end_time: Optional[str]  # ISO format session end timestamp
    session_duration_seconds: int  # How long session lasted
    active_sessions: List[str]  # List of session IDs for this user
    session_count: int  # Total sessions for this user
    session_linked: bool  # Whether session linked to user history
    session_tracking_status: str  # Status of session tracking operation
    
    # Phase 14: Memory Routing by Session
    session_memory_status: str  # Status of session-based memory routing
    session_specific_context: Optional[Dict[str, Any]]  # Memory specific to current session
    previous_session_context: Optional[Dict[str, Any]]  # Context from previous sessions
    memory_routed_by_session: bool  # Whether memory successfully routed by session
    session_isolation_verified: bool  # Whether session isolation is maintained
    
    # Phase 15: Escalation State Management
    user_escalation_state: str  # Current user escalation level (none/low/medium/high/critical)
    escalation_state_updated: bool  # Whether escalation state was updated
    escalation_state_persisted: bool  # Whether state was persisted
    escalation_history_count: int  # Count of escalations in session
    escalation_state_management_status: str  # Status of escalation management operation
    escalation_influenced_response: bool  # Whether response tone influenced by escalation
    previous_escalation_level: str  # Previous escalation level before this interaction
    
    # Phase 16: Sentiment Trend Analysis
    sentiment_history: List[str]  # Recent sentiment sequence for user
    sentiment_trend: str  # Trend direction (improving/declining/stable)
    consecutive_negative_count: int  # Count of consecutive negative sentiments
    trend_escalation_recommended: bool  # Whether trend indicates escalation needed
    trend_escalation_reason: str  # Reason for trend-based escalation recommendation
    sentiment_trend_score: float  # Numerical trend score (-1 to +1)
    trend_analysis_status: str  # Status of trend analysis operation
    escalation_confidence: int  # Confidence level (0-100) for trend escalation


class ConversationStateOptional(TypedDict, total=False):
    """
    Optional version of ConversationState for partial updates
    Allows nodes to update only the fields they produce
    """
    
    user_input: str
    customer_id: str
    intent: str
    sentiment: str
    entities: Optional[Dict[str, Any]]
    conversation_summary: str
    kb_context: str
    history_context: str
    response: str
    validation_passed: bool
    final_audio_path: Optional[str]


class ConversationStateEnhanced(TypedDict, total=False):
    """
    Phase 2: Enhanced state with tracking and confidence metrics
    Backward compatible with ConversationState
    """
    
    user_input: str
    customer_id: str
    intent: str
    sentiment: str
    entities: Optional[Dict[str, Any]]
    conversation_summary: str
    kb_context: str
    history_context: str
    response: str
    validation_passed: bool
    final_audio_path: Optional[str]
    
    intent_confidence: float
    sentiment_confidence: float
    retry_count: int
    validation_attempts: int
    nodes_executed: List[str]
    timestamp_created: str
    timestamp_completed: str
    processing_time_ms: float
    error_log: List[Dict[str, Any]]


class StateValidator:
    """Phase 2: Validate state fields match constraints"""
    
    @staticmethod
    def validate_base_state(state: Dict[str, Any]) -> bool:
        if not isinstance(state.get("user_input"), str):
            return False
        if not isinstance(state.get("customer_id"), str):
            return False
        if not validate_intent(state.get("intent", "other")):
            return False
        if not validate_sentiment(state.get("sentiment", "NEUTRAL")):
            return False
        return True
    
    @staticmethod
    def validate_enhanced(state: Dict[str, Any]) -> bool:
        if not StateValidator.validate_base_state(state):
            return False
        if "intent_confidence" in state:
            if not (0 <= state["intent_confidence"] <= 1):
                return False
        if "sentiment_confidence" in state:
            if not (0 <= state["sentiment_confidence"] <= 1):
                return False
        if "retry_count" in state and state["retry_count"] < 0:
            return False
        return True
