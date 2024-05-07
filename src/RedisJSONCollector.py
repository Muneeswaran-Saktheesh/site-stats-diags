import json
import redis
from src.Collector import collect_fields

class RedisJSONCollector:
    """
    Connects to a Redis instance, collects JSON data, and sends it to the Collector class.
    """

    def __init__(self, host='localhost', port=6379, db=0):
        """
        Initializes the RedisJSONCollector object with connection parameters.

        Args:
            host (str): The Redis server host.
            port (int): The Redis server port.
            db (int): The Redis database number.
        """
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)

    def collect_json_data(self, key):
        """
        Collects JSON data from Redis.

        Args:
            key (str): The key to retrieve JSON data from Redis.

        Returns:
            dict: The JSON data as a dictionary.
        """
        json_data = self.redis_client.get(key)
        if json_data:
            return json.loads(json_data)
        else:
            return None

    def collect_and_process_data(self, key):
        """
        Collects JSON data from Redis, processes it, and returns it in the required format.

        Args:
            key (str): The key to retrieve JSON data from Redis.

        Returns:
            list: A list of Charger objects populated with the collected JSON data.
        """
        json_data = self.collect_json_data(key)
        if json_data:
            chargers = json_data.get("chargers", [])
            return collect_fields(chargers)
        else:
            return None

if __name__ == "__main__":
    # Example usage
    redis_collector = RedisJSONCollector()
    data = redis_collector.collect_and_process_data("chargers_data")
    if data:
        for charger in data:
            print("Charger ID:", charger.charger_id)
            print("Firmware Version:", charger.firmware_version)
            print("IP Address:", charger.ip_address)
            print("Status:", charger.status)
            for connector in charger.connectors:
                print("Connector ID:", connector.connector_id)
                print("Status:", connector.status)
                print("OCPP Error Code:", connector.ocpp_error_code)
                print("OCPP Error Info:", connector.ocpp_error_info)
                print("OCPP Error Timestamp:", connector.ocpp_error_timestamp)
            print("--------------------")
    else:
        print("No data found.")
