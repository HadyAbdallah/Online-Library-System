import redis
from app.config import settings

# Create a Redis client instance that can be imported and used by other parts of the app
redis_client = redis.from_url(settings.REDIS_URL)