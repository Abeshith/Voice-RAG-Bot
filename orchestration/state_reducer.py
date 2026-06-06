from typing import Dict, Any, List, Callable
from orchestration.state import ConversationState


class FieldReducer:
    """Phase 3: State field merge strategies for parallel node execution"""
    
    @staticmethod
    def merge_intent(existing: str, new: str) -> str:
        if not existing or existing == "other":
            return new
        if not new or new == "other":
            return existing
        return new
    
    @staticmethod
    def merge_sentiment(existing: str, new: str) -> str:
        if not existing or existing == "NEUTRAL":
            return new
        if not new or new == "NEUTRAL":
            return existing
        return existing
    
    @staticmethod
    def merge_entities(existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        if not existing:
            return new if new else {}
        if not new:
            return existing
        merged = existing.copy()
        for entity_type, values in new.items():
            if entity_type in merged:
                existing_vals = set(merged[entity_type]) if isinstance(merged[entity_type], list) else {merged[entity_type]}
                new_vals = set(values) if isinstance(values, list) else {values}
                merged[entity_type] = list(existing_vals | new_vals)
            else:
                merged[entity_type] = values
        return merged
    
    @staticmethod
    def merge_response(existing: str, new: str) -> str:
        if not existing:
            return new
        if not new:
            return existing
        return new if len(new) >= len(existing) else existing
    
    @staticmethod
    def merge_kb_context(existing: str, new: str) -> str:
        if not existing:
            return new
        if not new:
            return existing
        return new
    
    @staticmethod
    def merge_history_context(existing: str, new: str) -> str:
        if not existing:
            return new
        if not new:
            return existing
        return new
    
    REDUCERS: Dict[str, Callable] = {
        "intent": merge_intent.__func__,
        "sentiment": merge_sentiment.__func__,
        "entities": merge_entities.__func__,
        "response": merge_response.__func__,
        "kb_context": merge_kb_context.__func__,
        "history_context": merge_history_context.__func__,
    }


class StateReducerManager:
    """Manages state merging when multiple nodes update same fields"""
    
    @staticmethod
    def apply_updates(base_state: Dict[str, Any], *updates: Dict[str, Any]) -> Dict[str, Any]:
        result = base_state.copy()
        
        for update in updates:
            for key, value in update.items():
                if key in FieldReducer.REDUCERS:
                    reducer = FieldReducer.REDUCERS[key]
                    existing = result.get(key)
                    result[key] = reducer(existing, value)
                else:
                    result[key] = value
        
        return result
    
    @staticmethod
    def merge_parallel_outputs(outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not outputs:
            return {}
        
        merged = outputs[0].copy()
        
        for output in outputs[1:]:
            for key, value in output.items():
                if key in FieldReducer.REDUCERS:
                    reducer = FieldReducer.REDUCERS[key]
                    existing = merged.get(key)
                    merged[key] = reducer(existing, value)
                else:
                    merged[key] = value
        
        return merged
    
    @staticmethod
    def validate_state(state: Dict[str, Any]) -> bool:
        required_fields = {
            "user_input": str,
            "customer_id": str,
            "intent": str,
            "sentiment": str,
            "response": str,
        }
        
        for field, expected_type in required_fields.items():
            if field not in state:
                return False
            if not isinstance(state[field], expected_type):
                return False
        
        return True
