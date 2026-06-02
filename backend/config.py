"""
Central Configuration Management using Pydantic Settings
Loads environment variables from .env file
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""
    
    # Groq LLM Configuration
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.7
    groq_max_tokens: int = 1024
    
    # Qdrant Vector Database Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None  # Optional for local Docker setup
    
    # Embedding Model Configuration
    embedding_model: str = "BAAI/bge-m3"
    embedding_batch_size: int = 32
    
    # Collection Names
    kb_collection_name: str = "knowledge_base"
    history_collection_name: str = "customer_history"
    
    # Vector Dimensions (BGE-M3 uses 1024 dimensions)
    vector_dimension: int = 1024
    
    # Model Configuration for NLP Tasks
    sentiment_model: str = "distilbert-base-uncased-finetuned-sst-2-english"
    
    # Application Configuration
    app_name: str = "Voice RAG Bot"
    app_version: str = "1.0.0"
    debug_mode: bool = False
    
    # Conversation Memory
    max_conversation_history: int = 10
    summary_interval: int = 5  # Generate summary every 5 turns
    
    # Audio Configuration
    sample_rate: int = 16000  # 16kHz for Whisper
    audio_format: str = "wav"
    
    class Config:
        """Pydantic config for reading from .env file"""
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False
        extra = "ignore"  # Ignore unknown fields from .env
        
    def __repr__(self) -> str:
        """String representation (hides API keys)"""
        return (
            f"Settings("
            f"groq_model={self.groq_model}, "
            f"qdrant_url={self.qdrant_url}, "
            f"embedding_model={self.embedding_model})"
        )


# Global settings instance
settings = Settings()
