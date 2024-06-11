import redis
import logging

class RedisHandler:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_client = self.connect()

    def connect(self):
        """
        Establish a connection to the Redis server.
        """
        try:
            client = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password)
            # Test the connection
            client.ping()
            logging.info("Connected to Redis server successfully")
            return client
        except redis.ConnectionError as e:
            logging.error(f"Could not connect to Redis server: {e}")
            raise e

    def get_value(self, key):
        """
        Retrieve a value from Redis by key.
        """
        try:
            value = self.redis_client.get(key)
            return value.decode('utf-8') if value is not None else None
        except redis.RedisError as e:
            logging.error(f"Error retrieving key {key} from Redis: {e}")
            return None

    def set_value(self, key, value):
        """
        Set a value in Redis by key.
        """
        try:
            self.redis_client.set(key, value)
            logging.info(f"Key {key} set successfully")
        except redis.RedisError as e:
            logging.error(f"Error setting key {key} in Redis: {e}")

    def delete_value(self, key):
        """
        Delete a value from Redis by key.
        """
        try:
            result = self.redis_client.delete(key)
            if result == 1:
                logging.info(f"Key {key} deleted successfully")
            else:
                logging.info(f"Key {key} does not exist")
        except redis.RedisError as e:
            logging.error(f"Error deleting key {key} from Redis: {e}")

    def exists(self, key):
        """
        Check if a key exists in Redis.
        """
        try:
            return self.redis_client.exists(key) == 1
        except redis.RedisError as e:
            logging.error(f"Error checking existence of key {key} in Redis: {e}")
            return False

# Example usage:
# redis_handler = RedisHandler()
# redis_handler.set_value('test_key', 'test_value')
# value = redis_handler.get_value('test_key')
# print(value)
# redis_handler.delete_value('test_key')
# print(redis_handler.exists('test_key'))
