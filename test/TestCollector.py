# test_collector.py
import unittest
from src.Collector import collect_charger_fields, collect_connector_fields, collect_fields

class TestCollector(unittest.TestCase):
    """
    Unit tests for the collector functions.
    """

    def test_collect_charger_fields(self):
        """
        Test the collect_charger_fields function.
        """
        charger_data = {
            "id": "ACE0237625",
            "firmware_version": "6.5.0-QA2-LA-9332",
            "ip_address": "172.22.0.220",
            "status": "online",
            "connectors": []
        }
        charger = collect_charger_fields(charger_data)
        self.assertEqual(charger.charger_id, "ACE0237625")
        self.assertEqual(charger.firmware_version, "6.5.0-QA2-LA-9332")
        self.assertEqual(charger.ip_address, "172.22.0.220")
        self.assertEqual(charger.status, "online")
        self.assertEqual(charger.connectors, [])

    def test_collect_connector_fields(self):
        """
        Test the collect_connector_fields function.
        """
        connector_data = {
            "id": 1,
            "status": "available",
            "ocpp_error_code": "NoError",
            "ocpp_error": None
        }
        connector = collect_connector_fields(connector_data)
        self.assertEqual(connector.connector_id, 1)
        self.assertEqual(connector.status, "available")
        self.assertEqual(connector.ocpp_error_code, "NoError")
        self.assertIsNone(connector.ocpp_error_info)
        self.assertIsNone(connector.ocpp_error_timestamp)

    # Additional tests for collect_fields function can be added if needed

if __name__ == '__main__':
    unittest.main()
