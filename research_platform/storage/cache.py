import json
import hashlib
from typing import Optional, Any
from functools import lru_cache
from loguru import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheManager:
    def __init__(self, redis_url: Optional[str] = None, ttl: int = 3600):
        self.ttl = ttl
        self.redis_client = None
        self.in_memory_cache = {}
        
        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Redis connection failed, using in-memory cache: {e}")
        else:
            logger.info("Using in-memory cache")
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        data_str = json.dumps(data, sort_keys=True)
        hash_digest = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_digest}"
    
    def get(self, key: str) -> Optional[Any]:
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.in_memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        try:
            ttl = ttl or self.ttl
            value_json = json.dumps(value)
            
            if self.redis_client:
                self.redis_client.setex(key, ttl, value_json)
            else:
                self.in_memory_cache[key] = value
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str) -> None:
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.in_memory_cache.pop(key, None)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def clear(self) -> None:
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.in_memory_cache.clear()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")


@lru_cache()
def get_cache_manager(redis_url: Optional[str] = None) -> CacheManager:
    return CacheManager(redis_url=redis_url)
