import unittest
from src.Collector import collect_charger_fields, collect_connector_fields, collect_fields

class TestCollector(unittest.TestCase):
    """
    A test class to verify the functionality of field collection functions.
    """

    def setUp(self):
        """
        Set up sample charger and connector data for testing.
        """
        self.charger = {
            "id": "ACE0237625",
            "firmware_version": "6.5.0-QA2-LA-9332",
            "ip_address": "172.22.0.220",
            "status": "online",
            "connectors": [
                {
                    "id": 1,
                    "status": "available",
                    "ocpp_error_code": "NoError",
                    "ocpp_error": None
                }
            ]
        }

        self.connector = {
            "id": 1,
            "status": "available",
            "ocpp_error_code": "NoError",
            "ocpp_error": None
        }

    def test_collect_charger_fields(self):
        """
        Test the collect_charger_fields function.
        """
        charger_id, firmware_version, ip_address, status = collect_charger_fields(self.charger)
        self.assertEqual(charger_id, "ACE0237625")
        self.assertEqual(firmware_version, "6.5.0-QA2-LA-9332")
        self.assertEqual(ip_address, "172.22.0.220")
        self.assertEqual(status, "online")

    def test_collect_connector_fields(self):
        """
        Test the collect_connector_fields function.
        """
        connector_id, connector_status, ocpp_error_code, ocpp_error_info, ocpp_error_timestamp = collect_connector_fields(self.connector)
        self.assertEqual(connector_id, 1)
        self.assertEqual(connector_status, "available")
        self.assertEqual(ocpp_error_code, "NoError")
        self.assertIsNone(ocpp_error_info)
        self.assertIsNone(ocpp_error_timestamp)

    def test_collect_fields(self):
        """
        Test the collect_fields function.
        """
        chargers = [self.charger]
        collected_fields = collect_fields(chargers)
        self.assertEqual(len(collected_fields["charger_ids"]), 1)
        self.assertEqual(len(collected_fields["firmware_versions"]), 1)
        self.assertEqual(len(collected_fields["ip_addresses"]), 1)
        self.assertEqual(len(collected_fields["statuses"]), 1)
        self.assertEqual(len(collected_fields["connector_ids"]), 1)
        self.assertEqual(len(collected_fields["connector_statuses"]), 1)
        self.assertEqual(len(collected_fields["ocpp_error_codes"]), 1)
        self.assertEqual(len(collected_fields["ocpp_error_infos"]), 1)
        self.assertEqual(len(collected_fields["ocpp_error_timestamps"]), 1)

if __name__ == '__main__':
    unittest.main()
