import unittest
from datetime import datetime
from src.charging_stations_status import ChargingStationsStatus, Charger, Connector, OcppError


class TestChargingStationsStatus(unittest.TestCase):
    def test_get_ip_from_charger_id(self):
        chargers = [
            Charger(connectors=[], firmware_version="1.0", id="1", ip_address="192.168.1.1",
                    ocpp_error=OcppError(error_code="", info="", timestamp="", vendor_error_code="", vendor_id=""),
                    ocpp_error_code="", status=""),
            Charger(connectors=[], firmware_version="1.0", id="2", ip_address="192.168.1.2",
                    ocpp_error=OcppError(error_code="", info="", timestamp="", vendor_error_code="", vendor_id=""),
                    ocpp_error_code="", status="")
        ]
        charging_stations_status = ChargingStationsStatus(chargers)

        self.assertEqual(charging_stations_status.get_ip_from_charger_id("1"), "192.168.1.1")
        self.assertEqual(charging_stations_status.get_ip_from_charger_id("2"), "192.168.1.2")
        self.assertEqual(charging_stations_status.get_ip_from_charger_id("3"), "IP not found")

    def test_display(self):
        chargers = [
            Charger(
                connectors=[
                    Connector(id=1, ocpp_error=OcppError("", "", "", "", ""), ocpp_error_code="", priority=True,
                              status=""),
                    Connector(id=2, ocpp_error=OcppError("", "", "", "", ""), ocpp_error_code="", priority=False,
                              status="")
                ],
                firmware_version="1.0",
                id="1",
                ip_address="192.168.1.1",
                ocpp_error=OcppError("", "", "", "", ""),
                ocpp_error_code="",
                status=""
            ),
            Charger(
                connectors=[
                    Connector(id=3, ocpp_error=OcppError("", "", "", "", ""), ocpp_error_code="", priority=False,
                              status=""),
                    Connector(id=4, ocpp_error=OcppError("", "", "", "", ""), ocpp_error_code="", priority=True,
                              status="")
                ],
                firmware_version="1.0",
                id="2",
                ip_address="192.168.1.2",
                ocpp_error=OcppError("", "", "", "", ""),
                ocpp_error_code="",
                status=""
            )
        ]
        charging_stations_status = ChargingStationsStatus(chargers)

        output = charging_stations_status.display()

        # Assert output contains charger information
        self.assertIn("192.168.1.1", output)
        self.assertIn("192.168.1.2", output)

        # Assert output contains connector information
        self.assertIn("1", output)
        self.assertIn("2", output)
        self.assertIn("3", output)
        self.assertIn("4", output)

        # Assert output contains the string "UNKNOWN" for missing timestamps
        self.assertIn("UNKNOWN", output)

        # If there is a timestamp, it should be correctly formatted
        formatted_time = datetime.now().strftime("%y%m%d_%H%M")
        if any(connector.ocpp_error.timestamp for charger in chargers for connector in charger.connectors):
            self.assertIn(formatted_time, output)

        # Check specific structure and key elements in the output (further refinement can be added based on exact output format)
        self.assertIn("Chg ID", output)
        self.assertIn("Conn ID", output)
        self.assertIn("OCPP Err", output)
        self.assertIn("OCPP Err Ts", output)
        self.assertIn("Info", output)
        self.assertIn("Status", output)
        self.assertIn("IP Address", output)

if __name__ == '__main__':
    unittest.main()
