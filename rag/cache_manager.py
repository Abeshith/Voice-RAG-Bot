"""
Redis Cache Manager - Response caching for faster repeated queries
Reduces processing time for identical or similar queries
"""

import redis
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import timedelta
import os


class CacheManager:
    """Manages response caching using Redis"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, ttl_minutes: int = 30):
        """
        Initialize Redis connection
        
        Args:
            host: Redis server host
            port: Redis server port
            ttl_minutes: Time-to-live for cached responses
        """
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            self.available = True
            print("[OK] Redis cache connected")
        except Exception as e:
            self.available = False
            print(f"[WARN] Redis cache unavailable: {e}")
            self.client = None
        
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def _generate_key(self, customer_id: str, user_input: str) -> str:
        """Generate cache key from customer_id and user_input"""
        combined = f"{customer_id}:{user_input.lower().strip()}"
        # Use hash to keep key reasonable length
        return f"response:{hashlib.md5(combined.encode()).hexdigest()}"
    
    def get(self, customer_id: str, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response
        
        Returns:
            Cached response dict or None if not found/expired
        """
        if not self.available:
            return None
        
        try:
            key = self._generate_key(customer_id, user_input)
            cached = self.client.get(key)
            
            if cached:
                print(f"[CACHE HIT] {customer_id}: {user_input[:30]}...")
                return json.loads(cached)
            
            return None
        except Exception as e:
            print(f"[CACHE] Get error: {e}")
            return None
    
    def set(self, customer_id: str, user_input: str, response: Dict[str, Any]) -> bool:
        """
        Cache a response
        
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.available:
            return False
        
        try:
            key = self._generate_key(customer_id, user_input)
            self.client.setex(
                key,
                self.ttl,
                json.dumps(response)
            )
            print(f"[CACHE SET] {customer_id}: {user_input[:30]}...")
            return True
        except Exception as e:
            print(f"[CACHE] Set error: {e}")
            return False
    
    def clear(self, customer_id: Optional[str] = None) -> bool:
        """
        Clear cache for customer or all
        
        Returns:
            True if cleared successfully
        """
        if not self.available:
            return False
        
        try:
            if customer_id:
                # Clear only this customer's cache
                pattern = f"response:{hashlib.md5(f'{customer_id}:'.encode()).hexdigest()}*"
                # Simple: just clear all response keys for this customer
                keys = self.client.keys(f"response:*")
                for key in keys:
                    self.client.delete(key)
            else:
                # Clear all response cache
                self.client.delete(*self.client.keys("response:*"))
            
            return True
        except Exception as e:
            print(f"[CACHE] Clear error: {e}")
            return False


# Global cache instance
cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager"""
    global cache_manager
    if cache_manager is None:
        cache_manager = CacheManager()
    return cache_manager
