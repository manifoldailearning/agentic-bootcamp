# cache_store.py
import config
import redis 
import logging
REDIS_URL = config.REDIS_URL
CACHE_TTL_SECONDS = config.CACHE_TTL_SECONDS

# Initialize Redis client
try:
    redis_client = redis.Redis.from_url(REDIS_URL)
    redis_client.ping() # test the connection
    logging.info("Redis connection successful")
except Exception as e:
    logging.error(f"Error: {e}")
    redis_client = None


# key (query), value (response from llm) , ttl (time to live)

def _key(k: str) -> str:
    return f"rag:cache:{k}"

def get(k:str):
    _value = redis_client.get(_key(k))
    return _value.decode() if _value else None

def set(k:str, v:str, ttl:int = CACHE_TTL_SECONDS):
    redis_client.setex(_key(k), ttl, v)