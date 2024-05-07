import unittest
from unittest.mock import patch
from src import RedisJSONCollector


class TestRedisJSONCollector(unittest.TestCase):
    """
    Unit tests for the RedisJSONCollector class.
    """

    @patch('redis.StrictRedis')
    def test_collect_json_data(self, mock_redis):
        """
        Test the collect_json_data method.
        """
        # Setup
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.get.return_value = '{"chargers": [{"id": "ACE0237625", "firmware_version": "6.5.0-QA2-LA-9332", "ip_address": "172.22.0.220", "status": "online", "connectors": [{"id": 1, "status": "available", "ocpp_error_code": "NoError", "ocpp_error": null}]}]}'

        # Instantiate RedisJSONCollector
        redis_collector = RedisJSONCollector()

        # Test
        json_data = redis_collector.collect_json_data("test_key")

        # Assertions
        self.assertEqual(json_data['chargers'][0]['id'], 'ACE0237625')
        self.assertEqual(json_data['chargers'][0]['firmware_version'], '6.5.0-QA2-LA-9332')
        self.assertEqual(json_data['chargers'][0]['ip_address'], '172.22.0.220')
        self.assertEqual(json_data['chargers'][0]['status'], 'online')
        self.assertEqual(json_data['chargers'][0]['connectors'][0]['id'], 1)
        self.assertEqual(json_data['chargers'][0]['connectors'][0]['status'], 'available')
        self.assertEqual(json_data['chargers'][0]['connectors'][0]['ocpp_error_code'], 'NoError')
        self.assertIsNone(json_data['chargers'][0]['connectors'][0]['ocpp_error'])

    @patch('redis.StrictRedis')
    def test_collect_and_process_data(self, mock_redis):
        """
        Test the collect_and_process_data method.
        """
        # Setup
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.get.return_value = '{"chargers": [{"id": "ACE0237625", "firmware_version": "6.5.0-QA2-LA-9332", "ip_address": "172.22.0.220", "status": "online", "connectors": [{"id": 1, "status": "available", "ocpp_error_code": "NoError", "ocpp_error": null}]}]}'

        # Instantiate RedisJSONCollector
        redis_collector = RedisJSONCollector()

        # Test
        charger_objects = redis_collector.collect_and_process_data("test_key")

        # Assertions
        self.assertEqual(len(charger_objects), 1)
        charger = charger_objects[0]
        self.assertEqual(charger.charger_id, 'ACE0237625')
        self.assertEqual(charger.firmware_version, '6.5.0-QA2-LA-9332')
        self.assertEqual(charger.ip_address, '172.22.0.220')
        self.assertEqual(charger.status, 'online')
        self.assertEqual(len(charger.connectors), 1)
        connector = charger.connectors[0]
        self.assertEqual(connector.connector_id, 1)
        self.assertEqual(connector.status, 'available')
        self.assertEqual(connector.ocpp_error_code, 'NoError')
        self.assertIsNone(connector.ocpp_error)


if __name__ == '__main__':
    unittest.main()
