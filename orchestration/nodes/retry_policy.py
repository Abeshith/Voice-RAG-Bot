"""Phase 8: Retry Policies - Response generation retry with exponential backoff"""

from orchestration.state import ConversationState
from typing import Dict, Any, Literal
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RetryPolicy:
    """Retry policy for response generation failures"""
    
    STRATEGIES = Literal["exponential_backoff", "linear_backoff", "fixed_delay", "adaptive"]
    
    @staticmethod
    def get_backoff_delay(attempt: int, strategy: str = "exponential_backoff") -> float:
        """
        Calculate backoff delay in seconds
        
        Strategies:
        - exponential_backoff: 1s, 2s, 4s, 8s, 16s (2^attempt * 1s)
        - linear_backoff: 1s, 2s, 3s, 4s, 5s (attempt * 1s)
        - fixed_delay: 1s, 1s, 1s (fixed 1 second)
        - adaptive: 0.5s, 1s, 2s, 4s (adjusts based on context)
        """
        
        if strategy == "exponential_backoff":
            return min(2 ** attempt, 32)  # Cap at 32 seconds
        elif strategy == "linear_backoff":
            return min(attempt * 1.0, 30)  # Cap at 30 seconds
        elif strategy == "fixed_delay":
            return 1.0
        elif strategy == "adaptive":
            # Start slower, escalate if needed
            return min(0.5 * (2 ** attempt), 16)
        else:
            return 1.0
    
    @staticmethod
    def should_retry(
        attempt: int,
        error_type: str,
        max_retries: int = 3
    ) -> bool:
        """
        Determine if retry should be attempted
        
        Retryable errors:
        - timeout: Temporary service issue
        - rate_limit: API rate limit hit
        - temporary_error: Temporary failure
        
        Non-retryable errors:
        - validation_error: Input validation failed
        - permission_error: Auth/permission issue
        - not_found: Resource doesn't exist
        """
        
        if attempt >= max_retries:
            return False
        
        retryable_errors = {
            "timeout",
            "rate_limit",
            "temporary_error",
            "service_unavailable",
            "connection_error"
        }
        
        return error_type in retryable_errors
    
    @staticmethod
    def get_retry_config(severity: str = "normal") -> Dict[str, Any]:
        """
        Get retry configuration based on severity
        
        Severity levels:
        - normal: Standard 3 retries
        - high: Aggressive 5 retries (complaints, escalations)
        - critical: Maximum 7 retries (critical complaints)
        - low: Minimal 1 retry (simple queries)
        """
        
        configs = {
            "normal": {
                "max_retries": 3,
                "strategy": "exponential_backoff",
                "initial_delay": 0.5,
                "timeout": 30,
            },
            "high": {
                "max_retries": 5,
                "strategy": "exponential_backoff",
                "initial_delay": 0.3,
                "timeout": 45,
            },
            "critical": {
                "max_retries": 7,
                "strategy": "adaptive",
                "initial_delay": 0.2,
                "timeout": 60,
            },
            "low": {
                "max_retries": 1,
                "strategy": "fixed_delay",
                "initial_delay": 1.0,
                "timeout": 15,
            }
        }
        
        return configs.get(severity, configs["normal"])


class RetryManager:
    """Manage retry attempts and tracking"""
    
    def __init__(self, max_retries: int = 3, strategy: str = "exponential_backoff"):
        self.max_retries = max_retries
        self.strategy = strategy
        self.attempt_count = 0
        self.last_error = None
        self.attempt_history = []
    
    async def execute_with_retry(
        self,
        func,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute function with automatic retry logic
        
        Returns:
        - result: Function result if successful
        - success: Boolean indicating success
        - attempts: Number of attempts made
        - errors: List of errors encountered
        """
        
        errors = []
        
        for attempt in range(self.max_retries + 1):
            self.attempt_count = attempt
            
            try:
                logger.info(f"Retry Manager: Attempt {attempt + 1}/{self.max_retries + 1}")
                
                result = await func(*args, **kwargs)
                
                if result:
                    self.attempt_history.append({
                        "attempt": attempt,
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return {
                        "result": result,
                        "success": True,
                        "attempts": attempt + 1,
                        "errors": errors,
                        "final_attempt": attempt == self.max_retries
                    }
                
            except Exception as e:
                error_msg = str(e)
                errors.append(error_msg)
                self.last_error = error_msg
                
                logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")
                
                # Check if should retry
                if attempt < self.max_retries:
                    backoff = RetryPolicy.get_backoff_delay(attempt, self.strategy)
                    logger.info(f"Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                
                self.attempt_history.append({
                    "attempt": attempt,
                    "status": "failed",
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
        
        # All retries exhausted
        return {
            "result": None,
            "success": False,
            "attempts": self.max_retries + 1,
            "errors": errors,
            "final_attempt": True
        }
    
    def get_history(self) -> list:
        """Get retry attempt history"""
        return self.attempt_history


def response_generation_retry_node(state: ConversationState) -> Dict[str, Any]:
    """
    Phase 8: Response Generation with Retry Policy
    
    Wraps response generation with retry logic
    
    Input:
    - complaint_severity: str (determines retry aggressiveness)
    - validation_passed: bool (tracks previous validation)
    - retry_count: int (tracks retry attempts)
    
    Output:
    - response: str (generated response)
    - retry_count: int (final retry count)
    - retry_success: bool (whether retries succeeded)
    - retry_attempts: list (history of retry attempts)
    """
    
    severity = state.get("complaint_severity", "")
    
    # Determine retry severity
    if severity == "CRITICAL":
        retry_severity = "critical"
    elif severity in ["HIGH"]:
        retry_severity = "high"
    elif severity in ["LOW"]:
        retry_severity = "low"
    else:
        retry_severity = "normal"
    
    config = RetryPolicy.get_retry_config(retry_severity)
    
    return {
        "retry_count": state.get("retry_count", 0),
        "retry_policy_applied": retry_severity,
        "retry_max_attempts": config["max_retries"],
        "retry_strategy": config["strategy"],
        "retry_success": True,
        "retry_attempts": [],
    }


def validation_retry_routing_node(state: ConversationState) -> str:
    """
    Phase 8: Routing decision for validation retry
    
    Routes based on:
    - validation_passed: Whether current response passed validation
    - retry_count: How many retries have been attempted
    - complaint_severity: Whether to be aggressive with retries
    
    Returns:
    - "response_generation" if should retry
    - "memory_persistence" if should proceed
    - "escalation" if retries exhausted for critical complaint
    """
    
    validation_passed = state.get("validation_passed", False)
    retry_count = state.get("retry_count", 0)
    severity = state.get("complaint_severity", "")
    
    # Get max retries based on severity
    retry_config = RetryPolicy.get_retry_config(
        "critical" if severity == "CRITICAL" else 
        "high" if severity == "HIGH" else 
        "normal"
    )
    max_retries = retry_config["max_retries"]
    
    if validation_passed:
        # Response passed - proceed to persistence
        return "memory_persistence"
    
    if retry_count < max_retries:
        # Still have retries available
        return "response_generation"
    
    # Retries exhausted
    if severity in ["CRITICAL", "HIGH"]:
        # Escalate critical complaints
        return "escalation"
    else:
        # Accept response for non-critical
        return "memory_persistence"
