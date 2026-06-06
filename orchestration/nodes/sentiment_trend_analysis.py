"""Phase 16: Sentiment Trend Analysis - Detect sentiment patterns and predict escalation"""

from orchestration.state import ConversationState
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import threading
import logging

logger = logging.getLogger(__name__)

_cross_thread_lock = threading.RLock()
_cross_thread_memory = {}

SENTIMENT_WEIGHT = {"NEGATIVE": -1, "NEUTRAL": 0, "POSITIVE": 1}


def sentiment_trend_analysis_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 16: Sentiment Trend Analysis
    
    Detects sentiment patterns and predicts escalation needs
    
    Features:
    1. Track sentiment history per user
    2. Detect consecutive negative sentiments (trend detection)
    3. Calculate sentiment trend (improving/declining/stable)
    4. Recommend escalation based on trend patterns
    5. Provide predictive escalation signals
    
    Trend Detection Rules:
    - 2+ consecutive NEGATIVE: Low trend alert
    - 3+ consecutive NEGATIVE: Medium trend alert (auto-escalate)
    - 4+ consecutive NEGATIVE: High trend alert (strong escalation)
    - 3+ improvements from baseline: Positive trend (deescalate consideration)
    
    Input State Fields:
    - user_id: Authenticated user identifier
    - sentiment: Current sentiment (POSITIVE/NEGATIVE/NEUTRAL)
    - session_id: Current session
    - user_escalation_state: Current escalation state
    
    Output:
    - sentiment_history: User's recent sentiment sequence
    - sentiment_trend: Direction of sentiment (improving/declining/stable)
    - consecutive_negative_count: Count of consecutive negative sentiments
    - trend_escalation_recommended: Whether trend indicates escalation needed
    - trend_escalation_reason: Reason for escalation recommendation
    - sentiment_trend_score: Numerical trend score (-1 to +1)
    - trend_analysis_status: Operation status
    - escalation_confidence: Confidence level (0-100) for trend-based escalation
    """
    
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    current_sentiment = state.get("sentiment", "NEUTRAL")
    current_escalation_state = state.get("user_escalation_state", "none")
    
    if not user_id:
        return {
            "sentiment_history": [],
            "sentiment_trend": "stable",
            "consecutive_negative_count": 0,
            "trend_escalation_recommended": False,
            "trend_escalation_reason": "no_user",
            "sentiment_trend_score": 0.0,
            "trend_analysis_status": "no_user",
            "escalation_confidence": 0,
        }
    
    try:
        with _cross_thread_lock:
            sentiment_key = f"{user_id}:sentiment_history"
            
            sentiment_data = _cross_thread_memory.get(sentiment_key, {
                "data": {
                    "user_id": user_id,
                    "history": [],
                    "trend": "stable",
                }
            })
            
            sentiment_info = sentiment_data.get("data", {})
            history = sentiment_info.get("history", [])
            
            history.append({
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "sentiment": current_sentiment,
                "escalation_state_at_time": current_escalation_state,
            })
            
            history = history[-50:]
            
            sentiment_trend = "stable"
            consecutive_negative_count = 0
            trend_escalation_recommended = False
            trend_escalation_reason = ""
            sentiment_trend_score = 0.0
            escalation_confidence = 0
            
            if len(history) >= 2:
                recent_sentiments = [h["sentiment"] for h in history[-5:]]
                
                consecutive_negative_count = _count_consecutive(recent_sentiments, "NEGATIVE")
                consecutive_positive_count = _count_consecutive(recent_sentiments, "POSITIVE")
                
                trend_score = sum([SENTIMENT_WEIGHT.get(s, 0) for s in recent_sentiments[-3:]])
                
                if trend_score > 0:
                    sentiment_trend = "improving"
                    sentiment_trend_score = min(trend_score / 3.0, 1.0)
                elif trend_score < 0:
                    sentiment_trend = "declining"
                    sentiment_trend_score = max(trend_score / 3.0, -1.0)
                else:
                    sentiment_trend = "stable"
                    sentiment_trend_score = 0.0
                
                if consecutive_negative_count >= 4:
                    trend_escalation_recommended = True
                    trend_escalation_reason = "4_consecutive_negative_high_alert"
                    escalation_confidence = 95
                elif consecutive_negative_count >= 3:
                    trend_escalation_recommended = True
                    trend_escalation_reason = "3_consecutive_negative_medium_alert"
                    escalation_confidence = 85
                elif consecutive_negative_count >= 2:
                    trend_escalation_recommended = True
                    trend_escalation_reason = "2_consecutive_negative_low_alert"
                    escalation_confidence = 70
                
                if consecutive_positive_count >= 3 and current_escalation_state not in ["none"]:
                    trend_escalation_recommended = False
                    trend_escalation_reason = "positive_trend_deescalation"
                    escalation_confidence = 0
            
            sentiment_info["history"] = history
            sentiment_info["trend"] = sentiment_trend
            sentiment_info["updated_at"] = datetime.now().isoformat()
            
            _cross_thread_memory[sentiment_key] = {"data": sentiment_info}
            
            logger.debug(f"Sentiment trend: user={user_id}, trend={sentiment_trend}, consecutive_neg={consecutive_negative_count}, recommend_escalation={trend_escalation_recommended}")
            
            return {
                "sentiment_history": recent_sentiments if len(history) >= 2 else [],
                "sentiment_trend": sentiment_trend,
                "consecutive_negative_count": consecutive_negative_count,
                "trend_escalation_recommended": trend_escalation_recommended,
                "trend_escalation_reason": trend_escalation_reason,
                "sentiment_trend_score": sentiment_trend_score,
                "trend_analysis_status": "success",
                "escalation_confidence": escalation_confidence,
            }
        
    except Exception as e:
        logger.error(f"Sentiment trend analysis error (user_id={user_id}): {str(e)}")
        return {
            "sentiment_history": [],
            "sentiment_trend": "stable",
            "consecutive_negative_count": 0,
            "trend_escalation_recommended": False,
            "trend_escalation_reason": f"error: {str(e)}",
            "sentiment_trend_score": 0.0,
            "trend_analysis_status": f"error: {str(e)}",
            "escalation_confidence": 0,
        }


def _count_consecutive(sentiments: List[str], target: str) -> int:
    """Count consecutive occurrences of target sentiment from end of list"""
    if not sentiments:
        return 0
    
    count = 0
    for sentiment in reversed(sentiments):
        if sentiment == target:
            count += 1
        else:
            break
    
    return count


def get_sentiment_trend_for_user(user_id: str) -> Dict[str, Any]:
    """Retrieve sentiment trend information for user"""
    
    if not user_id:
        return {"trend": "stable", "history": []}
    
    try:
        with _cross_thread_lock:
            sentiment_key = f"{user_id}:sentiment_history"
            sentiment_data = _cross_thread_memory.get(sentiment_key, {})
            sentiment_info = sentiment_data.get("data", {})
            
            return {
                "trend": sentiment_info.get("trend", "stable"),
                "history": sentiment_info.get("history", []),
            }
    except Exception as e:
        logger.error(f"Error retrieving sentiment trend: {str(e)}")
        return {"trend": "stable", "history": []}


def clear_sentiment_history(user_id: str) -> bool:
    """Clear sentiment history for user when resetting escalation"""
    
    if not user_id:
        return False
    
    try:
        with _cross_thread_lock:
            sentiment_key = f"{user_id}:sentiment_history"
            if sentiment_key in _cross_thread_memory:
                _cross_thread_memory[sentiment_key] = {
                    "data": {
                        "user_id": user_id,
                        "history": [],
                        "trend": "stable",
                    }
                }
                logger.info(f"Sentiment history cleared for user: {user_id}")
                return True
        return False
    except Exception as e:
        logger.error(f"Error clearing sentiment history: {str(e)}")
        return False
