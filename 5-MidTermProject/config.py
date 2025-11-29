# central configuration file

REDIS_URL = "redis://localhost:6379"
EMBEDDING_MODEL = "text-embedding-3-small"
INDEX_NAME = "documents"

DEFAULT_MODEL = "gpt-4.1-nano"
TEMPERATURE = 0.2
MAX_TOKENS = 512

# Cache
CACHE_TTL_SECONDS = 1800 # 30 minutes