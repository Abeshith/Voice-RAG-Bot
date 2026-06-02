"""
Sentiment Analysis Node - Emotion detection using DistilBERT
Analyzes user input sentiment for tone-aware response generation
"""

from transformers import pipeline
from orchestration.state import ConversationState
from typing import Dict, Any


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


def sentiment_analysis_node(state: ConversationState) -> Dict[str, Any]:
    """
    Analyze sentiment of user input using DistilBERT
    
    Returns:
        state update with sentiment field populated:
        {"sentiment": {"label": "POSITIVE|NEGATIVE|NEUTRAL", "score": float}}
    """
    try:
        # Use cached model
        sentiment_pipeline = get_sentiment_model()
        
        # Analyze ONLY user input
        result = sentiment_pipeline(state['user_input'])[0]
        
        sentiment = {
            "label": result['label'].upper(),  # POSITIVE, NEGATIVE, or NEUTRAL
            "score": result['score']
        }
        
        return {"sentiment": sentiment}
    except Exception as e:
        # Default to neutral on error
        return {"sentiment": {"label": "NEUTRAL", "score": 0.5}}
