"""Intent classification using Groq LLM"""

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from orchestration.state import ConversationState
from typing import Dict, Any
import json
from backend.config import settings
from orchestration.latency_tracker import get_tracker


def intent_detection_node(state: ConversationState) -> Dict[str, Any]:
    """
    Detect user intent using Groq LLM
    
    Returns:
        state update with intent field:
        {"intent": {"intent": "...", "confidence": float}}
    """
    tracker = get_tracker()
    tracker.start("intent_detection")
    
    # Initialize Groq LLM
    llm = ChatGroq(
        model=settings.groq_model,
        temperature=0.3,  # Low temp for consistent intent detection
        groq_api_key=settings.groq_api_key
    )
    
    # Prompt template for intent detection
    intent_prompt = PromptTemplate(
        input_variables=["user_input"],
        template="""Analyze the user's input and determine their intent. Respond ONLY with JSON.

User Input: {user_input}

Intent Definitions:
- complaint: Customer reporting a problem, issue, or dissatisfaction (e.g., delayed order, defective product, billing error)
- escalation: Customer is angry, demanding immediate action, or asking to speak to manager/supervisor
- refund_request: Customer asking for money back
- order_status: Customer asking about order tracking or status
- inquiry: General questions about products or services
- billing: Questions about charges, payments, or pricing
- account_issue: Problems with account access or login
- product_question: Questions about product features or specifications
- other: Any other intent

Response format:
{{
  "intent": "<selected_intent>",
  "confidence": <0.0-1.0>
}}"""
    )
    
    # Generate intent using chain pattern
    chain = intent_prompt | llm
    response = chain.invoke({"user_input": state['user_input']})
    
    try:
        # Parse JSON response from LLM
        intent_data = json.loads(response.content.strip())
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        intent_data = {
            "intent": "other",
            "confidence": 0.5
        }
    
    tracker.end("intent_detection")
    # Return just the intent string, not the whole dict
    return {"intent": intent_data.get("intent", "other")}
