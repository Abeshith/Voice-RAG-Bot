"""Named entity extraction using BERT-NER"""

from transformers import pipeline
from orchestration.state import ConversationState
from typing import Dict, Any
from orchestration.latency_tracker import get_tracker


# Global model cache
_ner_model = None


def get_ner_model():
    """Load NER model once and cache"""
    global _ner_model
    if _ner_model is None:
        _ner_model = pipeline(
            "token-classification",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
    return _ner_model


def entity_extraction_node(state: ConversationState) -> Dict[str, Any]:
    """
    Extract named entities from user input
    Uses token classification model to identify entity types
    
    Returns:
        state update with entities field
    """
    tracker = get_tracker()
    tracker.start("entity_extraction")
    
    try:
        ner_pipeline = get_ner_model()
        
        # Extract entities
        entities_raw = ner_pipeline(state['user_input'])
        
        # Format entities as dict with types
        entities_dict = {}
        for entity in entities_raw:
            entity_type = entity['entity_group']
            if entity_type not in entities_dict:
                entities_dict[entity_type] = []
            entities_dict[entity_type].append(entity['word'])
        
        # Return formatted entities
        tracker.end("entity_extraction")
        if entities_dict:
            return {"entities": entities_dict}
        else:
            return {"entities": None}
    except Exception as e:
        tracker.end("entity_extraction")
        return {"entities": None}
