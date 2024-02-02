import redis
import os

# Get the Redis URL from environment variables
redis_url = os.getenv('REDIS_URL')

redis_instance = redis.from_url(redis_url, decode_responses=True)
