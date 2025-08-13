import redis

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Scan and fetch all keys
for key in redis_client.scan_iter():
    value = redis_client.get(key)
    print(f"{key} => {value}")
