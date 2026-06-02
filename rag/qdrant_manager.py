"""
Qdrant Manager - Vector database client for RAG persistence and retrieval
Manages collections, embeddings, and search operations
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
from uuid import uuid4
from backend.config import settings


class QdrantManager:
    """Singleton for managing Qdrant vector database"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # Initialize Qdrant client
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key
            )
            self._initialized = True
            self._ensure_collections()
    
    def _ensure_collections(self):
        """Create collections if they don't exist"""
        collections = [
            settings.kb_collection_name,
            settings.history_collection_name
        ]
        
        for collection_name in collections:
            try:
                # Try to get collection info
                self.client.get_collection(collection_name)
            except Exception:
                # Create if doesn't exist
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=settings.vector_dimension,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created collection: {collection_name}")
    
    def add_to_kb(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to knowledge base collection
        
        Args:
            documents: List of dicts with 'id', 'text', 'embedding' keys
        """
        from rag.embedding_manager import embedding_manager
        
        points = []
        for doc in documents:
            embedding = embedding_manager.embed(doc['text'])
            point = PointStruct(
                id=int(uuid4().int % (10**8)),
                vector=embedding,
                payload={
                    "text": doc['text'],
                    "source": doc.get('source', 'unknown'),
                    "document_id": doc.get('document_id', str(uuid4()))
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=settings.kb_collection_name,
            points=points
        )
        print(f"✅ Added {len(documents)} documents to KB collection")
    
    def search_kb(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search knowledge base
        
        Args:
            query: Search query text
            limit: Number of results to return
            
        Returns:
            List of similar documents
        """
        from rag.embedding_manager import embedding_manager
        
        query_embedding = embedding_manager.embed(query)
        
        results = self.client.query_points(
            collection_name=settings.kb_collection_name,
            query=query_embedding,
            limit=limit
        ).points
        
        return [
            {
                "text": r.payload['text'],
                "source": r.payload.get('source', 'unknown'),
                "score": r.score
            }
            for r in results
        ]
    
    def search_history(self, query: str, customer_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search customer history with customer_id filter
        
        Args:
            query: Search query text
            customer_id: Filter by customer
            limit: Number of results
            
        Returns:
            List of similar history records for customer
        """
        from rag.embedding_manager import embedding_manager
        
        query_embedding = embedding_manager.embed(query)
        
        results = self.client.query_points(
            collection_name=settings.history_collection_name,
            query=query_embedding,
            limit=limit,
            query_filter={
                "must": [
                    {
                        "key": "customer_id",
                        "match": {"value": customer_id}
                    }
                ]
            }
        ).points
        
        return [
            {
                "text": r.payload['text'],
                "customer_id": r.payload.get('customer_id'),
                "interaction_type": r.payload.get('interaction_type'),
                "score": r.score
            }
            for r in results
        ]
    
    def add_to_history(self, customer_id: str, text: str, interaction_type: str) -> None:
        """
        Add conversation to customer history
        
        Args:
            customer_id: Customer identifier
            text: Conversation text
            interaction_type: Type of interaction (e.g., 'complaint', 'refund_request')
        """
        from rag.embedding_manager import embedding_manager
        
        embedding = embedding_manager.embed(text)
        point = PointStruct(
            id=int(uuid4().int % (10**8)),
            vector=embedding,
            payload={
                "customer_id": customer_id,
                "text": text,
                "interaction_type": interaction_type,
                "timestamp": str(__import__('datetime').datetime.now())
            }
        )
        
        self.client.upsert(
            collection_name=settings.history_collection_name,
            points=[point]
        )
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        info = self.client.get_collection(collection_name)
        return {
            "name": collection_name,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count
        }


# Global singleton instance
qdrant_manager = QdrantManager()
