"""Voice Bot Controller - Session management for conversations"""

from typing import Dict, Any
from datetime import datetime
import asyncio
from rag.session_manager import get_session_manager
from rag.cache_manager import get_cache_manager
from rag.tts_generator import get_tts_generator
from orchestration.langgraph_workflow import run_workflow


class VoiceBotController:
    def __init__(self):
        self.session_mgr = get_session_manager()
        self.cache_mgr = get_cache_manager()
        self.tts_gen = get_tts_generator()
        self.current_session = None
        self.customer_id = None
        self.conversation_history = []
    
    async def start_session(self, customer_id: str) -> Dict[str, Any]:
        self.customer_id = customer_id
        self.current_session = self.session_mgr.create_session(customer_id)
        self.conversation_history = []
        
        greeting = "Hello! How can I help you today?"
        audio_path = self.tts_gen.generate_greeting(customer_id)
        
        return {
            "session_id": self.current_session,
            "greeting": greeting,
            "audio_path": audio_path,
            "status": "listening"
        }
    
    async def process_user_message(self, user_message: str) -> Dict[str, Any]:
        if not self.current_session:
            return {"error": "No active session"}
        
        self.session_mgr.add_message(self.current_session, "user", user_message)
        
        cached_response = self.cache_mgr.get(self.customer_id, user_message)
        if cached_response:
            response_text = cached_response.get("response_text", "")
            intent = cached_response.get("intent", {}).get("intent", "")
            sentiment = cached_response.get("sentiment", {}).get("label", "")
        else:
            try:
                result = await run_workflow(user_message, self.customer_id)
                response_text = result.get("response", "")
                intent = result.get("intent", {}).get("intent", "")
                sentiment = result.get("sentiment", {}).get("label", "")
                self.cache_mgr.set(self.customer_id, user_message, result)
            except Exception as e:
                response_text = f"Error processing request: {str(e)}"
                intent = "error"
                sentiment = "NEGATIVE"
        
        self.session_mgr.add_message(self.current_session, "assistant", response_text, intent=intent, sentiment=sentiment)
        
        follow_up = self._generate_follow_up(intent, sentiment)
        should_continue = self._should_continue(intent, sentiment)
        audio_path = self.tts_gen.generate_audio(response_text, self.customer_id, self.current_session)
        
        return {
            "response": response_text,
            "intent": intent,
            "sentiment": sentiment,
            "follow_up": follow_up,
            "audio_path": audio_path,
            "status": "listening" if should_continue else "done",
            "session_id": self.current_session
        }
    
    def _generate_follow_up(self, intent: str, sentiment: str) -> str:
        """Generate context-aware follow-up question"""
        follow_ups = {
            "refund_request": "Would you like assistance with starting a return?",
            "product_inquiry": "Do you need more details about this product?",
            "billing_issue": "Can I help you further with your billing concern?",
            "warranty_claim": "Would you like to proceed with the warranty claim?",
            "order_status": "Is there anything else about your order?",
            "complaint": "How can I make this right for you?",
            "general_support": "Is there anything else I can help you with?"
        }
        
        # Choose follow-up based on intent
        if intent in follow_ups:
            return follow_ups[intent]
        
        # Default follow-ups based on sentiment
        if sentiment == "NEGATIVE":
            return "I apologize for the inconvenience. Is there anything else I can help resolve?"
        elif sentiment == "POSITIVE":
            return "Great! Is there anything else I can help you with today?"
        else:
            return "Is there anything else I can help you with?"
    
    def _should_continue(self, intent: str, sentiment: str) -> bool:
        """Determine if conversation should continue"""
        # Continue unless user explicitly ends or issue resolved
        end_indicators = ["goodbye", "thanks", "that's it", "no thanks"]
        
        # For now, always continue unless error
        return intent != "error"
    
    async def end_session(self) -> Dict[str, Any]:
        if self.current_session:
            self.session_mgr.close_session(self.current_session)
            history = self.session_mgr.get_session_history(self.current_session)
            return {
                "session_id": self.current_session,
                "status": "closed",
                "message_count": len(history),
                "farewell": "Thank you for contacting us. Goodbye!"
            }
        return {"error": "No active session"}
    
    def get_session_history(self) -> list:
        if not self.current_session:
            return []
        return self.session_mgr.get_session_history(self.current_session)


# Global controller instance
_voice_bot_controller = None


def get_voice_bot_controller() -> VoiceBotController:
    """Get or create global voice bot controller"""
    global _voice_bot_controller
    if _voice_bot_controller is None:
        _voice_bot_controller = VoiceBotController()
    return _voice_bot_controller
