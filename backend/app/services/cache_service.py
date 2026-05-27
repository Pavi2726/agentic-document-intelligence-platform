"""Redis caching service for production."""
import json
import hashlib
from typing import Optional, Any
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings


class CacheService:
    def __init__(self):
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            print("[Cache] Redis not available, caching disabled")
            return
        
        try:
            self.redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                password=getattr(settings, 'REDIS_PASSWORD', None),
                db=1,  # Use db 1 for caching (db 0 for sessions)
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            print("[Cache] Redis connected successfully")
        except Exception as e:
            print(f"[Cache] Redis connection failed: {e}")
            self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"cache:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"[Cache] Get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (default 5 minutes)."""
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"[Cache] Set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"[Cache] Delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"[Cache] Clear pattern error: {e}")
            return 0
    
    def cache_query_result(self, query: str, result: Any, ttl: int = 300):
        """Cache query result."""
        key = self._generate_key("query", query)
        return self.set(key, result, ttl)
    
    def get_cached_query(self, query: str) -> Optional[Any]:
        """Get cached query result."""
        key = self._generate_key("query", query)
        return self.get(key)
    
    def cache_document_chunks(self, filename: str, chunks: list, ttl: int = 3600):
        """Cache document chunks."""
        key = self._generate_key("doc_chunks", filename)
        return self.set(key, chunks, ttl)
    
    def get_cached_chunks(self, filename: str) -> Optional[list]:
        """Get cached document chunks."""
        key = self._generate_key("doc_chunks", filename)
        return self.get(key)
    
    def cache_vector_search(self, query: str, results: list, ttl: int = 600):
        """Cache vector search results."""
        key = self._generate_key("vector_search", query)
        return self.set(key, results, ttl)
    
    def get_cached_vector_search(self, query: str) -> Optional[list]:
        """Get cached vector search results."""
        key = self._generate_key("vector_search", query)
        return self.get(key)
    
    def cache_graph_query(self, query: str, results: list, ttl: int = 600):
        """Cache knowledge graph query results."""
        key = self._generate_key("graph_query", query)
        return self.set(key, results, ttl)
    
    def get_cached_graph_query(self, query: str) -> Optional[list]:
        """Get cached graph query results."""
        key = self._generate_key("graph_query", query)
        return self.get(key)
    
    def invalidate_document_cache(self, filename: str):
        """Invalidate all cache related to a document."""
        patterns = [
            f"cache:doc_chunks:*{filename}*",
            f"cache:vector_search:*",
            f"cache:query:*{filename}*"
        ]
        
        total = 0
        for pattern in patterns:
            total += self.clear_pattern(pattern)
        
        print(f"[Cache] Invalidated {total} keys for document: {filename}")
        return total
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.redis_client:
            return {"status": "disabled"}
        
        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global cache service instance
cache_service = CacheService()
