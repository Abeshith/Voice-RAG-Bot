"""Hybrid sentiment classifier - keyword-based + model fallback"""

from orchestration.state import ConversationState
from typing import Dict, Any
from transformers import pipeline
from orchestration.latency_tracker import get_tracker


# Global model cache
_sentiment_model = None


def get_sentiment_model():
    """Load model once and cache"""
    global _sentiment_model
    if _sentiment_model is None:
        _sentiment_model = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    return _sentiment_model


def sentiment_analysis_hybrid(state: ConversationState) -> Dict[str, Any]:
    """
    Hybrid sentiment classification:
    1. Check FAQ keywords → NEUTRAL
    2. Check explicit sentiment words → POSITIVE/NEGATIVE
    3. Fall back to DistilBERT model
    
    Returns:
        {"sentiment": {"label": "POSITIVE|NEGATIVE|NEUTRAL", "score": 0.95}}
    """
    tracker = get_tracker()
    tracker.start("sentiment_analysis")
    
    user_input = state['user_input'].lower()
    
    # Step 1: FAQ keywords → Always NEUTRAL (domain-specific)
    faq_keywords = [
        "policy", "return", "warranty", "shipping", "account", 
        "details", "information", "how", "what", "when", "where",
        "can i", "do you", "tell me", "help", "need", "about"
    ]
    
    if any(kw in user_input for kw in faq_keywords):
        # Still check for strong sentiment words within FAQ
        strong_negative = ["frustrated", "angry", "hate", "terrible", "broken", "worst", "useless"]
        strong_positive = ["thank", "love", "great", "excellent", "amazing", "perfect"]
        
        if any(word in user_input for word in strong_negative):
            tracker.end("sentiment_analysis")
            return {
                "sentiment": {
                    "label": "NEGATIVE",
                    "score": 0.95,
                    "reason": "Complaint with sentiment"
                }
            }
        elif any(word in user_input for word in strong_positive):
            tracker.end("sentiment_analysis")
            return {
                "sentiment": {
                    "label": "POSITIVE",
                    "score": 0.95,
                    "reason": "Praise with sentiment"
                }
            }
        else:
            # Pure FAQ question = NEUTRAL
            tracker.end("sentiment_analysis")
            return {
                "sentiment": {
                    "label": "NEUTRAL",
                    "score": 0.99,
                    "reason": "FAQ inquiry"
                }
            }
    
    # Step 2: Explicit strong sentiment words
    strong_negative = [
        "frustrated", "angry", "hate", "terrible", "broken", 
        "worst", "useless", "disaster", "awful", "horrible",
        "unacceptable", "disgusted", "disappointed"
    ]
    strong_positive = [
        "thank", "love", "great", "excellent", "amazing", 
        "perfect", "wonderful", "fantastic", "awesome", "impressed"
    ]
    
    if any(word in user_input for word in strong_negative):
        tracker.end("sentiment_analysis")
        return {
            "sentiment": {
                "label": "NEGATIVE",
                "score": 0.95,
                "reason": "Strong negative sentiment"
            }
        }
    
    if any(word in user_input for word in strong_positive):
        tracker.end("sentiment_analysis")
        return {
            "sentiment": {
                "label": "POSITIVE",
                "score": 0.95,
                "reason": "Strong positive sentiment"
            }
        }
    
    # Step 3: Fall back to DistilBERT model
    try:
        sentiment_pipeline = get_sentiment_model()
        result = sentiment_pipeline(state['user_input'])[0]
        
        tracker.end("sentiment_analysis")
        return {
            "sentiment": {
                "label": result['label'].upper(),
                "score": result['score'],
                "reason": "Model inference"
            }
        }
    except Exception as e:
        # Default to neutral on error
        tracker.end("sentiment_analysis")
        return {
            "sentiment": {
                "label": "NEUTRAL",
                "score": 0.5,
                "reason": "Error - defaulting to neutral"
            }
        }
