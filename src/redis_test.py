import random
import os
from rediscluster import RedisCluster

print("0")

# Get the Redis URL from environment variables
redis_uri = os.getenv("REDIS_URI")

print(redis_uri)

# redis_instance = redis.from_url(redis_url, decode_responses=True)
redis_instance = RedisCluster.from_url(redis_uri, decode_responses=True)

print("1")

auto_expire_nonce = 60 * 10

print("2")

redis_instance.setex(
    f"{random.randint(0, 1000000)}", auto_expire_nonce, random.randint(0, 1000000)
)

print("3")
