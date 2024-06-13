import json
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

# Ensure that the main function and other modules are correctly imported
from src.site_status_diags import main
from src.redis_handler import RedisHandler
from src.site_status import SiteStatus
from src.charging_stations_status import ChargingStationsStatus
from src.dnsmasq_leases import DnsmasqLeases

class TestMainFunction(unittest.TestCase):

    @patch('src.redis_handler.RedisHandler.get_value')
    @patch('src.dnsmasq_leases.DnsmasqLeases.read_leases')
    @patch('src.site_status.SiteStatus.from_json')
    @patch('src.charging_stations_status.ChargingStationsStatus.from_json')
    @patch('src.site_status.SiteStatus.display')
    @patch('src.dnsmasq_leases.DnsmasqLeases.__init__', return_value=None)  # Mock __init__ to do nothing
    def test_main(
            self, mock_dnsmasq_init, mock_display, mock_charging_stations_from_json,
            mock_site_status_from_json, mock_read_leases, mock_get_value):

        # Mock return values for Redis get_value
        mock_get_value.side_effect = [
            json.dumps({"status": "active", "error": None, "datetime": "2023-01-01T00:00:00Z", "charging_stations": [], "evs": [], "offline_chargers": []}),
            json.dumps({"chargers": []})
        ]

        # Mock return values for from_json methods
        mock_site_status_instance = MagicMock()
        mock_site_status_from_json.return_value = mock_site_status_instance

        mock_charging_status_instance = MagicMock()
        mock_charging_stations_from_json.return_value = mock_charging_status_instance

        # Mock the DnsmasqLeases read_leases method to do nothing
        mock_read_leases.return_value = None

        with patch('builtins.print') as mock_print:
            main()

            # Check if Redis get_value was called correctly
            mock_get_value.assert_any_call('cgw/SiteStatus')
            mock_get_value.assert_any_call('cgw/ChargingStationsStatus')

            # Check if from_json was called with the correct data
            mock_site_status_from_json.assert_called_once_with({"status": "active", "error": None, "datetime": "2023-01-01T00:00:00Z", "charging_stations": [], "evs": [], "offline_chargers": []})
            mock_charging_stations_from_json.assert_called_once_with({"chargers": []})

            # Check if read_leases was called
            mock_read_leases.assert_called_once()

            # Ensure the site_status instance used is the one we mocked
            mock_site_status_instance.display.assert_called_once_with(
                mock.ANY,  # dnsmasq_leases instance
                mock_charging_status_instance
            )

            # Ensure that `print` was called but with specific content
            mock_print.assert_called()

if __name__ == '__main__':
    unittest.main()
