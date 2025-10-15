import redis

client = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

def create(key, value):
    """Create a key-value pair if it doesn't already exist."""
    if client.exists(key):
        raise KeyError(f"Key '{key}' already exists.")
    client.set(key, value)
    return True

def read(key):
    """Read the value of a given key."""
    value = client.get(key)
    if value is None:
        raise KeyError(f"Key '{key}' not found.")
    return value

def update(key, value):
    """Update the value of an existing key."""
    if not client.exists(key):
        raise KeyError(f"Key '{key}' not found.")
    client.set(key, value)
    return True

def delete(key):
    """Delete a specific key."""
    if not client.exists(key):
        raise KeyError(f"Key '{key}' not found.")
    client.delete(key)
    return True

def list_keys(pattern='*'):
    """List all keys matching a given pattern."""
    return client.keys(pattern)

# Example usage:
# redis_util = RedisUtility()
# redis_util.create('user:1', 'Alice')
# print(redis_util.read('user:1'))
# redis_util.update('user:1', 'Bob')
# redis_util.delete('user:1')
