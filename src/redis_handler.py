import redis

class RedisHandler:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)

    def get_value(self, key):
        value = self.redis_client.get(key)
        return value.decode('utf-8') if value is not None else None