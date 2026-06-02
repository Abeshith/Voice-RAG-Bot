"""
Embedding Manager - Singleton for BGE-M3 embeddings
Handles text → vector conversion for RAG queries and persistence
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from backend.config import settings


class EmbeddingManager:
    """Singleton for managing embeddings with BGE-M3"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.model = SentenceTransformer(settings.embedding_model)
            self._initialized = True
    
    def embed(self, text: str) -> List[float]:
        """
        Convert single text to embedding vector
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats (1024-dimensional for BGE-M3)
        """
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Convert multiple texts to embeddings (efficient batch processing)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(
            texts,
            batch_size=settings.embedding_batch_size,
            convert_to_tensor=False
        )
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return settings.vector_dimension


# Global singleton instance
embedding_manager = EmbeddingManager()
