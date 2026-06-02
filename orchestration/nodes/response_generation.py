"""Response generation using Groq LLM"""

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from orchestration.state import ConversationState
from typing import Dict, Any
import logging
from backend.config import settings
from orchestration.latency_tracker import get_tracker

logger = logging.getLogger(__name__)


def response_generation_node(state: ConversationState) -> Dict[str, Any]:
    """
    Generate final response using Groq LLM
    Incorporates KB context, customer history, intent, and sentiment
    
    Returns:
        state update with response field
    """
    tracker = get_tracker()
    tracker.start("response_generation")
    
    try:
        logger.info("Response Generation: Initializing Groq LLM...")
        
        # Initialize Groq LLM
        llm = ChatGroq(
            model=settings.groq_model,
            temperature=settings.groq_temperature,
            max_tokens=settings.groq_max_tokens,
            groq_api_key=settings.groq_api_key
        )
        
        # Determine tone based on sentiment
        sentiment_label = state['sentiment']['label']
        tone_instruction = {
            "POSITIVE": "Use a friendly, upbeat tone.",
            "NEGATIVE": "Use an empathetic, understanding tone. Acknowledge frustration.",
            "NEUTRAL": "Use a professional, helpful tone."
        }.get(sentiment_label, "Use a professional tone.")
        
        # Build response prompt
        response_prompt = PromptTemplate(
            input_variables=[
                "user_input",
                "intent",
                "kb_context",
                "history_context",
                "tone_instruction"
            ],
            template="""You are a helpful customer service AI assistant.

User Intent: {intent}
{tone_instruction}

Knowledge Base Context:
{kb_context}

Customer History:
{history_context}

User Message: {user_input}

Provide a helpful, accurate response based on the context above. Keep response concise (2-3 sentences).
If you don't have relevant information, say so clearly."""
        )
        
        # Generate response using chain pattern
        logger.info("🤖 Response Generation: Invoking LLM chain...")
        chain = response_prompt | llm
        response = chain.invoke({
            "user_input": state['user_input'],
            "intent": state['intent']['intent'],
            "kb_context": state['kb_context'],
            "history_context": state['history_context'],
            "tone_instruction": tone_instruction
        })
        
        response_text = response.content.strip()
        logger.info(f"✅ Response generated: '{response_text[:80]}...'")
        
        tracker.end("response_generation")
        return {"response": response_text}
        
    except Exception as e:
        logger.error(f"❌ Response generation failed: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        tracker.end("response_generation")
        # Return fallback response
        return {"response": "I apologize, but I encountered an error processing your request. Please try again."}
