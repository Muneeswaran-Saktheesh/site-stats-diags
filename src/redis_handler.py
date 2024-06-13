import redis
import logging


class RedisHandler:
    def __init__(self, host='localhost', port=6379, db=0, password=None, external_host=None, external_port=None,
                 external_password=None):
        self.local_config = {
            'host': host,
            'port': port,
            'db': db,
            'password': password
        }
        self.external_config = {
            'host': external_host,
            'port': external_port,
            'db': db,
            'password': external_password
        } if external_host and external_port else None
        self.redis_client = self.connect()

    def connect(self):
        """
        Establish a connection to the Redis server.
        First try the external configuration, then fall back to local.
        """
        if self.external_config:
            try:
                client = redis.StrictRedis(**self.external_config)
                client.ping()
                logging.info("Connected to external Redis server successfully")
                return client
            except redis.ConnectionError as e:
                logging.error(f"Could not connect to external Redis server: {e}")

        # Fall back to local Redis connection
        try:
            client = redis.StrictRedis(**self.local_config)
            client.ping()
            logging.info("Connected to local Redis server successfully")
            return client
        except redis.ConnectionError as e:
            logging.error(f"Could not connect to local Redis server: {e}")
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
# For external Redis server, provide external_host, external_port, and external_password
# redis_handler = RedisHandler(external_host='external_host', external_port=6379, external_password='external_password')

# For local Redis server
# redis_handler = RedisHandler()
