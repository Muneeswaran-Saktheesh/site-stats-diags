# test_charger.py
import unittest
from src import Charger

class TestCharger(unittest.TestCase):
    """
    Unit tests for the Charger class.
    """

    def test_init(self):
        """
        Test the initialization of the Charger object.
        """
        charger = Charger("ACE0237625", "6.5.0-QA2-LA-9332", "172.22.0.220", "online", [])
        self.assertEqual(charger.charger_id, "ACE0237625")
        self.assertEqual(charger.firmware_version, "6.5.0-QA2-LA-9332")
        self.assertEqual(charger.ip_address, "172.22.0.220")
        self.assertEqual(charger.status, "online")
        self.assertEqual(charger.connectors, [])

if __name__ == '__main__':
    unittest.main()
