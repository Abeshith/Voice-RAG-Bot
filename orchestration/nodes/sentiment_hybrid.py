"""Hybrid sentiment classifier - keyword-based + model fallback"""

from orchestration.state import ConversationState
from typing import Dict, Any
from transformers import pipeline
from orchestration.latency_tracker import get_tracker


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
    """Hybrid sentiment classification returns: {"sentiment": "POSITIVE|NEGATIVE|NEUTRAL"}"""
    tracker = get_tracker()
    tracker.start("sentiment_analysis")
    
    user_input = state['user_input'].lower()
    
    # Step 1: Check strong sentiment words first
    strong_negative = ["frustrated", "angry", "hate", "terrible", "broken", "worst", "useless", "unacceptable"]
    strong_positive = ["thank", "love", "great", "excellent", "amazing", "perfect", "wonderful", "fantastic"]
    
    if any(word in user_input for word in strong_negative):
        tracker.end("sentiment_analysis")
        return {"sentiment": "NEGATIVE"}
    
    if any(word in user_input for word in strong_positive):
        tracker.end("sentiment_analysis")
        return {"sentiment": "POSITIVE"}
    
    # Step 2: Check FAQ keywords → typically NEUTRAL
    faq_keywords = ["policy", "return", "warranty", "shipping", "account", "details", "information", "how", "what", "tell me"]
    if any(kw in user_input for kw in faq_keywords):
        tracker.end("sentiment_analysis")
        return {"sentiment": "NEUTRAL"}
    
    # Step 3: Fall back to DistilBERT
    try:
        sentiment_pipeline = get_sentiment_model()
        result = sentiment_pipeline(state['user_input'][:512])[0]
        label = result['label'].upper()
        score = result['score']
        if label == "POSITIVE" and score > 0.7:
            tracker.end("sentiment_analysis")
            return {"sentiment": "POSITIVE"}
        elif label == "NEGATIVE" and score > 0.7:
            tracker.end("sentiment_analysis")
            return {"sentiment": "NEGATIVE"}
    except Exception:
        pass
    
    tracker.end("sentiment_analysis")
    return {"sentiment": "NEUTRAL"}
