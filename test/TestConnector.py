# test_connector.py
import unittest
from connector import Connector

class TestConnector(unittest.TestCase):
    """
    Unit tests for the Connector class.
    """

    def test_init(self):
        """
        Test the initialization of the Connector object.
        """
        connector = Connector(1, "available", "NoError", None, None)
        self.assertEqual(connector.connector_id, 1)
        self.assertEqual(connector.status, "available")
        self.assertEqual(connector.ocpp_error_code, "NoError")
        self.assertIsNone(connector.ocpp_error_info)
        self.assertIsNone(connector.ocpp_error_timestamp)

if __name__ == '__main__':
    unittest.main()
